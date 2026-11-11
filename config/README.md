# Config Tool Usage

This directory provides example configuration files and a validation tool to help you write and verify your own configuration files.

## Table of Contents
- [Overview](#overview)
- [How to Use](#how-to-use)
- [Config Format](#config-format)

## Overview

- `tools/config_sample.json`  
  A sample configuration file. Please refer to this format when writing your own.

- `tools/config_validation.py`  
  A config validation tool to help check whether your configuration file meets the required format.

## How to Use

1. **Write your configuration file**  
   Use `config_sample.json` as a reference and follow the same field structure.

2. **Run validation**  
   Use `config_validation.py` to check if your configuration is valid:

   ```powershell
   python tools/config_validation.py <path_to_your_config_file>
   ```

## Config Format

```json
{
    "strategy": (string) Name of the scheduling strategy,
    "total_flow": (int) Total number of people to be generated,
    "building_config": {
        "num_floors": (int) Total number of floors,
        "floor_height": (float) Height per floor [m],
        "num_elevators": (int) Number of elevators,
        "door_open_time": (int) Time for door opening and closing [s],
        "move_speed_per_floor": (int) Time for moving 1 floor [s]
        "elevator_configs": [
            {
                "weight": (int) Elevator empty weight [kg],
                "capacity": (int) Maximum number of people per elevator,
                "init_floor": (int) Initial floor position,
                "scheduling_win_size": (int) Size of the scheduling list,
                "motor_config": {
                    "startup_energy_loss": (float) Motor startup energy loss [J]
                }
            }
            ... (Repeat for each elevator, total should match `num_elevators`)
        ]
    }
}
```