def motor_config_validation(config:dict) -> bool:
    """
    Validate the motor configuration file for the elevator system.
    """
    table = {
        'startup_energy_loss': 0.0
    }
    for key in table.keys():
        if key not in config:
            print(f"Error: Attribute '{key}' is missing.\n")
            return False
    for key in table.keys():
        if not isinstance(config[key], type(table[key])):
            print(f"Error: Attribute '{key}' should be of type {type(table[key])}.\n")
            return False
    for key in table.keys():
        if config[key] <= table[key]:
            print(f"Error: Attribute '{key}' should be greater than 0.\n")
            return False
    return True
    
def elevator_config_validation(config:dict) -> bool:
    """
    Validate the elevator configuration file for the elevator system.
    """
    table = {
        "weight": 0,
        "capacity": 0,
        "init_floor": -1,
        "scheduling_win_size": 0,
        "motor_config": {}
    }
    for key in table.keys():
        if key not in config:
            print(f"Error: Attribute '{key}' is missing.\n")
            return False
    for key in table.keys():
        if not isinstance(config[key], type(table[key])):
            print(f"Error: Attribute '{key}' should be of type {type(table[key])}.\n")
            return False
    for key in table.keys():
        if key != 'motor_config':
            if config[key] <= table[key]:
                print(f"Error: Attribute '{key}' should be greater than 0.\n")
                return False
        else:
            if not motor_config_validation(config['motor_config']):
                return False
    return True

def building_config_validation(config:dict) -> bool:
    """
    Validate the building configuration file for the elevator system.
    """
    table = {
        'num_floors': 0,
        'floor_height': 0.0,
        'num_elevators': 0,
        "door_open_time": 0,
        "move_time_per_floor": 0,
        'elevator_configs': []
    }
    for key in table.keys():
        if key not in config:
            print(f"Error: Attribute '{key}' is missing.\n")
            return False
    for key in table.keys():
        if not isinstance(config[key], type(table[key])):
            print(f"Error: Attribute '{key}' should be of type {type(table[key])}.\n")
            return False
    for key in table.keys():
        if key == 'move_time_per_floor':
            if config[key] > config['door_open_time']:
                print(f"Error: Attribute '{key}' should be less than or equal to 'door_open_time'.\n")
                return False
            elif config['door_open_time'] % config[key] != 0:
                print(f"Error: Attribute 'door_open_time' should be a multiple of '{key}'.\n")
                return False
        elif key != 'elevator_configs':
            if config[key] <= table[key]:
                print(f"Error: Attribute '{key}' should be greater than 0.\n")
                return False
        else:
            if len(config[key]) != config['num_elevators']:
                print(f"Error: Attribute '{key}' should be a list of length {config['num_elevators']}.\n")
                return False
    for elevator in config['elevator_configs']:
        if not elevator_config_validation(elevator):
            return False
    return True

def config_validation(config:dict) -> bool:
    """
    Validate the configuration file for the elevator system.
    """
    table = {
        'strategy': 'scan',
        'total_flow': 0,
        'building_config': {}
    }
    for key in table.keys():
        if key not in config:
            print(f"Error: Attribute '{key}' is missing.\n")
            return False
    for key in table.keys():
        if not isinstance(config[key], type(table[key])):
            print(f"Error: Attribute '{key}' should be of type {type(table[key])}.\n")
            return False
    for key in table.keys():
        if key == 'total_flow':
            if config[key] <= 0:
                print(f"Error: Attribute '{key}' should be greater than 0.\n")
                return False
        # elif key == 'strategy':
        #     if config[key] != table[key]:
        #         print(f"Error: Attribute '{key}' should be '{table[key]}'.\n")
        #         return False
        else:
            if not building_config_validation(config['building_config']):
                return False
    return True

if __name__ == "__main__":
    import json
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python config_validation.py <config_file>")
        sys.exit(1)
    
    file_path = sys.argv[1]
    
    with open(file_path, 'r') as config_file:
        config:dict = json.load(config_file)
        if config_validation(config):
            print("Configuration is valid.")
        else:
            print("Configuration is invalid.")