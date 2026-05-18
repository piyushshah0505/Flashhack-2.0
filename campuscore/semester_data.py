"""
Shared dataset for CampusCore - Semester Manager
Contains courses, rooms, GPU jobs, services, and system constraints
"""

# Course data: each course has an id, start time (hour), and end time (hour)
COURSES = [
    {"id": "CS101", "start": 8, "end": 10},
    {"id": "MA201", "start": 9, "end": 11},
    {"id": "PH301", "start": 10, "end": 12},
    {"id": "CS201", "start": 8, "end": 9},
    {"id": "EN101", "start": 13, "end": 14},
    {"id": "BIO101", "start": 14, "end": 16},
    {"id": "CHEM201", "start": 11, "end": 13},
    {"id": "PSY101", "start": 15, "end": 17},
]

# Room inventory
ROOMS = ["R1", "R2", "R3"]

# GPU jobs: each job has id, student name, memory required (GB), and value
GPU_JOBS = [
    {"id": "JOB1", "student": "Alice", "memory": 4, "value": 100},
    {"id": "JOB2", "student": "Bob", "memory": 3, "value": 85},
    {"id": "JOB3", "student": "Charlie", "memory": 5, "value": 120},
    {"id": "JOB4", "student": "Diana", "memory": 2, "value": 60},
    {"id": "JOB5", "student": "Eve", "memory": 4, "value": 95},
    {"id": "JOB6", "student": "Frank", "memory": 3, "value": 75},
]

# System constraints
GPU_MEMORY_LIMIT = 10
MAX_CONCURRENT_USERS = 3

# Service dependency map: service name -> list of dependencies
SERVICES = {
    "Database": [],
    "AuthService": ["Database"],
    "FileStorage": ["Database"],
    "Portal": ["AuthService", "FileStorage"],
    "Dashboard": ["Portal"],
    "EmailService": ["AuthService"],
    "Analytics": ["Dashboard", "FileStorage"],
}
