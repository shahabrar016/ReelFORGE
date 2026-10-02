#!/usr/bin/env python3
"""
ReelForge — Manim animation + AI voiceover (Gemini TTS / ElevenLabs) -> ready-to-post vertical reel.

Commands
  python reelforge.py voice   project.yaml   # generate voice blocks + timings.json (audio-first workflow)
  python reelforge.py analyze project.yaml   # render/analyse video, print the placement plan, no final render
  python reelforge.py build   project.yaml   # full pipeline -> output mp4

How placement works
  1. Every narration block is generated (or loaded), silence-trimmed and measured.
  2. The video is cut into "beats":
       - Manim sections (self.next_section) if available, otherwise
       - animation starts detected with ffmpeg freezedetect (end of each self.wait()).
  3. Blocks are matched to beats:
       - direct mode: every block names its section
       - auto mode:   dynamic programming over (blocks x beats) that minimises
                      frozen-frame time (audio longer than its visuals) and dead air.
  4. Where a block needs more time than its visuals, the last frame of that beat is held.
  5. ffmpeg composes a 1080x1920 H.264 reel: mixed voice, optional ducked music,
     loudness-normalised to -14 LUFS, optional word-highlight captions.
"""
from __future__ import annotations

import argparse
import base64
import hashlib
import json
import os
import re
import subprocess
import sys
import wave
from dataclasses import dataclass, field
from pathlib import Path

import yaml

# --------------------------------------------------------------------------- defaults
DEFAULT_REEL = {
    "width": 1080, "height": 1920, "fps": 30,
    "fit": "blur",            # blur | pad | crop  (how a non-9:16 video is fitted)
    "pad_color": "black",
    "lead": 0.25,             # delay between a beat starting and its narration starting
    "gap": 0.25,              # pause between consecutive blocks in the same beat
    "tail": 0.35,             # breathing room after the last block of a beat
    "end_hold": 0.8,          # extra hold on the very last frame
    "overflow_weight": 1.0,   # auto-align cost of frozen frames (per second)
    "silence_weight": 0.3,    # auto-align cost of animation playing with no voice (per second)
    "sync_weight": 0.6,       # auto-align cost per extra block/beat merged into one group (keeps voice on cue)
    "captions": True,
    "caption_words": 3,
    "caption_font": "Arial",
    "caption_size": 84,
    "caption_margin_v": 420,
    "caption_highlight": "&H0000E5FF",   # ASS BGR colour (yellow-orange)
    "loudness": -14,
    "crf": 18,
    "max_seconds": 180,
}
DEFAULT_ANALYSIS = {"freeze_noise": "-60dB", "freeze_min": 0.3, "min_beat": 0.8}


# --------------------------------------------------------------------------- helpers
def log(msg: str) -> None:
    print(f"[reelforge] {msg}", flush=True)


def run(cmd: list, cwd: Path | None = None) -> subprocess.CompletedProcess:
    p = subprocess.run([str(c) for c in cmd], cwd=cwd, capture_output=True, text=True)
    if p.returncode != 0:
        sys.stderr.write(p.stderr[-4000:] + "\n")
        raise RuntimeError(f"Command failed: {' '.join(map(str, cmd[:6]))} ...")
    return p


def ffprobe_duration(path: Path) -> float:
    p = run(["ffprobe", "-v", "error", "-show_entries", "format=duration",
             "-of", "default=nw=1:nk=1", path])
    return float(p.stdout.strip())


def ffmpeg_stderr(args: list) -> str:
    """Run an analysis filter and return ffmpeg's log (analysis output lives in stderr)."""
    p = subprocess.run(["ffmpeg", "-hide_banner", "-nostats", *map(str, args)],
                       capture_output=True, text=True)
    return p.stderr


@dataclass
class Word:
    text: str
    start: float
    end: float


@dataclass
class Block:
    idx: int
    path: Path
    duration: float
    text: str = ""
    section: str | None = None
    words: list[Word] = field(default_factory=list)
    start: float = 0.0   # position on the OUTPUT timeline, filled by the planner


@dataclass
class Beat:
    name: str
    start: float
    end: float

    @property
    def length(self) -> float:
        return self.end - self.start


