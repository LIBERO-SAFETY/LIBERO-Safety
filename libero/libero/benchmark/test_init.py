import abc
import os
import glob
import random
import torch
import re

from typing import List, NamedTuple, Type
from libero.libero import get_libero_path
from libero.libero.benchmark.libero_suite_task_map import libero_task_map
import libero.libero.envs.bddl_utils as BDDLUtils
from libero.libero.benchmark.vla_safety_task_map import (
    vla_safety_task_map,
)

BENCHMARK_MAPPING = {}


def register_benchmark(target_class):
    """We design the mapping to be case-INsensitive."""
    BENCHMARK_MAPPING[target_class.__name__.lower()] = target_class


def get_benchmark_dict(help=False):
    if help:
        print("Available benchmarks:")
        for benchmark_name in BENCHMARK_MAPPING.keys():
            print(f"\t{benchmark_name}")
    return BENCHMARK_MAPPING


def get_benchmark(benchmark_name):
    return BENCHMARK_MAPPING[benchmark_name.lower()]


def print_benchmark():
    print(BENCHMARK_MAPPING)


class Task(NamedTuple):
    name: str
    language: str
    problem: str
    problem_folder: str
    bddl_file: str
    init_states_file: str
    level: int
    level_id: int


def grab_language_from_filename(x):
    if x[0].isupper():  # LIBERO-100
        if "SCENE10" in x:
            language = " ".join(x[x.find("SCENE") + 8 :].split("_"))
        else:
            language = " ".join(x[x.find("SCENE") + 7 :].split("_"))
    else:
        language = " ".join(x.split("_"))
    en = language.find(".bddl")
    return language[:en]


vla_safety_suites = [
    # Safety benchmarks
    'human_safety',
    'obstacle_avoidance',
    'affordance',
    'reasoning_safety',
    # Libero benchmarks
    'libero_10',
    'libero_90',
    'libero_spatial',
    'libero_object',
    'libero_goal',
]

task_maps = {}
max_len = 0
for vla_safety_suite in vla_safety_suites:
    task_maps[vla_safety_suite] = {0: {}, 1: {}, 2: {}}

    # Build task maps using the level-based structure from vla_arena_task_map
    for level in [0, 1, 2]:
        if level in vla_safety_task_map[vla_safety_suite]:
            level_tasks = vla_safety_task_map[vla_safety_suite][level]

            for level_id, task in enumerate(level_tasks):

                # Determine the actual problem folder name
                problem_folder = vla_safety_suite
                level_dir = f'L{level}'

                # Get language (removing level suffix for processing)
                language = grab_language_from_filename(task + '.bddl')

                bddl_filename = f'{task}.bddl'
                init_states_filename = f'{task}.pruned_init'
                task_maps[vla_safety_suite][level][task] = Task(
                    name=task,
                    language=language,
                    problem='vla_safety',
                    problem_folder=problem_folder,
                    bddl_file=bddl_filename,
                    init_states_file=init_states_filename,
                    level=level,
                    level_id=level_id,
                )


def get_all_tasks_for_suite(suite_name):
    """Get all tasks for a suite, combining all levels."""
    if suite_name not in vla_safety_task_map:
        return []

    all_tasks = []
    for level in [0, 1, 2]:
        if level in vla_safety_task_map[suite_name]:
            all_tasks.extend(vla_safety_task_map[suite_name][level])
    return all_tasks

def get_tasks_by_level(suite_name, level):
    """Get tasks for a specific suite and level."""
    if suite_name not in vla_safety_task_map:
        return []

    if level not in vla_safety_task_map[suite_name]:
        return []

    return vla_safety_task_map[suite_name][level]


