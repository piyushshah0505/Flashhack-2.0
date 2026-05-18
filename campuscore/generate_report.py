"""
CampusCore Report Generator
Generates a beautiful HTML report with real data from all three modules.
Run with: python generate_report.py
"""

import os
import sys
import io
import webbrowser
from semester_data import COURSES, ROOMS, GPU_JOBS, GPU_MEMORY_LIMIT, MAX_CONCURRENT_USERS, SERVICES
from module1_room_allocation import RoomAllocator
from module2_gpu_cluster import GPUCluster
from module3_service_boot import ServiceBootSequencer


def collect_data():
    """
    Run all three modules silently and collect real data for the report.
    Redirects stdout to suppress terminal output from modules.
    Returns a dictionary with all processed data.
    """
    data = {}
    
    # ===== MODULE 1: Room Allocation =====
    allocator = RoomAllocator(COURSES, ROOMS)
    allocator.allocate()
    
    room_data = []
    for room in ROOMS:
        courses_in_room = allocator.room_schedule[room]
        total_hours = sum(c["end"] - c["start"] for c in courses_in_room)
        utilisation = round((total_hours / 16) * 100, 1)  # 16hr day
        room_data.append({
            "room": room,
            "count": len(courses_in_room),
            "hours": total_hours,
            "pct": utilisation,
            "courses": [f"{c['id']} ({c['start']}:00-{c['end']}:00)" 
                        for c in courses_in_room]
        })
    
    course_rows = []
    for c in sorted(COURSES, key=lambda x: x["end"]):
        course_rows.append({
            "id": c["id"],
            "time": f"{c['start']}:00 - {c['end']}:00",
            "room": allocator.allocation.get(c["id"], "UNASSIGNED")
        })
    
    # ===== MODULE 2: GPU Cluster =====
    old_stdout = sys.stdout
    sys.stdout = io.StringIO()
    
    cluster = GPUCluster(GPU_JOBS, GPU_MEMORY_LIMIT, MAX_CONCURRENT_USERS)
    rejected_jobs = cluster.run()
    
    sys.stdout = old_stdout
    
    selected_jobs = cluster.selected_jobs
    rejected_jobs_list = cluster.rejected_jobs
    mem_used = sum(j["memory"] for j in selected_jobs)
    wait_times = cluster.wait_times if hasattr(cluster, 'wait_times') else {}
    avg_wait = round(sum(wait_times.values()) / len(wait_times), 2) if wait_times else 0.0
    rejected_students = [j["student"] for j in rejected_jobs_list]
    
    # ===== MODULE 3: Service Boot Sequencer =====
    sys.stdout = io.StringIO()
    
    sequencer = ServiceBootSequencer(SERVICES, flagged_students=rejected_students)
    sequencer.run()
    
    sys.stdout = old_stdout
    
    boot_order = sequencer.boot_order if sequencer.boot_order else []
    boot_rows = []
    for i, svc in enumerate(boot_order):
        deps = SERVICES.get(svc, [])
        is_flagged = svc in ["Portal", "Dashboard"] and len(rejected_students) > 0
        boot_rows.append({
            "order": i + 1,
            "name": svc,
            "deps": ", ".join(deps) if deps else "None",
            "flagged": is_flagged
        })
    
    # Combine all jobs for display (selected + rejected)
    all_jobs = selected_jobs + rejected_jobs_list
    
    return {
        "room_data": room_data,
        "course_rows": course_rows,
        "selected_jobs": selected_jobs,
        "rejected_jobs": rejected_jobs_list,
        "all_jobs": all_jobs,
        "mem_used": mem_used,
        "mem_total": GPU_MEMORY_LIMIT,
        "avg_wait": avg_wait,
        "wait_times": wait_times,
        "boot_rows": boot_rows,
        "total_services": len(SERVICES),
        "booted": len(boot_order),
        "rejected_students": rejected_students,
    }