# --------------------------------------------------------------------------- TTS providers
def words_from_chars(chars, starts, ends) -> list[Word]:
    words, buf, ws, we = [], "", None, None
    for ch, s, e in zip(chars, starts, ends):
        if ch.isspace():
            if buf:
                words.append(Word(buf, ws, we))
            buf, ws = "", None
            continue
        if ws is None:
            ws = s
        buf += ch
        we = e
    if buf:
        words.append(Word(buf, ws, we))
    return words


def tts_elevenlabs(text: str, cfg: dict, out_base: Path, prev_text: str, next_text: str):
    import requests
    key = os.environ.get("ELEVENLABS_API_KEY")
    if not key:
        raise SystemExit("Set ELEVENLABS_API_KEY in your environment.")
    voice = cfg.get("voice_id", "21m00Tcm4TlvDq8ikWcM")
    body = {"text": text, "model_id": cfg.get("model_id", "eleven_multilingual_v2")}
    if cfg.get("voice_settings"):
        body["voice_settings"] = cfg["voice_settings"]
    if cfg.get("context", True):           # keeps intonation continuous across blocks
        if prev_text:
            body["previous_text"] = prev_text
        if next_text:
            body["next_text"] = next_text
    r = requests.post(
        f"https://api.elevenlabs.io/v1/text-to-speech/{voice}/with-timestamps",
        params={"output_format": cfg.get("output_format", "mp3_44100_128")},
        headers={"xi-api-key": key}, json=body, timeout=180)
    if r.status_code >= 400:
        raise RuntimeError(f"ElevenLabs error {r.status_code}: {r.text[:400]}")
    data = r.json()
    path = out_base.with_suffix(".mp3")
    path.write_bytes(base64.b64decode(data["audio_base64"]))
    al = data.get("alignment") or data.get("normalized_alignment")
    words = words_from_chars(al["characters"], al["character_start_times_seconds"],
                             al["character_end_times_seconds"]) if al else []
    return path, words


def tts_gemini(text: str, cfg: dict, out_base: Path, *_):
    from google import genai
    from google.genai import types
    client = genai.Client()  # reads GEMINI_API_KEY / GOOGLE_API_KEY
    prompt = f"{cfg['style'].strip()} {text}" if cfg.get("style") else text
    speech = types.SpeechConfig(voice_config=types.VoiceConfig(
        prebuilt_voice_config=types.PrebuiltVoiceConfig(voice_name=cfg.get("voice", "Kore"))))
    resp = client.models.generate_content(
        model=cfg.get("model", "gemini-2.5-flash-preview-tts"),
        contents=prompt,
        config=types.GenerateContentConfig(response_modalities=["AUDIO"], speech_config=speech))
    inline = resp.candidates[0].content.parts[0].inline_data
    pcm = inline.data if isinstance(inline.data, bytes) else base64.b64decode(inline.data)
    m = re.search(r"rate=(\d+)", inline.mime_type or "")
    rate = int(m.group(1)) if m else 24000
    path = out_base.with_suffix(".wav")
    with wave.open(str(path), "wb") as w:   # Gemini returns raw 16-bit mono PCM
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(rate)
        w.writeframes(pcm)
    return path, []   # Gemini has no word timestamps -> estimated later


PROVIDERS = {"elevenlabs": tts_elevenlabs, "gemini": tts_gemini}


def synthesize(text, provider, pcfg, cache_dir: Path, prev_text="", next_text=""):
    key = hashlib.sha1(json.dumps([provider, pcfg, text, prev_text, next_text],
                                  sort_keys=True).encode()).hexdigest()[:16]
    meta = cache_dir / f"{key}.json"
    if meta.exists():                       # re-runs never spend credits twice
        m = json.loads(meta.read_text())
        return Path(m["path"]), [Word(**w) for w in m["words"]]
    log(f"TTS ({provider}): {text[:60]}{'...' if len(text) > 60 else ''}")
    path, words = PROVIDERS[provider](text, pcfg, cache_dir / key, prev_text, next_text)
    meta.write_text(json.dumps({"path": str(path), "words": [w.__dict__ for w in words]}))
    return path, words


