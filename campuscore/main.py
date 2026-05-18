"""
CampusCore Main Driver
Runs Module 1 (Room Allocation) and Module 3 (Service Boot Sequencer)
"""

from semester_data import COURSES, ROOMS, SERVICES
from module1_room_allocation import RoomAllocator
from module3_service_boot import ServiceBootSequencer


def print_separator(title):
    """
    Print a formatted separator banner with title.
    
    Args:
        title: String to display in the banner
    """
    width = 38
    print("\n╔" + "═" * (width - 2) + "╗")
    print(f"║   {title:34} ║")
    print("╚" + "═" * (width - 2) + "╝")


def main():
    """
    Main function: Run Module 1 and Module 3 of CampusCore.
    """
    # Print main header
    print_separator("CAMPUSCORE — SEMESTER MANAGER")
    
    # ===== MODULE 1: ROOM ALLOCATION =====
    print("\n===== MODULE 1: ROOM ALLOCATION =====")
    
    # Create and run room allocator
    allocator = RoomAllocator(COURSES, ROOMS)
    allocator.allocate()
    allocator.report()
    
    # ===== MODULE 3: SERVICE BOOT SEQUENCER =====
    print("\n\n===== MODULE 3: SERVICE BOOT SEQUENCER =====")
    
    # Create and run service boot sequencer (no flagged students for this run)
    sequencer = ServiceBootSequencer(SERVICES, flagged_students=[])
    sequencer.run()
    
    # ===== NOTE =====
    print("\n" + "=" * 70)
    print("NOTE: Module 2 (GPU Cluster) will be integrated from Laptop 2")
    print("=" * 70)


if __name__ == "__main__":
    main()