class Benchmark(abc.ABC):
    """A Benchmark."""

    def __init__(self, task_order_index=0):
        self.task_embs = None
        self.task_order_index = task_order_index
        self.level_task_maps = {}


    def _make_benchmark(self):
        self.level_task_maps = {0: [], 1: [], 2: []}
        for level in [0, 1, 2]:
            if level in vla_safety_task_map[self.name]:
                level_tasks = vla_safety_task_map[self.name][level]
                for task_name in level_tasks:
                    if task_name in task_maps[self.name][level]:
                        self.level_task_maps[level].append(
                            task_maps[self.name][level][task_name]
                        )
        self.tasks = [task 
                        for level_dict in task_maps[self.name].values() 
                        for task in level_dict.values()
                    ]
        self.n_tasks = len(self.tasks)

    def get_num_tasks(self):
        return self.n_tasks

    def get_task_names(self):
        return [task.name for task in self.tasks]

    def get_task_problems(self):
        return [task.problem for task in self.tasks]

    def get_task_bddl_files(self):
        return [task.bddl_file for task in self.tasks]

    
    def get_task_by_level_id(self, level: int, level_id: int) -> Task | None:
        """
        Get task by level and level_id.

        Args:
            level: The difficulty level (0, 1, or 2)
            level_id: The index within that level (0-based)

        Returns:
            Task object or None if not found
        """
        if level not in [0, 1, 2]:
            raise ValueError(f'Level must be 0, 1, or 2, got {level}')

        if level not in self.level_task_maps:
            return None

        level_tasks = self.level_task_maps[level]
        if 0 <= level_id < len(level_tasks):
            return level_tasks[level_id]
        return None

    def _get_task_file_path(
        self,
        level: int,
        level_id: int,
        file_type: str,
        file_extension: str,
    ) -> str | None:
        """
        Generic method to get file paths by level and level_id.

        Args:
            level: The difficulty level (0, 1, or 2)
            level_id: The index within that level (0-based)
            file_type: Type of file ("bddl_files", "init_states", etc.)
            file_extension: File extension (".bddl", ".pruned_init", etc.)
        """
        task = self.get_task_by_level_id(level, level_id)
        if task is None:
            return None

        level_dir = f'L{task.level}'

        if file_type == 'bddl_files':
            filename = task.bddl_file
        elif file_type == 'init_states':
            filename = task.init_states_file
        else:
            return None

        file_path = os.path.join(
            get_libero_path(file_type),
            task.problem_folder,
            level_dir,
            filename,
        )
        return file_path

    def get_task_bddl_file_path_by_level_id(
        self, level: int, level_id: int
    ) -> str | None:
        """Get the bddl file path by level and level_id."""
        return self._get_task_file_path(level, level_id, 'bddl_files', '.bddl')

    def get_task_init_states_by_level_id(self, level: int, level_id: int):
        """Get init states by level and level_id."""
        init_states_path = self._get_task_file_path(
            level, level_id, 'init_states', '.pruned_init'
        )
        if init_states_path is None:
            return None
        return torch.load(init_states_path, weights_only=False)

    # crx 0201
    def get_task_demonstration_by_level_id(
        self, level: int, level_id: int
    ) -> str | None:
        """Get demonstration path by level and level_id."""
        task = self.get_task_by_level_id(level, level_id)
        if task is None:
            return None

        # Extract base task name without level suffix for demo file
        base_task_name = re.sub(r'_L[0-2]$', '', task.name)
        level_dir = f'L{task.level}'
        demo_path = (
            f'{task.problem_folder}/{level_dir}/{base_task_name}_demo.hdf5'
        )
        return demo_path

    def get_num_tasks_by_level(self, level: int) -> int:
        """Get the number of tasks for a specific level."""
        if level not in [0, 1, 2]:
            raise ValueError(f'Level must be 0, 1, or 2, got {level}')
        return len(self.level_task_maps.get(level, []))

    def get_all_tasks_by_level(self, level: int) -> list[Task]:
        """Get all tasks for a specific level."""
        if level not in [0, 1, 2]:
            raise ValueError(f'Level must be 0, 1, or 2, got {level}')
        return self.level_task_maps.get(level, [])
    
    def get_task_bddl_file_path(self, level, i):
        """Get the bddl file path with level-based directory structure."""
        return self.get_task_bddl_file_path_by_level_id(level, i)

    def get_task_demonstration(self, i):
        """Get demonstration path by task index."""
        assert (
            i >= 0 and i < self.n_tasks
        ), f'[error] task number {i} is outer of range {self.n_tasks}'

        task = self.tasks[i]
        return self.get_task_demonstration_by_level_id(
            task.level, task.level_id
        )

    def get_task(self, i):
        return self.tasks[i]

    def get_task_emb(self, i):
        return self.task_embs[i]
    
    def get_task_init_states(self, level, i):
        return self.get_task_init_states_by_level_id(level, i)


    def get_tasks_by_level(self, level):
        """Get all tasks with a specific level."""
        assert level in [0, 1, 2], f'Level must be 0, 1, or 2, got {level}'
        return [task for task in self.tasks if task.level == level]

    def get_task_distribution_by_level(self):
        """Get the distribution of tasks across levels."""
        distribution = {0: 0, 1: 0, 2: 0}
        for task in self.tasks:
            distribution[task.level] += 1
        return distribution

    def set_task_embs(self, task_embs):
        self.task_embs = task_embs


def create_benchmark_class(name):
    """Create a benchmark class with the given name."""

    class BenchmarkClass(Benchmark):
        def __init__(self, task_order_index=0):
            super().__init__(task_order_index=task_order_index)
            self.name = name
            self._make_benchmark()

    BenchmarkClass.__name__ = name
    return BenchmarkClass


for name in vla_safety_suites:
    benchmark_class = create_benchmark_class(name)
    register_benchmark(benchmark_class)


# Example usage:
if __name__ == '__main__':
    # Test all benchmarks
    # Organized by category for better readability
    all_benchmarks = [
        # Safety benchmarks
        'human_safety',
        'obstacle_avoidance',
        'affordance',
        'reasoning_safety',
        # # Libero benchmarks
        # 'libero_10',
        # 'libero_90',
        # 'libero_spatial',
        # 'libero_object',
        # 'libero_goal',
    ]

    print('Testing all VLA Arena benchmarks:')
    print('=' * 60)

    for benchmark_name in all_benchmarks:
        # Get benchmark class
        benchmark_class = get_benchmark(benchmark_name)

        # Create instance
        benchmark = benchmark_class()

        # Print summary
        print(f'\n{benchmark_name.upper()}')
        print('-' * 40)

        # Get task distribution
        distribution = benchmark.get_task_distribution_by_level()
        total = sum(distribution.values())

        print(f'Total tasks: {total}')
        for level in [0, 1, 2]:
            print(f'  Level {level}: {distribution[level]} tasks')

        # Test accessing a task from each level
        for level in [0, 1, 2]:
            if distribution[level] > 0:
                task = benchmark.get_task_by_level_id(level, 0)
                if task:
                    print(f'  Sample Level {level} task: {task.name}')

    print('\n' + '=' * 60)
    print('All benchmarks loaded successfully!')