"""
Module 1: Room Allocation using Greedy Interval Scheduling
Allocates courses to rooms using earliest-finish-time scheduling algorithm
"""


class RoomAllocator:
    """
    Allocates courses to rooms using greedy interval scheduling.
    Uses earliest-finish-time (EFT) rule to minimize room conflicts.
    """

    def __init__(self, courses, rooms):
        """
        Initialize the RoomAllocator with courses and available rooms.
        
        Args:
            courses: List of course dicts with 'id', 'start', 'end' keys
            rooms: List of room identifiers (strings)
        """
        self.courses = courses
        self.rooms = rooms
        self.allocation = {}  # Maps course_id to assigned room
        self.room_schedule = {room: [] for room in rooms}  # Tracks courses per room

    def _is_free(self, room, course):
        """
        Check if a room is free during the course's time slot.
        
        Args:
            room: Room identifier
            course: Course dict with 'start' and 'end' keys
            
        Returns:
            True if room has no time conflicts, False otherwise
        """
        # Check each course already assigned to this room
        for assigned_course in self.room_schedule[room]:
            # Check for time overlap
            assigned_start = assigned_course["start"]
            assigned_end = assigned_course["end"]
            course_start = course["start"]
            course_end = course["end"]
            
            # Courses overlap if one starts before the other ends
            if not (course_end <= assigned_start or course_start >= assigned_end):
                return False
        
        return True

    def allocate(self):
        """
        Allocate courses to rooms using greedy earliest-finish-time scheduling.
        Sorts courses by end time and assigns each to the first available room.
        
        Returns:
            Dictionary mapping course_id to assigned room
        """
        if not self.courses or not self.rooms:
            return self.allocation
        
        # Sort courses by end time (earliest finish time first)
        sorted_courses = sorted(self.courses, key=lambda c: c["end"])
        
        # Try to allocate each course to a room
        for course in sorted_courses:
            allocated = False
            
            # Find the first room that is free during this course's time
            for room in self.rooms:
                if self._is_free(room, course):
                    self.allocation[course["id"]] = room
                    self.room_schedule[room].append(course)
                    allocated = True
                    break
            
            # If no room is available, course cannot be scheduled
            if not allocated:
                self.allocation[course["id"]] = None
        
        return self.allocation

    def report(self):
        """
        Print a formatted report of room allocations and utilization statistics.
        Displays: course-to-room mapping, per-room utilization, and overall utilization.
        """
        print("\n" + "=" * 50)
        print("ALLOCATION DETAILS:")
        print("=" * 50)
        
        # Print course allocations
        for course in self.courses:
            course_id = course["id"]
            start = course["start"]
            end = course["end"]
            room = self.allocation.get(course_id, "UNALLOCATED")
            time_str = f"{start:02d}:00–{end:02d}:00"
            print(f"  {course_id:10} ({time_str})  →  {room}")
        
        # Calculate and print room utilization
        print("\n" + "=" * 50)
        print("ROOM UTILISATION:")
        print("=" * 50)
        
        total_possible_hours = 24  # Assuming 24-hour day for utilization %
        overall_hours_used = 0
        
        for room in self.rooms:
            courses_in_room = self.room_schedule[room]
            num_courses = len(courses_in_room)
            
            # Calculate total hours used in this room
            hours_used = 0
            for course in courses_in_room:
                hours_used += course["end"] - course["start"]
            
            # Calculate utilization percentage
            utilization_pct = (hours_used / total_possible_hours) * 100
            
            overall_hours_used += hours_used
            
            print(f"  {room}: {num_courses} courses | {hours_used} hrs | {utilization_pct:.1f}%")
        
        # Overall utilization
        total_room_hours_available = len(self.rooms) * total_possible_hours
        overall_utilization = (overall_hours_used / total_room_hours_available) * 100
        
        print("\n" + "=" * 50)
        print(f"OVERALL UTILISATION: {overall_utilization:.1f}%")
        print("=" * 50)
