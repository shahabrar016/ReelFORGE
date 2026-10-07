"""Run in repo: python prepare_rutherford.py determinants.yaml
Copies working provider settings; changes topic/video/narration only.
Does not import Manim or modify the input project.
"""
import ast
from pathlib import Path
import sys
import yaml

base = Path(sys.argv[1] if len(sys.argv) > 1 else "determinants.yaml")
out = Path("rutherford.yaml")
if out.exists():
    raise SystemExit("rutherford.yaml already exists; rename it before generating another.")
project = yaml.safe_load(base.read_text(encoding="utf-8"))
if not isinstance(project, dict):
    raise SystemExit("Expected a YAML project mapping.")
tree = ast.parse(Path(__file__).with_name("rutherford_scene.py").read_text(encoding="utf-8"))
lines = next(ast.literal_eval(n.value) for n in tree.body if isinstance(n, ast.Assign)
             and any(isinstance(t, ast.Name) and t.id == "NARRATION" for t in n.targets))
project["video"] = dict(manim_file="rutherford_scene.py", scene="RutherfordAtom", quality="h", vertical=True)
project["narration"] = [dict(section=section, text=text) for section,text in lines]
project.pop("audio_file", None)
project["reel"] = {**project.get("reel", {}), "width":1080,"height":1920,"fps":30}
project["work_dir"] = "reel_work"
project["output"] = "out/rutherford.mp4"
out.write_text(yaml.safe_dump(project, sort_keys=False, allow_unicode=True), encoding="utf-8")
print("Created rutherford.yaml. Your existing TTS settings were preserved.")
