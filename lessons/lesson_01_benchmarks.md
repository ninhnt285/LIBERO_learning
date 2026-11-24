# Lesson 1 — LIBERO Architecture, Benchmarks, and Tasks

**Goal:** Know what LIBERO, LeRobot and SmolVLA each do. Understand suites, tasks, episodes, observations, actions and success, and list the 10 LIBERO-Spatial tasks.

**Deliverable:** A list of the 10 LIBERO-Spatial tasks and a short explanation of the evaluation loop.

## What you'll learn in this lesson
| Step | Topic | What you'll do | What you'll get |
|---|---|---|---|
| 1 | The control loop, the three components, and the files on disk | Map LIBERO evaluation onto Sense-Plan-Act; read a `.bddl` file; find the init-state files and the success check | A written explanation of the evaluation loop |
| 2 | The benchmark API | Write `lesson_01_benchmarks.py` and use `libero.libero.benchmark` to load suites and tasks from Python | A script that loads any suite and task |
| 3 | Compare the suites | Extend the script to print every suite with its task count and example tasks | A table comparing the five suites |
| 4 | The LIBERO-Spatial tasks | Print all 10 `libero_spatial` tasks and work out what stays the same and what changes | The list of the 10 tasks |

---

## Step 1 — The control loop, the three components, and the files on disk

### 1.1 Sense-Plan-Act: the classic robotics loop

LIBERO evaluation follows the same closed loop as classic robotics: **Sense → Plan → Act**, repeated every control step.

| Classic stage | In a LIBERO + VLA evaluation | Who does it |
|---|---|---|
| **Sense** | The simulator renders camera images and reads robot state → `obs` | LIBERO (MuJoCo / robosuite) |
| **Plan** | The policy maps `(images, state, instruction)` → next action | SmolVLA (via LeRobot) |
| **Act** | `env.step(action)` moves the robot and advances the physics | LIBERO (MuJoCo / robosuite) |
| *(Judge)* | After every step, check whether the BDDL goal is true | LIBERO (`_check_success`) |

**Difference from the classic pipeline:** in classic robotics, "Plan" is separate hand-written modules (perception → state estimation → motion planning → control). A VLA is **end-to-end**: one neural network goes straight from pixels and text to an action, with no explicit plan or map. It also **re-plans every step**, because each new observation produces a new action (or a short chunk of actions).

```
 ┌──────────────── LIBERO (benchmark + MuJoCo simulator) ────────────────┐
 │  task (.bddl)  +  initial state (1 of 50)  →  env.reset()             │
 │                                                  │                    │
 │                         SENSE: observation (images, robot state)      │
 └──────────────────────────────────────────────────┼────────────────────┘
                                                    ▼
        LeRobot: preprocessing (rename cameras, normalize state)
                                                    ▼
        PLAN — SmolVLA:  (images + state + instruction) → action (7-D)
                                                    ▼
        LeRobot: postprocessing (un-normalize the action)
                                                    ▼
 ┌──────────────── LIBERO ───────────────────────────────────────────────┐
 │  ACT: env.step(action) → new obs, reward, done                        │
 │  JUDGE: done = True when every BDDL goal predicate is true            │
 └───────────────────────────────────────────────────────────────────────┘
        repeat until success or max_steps → 1 episode → success / fail
```

### 1.2 Three components
| Component | Role | In this course |
|---|---|---|
| **LIBERO** | The benchmark: task definitions (BDDL files), saved initial states, a MuJoCo/robosuite simulator and success checks | Lessons 1–8 |
| **LeRobot** | Tools: the policy implementations, dataset format, env wrappers and evaluation scripts | Lessons 3, 6, 8 |
| **SmolVLA** | The policy: a vision-language-action model. Input: images + robot state + instruction. Output: actions | Lessons 6, 8 |

