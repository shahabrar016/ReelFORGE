# Rutherford atomic model — ReelForge

A nine-section narrated lesson, designed for approximately 80–100 seconds (actual duration depends on your voice). Output: **1080 × 1920, 9:16, 30 fps**. Internal frame: **9 × 16**. Essential visuals stay above the caption area, between approximately y = −2.9 and 6.7. No LaTeX, image assets, or additional Python dependencies beyond your existing repository requirements.

## Add to your repository

1. Put `rutherford_scene.py` and `prepare_rutherford.py` beside `reelforge.py` and `example_scene.py`.
2. In your repository terminal, generate a project from your working voice settings:

   ```bash
   python prepare_rutherford.py determinants.yaml
   ```

   If `project.yaml` has your working voice instead, use that filename. The source YAML is unchanged. The generated file is `rutherford.yaml`; review and commit it along with the scene. Provider/model/voice settings are inherited, so no guessed voice ID is supplied.

3. Run your existing GitHub Actions **Build reel** workflow with project input `rutherford.yaml`.
4. Download the reel artifact. The final file is `out/rutherford.mp4`.

Local equivalent:

```bash
python reelforge.py voice rutherford.yaml
python reelforge.py build rutherford.yaml
```

The scene imports your existing `SyncedScene` from `example_scene.py`, calls `section(name)` and `fill()` as documented, and uses `reel_work` for compatibility with its timing file. The guide does not contain your implementation, so integration with the actual repository has not been executed here.

For a silent direct render, run:

```bash
python -m manim --save_sections rutherford_scene.py RutherfordAtom
```

Outside the repository, the scene falls back to eight-second sections. Within the repository, your existing timing class controls holds. A direct preview may therefore reuse existing timings; the two ReelForge commands above are the recommended full build.

## Scientific choices

- Identifies Geiger and Marsden's experiment separately from Rutherford's 1911 interpretation.
- Explains near-straight transmission, deflection, and rare scattering through more than 90 degrees without inventing a universal percentage.
- Uses numerical inverse-square **repulsive Coulomb** trajectories for the close-up. The nucleus is stationary (heavy-target approximation); all three alpha particles have the same initial speed. This is an illustrative classical calculation, not a calibrated gold-foil simulation or frequency distribution.
- No hard-sphere bounce, neutrons attributed to 1911, or Bohr energy shells. Electron markers are illustrative and do not represent the electron count of gold. The dashed atom boundary is a size guide, not a shell or orbit.
- Labels enlarged nuclei and schematic apparatus. Gives modern approximate atomic/nuclear radius scales with their variability.
- States the classical model's limitations and distinguishes modern quantum orbitals from planetary trajectories.

References:
- https://www.aps.org/apsnews/2006/05/rutherford-discovery-atomic-nucleus
- https://history.aip.org/exhibits/rutherford/sections/alpha-particles-atom.html
- https://openstax.org/books/physics/pages/22-1-the-structure-of-the-atom
- https://docs.manim.community/en/stable/reference/manim.scene.scene.Scene.html

## Validation

Python syntax and section/narration matching were checked. Manim and its native rendering dependencies are unavailable in the authoring environment, so no rendered MP4 or visual render verification is claimed. Check the first GitHub render for your existing caption styling and voice timing before publishing.
