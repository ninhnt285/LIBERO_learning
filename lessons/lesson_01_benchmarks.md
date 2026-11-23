# Lesson 1 — LIBERO Architecture, Benchmarks, and Tasks

**Goal:** Know what LIBERO, LeRobot and SmolVLA each do. Understand suites, tasks, episodes, observations, actions and success, and list the 10 LIBERO-Spatial tasks.

**Deliverable:** A list of the 10 LIBERO-Spatial tasks and a short explanation of the evaluation loop.

**Status:**
| Step | Description | Status |
|---|---|---|
| 1 | The control loop and the three components | In progress |
| 2 | Explore the benchmark API (`lesson_01_benchmarks.py`) | Not started |
| 3 | Compare the suites | Not started |
| 4 | List the LIBERO-Spatial tasks: what stays the same and what changes | Not started |

---

## Step 1 — The control loop and the three components (In progress)

### Three components
| Component | Role | In this course |
|---|---|---|
| **LIBERO** | The benchmark: task definitions (BDDL files), saved initial states, a MuJoCo/robosuite simulator and success checks | Lessons 1–8 |
| **LeRobot** | Tools: the policy implementations, dataset format, env wrappers and evaluation scripts | Lessons 3, 6, 8 |
| **SmolVLA** | The policy: a vision-language-action model. Input: images + robot state + instruction. Output: actions | Lessons 6, 8 |

### Vocabulary
- **Suite:** a group of tasks built to test one kind of variation (e.g. `libero_spatial`).
- **Task:** one language goal in one scene layout, defined by a `.bddl` file.
- **Initial state:** one saved simulator snapshot for a task. Each task has 50, so evaluations can be reproduced.
- **Episode:** one rollout. Reset to an initial state, then run steps until success or the step limit.
- **Observation:** what the env returns each step (camera images, robot state, ...).
- **Action:** what the policy sends each step (7-D: end-effector delta pose + gripper).
- **Success:** the BDDL goal predicates are true, e.g. `(On bowl plate)`.

### The evaluation loop
```
reset(env, initial_state)  ->  obs
repeat until success or max_steps:
    action = policy(obs, instruction)      # SmolVLA (LeRobot)
    obs, reward, done, info = env.step(action)   # LIBERO / MuJoCo
success rate = (# successful episodes) / (# episodes)
```