### 1.3 Vocabulary
- **Suite:** a group of tasks built to test one kind of variation (e.g. `libero_spatial`).
- **Task:** one language goal in one scene layout, defined by one `.bddl` file.
- **Initial state:** one saved simulator snapshot for a task. Each task has 50, so evaluations can be reproduced.
- **Episode:** one rollout. Reset to an initial state, then run steps until success or the step limit.
- **Observation:** what the env returns each step (camera images, robot state, ...). This is what the policy *can* see.
- **Simulator state:** the full physics state (every joint and object pose). The policy *cannot* see this; it's "privileged" information.
- **Action:** what the policy sends each step. 7-D: `[dx, dy, dz, droll, dpitch, dyaw, gripper]`, a small end-effector pose change plus open/close of the gripper.
- **Success:** every BDDL goal predicate is true, e.g. `(On akita_black_bowl_1 plate_1)`.

### 1.4 The evaluation loop
```
for each task in suite:
    for each initial_state in task's 50 states:
        obs = env.reset(); env.set_init_state(initial_state)        # SENSE
        repeat until success or max_steps:
            action = policy(obs, instruction)                         # PLAN (SmolVLA)
            obs, reward, done, info = env.step(action)                # ACT (LIBERO/MuJoCo)
        record success / fail
success rate = (# successful episodes) / (# episodes)
```

---

### 1.5 Where LIBERO keeps its files

Make a shortcut to the installed package (venv active, in the project root):
```bash
LIB=.venv/lib/python3.12/site-packages/libero/libero
```
```bash
ls $LIB
```

| Folder | Contents |
|---|---|
| `$LIB/bddl_files/<suite>/` | One `.bddl` file per task (the task definition) |
| `$LIB/init_files/<suite>/` | One `.init` / `.pruned_init` file per task (the saved initial states) |
| `$LIB/benchmark/` | The Python API: suite classes, `libero_suite_task_map.py` (which tasks belong to which suite) |
| `$LIB/envs/` | The simulator side: scenes, objects, `predicates/` (On, In, Open...) and success checks |
| `~/.cache/libero/assets` | Meshes and textures for objects and scenes |
| `.libero/config.yaml` | Tells LIBERO where all of the above are (set up in Lesson 0) |

LIBERO code never hard-codes these paths. It looks them up with `get_libero_path("bddl_files")`, `get_libero_path("init_states")`, etc., which read `config.yaml`.

---

### 1.6 The five suites

| Suite | What it tests | Tasks | BDDL folder | Init folder | LeRobot `max_steps` |
|---|---|---:|---|---|---:|
| `libero_spatial` | **Where**: same objects, the target black bowl starts at a different location; always "place it on the plate" | 10 | `$LIB/bddl_files/libero_spatial/` | `$LIB/init_files/libero_spatial/` | 280 |
| `libero_object` | **Which object**: same layout style, pick a different grocery item and place it in the basket | 10 | `$LIB/bddl_files/libero_object/` | `$LIB/init_files/libero_object/` | 280 |
| `libero_goal` | **What to do**: same scene and objects, a different goal (open drawer, put bowl on stove, ...) | 10 | `$LIB/bddl_files/libero_goal/` | `$LIB/init_files/libero_goal/` | 300 |
| `libero_10` | **Long-horizon**: two sub-goals per task (e.g. "turn on the stove and put the moka pot on it") | 10 | `$LIB/bddl_files/libero_10/` | `$LIB/init_files/libero_10/` | 520 |
| `libero_90` | **Variety**: 90 short tasks across many kitchen, living-room and study scenes; mostly used for pre-training | 90 | `$LIB/bddl_files/libero_90/` | `$LIB/init_files/libero_90/` | 400 |

- `libero_100` (= `libero_90` + `libero_10`) is also registered in the API, but in this `hf-libero` version creating it raises a `KeyError` (it has no entry in the task map). Skip it.
- Spatial, Object and Goal file names are just the instruction (`pick_up_the_black_bowl_..._on_the_plate.bddl`). `libero_10` and `libero_90` names start with the scene, e.g. `KITCHEN_SCENE3_turn_on_the_stove_and_put_the_moka_pot_on_it.bddl`.
- `max_steps` is the episode step limit LeRobot uses (from `lerobot/sim/integrations/libero.py`). Each is set a bit above the longest human demonstration for that suite. Reaching it without success = failed episode.

