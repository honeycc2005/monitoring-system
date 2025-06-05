import random

def generate_attack_scenario():
    attack_type = random.choice(["cpu_spike", "memory_spike", "disk_flood", "network_burst", "combo_anomaly"])
    
    if attack_type == "cpu_spike":
        return [random.uniform(85, 100), random.uniform(30, 60), random.uniform(30, 60)]
    elif attack_type == "memory_spike":
        return [random.uniform(30, 60), random.uniform(85, 100), random.uniform(30, 60)]
    elif attack_type == "disk_flood":
        return [random.uniform(30, 60), random.uniform(30, 60), random.uniform(85, 100)]
    elif attack_type == "network_burst":
        return [random.uniform(30, 60), random.uniform(30, 60), random.uniform(30, 60), random.uniform(1e8, 1e9)]  # Add net
    elif attack_type == "combo_anomaly":
        return [random.uniform(90, 100), random.uniform(90, 100), random.uniform(90, 100)]
