# LIBERO Crash Course for VLA Research

**Duration:** 4 hours (240 minutes)  
**Format:** 8 short, hands-on lessons  
**Prerequisites:** Python, basic robotics concepts, and a working LIBERO + LeRobot + SmolVLA environment  
**Goal:** Understand LIBERO well enough to inspect tasks and simulator states, evaluate a frozen VLA policy, and design controlled experiments with object positions and camera viewpoints.

> **Scope:** Four hours is enough for guided exploration and a small pilot, not a statistically rigorous research study. The course does **not** cover installing LIBERO or training a VLA from scratch.

## Course Schedule

| Lesson | Title | Time | Progress |
|---|---|---:|---|
| 1 | LIBERO Architecture, Benchmarks, and Tasks | 30 min | Completed |
| 2 | Initial States and Task Configurations | 30 min | In progress |
| 3 | Observations, Cameras, and Robot States | 30 min | Not started |
| 4 | Robot Actions and Simulation Execution | 25 min | Not started |
| 5 | Demonstration Datasets, Training, and Evaluation | 25 min | Partially discussed |
| 6 | Evaluating a Pretrained VLA Policy | 30 min | Not started |
| 7 | Modifying Object Positions and Camera Viewpoints | 40 min | Not started |
| 8 | Designing a Controlled VLA Research Experiment | 30 min | Not started |
| **Total** | | **240 min** | |

## Lesson 1 — LIBERO Architecture, Benchmarks, and Tasks (30 min)

**Learning goals**
- Distinguish LIBERO (benchmark/simulator) from LeRobot (tooling) and SmolVLA (policy).
- Understand suites, tasks, episodes, observations, actions, and success conditions.
- Locate the benchmark APIs and enumerate the tasks in `libero_spatial`.

**Topics and activities**
1. Map the control loop: simulator observation → VLA policy → robot action → simulator step.
2. Compare `libero_spatial`, `libero_object`, `libero_goal`, `libero_10`, and `libero_90`.
3. Run `benchmark.get_benchmark_dict()`, `suite.get_num_tasks()`, and `suite.get_task(task_index)`.
4. Read the task names and identify what stays constant versus what changes.

**Deliverable:** A list of the 10 LIBERO-Spatial tasks and a short explanation of the evaluation loop.

## Lesson 2 — Initial States and Task Configurations (30 min)

**Learning goals**
- Distinguish a task from one of its saved initial states.
- Interpret the `get_task_init_states(task_index)` return value.
- Find which simulator state components vary and map them to named joints/objects.

**Topics and activities**
1. Inspect Task 2 (`pick_up_the_black_bowl_from_table_center_and_place_it_on_the_plate`).
2. Verify the local array shape: `(50, 92)` (50 configurations, each represented by 92 values).
3. Compare initial states and find changing vector components.
4. Load one state with the environment API and inspect robot and object poses by name.
5. Discuss why changes in both robot and object state are confounding factors for position experiments.

**Naming convention:** Use `task_index` to select a task, `state_index` to select an initial state, `num_tasks` and `num_states` for counts.

**Deliverable:** A script showing the task name, state array shape, differing indices, and bowl position for selected states.

## Lesson 3 — Observations, Cameras, and Robot States (30 min)

**Learning goals**
- Identify the observations available from LIBERO.
- Determine which fields a particular pretrained policy actually consumes.
- Understand camera frames, wrist-camera images, and robot proprioception.

**Topics and activities**
1. Call `env.reset()` and inspect observation keys, shapes, and data types.
2. Display/save agent-view and eye-in-hand images.
3. Inspect end-effector pose, joint positions, and gripper state.
4. Trace the LeRobot observation preprocessing and feature names expected by SmolVLA.
5. Differentiate privileged simulator state from policy-visible observation.

**Deliverable:** Two saved camera images and a documented observation schema for the running policy.

## Lesson 4 — Robot Actions and Simulation Execution (25 min)

**Learning goals**
- Understand the action interface and how actions affect the simulated robot.
- Inspect action dimensions, units/conventions, and execution frequency.
- Distinguish one simulation step from an entire evaluation episode.

**Topics and activities**
1. Inspect the action specification for the selected LIBERO environment.
2. Execute a safe small test action, then read the updated observation.
3. Inspect end-effector movement and gripper response.
4. Understand action normalization, VLA action chunks, and episode horizons.
5. Determine how task success and termination are checked.

**Deliverable:** A short action-rollout script and a recorded change in robot state.

## Lesson 5 — Demonstration Datasets, Training, and Evaluation (25 min)