Count the tasks in each suite:
```bash
for d in $LIB/bddl_files/*/; do echo "$(basename $d): $(ls $d*.bddl | wc -l)"; done
```

---

### 1.7 BDDL: the task definition file

**BDDL** = *Behavior Domain Definition Language*. It's based on **PDDL**, the classic AI-planning language, and was first used by the BEHAVIOR benchmark. A BDDL file is a **text description of one task**: which objects exist, where they start, and what has to be true at the end. LIBERO reads it to **build the scene** and to **check success**.

Example:
```bash
cat $LIB/bddl_files/libero_spatial/pick_up_the_black_bowl_from_table_center_and_place_it_on_the_plate.bddl
```

#### Syntax
- Lisp-style: everything is a nested list in parentheses, `(keyword arg1 arg2 ...)`.
- A section starts with a colon: `(:language ...)`, `(:regions ...)`, `(:goal ...)`.
- A typed declaration is `name - type`, e.g. `plate_1 - plate` means "an object called `plate_1` of type `plate`". Several names can share one type: `akita_black_bowl_1 akita_black_bowl_2 - akita_black_bowl`.
- Predicates (facts that can be true or false) look like `(Predicate arg1 arg2)`, e.g. `(On plate_1 main_table_plate_region)`.

#### The sections, in file order
```lisp
(define (problem LIBERO_Tabletop_Manipulation)   ; scene class used to build the env
  (:domain robosuite)                             ; always robosuite in LIBERO
  (:language Pick the akita black bowl from table center and place it on the plate)
  (:regions ...)
  (:fixtures ...)
  (:objects ...)
  (:obj_of_interest ...)
  (:init ...)
  (:goal ...)
)
```

| Section | Meaning | Example from the file |
|---|---|---|
| `problem` | The scene type. Selects the Python env class (tabletop, kitchen, living room, study...) | `LIBERO_Tabletop_Manipulation` |
| `:domain` | The simulator back-end | `robosuite` |
| `:language` | Human-readable instruction written in the file | `Pick the akita black bowl from table center ...` |
| `:regions` | Named areas where things can be placed or checked | `plate_region`, `table_center`, `top_region` of the cabinet |
| `:fixtures` | Large things that don't get picked up: table, cabinet, stove | `main_table - table`, `wooden_cabinet_1 - wooden_cabinet` |
| `:objects` | Movable objects | `akita_black_bowl_1 akita_black_bowl_2 - akita_black_bowl`, `plate_1 - plate` |
| `:obj_of_interest` | Objects the task is really about (the rest are distractors) | `akita_black_bowl_1`, `plate_1` |
| `:init` | Starting layout, as predicates | `(On akita_black_bowl_1 main_table_table_center)` |
| `:goal` | Success condition, as predicates | `(And (On akita_black_bowl_1 plate_1))` |

#### Regions in detail
```lisp
(plate_region
    (:target main_table)                 ; the region is on the main table
    (:ranges ((0.05 0.19 0.07 0.21)))    ; (x_min y_min x_max y_max) in meters, table frame
)
(cabinet_region
    (:target main_table)
    (:ranges ((0.02 -0.28 0.04 -0.26)))
    (:yaw_rotation ((2.66 2.72)))        ; allowed rotation around z, in radians
)
(top_region (:target wooden_cabinet_1))  ; a region that belongs to a fixture (the top drawer)
```
- `:ranges` is a small rectangle on the target. At reset, the object is placed at a **random point inside it**, which is why one task has many different initial states.
- In `:init`, a region is referred to as `<target>_<region>`: `table_center` on `main_table` becomes `main_table_table_center`.
- These rectangles are only 2 cm wide, so object positions vary slightly between initial states. Lesson 7 changes them on purpose.

#### Predicates
Predicates used in `:init` and `:goal` across all suites:

| Predicate | Meaning | Example |
|---|---|---|
| `On a b` | `a` rests on top of `b` (object or region) | `(On akita_black_bowl_1 plate_1)` |
| `In a b` | `a` is inside `b` (basket, drawer, microwave) | `(In alphabet_soup_1 basket_1_contain_region)` |
| `Open x` / `Close x` | An articulated fixture (drawer, microwave door) is open/closed | `(Open wooden_cabinet_1_top_region)` |
| `Turnon x` / `Turnoff x` | A stove or faucet is on/off | `(Turnon flat_stove_1)` |
| `And ...` | All listed predicates must be true | `(And (On ...) (Close ...))` |