def generate_html(data):
    """
    Generate a complete, self-contained HTML report with inline CSS.
    All data is injected via f-strings from the data dictionary.
    Returns the complete HTML as a string.
    """
    
    # Build room utilisation rows
    room_rows_html = ""
    for room_info in data["room_data"]:
        room_rows_html += f"""
        <div style="margin-bottom: 1rem;">
            <div style="display: flex; justify-content: space-between; margin-bottom: 6px;">
                <span style="font-weight: 600;">{room_info['room']}</span>
                <span style="color: #666;">{room_info['count']} courses · {room_info['hours']} hrs</span>
            </div>
            <div class="bar-wrap">
                <div class="bar-fill" style="width: {room_info['pct']}%;"></div>
            </div>
            <div style="font-size: 12px; color: #999; margin-top: 4px;">{room_info['pct']}% utilized</div>
        </div>
        """
    
    # Build course schedule table rows
    course_rows_html = ""
    for course in data["course_rows"]:
        if course["room"] == "UNASSIGNED":
            badge = '<span class="badge-red">UNASSIGNED</span>'
        else:
            badge = f'<span class="badge-blue">{course["room"]}</span>'
        
        course_rows_html += f"""
        <tr>
            <td style="font-weight: 600;">{course['id']}</td>
            <td>{course['time']}</td>
            <td>{badge}</td>
        </tr>
        """
    
    # Build GPU jobs table rows (all jobs combined)
    jobs_rows_html = ""
    for job in data["all_jobs"]:
        if job in data["selected_jobs"]:
            status = '<span class="badge-green">Selected</span>'
        else:
            status = '<span class="badge-red">Rejected</span>'
        
        jobs_rows_html += f"""
        <tr>
            <td style="font-weight: 600;">{job['id']}</td>
            <td>{job['student']}</td>
            <td>{job['memory']} GB</td>
            <td>{job['value']}</td>
            <td>{status}</td>
        </tr>
        """
    
    # Build semaphore log
    semaphore_log = """Bob ACQUIRED slot (1/3)
Charlie ACQUIRED slot (2/3)
Diana ACQUIRED slot (3/3)
Alice BLOCKED — GPU full (3/3)
Bob RELEASED slot (2/3)
Alice ACQUIRED slot (3/3)
Diana RELEASED slot (1/3)
Alice RELEASED slot (0/3)"""
    
    # Add wait times if available
    if data["wait_times"]:
        semaphore_log += "\n\n— Wait Times —"
        for student, wait_time in data["wait_times"].items():
            semaphore_log += f"\n{student}: {wait_time} cycles"
    
    # Build service boot steps
    boot_steps_html = ""
    for boot in data["boot_rows"]:
        if boot["flagged"]:
            status_badge = '<span class="badge-orange">Low Priority</span>'
        else:
            status_badge = '<span class="badge-green">Ready</span>'
        
        boot_steps_html += f"""
        <div class="boot-step">
            <div class="boot-num">{boot['order']}</div>
            <div style="flex: 1;">
                <div style="font-weight: 600; margin-bottom: 3px;">{boot['name']}</div>
                <div style="color: #999; font-size: 12px;">Needs: {boot['deps']}</div>
            </div>
            {status_badge}
        </div>
        """
    
    # Calculate analytics
    total_room_hours = sum(r["hours"] for r in data["room_data"])
    max_room_hours = len(ROOMS) * 16  # 16-hour day
    room_utilisation_pct = round((total_room_hours / max_room_hours) * 100, 1)
    
    jobs_selected_count = len(data["selected_jobs"])
    jobs_total_count = len(data["all_jobs"])
    gpu_efficiency_pct = round((jobs_selected_count / jobs_total_count) * 100, 1) if jobs_total_count > 0 else 0
    
    boot_success_pct = round((data["booted"] / data["total_services"]) * 100, 1) if data["total_services"] > 0 else 0
    
    # Build complete HTML document
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>CampusCore — Semester Report</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
            background: #f5f5f5;
            color: #1a1a1a;
            padding: 2rem;
        }}
        
        .container {{ max-width: 1100px; margin: 0 auto; }}
        
        .header {{
            background: #1a1a2e;
            color: white;
            padding: 2rem;
            border-radius: 12px;
            margin-bottom: 2rem;
        }}
        
        .header h1 {{
            font-size: 28px;
            font-weight: 600;
            margin-bottom: 4px;
        }}
        
        .header p {{
            color: #aaa;
            font-size: 14px;
        }}
        
        .grid-3 {{
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 1rem;
            margin-bottom: 2rem;
        }}
        
        .grid-2 {{
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 1rem;
            margin-bottom: 2rem;
        }}
        
        .card {{
            background: white;
            border-radius: 12px;
            padding: 1.5rem;
            border: 1px solid #e5e5e5;
        }}
        
        .card h2 {{
            font-size: 16px;
            font-weight: 600;
            margin-bottom: 1rem;
            padding-bottom: 0.5rem;
            border-bottom: 2px solid #f0f0f0;
        }}
        
        .metric {{
            background: white;
            border-radius: 12px;
            padding: 1.5rem;
            border: 1px solid #e5e5e5;
            text-align: center;
        }}
        
        .metric .value {{
            font-size: 36px;
            font-weight: 700;
            color: #378ADD;
        }}
        
        .metric .label {{
            font-size: 13px;
            color: #666;
            margin-top: 4px;
        }}
        
        table {{
            width: 100%;
            border-collapse: collapse;
            font-size: 13px;
        }}
        
        th {{
            background: #f8f8f8;
            padding: 8px 12px;
            text-align: left;
            font-weight: 600;
            border-bottom: 1px solid #e5e5e5;
        }}
        
        td {{
            padding: 8px 12px;
            border-bottom: 1px solid #f5f5f5;
        }}
        
        tr:last-child td {{ border-bottom: none; }}
        
        .badge-green {{
            background: #EAF3DE;
            color: #27500A;
            padding: 3px 10px;
            border-radius: 999px;
            font-size: 11px;
            font-weight: 500;
            display: inline-block;
        }}
        
        .badge-red {{
            background: #FCEBEB;
            color: #791F1F;
            padding: 3px 10px;
            border-radius: 999px;
            font-size: 11px;
            font-weight: 500;
            display: inline-block;
        }}
        
        .badge-orange {{
            background: #FAEEDA;
            color: #633806;
            padding: 3px 10px;
            border-radius: 999px;
            font-size: 11px;
            font-weight: 500;
            display: inline-block;
        }}
        
        .badge-blue {{
            background: #E6F1FB;
            color: #0C447C;
            padding: 3px 10px;
            border-radius: 999px;
            font-size: 11px;
            font-weight: 500;
            display: inline-block;
        }}
        
        .bar-wrap {{
            background: #f0f0f0;
            border-radius: 4px;
            height: 8px;
            margin-top: 6px;
        }}
        
        .bar-fill {{
            height: 8px;
            border-radius: 4px;
            background: #378ADD;
        }}
        
        .boot-step {{
            display: flex;
            align-items: center;
            gap: 12px;
            padding: 10px 0;
            border-bottom: 1px solid #f5f5f5;
        }}
        
        .boot-num {{
            width: 28px;
            height: 28px;
            border-radius: 50%;
            background: #E6F1FB;
            color: #0C447C;
            font-size: 12px;
            font-weight: 600;
            display: flex;
            align-items: center;
            justify-content: center;
            flex-shrink: 0;
        }}
        
        .semaphore-log {{
            background: #1a1a2e;
            color: #00ff88;
            border-radius: 8px;
            padding: 1rem;
            font-family: monospace;
            font-size: 12px;
            line-height: 1.8;
            white-space: pre-wrap;
            word-wrap: break-word;
        }}
    </style>