# --------------------------------------------------------------------------- audio analysis
def silences(path: Path, noise="-45dB", d=0.15):
    log_txt = ffmpeg_stderr(["-i", path, "-af", f"silencedetect=noise={noise}:d={d}", "-f", "null", "-"])
    starts = [float(x) for x in re.findall(r"silence_start: (-?[\d.]+)", log_txt)]
    ends = [float(x) for x in re.findall(r"silence_end: ([\d.]+)", log_txt)]
    return starts, ends


def trim_and_normalize(src: Path, dst: Path):
    """Cut leading/trailing silence so placement is exact. Returns (head_offset, duration)."""
    D = ffprobe_duration(src)
    starts, ends = silences(src)
    head, tail = 0.0, D
    if starts and starts[0] <= 0.02 and ends:
        head = ends[0]
    if starts and (len(ends) < len(starts) or ends[-1] >= D - 0.05) and starts[-1] > head:
        tail = starts[-1]
    head, tail = max(0.0, head - 0.04), min(D, tail + 0.12)
    run(["ffmpeg", "-y", "-v", "error", "-i", src, "-ss", f"{head:.3f}", "-to", f"{tail:.3f}",
         "-ar", "48000", "-ac", "2", dst])
    return head, ffprobe_duration(dst)


def split_audio_file(src: Path, out_dir: Path, min_silence=0.55):
    """Split one long narration file into blocks at its natural pauses."""
    D = ffprobe_duration(src)
    starts, ends = silences(src, noise="-38dB", d=min_silence)
    cuts = [0.0] + [(s + e) / 2 for s, e in zip(starts, ends) if 0.3 < s and e < D - 0.3] + [D]
    paths = []
    for i, (a, b) in enumerate(zip(cuts, cuts[1:])):
        if b - a < 0.35:
            continue
        p = out_dir / f"split_{i:02d}.wav"
        run(["ffmpeg", "-y", "-v", "error", "-i", src, "-ss", f"{a:.3f}", "-to", f"{b:.3f}", p])
        paths.append(p)
    log(f"Split {src.name} into {len(paths)} blocks at natural pauses")
    return paths


def estimate_words(text: str, duration: float) -> list[Word]:
    """Distribute words over the clip proportionally to their length (for Gemini / own files)."""
    toks = text.split()
    if not toks:
        return []
    weights = [len(t) + 2 for t in toks]
    total, t, out = sum(weights), 0.0, []
    for tok, w in zip(toks, weights):
        dur = duration * w / total
        out.append(Word(tok, t, t + dur))
        t += dur
    return out


def prepare_blocks(cfg: dict, base: Path, work: Path) -> list[Block]:
    tts = cfg.get("tts", {})
    provider = tts.get("provider", "elevenlabs")
    items = list(cfg.get("narration") or [])
    cache = work / "tts_cache"
    bdir = work / "blocks"
    cache.mkdir(parents=True, exist_ok=True)
    bdir.mkdir(parents=True, exist_ok=True)

    sources: list[tuple[Path, list[Word], dict]] = []
    if cfg.get("audio_file"):
        parts = split_audio_file(base / cfg["audio_file"], bdir, cfg.get("split_min_silence", 0.55))
        for i, p in enumerate(parts):
            it = items[i] if len(items) == len(parts) else {}
            sources.append((p, [], it))
    else:
        texts = [it.get("text", "") for it in items]
        for i, it in enumerate(items):
            if it.get("audio"):
                sources.append((base / it["audio"], [], it))
            else:
                prov = it.get("provider", provider)
                pcfg = {**tts.get(prov, {}), **it.get("voice", {})}
                prev_t = texts[i - 1] if i > 0 else ""
                next_t = texts[i + 1] if i + 1 < len(texts) else ""
                path, words = synthesize(it["text"], prov, pcfg, cache, prev_t, next_t)
                sources.append((path, words, it))

    blocks = []
    for i, (src, words, it) in enumerate(sources):
        dst = bdir / f"block_{i:02d}.wav"
        head, dur = trim_and_normalize(src, dst)
        words = [Word(w.text, max(0.0, w.start - head), min(dur, w.end - head))
                 for w in words if w.end - head > 0]
        text = it.get("text", "")
        if not words and text:
            words = estimate_words(text, dur)
        blocks.append(Block(i, dst, dur, text, it.get("section"), words))
    log(f"{len(blocks)} voice blocks, {sum(b.duration for b in blocks):.1f}s of speech")
    return blocks


