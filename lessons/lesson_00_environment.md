# Lesson 0 — Setting Up the Environment

**Goal:** A separate, reproducible Python environment in `~/Projects/LIBERO_learning` with LIBERO + LeRobot + SmolVLA. It must not depend on any other project.

**Status:** Complete

| Step | Description | Status |
|---|---|---|
| 1 | Create the venv with Python 3.12 | Done |
| 2 | Install LeRobot with the LIBERO and SmolVLA extras | Done |
| 3 | Save exact versions in `requirements.txt` | Done |
| 4 | Check the packages and the GPU | Done |
| 5 | Give the project its own LIBERO config and check that LIBERO loads | Done |
| 6 | Set `MUJOCO_GL=egl` automatically when the venv is activated | Done |

---

## Key concepts

### Why LeRobot?
- **LIBERO** is the benchmark and simulator: suites, tasks, initial states, environments and success checks. On its own it's enough for Lessons 1, 2, 4, 5 and 7.
- **LeRobot** contains **SmolVLA**: the model code, the pretrained LIBERO checkpoint and the preprocessing that maps LIBERO observations to policy inputs (camera names, state vector, action un-normalization). Lessons 3 (step 4), 6 and 8 need it.
- LeRobot installs LIBERO through **`hf-libero`**, a pip-installable copy of LIBERO with updated dependency pins. The original LIBERO repo targets Python 3.8 and old versions of torch and robosuite, and has to be cloned and installed by hand.
- Using `hf-libero` means your simulator matches the one the SmolVLA checkpoint was evaluated on.

### Why pin the version (`==0.7.0`)?
Without a pin, uv installs the newest compatible release. Today that's 0.7.0, but:
1. **Reproducibility:** a later rebuild may install 0.8 or newer. LeRobot often breaks its API between minor versions (renamed modules, changed configs).
2. **Silent downgrades:** if a dependency conflicts, uv may pick an older lerobot without telling you.
3. **Extras can disappear:** if a future version renames or drops the `libero` or `smolvla` extra, uv only warns and installs without them.
4. **Checkpoint compatibility:** the format of the saved SmolVLA config is tied to the LeRobot version.

---

## Step 1 — Create the venv (Done)

```bash
cd ~/Projects/LIBERO_learning
```
```bash
uv venv --python 3.12
```
```bash
source .venv/bin/activate
```

Check: `python --version` should show `3.12.x`, and `which python` should point to `~/Projects/LIBERO_learning/.venv/bin/python`.

Python 3.12 is required: `lerobot==0.7.0` needs Python >= 3.12.

## Step 2 — Install LeRobot + LIBERO + SmolVLA (Done)

```bash
uv pip install "lerobot[libero,smolvla]==0.7.0"
```

- `libero` extra: `hf-libero` (>=0.1.4,<0.2), robosuite, MuJoCo, plus the dataset and transformers packages.
- `smolvla` extra: transformers, accelerate, num2words.
- Quote the package string so bash doesn't interpret the `[...]`.
- The download is a few GB (torch + CUDA). uv reuses cached wheels where it can.

## Step 3 — Save exact versions (Done)

```bash
uv pip freeze > requirements.txt
```

To rebuild the identical environment later: `uv pip install -r requirements.txt`.

## Step 4 — Check the packages and the GPU (Done)

```bash
uv pip list | grep -iE "lerobot|libero|robosuite|mujoco|torch"
```
```bash
python -c "import torch; print(torch.__version__, torch.cuda.is_available())"
```

Expected: all five packages are listed, and the second command prints `... True`.

Verified result:
| Package | Version |
|---|---|
| lerobot | 0.7.0 |
| hf-libero | 0.1.5 |
| robosuite | 1.4.0 |
| mujoco | 3.8.1 |
| torch | 2.15.0+cu132 (`cuda.is_available() = True`) |

## Step 5 — Give the project its own LIBERO config and check that LIBERO loads (Done)

**Problem:** LIBERO reads its paths (BDDL task files, initial states, datasets, assets) from one global file, `~/.libero/config.yaml`. That file was created by an earlier project and points to **another venv**, `~/Projects/VLA/vla-lerobo/.env/.../libero/`. Without a fix, this environment would quietly load task files and initial states from that project instead of its own `hf-libero 0.1.5`.

**Fix:** LIBERO uses the environment variable `LIBERO_CONFIG_PATH` instead of `~/.libero` when it is set (see `libero/libero/__init__.py`). Point it to a folder inside this project.

**5a. Set the variable automatically when the venv is activated**
```bash
echo 'export LIBERO_CONFIG_PATH="$HOME/Projects/LIBERO_learning/.libero"' >> .venv/bin/activate
```
```bash
deactivate && source .venv/bin/activate
```
```bash
echo $LIBERO_CONFIG_PATH
```

**5b. First import: create the config**
```bash
MUJOCO_GL=egl python -c "from libero.libero import benchmark; print(list(benchmark.get_benchmark_dict().keys()))"
```
At the prompt *"Do you want to specify a custom path for the dataset folder? (Y/N)"*:
- Answer **Y**, enter `~/Projects/LIBERO_learning`, and confirm with **Y**.
- Datasets then go to `~/Projects/LIBERO_learning/datasets` (outside `.venv`, so a venv rebuild keeps them).

Expected: the suite names are printed, including `libero_spatial`, `libero_object`, `libero_goal`, `libero_10` and `libero_90`.

**5c. Check the new config**
```bash
cat .libero/config.yaml
```
Expected: every path except `datasets` points into `LIBERO_learning/.venv/...`.

Verified result:
```yaml
assets: .../LIBERO_learning/.venv/lib/python3.12/site-packages/libero/libero/./assets
bddl_files: .../LIBERO_learning/.venv/lib/python3.12/site-packages/libero/libero/./bddl_files
benchmark_root: .../LIBERO_learning/.venv/lib/python3.12/site-packages/libero/libero
datasets: .../LIBERO_learning/datasets
init_states: .../LIBERO_learning/.venv/lib/python3.12/site-packages/libero/libero/./init_files
```

## Step 6 — Set `MUJOCO_GL=egl` automatically (Done)

**Why:** MuJoCo needs a rendering backend. On a machine without a display, `egl` renders offscreen on the GPU. Setting it in the activate script means you no longer type `MUJOCO_GL=egl` in front of every command.

```bash
echo 'export MUJOCO_GL=egl' >> .venv/bin/activate
```
```bash
deactivate && source .venv/bin/activate
```
```bash
echo $MUJOCO_GL
```

Expected: `egl`.

**Note:** `deactivate` does **not** unset `MUJOCO_GL` or `LIBERO_CONFIG_PATH`. They stay set in that terminal until you close it. That's harmless for this course.

---

## Notes for every later lesson
- **Headless rendering:** activating the venv sets `MUJOCO_GL=egl` (Step 6). Override it for one command with `MUJOCO_GL=osmesa python ...` if EGL fails.
- **Assets:** scene assets are cached in `~/.cache/libero/assets`, already downloaded from an earlier project.
- **Paths config:** this project uses its own config at `~/Projects/LIBERO_learning/.libero/config.yaml`, through `LIBERO_CONFIG_PATH`, which activating the venv sets. If you see path errors, check that the venv is active (`echo $LIBERO_CONFIG_PATH`) and then check this file.
- **Harmless warning:** robosuite's "No private macro file found" can be ignored.
