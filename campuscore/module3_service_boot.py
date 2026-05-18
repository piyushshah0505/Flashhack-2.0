"""
Module 3: Service Boot Sequencer using Topological Sort
Determines the correct order to boot services based on dependencies using Kahn's algorithm
"""


class ServiceBootSequencer:
    """
    Sequences service boot order using topological sorting (Kahn's algorithm).
    Handles service dependencies and flags services from flagged students.
    """

    def __init__(self, services, flagged_students=None):
        """
        Initialize the ServiceBootSequencer with service dependencies.
        
        Args:
            services: Dict mapping service name to list of dependencies
            flagged_students: Optional list of student names whose services are flagged
        """
        self.services = services
        self.flagged_students = flagged_students or []
        self.boot_order = []
        self.in_degree = {}
        self.adjacency_list = {}

    def topological_sort(self):
        """
        Implement Kahn's algorithm (BFS-based) to perform topological sorting.
        Detects cycles and returns boot order if no cycles exist.
        
        Returns:
            List of services in boot order, or None if a cycle is detected
        """
        # Initialize in-degree and adjacency list
        self.in_degree = {service: 0 for service in self.services}
        self.adjacency_list = {service: [] for service in self.services}
        
        # Build the dependency graph
        for service, dependencies in self.services.items():
            for dependency in dependencies:
                # Add edge: dependency -> service
                self.adjacency_list[dependency].append(service)
                # Increment in-degree of service
                self.in_degree[service] += 1
        
        # Queue for BFS: start with all nodes having in-degree 0
        queue = [service for service in self.services if self.in_degree[service] == 0]
        processed_count = 0
        self.boot_order = []
        
        # Process nodes in topological order
        while queue:
            current_service = queue.pop(0)
            self.boot_order.append(current_service)
            processed_count += 1
            
            # Reduce in-degree of dependent services
            for dependent in self.adjacency_list[current_service]:
                self.in_degree[dependent] -= 1
                
                # Add to queue if in-degree becomes 0
                if self.in_degree[dependent] == 0:
                    queue.append(dependent)
        
        # Check if all nodes were processed (no cycle)
        if processed_count != len(self.services):
            print("\n[ERROR] Cycle detected in service dependencies!")
            return None
        
        return self.boot_order

    def run(self):
        """
        Execute the boot sequence: sort services, print boot order with status.
        Marks services as [LOW PRIORITY] if owned by flagged students.
        
        Returns:
            List of services in boot order, or None if cycle detected
        """
        # Perform topological sort
        boot_order = self.topological_sort()
        
        if boot_order is None:
            print("[ERROR] Service boot sequence cannot be determined due to circular dependencies.")
            return None
        
        # Print boot sequence table
        print("\n" + "=" * 70)
        print("SERVICE BOOT SEQUENCE:")
        print("=" * 70)
        
        for index, service in enumerate(boot_order, start=1):
            # Get dependencies for this service
            dependencies = self.services[service]
            deps_str = ", ".join(dependencies) if dependencies else "None"
            
            # Check if this service is flagged (belongs to flagged student)
            # For this implementation, we check if service contains student name
            is_flagged = any(student.lower() in service.lower() for student in self.flagged_students)
            priority_marker = "[LOW PRIORITY]" if is_flagged else ""
            
            # Print service boot entry
            print(f"  [{index}] {service:15} ✓ Ready     (needs: {deps_str}) {priority_marker}")
        
        print("=" * 70)
        
        return self.boot_order