# --------------------------------------------------------------------------- video
def render_manim(v: dict, reel: dict, base: Path, work: Path) -> Path:
    media = work / "media"
    cmd = ["manim", f"-q{v.get('quality', 'h')}", "--save_sections", "--media_dir", media,
           "--fps", reel["fps"], base / v["manim_file"], v["scene"]]
    if v.get("vertical", True):
        cmd[2:2] = ["-r", f"{reel['width']},{reel['height']}"]
    log("Rendering Manim scene: " + " ".join(map(str, cmd)))
    run(cmd, cwd=base)
    found = [p for p in media.glob(f"videos/**/{v['scene']}.mp4")
             if "partial_movie_files" not in p.parts and "sections" not in p.parts]
    if not found:
        raise RuntimeError("Manim finished but no output video was found.")
    return max(found, key=lambda p: p.stat().st_mtime)


def manim_sections(video: Path, scene: str) -> list[Beat]:
    j = video.parent / "sections" / f"{scene}.json"
    if not j.exists():
        return []
    beats, t = [], 0.0
    for i, s in enumerate(json.loads(j.read_text())):
        f = j.parent / s["video"]
        if not f.exists():
            continue
        d = ffprobe_duration(f)
        beats.append(Beat(s.get("name") or f"section_{i}", t, t + d))
        t += d
    return beats


def detect_beats(video: Path, D: float, a: dict) -> list[Beat]:
    """Animation starts = moments where a frozen frame (self.wait) ends."""
    txt = ffmpeg_stderr(["-i", video, "-vf",
                         f"freezedetect=n={a['freeze_noise']}:d={a['freeze_min']}",
                         "-map", "0:v:0", "-f", "null", "-"])
    starts = [0.0]
    for t in sorted(float(x) for x in re.findall(r"freeze_end: ([\d.]+)", txt)):
        if t - starts[-1] >= a["min_beat"] and t < D - 0.3:
            starts.append(t)
    ends = starts[1:] + [D]
    return [Beat(f"beat_{i}", s, e) for i, (s, e) in enumerate(zip(starts, ends))]


# --------------------------------------------------------------------------- planning
def need_for(durs: list[float], reel: dict) -> float:
    return reel["lead"] + sum(durs) + reel["gap"] * (len(durs) - 1) + reel["tail"]


def plan_direct(blocks: list[Block], beats: list[Beat]):
    names = {b.name: i for i, b in enumerate(beats)}
    missing = sorted({b.section for b in blocks if b.section not in names})
    if missing:
        raise SystemExit(f"Narration refers to unknown sections {missing}. Available: {list(names)}")
    return [(j, j + 1, [b.idx for b in blocks if b.section == beat.name])
            for j, beat in enumerate(beats)]


def plan_auto(blocks: list[Block], beats: list[Beat], reel: dict):
    """Monotonic alignment: contiguous groups of blocks <-> contiguous groups of beats."""
    M, N = len(blocks), len(beats)
    d = [b.duration for b in blocks]
    ow, sw, mw = reel["overflow_weight"], reel["silence_weight"], reel["sync_weight"]
    INF = float("inf")
    dp = [[INF] * (N + 1) for _ in range(M + 1)]
    bk = [[None] * (N + 1) for _ in range(M + 1)]
    dp[0][0] = 0.0
    for i in range(1, M + 1):
        for j in range(1, N + 1):
            for i0 in range(i):
                need = need_for(d[i0:i], reel)
                for j0 in range(j):
                    if dp[i0][j0] == INF:
                        continue
                    L = beats[j - 1].end - beats[j0].start
                    c = (dp[i0][j0] + ow * max(0.0, need - L) + sw * max(0.0, L - need)
                         + mw * ((i - i0 - 1) + (j - j0 - 1)))
                    if c < dp[i][j]:
                        dp[i][j], bk[i][j] = c, (i0, j0)
    groups, i, j = [], M, N
    while i > 0:
        i0, j0 = bk[i][j]
        groups.append((j0, j, list(range(i0, i))))
        i, j = i0, j0
    return groups[::-1]