**Learning goals**
- Understand what LIBERO demonstrations contain.
- Distinguish training demonstrations from simulator evaluation rollouts.
- Critically interpret published LIBERO success rates and data overlap.

**Topics and activities**
1. Inspect the structure of a demonstration trajectory (images/states/actions/task metadata).
2. Review the original dataset organization and suite-specific demonstration counts.
3. Explain why there is no single mandatory train/validation/test split for every VLA paper.
4. Review in-domain fine-tuning versus held-out configurations or unseen tasks.
5. Identify evidence needed to verify training/evaluation contamination claims.

**Deliverable:** A concise dataset-and-evaluation protocol checklist for reading VLA papers.

## Lesson 6 — Evaluating a Pretrained VLA Policy (30 min)

**Learning goals**
- Run SmolVLA on a selected LIBERO task without training it.
- Record policy rollouts and compute empirical success rate.
- Understand the limits of estimates from a small number of episodes.

**Topics and activities**
1. Confirm the pretrained checkpoint and compatible observation mapping.
2. Run policy inference in a closed loop on one LIBERO task.
3. Log task, `state_index`, seed, actions, completion, and video.
4. Evaluate several initial states and compute successes / attempts.
5. Review fair comparisons: same seeds, resets, horizon, and checkpoint.

**Deliverable:** An evaluation table (episode, initial state, success/failure) and at least one rollout recording.

## Lesson 7 — Modifying Object Positions and Camera Viewpoints (40 min)

**Learning goals**
- Change scene configurations without modifying the frozen policy.
- Modify object poses and camera extrinsics in MuJoCo/LIBERO.
- Preserve task semantics and physical validity.

**Topics and activities**
1. Locate the black bowl's named body/joint and its world-frame pose.
2. Shift its position by a small controlled amount, then reset/settle the scene appropriately.
3. Check collision, reachability, placement constraints, and consistency with the task instruction.
4. Inspect camera positions/orientations and change a viewpoint while controlling other variables.
5. Save paired before/after images and configuration metadata.
6. Explain why changing the camera can introduce distribution shift rather than improved observability.

**Deliverable:** Reproducible scripts for one valid object perturbation and one camera perturbation.

## Lesson 8 — Designing a Controlled VLA Research Experiment (30 min)

**Learning goals**
- Turn observations into a falsifiable research hypothesis.
- Establish controls that separate intervention effects from confounders.
- Design a reproducible pilot for frozen-policy robustness.

**Topics and activities**
1. Define a hypothesis: performance varies with object position or camera viewpoint.
2. Specify intervention variables, fixed variables, and evaluation seeds.
3. Choose a small grid of physically valid object positions or camera poses.
4. Run paired policy evaluations; store results and failure categories.
5. Visualize a preliminary success-rate map and identify uncertainty.
6. Discuss whether a second robot could realize the most promising object repositioning interventions.

**Deliverable:** A one-page experiment specification and a pilot results table or plot.

## Suggested Repository Structure

```text
libero-crash-course/
├── README.md
├── lesson_01_benchmarks.py
├── lesson_02_initial_states.py
├── lesson_03_observations.py
├── lesson_04_actions.py
├── lesson_05_dataset_inspection.py
├── lesson_06_evaluate_policy.py
├── lesson_07_scene_perturbations.py
├── lesson_08_experiment.py
└── outputs/
    ├── images/
    ├── videos/
    └── results/
```

## Research Questions to Carry Forward

**Object intervention:** For a frozen policy $\pi$, how does the probability of success vary with an object's initial pose $s$?

$$
p(s) = P(\mathrm{success}\mid s,\pi).
$$

**Viewpoint intervention:** For a frozen policy $\pi$ and a fixed physical scene, how does camera configuration $c$ affect success?

$$
p(c) = P(\mathrm{success}\mid c,\pi).
$$

These expressions represent conditional success probabilities, **not** quantities provided directly by LIBERO. Estimation requires repeated valid rollouts and careful control of the evaluation distribution.

## References

- [LIBERO official repository](https://github.com/Lifelong-Robot-Learning/LIBERO)
- [LIBERO project page](https://libero-project.github.io/)
- [LeRobot repository](https://github.com/huggingface/lerobot)
- [LeRobot LIBERO documentation](https://huggingface.co/docs/lerobot/libero)

---

**Current position:** Lesson 1 is complete; Lesson 2 is in progress. Next: inspect how Task 2's 92-dimensional saved state maps to named simulator joints and objects.