The predicates are implemented in `$LIB/envs/predicates/base_predicates.py`. The success check is in `$LIB/envs/problems/libero_tabletop_manipulation.py`:
```bash
grep -n -A8 "def _check_success" $LIB/envs/problems/libero_tabletop_manipulation.py
```
It evaluates each goal predicate on the **current simulator state** and returns `True` only if all are true. The policy never sees this check.

#### Things to notice in the example
- **Two black bowls.** `akita_black_bowl_2` is a **distractor** placed next to the plate. The policy has to use the language and the scene to pick the right one.
- **Extra regions.** The file defines all ten Spatial locations (`table_center`, `stove_region`, `next_to_ramekin_region`...), but `:init` only uses some. All 10 Spatial BDDL files share the same scene; they differ in where `akita_black_bowl_1` starts.

---

### 1.8 `.init` and `.pruned_init`: the saved initial states

A BDDL file describes a scene with **random** placement inside regions. To make evaluation **reproducible**, LIBERO samples placements ahead of time, lets the physics settle, and saves each resulting simulator state. Every evaluation then starts from the same saved states.

**Where:** `$LIB/init_files/<suite>/<task_name>.init` and `<task_name>.pruned_init`
```bash
ls -la $LIB/init_files/libero_spatial/ | head
```

| File | Contents | Used by |
|---|---|---|
| `.init` | **100** sampled initial states, array shape `(100, 92)` for this task | Not used by the benchmark API (raw pool) |
| `.pruned_init` | **50** states selected from them, shape `(50, 92)` | `suite.get_task_init_states(task_index)` — the official evaluation states |

- Each row is one flattened MuJoCo state (time, joint positions `qpos`, joint velocities `qvel`). 92 values for this task; the length differs from task to task because scenes have different objects.
- The format is a numpy array saved with `torch.save`, which is why the files are really zip archives. Check: `file $LIB/init_files/libero_spatial/*table_center*.pruned_init`.
- `libero_goal` only ships `.pruned_init` files.
- The benchmark API always loads `.pruned_init`: in `$LIB/benchmark/__init__.py`, every task gets `init_states_file=f"{task}.pruned_init"`, and `get_task_init_states()` loads it with `torch.load`.
- You'll load one and decode its 92 values in Lesson 2.

---

### 1.9 Other important details

- **Which instruction does the policy get?** The benchmark API builds `task.language` from the **file name**, not from `(:language ...)`. For Task 2 the policy gets *"pick up the black bowl from table center and place it on the plate"*, while the BDDL says *"Pick the akita black bowl from table center..."*. LeRobot passes `task.language` (the file name version) to the policy (`lerobot/sim/integrations/libero.py`, `self.task_description = task.language`).
- **Task order.** `get_benchmark("libero_spatial")(task_order_index=0)` keeps the default order 0–9. Other `task_order_index` values shuffle the order (for lifelong-learning experiments). Always use `0` in this course so task indices stay the same.
- **Reproducibility = task + init state index.** "Task 2, state 7" always means the same starting scene. Use the names `task_index` and `state_index` in all scripts.
- **The policy sees observations, not state.** The success check and the init-state arrays use privileged simulator state. The policy only gets camera images + proprioception + text. Keep this in mind when reading results (Lesson 3).
- **Success rate resolution.** With 50 states per task and 1 episode each, a task's success rate moves in steps of 2%. A whole suite (10 × 50 = 500 episodes) moves in steps of 0.2%.

---

### Step 1 checklist
- [ ] Explain Sense-Plan-Act and which component does each part
- [ ] `cat` the Task 2 BDDL and find each section
- [ ] List the init files and say how `.init` and `.pruned_init` differ
- [ ] Find `_check_success`
- [ ] Write the evaluation loop in your own words (deliverable, part 1)

