# scripts/vm_log_simulator.py
import json
import time
import random
import os
from datetime import datetime

def generate_vm_logs():
    vm_ids = [f"vm-{i:03d}" for i in range(1, 31)]  # Simulate 30 VMs
    services = ["nginx", "application", "database", "redis", "auth"]
    log_levels = ["INFO", "WARN", "ERROR", "DEBUG"]
    
    while True:
        for vm_id in vm_ids:
            # Create VM directory
            vm_dir = f"/var/log/app/{vm_id}"
            os.makedirs(vm_dir, exist_ok=True)
            
            # Generate different types of logs
            for service in random.sample(services, random.randint(1, 3)):
                log_entry = {
                    "timestamp": datetime.utcnow().isoformat() + "Z",
                    "level": random.choice(log_levels),
                    "service": service,
                    "vm_id": vm_id,
                    "datacenter": "dc1",
                    "message": f"{service} processing request {random.randint(1000, 9999)}",
                    "response_time_ms": random.randint(10, 1000),
                    "status_code": random.choice([200, 201, 400, 404, 500])
                }
                
                with open(f"{vm_dir}/{service}.log", "a") as f:
                    f.write(json.dumps(log_entry) + "\n")
        
        time.sleep(2)  # Generate logs every 2 seconds

if __name__ == "__main__":
    generate_vm_logs()