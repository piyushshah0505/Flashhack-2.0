"""
Semester analytics reporting for CampusCore.
Aggregates room utilization, GPU cluster stats, and boot success metrics.
"""


class SemesterAnalytics:
    """
    Generates semester-end analytics across all modules.
    """

    def __init__(
        self,
        allocation,
        room_schedule,
        boot_order,
        gpu_jobs,
        selected_jobs,
        rejected_jobs,
        wait_times,
        rooms,
    ):
        # Store module outputs for reporting.
        self.allocation = allocation
        self.room_schedule = room_schedule
        self.boot_order = boot_order
        self.gpu_jobs = gpu_jobs
        self.selected_jobs = selected_jobs
        self.rejected_jobs = rejected_jobs
        self.wait_times = wait_times
        self.rooms = rooms
        self.memory_limit = None

    def room_utilisation_report(self):
        # Calculate per-room and overall utilization statistics.
        total_possible_hours = 24
        stats = {}
        overall_hours_used = 0

        for room in self.rooms:
            courses_in_room = self.room_schedule.get(room, [])
            num_courses = len(courses_in_room)
            hours_used = sum(course["end"] - course["start"] for course in courses_in_room)
            percent = (hours_used / total_possible_hours) * 100 if total_possible_hours else 0
            stats[room] = {
                "courses": num_courses,
                "hours": hours_used,
                "percent": round(percent, 1),
            }
            overall_hours_used += hours_used

        total_room_hours_available = len(self.rooms) * total_possible_hours
        overall_percent = (
            (overall_hours_used / total_room_hours_available) * 100
            if total_room_hours_available
            else 0
        )
        stats["overall"] = round(overall_percent, 1)
        return stats

    def gpu_report(self):
        # Build GPU cluster summary statistics.
        total_jobs = len(self.gpu_jobs)
        selected = len(self.selected_jobs)
        rejected = len(self.rejected_jobs)
        memory_used = sum(job["memory"] for job in self.selected_jobs)
        memory_total = self.memory_limit if self.memory_limit is not None else memory_used

        wait_values = list(self.wait_times.values())
        avg_wait = sum(wait_values) / len(wait_values) if wait_values else 0

        return {
            "submitted": total_jobs,
            "selected": selected,
            "rejected": rejected,
            "memory_used": memory_used,
            "memory_total": memory_total,
            "avg_wait": round(avg_wait, 2),
        }

    def boot_report(self, boot_order, total_services):
        # Calculate boot success statistics.
        booted = len(boot_order) if boot_order else 0
        success_rate = (booted / total_services) * 100 if total_services else 0
        return {
            "booted": booted,
            "total": total_services,
            "success_rate": round(success_rate, 1),
        }

    def print_summary(self, room_stats, gpu_stats, boot_stats):
        # Print the formatted analytics summary.
        print("\n╔══════════════════════════════════════════╗")
        print("║       SEMESTER-END ANALYTICS REPORT      ║")
        print("╚══════════════════════════════════════════╝")

        print("\n📊 ROOM UTILISATION")
        print("─" * 40)
        for room in self.rooms:
            stats = room_stats.get(room, {"courses": 0, "hours": 0, "percent": 0})
            print(
                f"  {room}: {stats['courses']} courses | "
                f"{stats['hours']} hrs  | {stats['percent']:.1f}%"
            )
        overall = room_stats.get("overall", 0)
        print(f"  Overall: {overall:.1f}%")

        print("\n💻 GPU CLUSTER")
        print("─" * 40)
        print(f"  Jobs submitted : {gpu_stats['submitted']}")
        print(f"  Jobs selected  : {gpu_stats['selected']}")
        print(f"  Jobs rejected  : {gpu_stats['rejected']}")
        print(
            f"  Memory used    : {gpu_stats['memory_used']}/{gpu_stats['memory_total']} GB"
        )
        print(f"  Avg wait time  : {gpu_stats['avg_wait']:.2f}s")

        print("\n⚙️  SERVICE BOOT")
        print("─" * 40)
        print(
            f"  Services booted : {boot_stats['booted']}/{boot_stats['total']}"
        )
        print(f"  Success rate    : {boot_stats['success_rate']:.1f}%")

    def run(self, boot_order, total_services):
        # Run all analytics reports and print the summary.
        room_stats = self.room_utilisation_report()
        gpu_stats = self.gpu_report()
        boot_stats = self.boot_report(boot_order, total_services)
        self.print_summary(room_stats, gpu_stats, boot_stats)
        return {"rooms": room_stats, "gpu": gpu_stats, "boot": boot_stats}