### Self-check questions
1. Which component decides success, and can the policy "see" that check?
2. What's the difference between a **task** and an **initial state**?
3. Why does the BDDL scene contain two black bowls if the instruction only mentions one?
4. If a task has 50 initial states and you run 1 episode per state, what are the possible success-rate values?
5. Why are initial states saved to files instead of sampled from the BDDL regions at every reset?

---

## Step 2 — The benchmark API

### What is the "benchmark API"?
"API" here means **the Python functions LIBERO gives you** to reach suites and tasks without digging through folders by hand. They live in one module:

```
$LIB/benchmark/__init__.py      →  imported as  libero.libero.benchmark
```

In Step 1 you used `ls` and `cat`. The benchmark API gives the same information in Python:

| Shell (Step 1) | Benchmark API |
|---|---|
| `ls $LIB/bddl_files/` (list the suites) | `benchmark.get_benchmark_dict()` |
| `ls ... \| wc -l` (count tasks) | `suite.get_num_tasks()` |
| Read one task's file name / instruction | `suite.get_task(task_index)` |
| Path to a `.bddl` file | `suite.get_task_bddl_file_path(task_index)` |
| Load a `.pruned_init` file | `suite.get_task_init_states(task_index)` (Lesson 2) |

Every later lesson starts the same way: **pick a suite → pick a task → build the environment from it.**

### What is `lesson_01_benchmarks.py`?
It's the script **you write** for this lesson. It's not part of LIBERO. Each lesson has one (`lesson_02_initial_states.py`, `lesson_03_observations.py`, ...). Create it in the project root:
```bash
cd ~/Projects/LIBERO_learning
```
```bash
touch lesson_01_benchmarks.py
```

You build it in two parts and run it after each part.

### Part A — List the suites

```python
from libero.libero import benchmark

# 1. Get every registered suite: {name: class}
benchmark_dict = benchmark.get_benchmark_dict()

print("Available suites:")
for suite_name in benchmark_dict:
    print(" ", suite_name)
```
```bash
python lesson_01_benchmarks.py
```

**Expected:** `libero_spatial`, `libero_object`, `libero_goal`, `libero_90`, `libero_10`, `libero_100`.

**What to notice:**
- The dict values are **classes**, not suites yet: `print(benchmark_dict["libero_spatial"])` shows `<class '...LIBERO_SPATIAL'>`.
- The names are lowercase because `register_benchmark` stores `ClassName.lower()`.
- `benchmark.get_benchmark("libero_spatial")` is a shortcut that returns the same class (case-insensitive).

### Part B — Load one suite and inspect one task

Add below Part A:
```python
# 2. Create a suite object from its class (note the "()" at the end)
suite_name = "libero_spatial"
suite = benchmark_dict[suite_name](task_order_index=0)

# 3. How many tasks?
num_tasks = suite.get_num_tasks()
print(f"\n{suite_name}: {num_tasks} tasks")

# 4. Look at one task
task_index = 2
task = suite.get_task(task_index)
print(f"\nTask {task_index}:")
print("  name            :", task.name)
print("  language        :", task.language)
print("  problem_folder  :", task.problem_folder)
print("  bddl_file       :", task.bddl_file)
print("  init_states_file:", task.init_states_file)

# 5. Full path to its .bddl file
print("  bddl path       :", suite.get_task_bddl_file_path(task_index))
```
```bash
python lesson_01_benchmarks.py
```

**What to notice:**
- Task indices follow the order in `$LIB/benchmark/libero_suite_task_map.py`, **not** alphabetical order (which is what `ls` shows). Index 2 is the "table center" task used in Lesson 2.
- Creating the suite prints `[info] using task orders [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]`. That's `task_order_index=0`, the default order. Keep it at 0 so task indices always mean the same task.
- `task` is a `Task` (a Python `NamedTuple`) with 6 fields:

