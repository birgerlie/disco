"""
Endpoint Classification Worker Module
------------------------------------
Implements a worker-based system for classifying video endpoints using a queue.
This improves performance by allowing parallel classification of endpoints.
"""

import threading
import queue
from typing import List, Dict, Any
from discovery_system.endpoint_details import extract_endpoint_details


class EndpointClassificationWorker:
    """
    Worker class that processes video endpoints from a queue and classifies them.
    
    This allows for parallel classification of endpoints, improving performance.
    """
    
    def __init__(self, endpoint_queue, results, lock, username="admin", password="TANDBERG"):
        """
        Initialize the worker.
        
        Args:
            endpoint_queue (Queue): Queue containing endpoints to classify
            results (list): Shared list to store classified endpoints
            lock (Lock): Thread lock for synchronized access to results
            username (str): Username for authenticating with endpoints
            password (str): Password for authenticating with endpoints
        """
        self.endpoint_queue = endpoint_queue
        self.results = results
        self.lock = lock
        self.username = username
        self.password = password
        
    def run(self):
        """Process endpoints from the queue until a sentinel value (None) is received."""
        while True:
            # Get the next endpoint from the queue
            endpoint = self.endpoint_queue.get()
            
            # Check for sentinel value (None) to exit
            if endpoint is None:
                break
            
            # Process the endpoint
            try:
                # Extract detailed information about the endpoint
                detailed_endpoint = extract_endpoint_details(
                    endpoint, 
                    username=self.username, 
                    password=self.password
                )
                
                # Preserve original endpoint properties that might be overwritten
                # This is crucial for keeping original names and other data from the scan
                for key in ['name', 'hostname', 'ip', 'open_ports', 'type']:
                    if key in endpoint and key not in detailed_endpoint:
                        detailed_endpoint[key] = endpoint[key]
                
                # Add status and capabilities information if not already present
                if 'status' not in detailed_endpoint:
                    detailed_endpoint['status'] = 'online'
                    
                if 'capabilities' not in detailed_endpoint:
                    detailed_endpoint['capabilities'] = ['video', 'audio']
                
                # Add the classified endpoint to the results
                with self.lock:
                    self.results.append(detailed_endpoint)
                    
                print(f"Classified endpoint at {endpoint['ip']}: "
                      f"{detailed_endpoint.get('manufacturer', 'Unknown')} "
                      f"{detailed_endpoint.get('model', 'Unknown')}")
                
            except Exception as e:
                print(f"Error classifying endpoint at {endpoint['ip']}: {str(e)}")
                
                # Add the endpoint to results even if classification failed
                with self.lock:
                    self.results.append(endpoint)
            
            # Mark the task as done
            self.endpoint_queue.task_done()


def classify_endpoints(endpoints, num_workers=4, username="admin", password="TANDBERG"):
    """
    Classify a list of endpoints using multiple worker threads.
    
    Args:
        endpoints (list): List of endpoints to classify
        num_workers (int): Number of worker threads to use
        username (str): Username for authenticating with endpoints
        password (str): Password for authenticating with endpoints
        
    Returns:
        list: List of classified endpoints
    """
    # Create a queue for endpoints
    endpoint_queue = queue.Queue()
    
    # Create a list for results with a lock for thread-safe access
    results = []
    lock = threading.Lock()
    
    # Create and start worker threads
    workers = []
    for _ in range(num_workers):
        worker = EndpointClassificationWorker(
            endpoint_queue=endpoint_queue,
            results=results,
            lock=lock,
            username=username,
            password=password
        )
        
        thread = threading.Thread(target=worker.run)
        thread.daemon = True
        thread.start()
        workers.append(thread)
    
    # Add endpoints to the queue
    for endpoint in endpoints:
        endpoint_queue.put(endpoint)
    
    # Add sentinel values to signal workers to exit
    for _ in range(num_workers):
        endpoint_queue.put(None)
    
    # Wait for all worker threads to finish
    for worker in workers:
        worker.join()
    
    return results