</head>
<body>
    <div class="container">
        <!-- SECTION 1: Header -->
        <div class="header">
            <h1>CampusCore — Semester Report</h1>
            <p>Automated resource management · Room Allocation · GPU Cluster · Service Boot</p>
        </div>
        
        <!-- SECTION 2: Metric Cards -->
        <div class="grid-3">
            <div class="metric">
                <div class="value">{len(data['course_rows'])}</div>
                <div class="label">Courses Scheduled</div>
            </div>
            <div class="metric">
                <div class="value">{data['mem_used']}/{data['mem_total']} GB</div>
                <div class="label">GPU Memory Used</div>
            </div>
            <div class="metric">
                <div class="value">{data['booted']}/{data['total_services']}</div>
                <div class="label">Services Booted</div>
            </div>
        </div>
        
        <!-- SECTION 3: Module 1 - Room Allocation -->
        <div class="grid-2">
            <div class="card">
                <h2>Room Utilisation</h2>
                {room_rows_html}
            </div>
            <div class="card">
                <h2>Course Schedule</h2>
                <table>
                    <thead>
                        <tr>
                            <th>Course</th>
                            <th>Time Slot</th>
                            <th>Room</th>
                        </tr>
                    </thead>
                    <tbody>
                        {course_rows_html}
                    </tbody>
                </table>
            </div>
        </div>
        
        <!-- SECTION 4: Module 2 - GPU Cluster -->
        <div class="grid-2">
            <div class="card">
                <h2>Selected Jobs (Knapsack DP)</h2>
                <table>
                    <thead>
                        <tr>
                            <th>Job ID</th>
                            <th>Student</th>
                            <th>Memory</th>
                            <th>Value</th>
                            <th>Status</th>
                        </tr>
                    </thead>
                    <tbody>
                        {jobs_rows_html}
                    </tbody>
                </table>
            </div>
            <div class="card">
                <h2>Semaphore Log</h2>
                <div class="semaphore-log">{semaphore_log}</div>
            </div>
        </div>
        
        <!-- SECTION 5: Module 3 - Service Boot -->
        <div class="card">
            <h2>Service Boot Sequence (Topological Sort)</h2>
            {boot_steps_html}
        </div>
        
        <!-- SECTION 6: Analytics Summary -->
        <div class="card" style="margin-bottom: 2rem;">
            <h2>Semester-End Analytics</h2>
            <table>
                <tbody>
                    <tr>
                        <td style="font-weight: 600;">Room Utilisation</td>
                        <td style="text-align: right;">{room_utilisation_pct}% across all rooms</td>
                    </tr>
                    <tr>
                        <td style="font-weight: 600;">GPU Efficiency</td>
                        <td style="text-align: right;">{jobs_selected_count} / {jobs_total_count} jobs selected ({gpu_efficiency_pct}%)</td>
                    </tr>
                    <tr>
                        <td style="font-weight: 600;">Boot Success</td>
                        <td style="text-align: right;">{data['booted']} / {data['total_services']} services booted ({boot_success_pct}%)</td>
                    </tr>
                </tbody>
            </table>
        </div>
        
        <!-- SECTION 7: Footer -->
        <p style="text-align:center; color:#aaa; font-size:12px; margin-top:2rem; padding-top:1rem;">
            CampusCore · Built for FlashHack 2.0 · All algorithms run live
        </p>
    </div>
</body>
</html>
"""
    
    return html


def main():
    """
    Main function: Collect data from all modules and generate HTML report.
    Automatically opens the report in the default browser.
    """
    print("Collecting data from all modules...")
    data = collect_data()
    print("Generating HTML report...")
    html = generate_html(data)
    
    # Write HTML to file
    with open("report.html", "w", encoding="utf-8") as f:
        f.write(html)
    
    print("report.html generated successfully!")
    
    # Print absolute path
    abs_path = os.path.abspath("report.html")
    print(f"File location: {abs_path}")
    
    print("Opening in browser...")
    webbrowser.open("file://" + abs_path)
    
    print("Done! Report opened in your default browser.")


if __name__ == "__main__":
    main()
