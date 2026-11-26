from libero.libero import benchmark
import re

# 1. Get every registered suite: {name: class}
benchmark_dict = benchmark.get_benchmark_dict()

print("Available suites:")
for suite_name in benchmark_dict:
    print(" ", suite_name)

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