| Field | Meaning | Example (`libero_spatial`, task 2) |
|---|---|---|
| `name` | File name without `.bddl` | `pick_up_the_black_bowl_from_table_center_and_place_it_on_the_plate` |
| `language` | The instruction given to the policy: `name` with `_` → space | `pick up the black bowl from table center and place it on the plate` |
| `problem` | Always `"Libero"` | `Libero` |
| `problem_folder` | The suite folder under `bddl_files/` and `init_files/` | `libero_spatial` |
| `bddl_file` | The task definition file | `<name>.bddl` |
| `init_states_file` | The saved initial states (always the pruned file) | `<name>.pruned_init` |

- `language` comes from the file name, **not** from the `(:language ...)` line inside the BDDL (see 1.9).
- The `bddl path` points into `.venv/...`, because it's read from `.libero/config.yaml` via `get_libero_path("bddl_files")`.

### Try it yourself
1. Set `task_index = 10`. You get an `IndexError`, because indices run from `0` to `num_tasks - 1`.
2. Set `suite_name = "libero_10"`. Task names start with the scene, e.g. `KITCHEN_SCENE3_...`, and `language` drops that prefix.
3. Set `suite_name = "libero_100"`. You get a `KeyError`. It's registered but has no task list in this version.
4. Print `suite.get_task_names()`. It returns a list of all task names in order.

### Useful `Benchmark` methods
| Method | Returns |
|---|---|
| `get_num_tasks()` | Number of tasks in the suite |
| `get_task(i)` | The `Task` at index `i` |
| `get_task_names()` | List of all task names |
| `get_task_bddl_files()` | List of all `.bddl` file names |
| `get_task_bddl_file_path(i)` | Full path to task `i`'s `.bddl` |
| `get_task_init_states(i)` | The 50 initial states of task `i` (Lesson 2) |
| `get_task_demonstration(i)` | Relative path to task `i`'s demo `.hdf5` in `datasets/` (Lesson 5) |

---

## Step 3 — Compare the suites

**Idea:** each suite is a controlled experiment. Inside a suite, **one factor changes** between tasks and everything else is held fixed. Knowing which factor tells you what a success rate on that suite actually measures.

You extend `lesson_01_benchmarks.py` with two more parts.

### Part C — Loop over every suite

Add at the end of the script:
```python
# 6. Compare all suites
print("\n" + "=" * 60)
print("SUITE COMPARISON")
print("=" * 60)

for suite_name, suite_class in benchmark_dict.items():
    if suite_name == "libero_100":      # registered, but has no task list -> KeyError
        continue

    suite = suite_class(task_order_index=0)
    num_tasks = suite.get_num_tasks()
    print(f"\n{suite_name}: {num_tasks} tasks")

    # show the first 3 instructions as examples
    for task_index in range(min(3, num_tasks)):
        task = suite.get_task(task_index)
        print(f"  [{task_index}] {task.language}")
```
```bash
python lesson_01_benchmarks.py
```

