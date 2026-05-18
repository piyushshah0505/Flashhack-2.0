"""
CampusCore Main Driver
Runs all modules and the semester analytics summary.
"""

from semester_data import (
    COURSES,
    ROOMS,
    GPU_JOBS,
    GPU_MEMORY_LIMIT,
    MAX_CONCURRENT_USERS,
    SERVICES,
)
from module1_room_allocation import RoomAllocator
from module2_gpu_cluster import GPUCluster
from module3_service_boot import ServiceBootSequencer
from analytics import SemesterAnalytics


def print_separator(title):
    """
    Print a formatted separator banner with title.
    """
    # Render a simple bordered title banner.
    width = 46
    print("\n╔" + "═" * (width - 2) + "╗")
    print(f"║   {title:40} ║")
    print("╚" + "═" * (width - 2) + "╝")


def run_module1():
    """
    Run Module 1: Room Allocation.
    """
    # Allocate rooms and print the report.
    allocator = RoomAllocator(COURSES, ROOMS)
    allocator.allocate()
    allocator.report()
    return allocator


def run_module2():
    """
    Run Module 2: GPU Cluster.
    """
    # Select jobs, simulate GPU access, and print stats.
    cluster = GPUCluster(GPU_JOBS, GPU_MEMORY_LIMIT, MAX_CONCURRENT_USERS)
    cluster.run()
    return cluster


def run_module3(rejected_jobs):
    """
    Run Module 3: Service Boot Sequencer.
    """
    # Flag services if any GPU jobs were rejected.
    rejected_students = [job["student"] for job in rejected_jobs]
    flagged_students = list(rejected_students)
    if rejected_students:
        flagged_students.extend(["Portal", "Dashboard"])
    sequencer = ServiceBootSequencer(SERVICES, flagged_students=flagged_students)
    sequencer.run()
    return sequencer


def run_analytics(allocator, cluster, sequencer):
    """
    Run Semester Analytics.
    """
    # Aggregate and print analytics across all modules.
    analytics = SemesterAnalytics(
        allocator.allocation,
        allocator.room_schedule,
        sequencer.boot_order,
        GPU_JOBS,
        cluster.selected_jobs,
        cluster.rejected_jobs,
        cluster.wait_times,
        ROOMS,
    )
    analytics.memory_limit = cluster.memory_limit
    analytics.run(sequencer.boot_order, len(SERVICES))
    return analytics


if __name__ == "__main__":
    # Run the full CampusCore pipeline.
    print_separator("CAMPUSCORE — SEMESTER MANAGER")

    print("\n===== MODULE 1: ROOM ALLOCATION =====")
    allocator = run_module1()

    print("\n===== MODULE 2: GPU CLUSTER =====")
    cluster = run_module2()

    print("\n===== MODULE 3: SERVICE BOOT SEQUENCER =====")
    sequencer = run_module3(cluster.rejected_jobs)

    run_analytics(allocator, cluster, sequencer)

    print("\nCampusCore simulation complete!")