def build_timeline(plan, blocks: list[Block], beats: list[Beat], reel: dict):
    vsegs, out_t = [], 0.0
    for j0, j1, idxs in plan:
        s, e = beats[j0].start, beats[j1 - 1].end
        L = e - s
        hold = max(0.0, need_for([blocks[k].duration for k in idxs], reel) - L) if idxs else 0.0
        t = out_t + reel["lead"]
        for k in idxs:
            blocks[k].start = t
            t += blocks[k].duration + reel["gap"]
        vsegs.append([s, e, hold])
        out_t += L + hold
    vsegs[-1][2] += reel["end_hold"]
    out_t += reel["end_hold"]
    merged = [vsegs[0]]                       # fewer filter chains -> faster encode
    for s, e, h in vsegs[1:]:
        if merged[-1][2] < 1e-3 and abs(merged[-1][1] - s) < 1e-6:
            merged[-1][1], merged[-1][2] = e, h
        else:
            merged.append([s, e, h])
    return merged, out_t


REEL_FOR_PRINT = DEFAULT_REEL


def print_plan(plan, blocks, beats, total):
    print("\n  beat(s)                   video    voice   hold   text")
    for j0, j1, idxs in plan:
        name = beats[j0].name if j1 - j0 == 1 else f"{beats[j0].name}..{beats[j1 - 1].name}"
        L = beats[j1 - 1].end - beats[j0].start
        v = sum(blocks[k].duration for k in idxs)
        hold = max(0.0, need_for([blocks[k].duration for k in idxs], REEL_FOR_PRINT) - L) if idxs else 0.0
        txt = " | ".join(blocks[k].text[:28] or f"<block {k}>" for k in idxs) or "(no voice)"
        print(f"  {name[:24]:<24} {L:7.2f}s {v:7.2f}s  {hold:5.2f}s  {txt[:60]}")
    print(f"\n  output length: {total:.2f}s\n")


# --------------------------------------------------------------------------- captions
def ass_time(t: float) -> str:
    cs = int(round(max(0.0, t) * 100))
    return f"{cs // 360000}:{cs // 6000 % 60:02d}:{cs // 100 % 60:02d}.{cs % 100:02d}"


def write_captions(blocks: list[Block], reel: dict, path: Path):
    esc = lambda s: s.replace("{", "(").replace("}", ")").replace("\\", "/")
    hl = reel["caption_highlight"]
    lines = []
    for b in blocks:
        chunks, cur = [], []
        for w in b.words:
            cur.append(w)
            if len(cur) >= reel["caption_words"] or re.search(r"[.!?,;:]$", w.text):
                chunks.append(cur)
                cur = []
        if cur:
            chunks.append(cur)
        for ci, ch in enumerate(chunks):
            for wi, w in enumerate(ch):
                st = b.start + w.start
                if wi + 1 < len(ch):
                    en = b.start + ch[wi + 1].start
                elif ci + 1 < len(chunks):
                    en = b.start + chunks[ci + 1][0].start
                else:
                    en = b.start + w.end + 0.15
                txt = " ".join(f"{{\\c{hl}&}}{esc(x.text)}{{\\c&H00FFFFFF&}}" if x is w else esc(x.text)
                               for x in ch)
                lines.append(f"Dialogue: 0,{ass_time(st)},{ass_time(en)},Reel,,0,0,0,,{txt}")
    W, H = reel["width"], reel["height"]
    path.write_text(f"""[Script Info]
ScriptType: v4.00+
PlayResX: {W}
PlayResY: {H}
WrapStyle: 0

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Reel,{reel['caption_font']},{reel['caption_size']},&H00FFFFFF,&H00FFFFFF,&H00000000,&H80000000,-1,0,0,0,100,100,0,0,1,6,2,2,80,80,{reel['caption_margin_v']},1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
""" + "\n".join(lines) + "\n", encoding="utf-8")