**Expected (first lines of each suite):**
```
libero_spatial: 10 tasks
  [0] pick up the black bowl between the plate and the ramekin and place it on the plate
  ...
libero_object: 10 tasks
  [0] pick up the alphabet soup and place it in the basket
  [1] pick up the cream cheese and place it in the basket
  [2] pick up the salad dressing and place it in the basket
libero_goal: 10 tasks
  [0] open the middle drawer of the cabinet
  [1] put the bowl on the stove
  [2] put the wine bottle on top of the cabinet
libero_90: 90 tasks
  [0] close the top drawer of the cabinet
  ...
libero_10: 10 tasks
  [0] put both the alphabet soup and the tomato sauce in the basket
  ...
```
The `[info] using task orders ...` line appears for every suite except `libero_90` (which doesn't support task orders).

### Part D — Count the scenes

`libero_10` and `libero_90` task names start with a scene ID (`KITCHEN_SCENE3_...`). The other three suites each use **one** scene, so their names have no prefix. Counting scenes shows how much the background changes inside a suite.

Add `import re` at the **top** of the script, then add at the end:
```python
# 7. How many different scenes does each suite use?
print("\n" + "=" * 60)
print("SCENES PER SUITE")
print("=" * 60)

for suite_name, suite_class in benchmark_dict.items():
    if suite_name == "libero_100":
        continue

    suite = suite_class(task_order_index=0)
    scenes = set()
    for task_name in suite.get_task_names():
        match = re.match(r"([A-Z_]+_SCENE\d+)_", task_name)   # e.g. "KITCHEN_SCENE3"
        scenes.add(match.group(1) if match else "(one shared scene)")

    print(f"{suite_name:15s} {len(scenes):3d} scene(s): {sorted(scenes)[:4]}")
```

**What the regex does:** `[A-Z_]+` matches the uppercase room name (`KITCHEN`, `LIVING_ROOM`, `STUDY`), `_SCENE\d+` matches `_SCENE` plus its number, and `group(1)` returns that whole prefix.

**Expected:** `libero_spatial`, `libero_object` and `libero_goal` show 1 scene each. `libero_10` shows 9 scenes and `libero_90` shows 20 (10 kitchen, 6 living room, 4 study).

### Result: the suite comparison

| Suite | Tasks | Scenes | What changes between tasks | What stays fixed | What it measures |
|---|---:|---:|---|---|---|
| `libero_spatial` | 10 | 1 | Start **location** of the target bowl | Objects, goal ("on the plate") | Spatial reasoning: does the policy find the right bowl by its position? |
| `libero_object` | 10 | 1 | **Which object** to pick | Layout style, goal ("in the basket") | Object recognition |
| `libero_goal` | 10 | 1 | **The goal** (open drawer, turn on stove, ...) | Scene and objects | Following different instructions in the same scene |
| `libero_10` | 10 | 9 | Everything; each task has **two sub-goals** | — | Long-horizon tasks (up to 520 steps) |
| `libero_90` | 90 | 20 | Everything | — | Variety; mostly used to pre-train before testing on the others |

**Why it matters for this course:** in `libero_spatial` only the bowl's position changes, so a drop in success can be blamed on position rather than on a new object or goal. That's why Lessons 2 and 7 use this suite for position experiments.

### Try it yourself
1. In Part C, print all tasks of `libero_goal` instead of 3. Which tasks touch the stove? Which touch the cabinet?
2. In Part D, print every scene of `libero_10` and check that they all also appear in `libero_90`.
3. Look at the `libero_10` instructions. Find the word that shows each task has two sub-goals ("and", "both").

---

## Step 4 — The LIBERO-Spatial tasks

**Goal:** list all 10 `libero_spatial` tasks, then prove what stays the same and what changes, first from the instructions and then from the BDDL files.

### Part E — List the 10 tasks

Add at the end of `lesson_01_benchmarks.py`:
```python
# 8. All LIBERO-Spatial tasks
print("\n" + "=" * 60)
print("LIBERO-SPATIAL TASKS")
print("=" * 60)

suite = benchmark_dict["libero_spatial"](task_order_index=0)

prefix = "pick up the black bowl "
suffix = " and place it on the plate"

for task_index in range(suite.get_num_tasks()):
    task = suite.get_task(task_index)
    location = task.language.removeprefix(prefix).removesuffix(suffix)
    print(f"[{task_index}] {location:45s} | {task.language}")
```
```bash
python lesson_01_benchmarks.py
```

- Every instruction is `prefix + <location> + suffix`. Removing the fixed parts leaves only the part that changes.
- `str.removeprefix()` / `str.removesuffix()` need Python 3.9 or newer (this venv uses 3.12).

### Part F — Check the BDDL files

The instruction only describes the **target** bowl. The BDDL `(:init ...)` section shows where **both** bowls start. Add at the end:
```python
# 9. Where do the two bowls start? Read it from each BDDL file.
import re

print("\n" + "=" * 60)
print("BOWL START POSITIONS (from BDDL :init)")
print("=" * 60)

for task_index in range(suite.get_num_tasks()):
    bddl_path = suite.get_task_bddl_file_path(task_index)
    with open(bddl_path) as f:
        text = f.read()

    # e.g. "(On akita_black_bowl_1 main_table_table_center)"
    target     = re.search(r"\((On|In) akita_black_bowl_1 (\S+)\)", text)
    distractor = re.search(r"\((On|In) akita_black_bowl_2 (\S+)\)", text)

    print(f"[{task_index}] target: {target.group(1)} {target.group(2):40s}"
          f" distractor: {distractor.group(1)} {distractor.group(2)}")
```
(If you already have `import re` at the top from Part D, you don't need it again.)

### Result: the 10 LIBERO-Spatial tasks

All instructions have the form *"pick up the black bowl **\<location\>** and place it on the plate"*.

| `task_index` | Location in the instruction | Target bowl starts (`akita_black_bowl_1`) | Distractor bowl starts (`akita_black_bowl_2`) |
|---:|---|---|---|
| 0 | between the plate and the ramekin | On `main_table_between_plate_ramekin_region` | On `main_table_next_to_ramekin_region` |
| 1 | next to the ramekin | On `main_table_next_to_ramekin_region` | On `main_table_next_to_box_region` |
| 2 | from table center | On `main_table_table_center` | On `main_table_next_to_plate_region` |
| 3 | on the cookie box | On `cookies_1` | On `wooden_cabinet_1_top_side` |
| 4 | in the top drawer of the wooden cabinet | **In** `wooden_cabinet_1_top_region` | On `wooden_cabinet_1_top_side` |
| 5 | on the ramekin | On `glazed_rim_porcelain_ramekin_1` | On `cookies_1` |
| 6 | next to the cookie box | On `main_table_next_to_box_region` | On `flat_stove_1_cook_region` |
| 7 | on the stove | On `flat_stove_1_cook_region` | On `wooden_cabinet_1_top_side` |
| 8 | next to the plate | On `main_table_next_to_plate_region` | On `main_table_next_to_ramekin_region` |
| 9 | on the wooden cabinet | On `wooden_cabinet_1_top_side` | On `flat_stove_1_cook_region` |

*(A ramekin is a small round ceramic dish.)*

### What stays the same and what changes

| Stays the same in all 10 tasks | Changes between tasks |
|---|---|
| Scene class (`LIBERO_Tabletop_Manipulation`) and the robot | Where the **target** bowl starts |
| Objects: 2 black bowls, plate, cookie box, ramekin | Where the **distractor** bowl starts |
| Fixtures: table, wooden cabinet, flat stove | The location phrase in the instruction |
| Positions of plate, cookie box, ramekin, cabinet and stove (same `:init` lines) | |
| Goal: `(And (On akita_black_bowl_1 plate_1))` | |
| `obj_of_interest`: `akita_black_bowl_1`, `plate_1` | |
| Instruction template, step limit (280) | |

You can check the "same" column from the shell. Every line appears 10 times, once per file:
```bash
cat $LIB/bddl_files/libero_spatial/*.bddl | grep -E "\(On (plate_1|cookies_1|glazed|wooden_cabinet_1|flat_stove_1) " | sort | uniq -c
```

### Why this matters
- **The bowls look identical.** The only way to know which bowl to pick is the **location phrase** in the instruction. A policy that ignores language and grabs the nearest bowl will fail in some tasks.
- **Two bowls move, not one.** Each task changes the target's start *and* the distractor's start. When comparing tasks, remember that both changed.
- **Hard cases:** task 4 needs `In` (the bowl is inside a drawer) and tasks 3, 5, 7, 9 put the bowl on top of another object. These are often harder than tasks where the bowl sits on the table.
- **Within one task**, the 50 initial states only move objects a little inside their 2 cm regions (Step 1.7). Lesson 2 measures exactly how much.

---

## Lesson 1 summary

**Deliverable**
1. **The evaluation loop** (your own words, Step 1.4): reset the env to one of the task's 50 saved initial states; each step the policy sees the observation (Sense), outputs a 7-D action (Plan), and the simulator applies it (Act); the episode ends when every BDDL goal predicate is true (success) or the suite's step limit is reached (failure); success rate = successful episodes / total episodes.
2. **The 10 LIBERO-Spatial tasks**: the table in Step 4.

**Final `lesson_01_benchmarks.py`** = Part A + Part B + Part C + Part D + Part E + Part F, in that order, with `import re` at the top.

**Next:** Lesson 2 opens task 2's `.pruned_init` file and decodes its `(50, 92)` array of initial states.
