"""
Module 2: GPU Cluster using 0-1 Knapsack and a Counting Semaphore.
Selects jobs within a memory limit and simulates concurrent GPU access.
"""

import threading
import time


class CountingSemaphore:
    """
    Simple counting semaphore with blocking acquire behavior.
    """

    def __init__(self, max_count):
        # Initialize semaphore state and synchronization primitives.
        self.max_count = max_count
        self.count = 0
        self.lock = threading.Lock()
        self.condition = threading.Condition(self.lock)

    def acquire(self, student_id):
        # Block until a slot is available, then acquire it.
        with self.condition:
            while self.count >= self.max_count:
                print(
                    f"[SEMAPHORE] {student_id} is BLOCKED — GPU full "
                    f"({self.count}/{self.max_count})"
                )
                self.condition.wait()
            self.count += 1
            print(
                f"[SEMAPHORE] {student_id} ACQUIRED slot "
                f"({self.count}/{self.max_count})"
            )

    def release(self, student_id):
        # Release a slot and notify waiting threads.
        with self.condition:
            self.count -= 1
            self.condition.notify_all()
            print(
                f"[SEMAPHORE] {student_id} RELEASED slot "
                f"({self.count}/{self.max_count})"
            )


class GPUCluster:
    """
    Selects GPU jobs with knapsack optimization and runs them concurrently.
    """

    def __init__(self, jobs, memory_limit, max_concurrent):
        # Store configuration and initialize tracking structures.
        self.jobs = jobs
        self.memory_limit = memory_limit
        self.semaphore = CountingSemaphore(max_concurrent)
        self.selected_jobs = []
        self.rejected_jobs = []
        self.wait_times = {}

    def knapsack_select(self):
        # Select jobs using 0-1 knapsack dynamic programming.
        if not self.jobs or self.memory_limit <= 0:
            self.selected_jobs = []
            self.rejected_jobs = list(self.jobs)
            return

        n = len(self.jobs)
        capacity = self.memory_limit
        dp = [[0 for _ in range(capacity + 1)] for _ in range(n + 1)]

        for i in range(1, n + 1):
            job = self.jobs[i - 1]
            mem = job["memory"]
            val = job["value"]
            for w in range(0, capacity + 1):
                dp[i][w] = dp[i - 1][w]
                if mem <= w:
                    candidate = dp[i - 1][w - mem] + val
                    if candidate > dp[i][w]:
                        dp[i][w] = candidate

        selected = []
        w = capacity
        for i in range(n, 0, -1):
            if dp[i][w] != dp[i - 1][w]:
                job = self.jobs[i - 1]
                selected.append(job)
                w -= job["memory"]

        self.selected_jobs = list(reversed(selected))
        selected_ids = {job["id"] for job in self.selected_jobs}
        self.rejected_jobs = [job for job in self.jobs if job["id"] not in selected_ids]

    def _run_job(self, job):
        # Simulate GPU execution for a single job and track wait time.
        student = job["student"]
        start_time = time.time()
        self.semaphore.acquire(student)
        acquired_time = time.time()
        wait_time = acquired_time - start_time
        self.wait_times[student] = round(wait_time, 2)
        time.sleep(0.3)
        self.semaphore.release(student)

    def run(self):
        # Execute selection, report results, and simulate GPU access.
        print("===== MODULE 2: GPU CLUSTER =====")
        self.knapsack_select()

        print("\nSelected Jobs:")
        print("  Job ID | Student  | Memory | Value")
        print("  " + "-" * 36)
        if not self.selected_jobs:
            print("  (none)")
        else:
            for job in self.selected_jobs:
                print(
                    f"  {job['id']:<6} | {job['student']:<8} | "
                    f"{job['memory']:>6} | {job['value']:>5}"
                )

        total_memory = sum(job["memory"] for job in self.selected_jobs)
        print(f"\nTotal Memory Used: {total_memory}/{self.memory_limit} GB")

        print("\nRejected Jobs:")
        if not self.rejected_jobs:
            print("  (none)")
        else:
            rejected_ids = ", ".join(job["id"] for job in self.rejected_jobs)
            print(f"  {rejected_ids}")

        print(f"\nSemaphore simulation (max {self.semaphore.max_count} concurrent):")

        simulation_jobs = list(self.selected_jobs)
        if len(simulation_jobs) <= self.semaphore.max_count and self.rejected_jobs:
            simulation_jobs.append(self.rejected_jobs[0])

        threads = [threading.Thread(target=self._run_job, args=(job,)) for job in simulation_jobs]
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join()

        print("\nWait Times:")
        if not self.wait_times:
            print("  No wait times recorded.")
        else:
            for student, wait_time in self.wait_times.items():
                print(f"  {student}: {wait_time:.2f}s")

        return self.rejected_jobs