# --------------------------------------------------------------------------- compose
def compose(video: Path, vsegs, blocks: list[Block], total: float, cfg: dict,
            reel: dict, work: Path, out: Path, base: Path):
    W, H, fps = reel["width"], reel["height"], reel["fps"]
    inputs = ["-i", video.resolve()]
    for b in blocks:
        inputs += ["-i", b.path.resolve()]
    music = cfg.get("music") or {}
    mus_idx = None
    if music.get("path"):
        mus_idx = len(blocks) + 1
        inputs += ["-stream_loop", "-1", "-i", (base / music["path"]).resolve()]

    fc = []
    for k, (s, e, hold) in enumerate(vsegs):
        pad = f",tpad=stop_mode=clone:stop_duration={hold:.3f}" if hold > 1e-3 else ""
        fc.append(f"[0:v]trim=start={s:.4f}:end={e:.4f},setpts=PTS-STARTPTS{pad}[v{k}]")
    fc.append("".join(f"[v{k}]" for k in range(len(vsegs)))
              + f"concat=n={len(vsegs)}:v=1:a=0,fps={fps},setsar=1[vc]")
    fit = reel["fit"]
    if fit == "blur":
        fc.append(f"[vc]split[bg][fg];"
                  f"[bg]scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H},"
                  f"gblur=sigma=40,eq=brightness=-0.12[bgb];"
                  f"[fg]scale={W}:{H}:force_original_aspect_ratio=decrease[fgs];"
                  f"[bgb][fgs]overlay=(main_w-overlay_w)/2:(main_h-overlay_h)/2[vf]")
    elif fit == "crop":
        fc.append(f"[vc]scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H}[vf]")
    else:
        fc.append(f"[vc]scale={W}:{H}:force_original_aspect_ratio=decrease,"
                  f"pad={W}:{H}:(ow-iw)/2:(oh-ih)/2:color={reel['pad_color']}[vf]")
    if reel["captions"] and any(b.words for b in blocks):
        write_captions(blocks, reel, work / "captions.ass")
        fc.append("[vf]subtitles=captions.ass,format=yuv420p[vout]")
    else:
        fc.append("[vf]format=yuv420p[vout]")

    for i, b in enumerate(blocks):
        ms = int(round(b.start * 1000))
        fc.append(f"[{i + 1}:a]aformat=sample_rates=48000:channel_layouts=stereo,"
                  f"adelay=delays={ms}:all=1[a{i}]")
    if len(blocks) > 1:
        fc.append("".join(f"[a{i}]" for i in range(len(blocks)))
                  + f"amix=inputs={len(blocks)}:normalize=0:dropout_transition=0[vmix]")
    else:
        fc.append("[a0]anull[vmix]")
    fc.append(f"[vmix]apad=whole_dur={total:.3f},atrim=0:{total:.3f}[voice]")

    if mus_idx is not None:
        vol = music.get("volume", 0.18)
        fo = max(0.0, total - 1.5)
        fc.append(f"[{mus_idx}:a]aformat=sample_rates=48000:channel_layouts=stereo,"
                  f"atrim=0:{total:.3f},volume={vol},afade=t=in:d=0.6,afade=t=out:st={fo:.3f}:d=1.5[mus]")
        if music.get("duck", True):
            fc.append("[voice]asplit=2[v1][vk];"
                      "[mus][vk]sidechaincompress=threshold=0.03:ratio=10:attack=15:release=400[duck];"
                      "[v1][duck]amix=inputs=2:normalize=0:duration=first[mix]")
        else:
            fc.append("[voice][mus]amix=inputs=2:normalize=0:duration=first[mix]")
    else:
        fc.append("[voice]anull[mix]")
    fc.append(f"[mix]loudnorm=I={reel['loudness']}:TP=-1.5:LRA=11,aresample=48000[aout]")

    graph = work / "filtergraph.txt"
    graph.write_text(";\n".join(fc))
    out.parent.mkdir(parents=True, exist_ok=True)
    cmd = ["ffmpeg", "-y", "-v", "error", "-stats", *inputs,
           "-filter_complex_script", graph.name,
           "-map", "[vout]", "-map", "[aout]",
           "-c:v", "libx264", "-preset", "medium", "-crf", reel["crf"],
           "-profile:v", "high", "-pix_fmt", "yuv420p", "-r", fps,
           "-c:a", "aac", "-b:a", "192k", "-ar", "48000",
           "-movflags", "+faststart", "-t", f"{total:.3f}", out.resolve()]
    log(f"Encoding {W}x{H} reel ({total:.1f}s)...")
    run(cmd, cwd=work)   # cwd=work keeps the subtitles path free of Windows escaping issues


# --------------------------------------------------------------------------- orchestration
def load_project(path: Path):
    cfg = yaml.safe_load(path.read_text(encoding="utf-8"))
    base = path.parent.resolve()
    work = base / cfg.get("work_dir", "reel_work")
    work.mkdir(parents=True, exist_ok=True)
    reel = {**DEFAULT_REEL, **(cfg.get("reel") or {})}
    analysis = {**DEFAULT_ANALYSIS, **(cfg.get("analysis") or {})}
    return cfg, base, work, reel, analysis


def cmd_voice(path: Path):
    cfg, base, work, reel, _ = load_project(path)
    blocks = prepare_blocks(cfg, base, work)
    timings: dict[str, float] = {}
    for sec in dict.fromkeys(b.section for b in blocks if b.section):
        timings[sec] = round(need_for([b.duration for b in blocks if b.section == sec], reel), 3)
    (work / "timings.json").write_text(json.dumps(timings, indent=2))
    log(f"Wrote {work / 'timings.json'} -> render Manim now and sections will match the voice exactly")
    for k, v in timings.items():
        print(f"  {k:<20} {v:6.2f}s")


def cmd_build(path: Path, dry: bool = False):
    cfg, base, work, reel, analysis = load_project(path)
    blocks = prepare_blocks(cfg, base, work)
    if not blocks:
        raise SystemExit("No narration blocks. Add `narration:` items or an `audio_file:`.")

    v = cfg.get("video", {})
    if v.get("path"):
        video = (base / v["path"]).resolve()
        beats = []
    else:
        video = render_manim(v, reel, base, work) if v.get("render", True) else None
        if video is None:
            raise SystemExit("Set video.path or video.render: true")
        beats = manim_sections(video, v["scene"])
    D = ffprobe_duration(video)

    all_named = all(b.section for b in blocks)
    if beats and len(beats) > 1 and all_named:
        mode, plan = "direct (Manim sections)", plan_direct(blocks, beats)
    else:
        if not beats or len(beats) <= 1:
            beats = detect_beats(video, D, analysis)
            src = "freezedetect"
        else:
            src = "Manim sections"
        mode, plan = f"auto ({src})", plan_auto(blocks, beats, reel)
    log(f"Video {D:.2f}s, {len(beats)} beats, placement mode: {mode}")

    vsegs, total = build_timeline(plan, blocks, beats, reel)
    global REEL_FOR_PRINT
    REEL_FOR_PRINT = reel
    print_plan(plan, blocks, beats, total)
    (work / "timeline.json").write_text(json.dumps({
        "video": str(video), "output_seconds": total,
        "video_segments": [{"src_start": s, "src_end": e, "hold": h} for s, e, h in vsegs],
        "blocks": [{"index": b.idx, "start": round(b.start, 3), "duration": round(b.duration, 3),
                    "text": b.text, "file": str(b.path)} for b in blocks],
    }, indent=2))
    if total > reel["max_seconds"]:
        log(f"WARNING: reel is {total:.0f}s, longer than max_seconds={reel['max_seconds']}")
    if dry:
        return
    out = base / cfg.get("output", "out/reel.mp4")
    compose(video, vsegs, blocks, total, cfg, reel, work, out, base)
    log(f"Done -> {out}")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("command", choices=["voice", "analyze", "build"])
    ap.add_argument("project", type=Path)
    a = ap.parse_args()
    if a.command == "voice":
        cmd_voice(a.project)
    else:
        cmd_build(a.project, dry=a.command == "analyze")


if __name__ == "__main__":
    main()
