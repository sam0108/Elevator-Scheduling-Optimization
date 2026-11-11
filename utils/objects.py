from enum import Enum
import json
import random
import sys
import time
from utils.data_structures import Queue
import copy
import os
from os import system

class Direction(Enum):
    """Direction of the elevator.

    Args:
        Enum (int): The direction of the elevator.
    """
    UP = 1
    DOWN = 2
    IDLE = 3
    OPEN = 4
    
class Human():
    """Only use when a new human is generated outside an elavator.
    """
    
    _human_count = 0
    
    def __init__(self, curr_floor:int, weight:int=70, direction:Direction=Direction.IDLE):
        self.weight:int = weight
        self.curr_floor:int = curr_floor
        self.direction:Direction = direction
        self.__seed:int = Human._human_count
        Human._human_count += 1
    
    def __repr__(self)->str:
        return f"Human({self.curr_floor}, {self.weight}, {self.direction})"
    
    def to_dict(self)->dict:
        """Convert the human object to a dictionary.

        Returns:
            dict: The dictionary representation of the human object.
        """
        return {
            'curr_floor': self.curr_floor,
            'weight': self.weight,
            'direction': self.direction.name
        }
        
    def pick_destination(self, num_floors:int)->int:
        """Pick a random destination floor for the human.
        
        Args:
            num_floors (int): The total number of floors in the building.
        
        Returns:
            int: The destination floor for the human.
        """
        if self.direction == Direction.UP:
            random.seed(self.__seed)
            self.destination = random.randint(self.curr_floor + 1, num_floors - 1)
        elif self.direction == Direction.DOWN:
            random.seed(self.__seed)
            self.destination = random.randint(0, self.curr_floor - 1)
        else:
            random.seed(self.__seed)
            self.destination = random.randint(0, num_floors - 1)
        return self.destination
        
    def pick_direction(self, num_floors:int)->Direction:
        """Pick a random direction for the human.

        Args:
            num_floors (int): The total number of floors in the building.

        Returns:
            Direction: The direction the human wants to go
        """
        if self.curr_floor == 0:
            self.direction = Direction.UP
        elif self.curr_floor == num_floors - 1:
            self.direction = Direction.DOWN
        else:
            random.seed(self.__seed)
            self.direction = random.choice([Direction.UP, Direction.DOWN])
        return self.direction
    
class Motor():
    def __init__(self, config:dict, debug:bool=False):
        self.__startup_energy_loss:dict = config['startup_energy_loss']
        self.__debug:bool = debug
        
    @property
    def startup_energy_loss(self)->float:
        """Get the startup energy loss of the motor.

        Returns:
            float: The startup energy loss of the motor in Joules.
        """
        return self.__startup_energy_loss
    
    def energy_consumption(self, start_floor:int, dest_floor:int, floor_height:float, total_weight:int)->float:
        """Calculate the energy consumption of the elevator based on the distance traveled.
        
        Args:
            start_floor (int): The starting floor of the elevator.
            dest_floor (int): The destination floor of the elevator.
            floor_height (float): The height of each floor in meters.
            total_weight (int): The total weight of the elevator and passengers in kg.
            
        Returns:
            float: The energy consumption of the elevator in Joules.
        """
        s = floor_height * abs(start_floor - dest_floor)
        g = 9.81
        m = float(total_weight)
        return m * g * s + self.__startup_energy_loss
    
class Elevator():
    def __init__(self, config:dict, num_floors:int, floor_height:float, debug:bool=False, ticktime:int=1):
        self.__ticktime:int = ticktime
        self.__weight:int = config['weight']
        self.__capacity:int = config['capacity']
        self.__curr_floor:int = config['init_floor']
        self.__dest_floor:int = None
        self.__scheduling_win_size:int = config['scheduling_win_size']
        self.__floor_height:float = floor_height
        self.__debug:bool = debug
        self.__curr_direction:Direction = Direction.IDLE
        self.__prev_direction:Direction = Direction.IDLE
        self.__num_people:int = 0
        self.__in_pending:list = [0 for _ in range(num_floors)]
        self.__scheduled_list:list = []
        self.__energy_comsumption:float = 0.0
        self.__motor:Motor = Motor(config['motor_config'], self.__debug)
        self.__accu_ticktime:int = 0
        self.__last_scheduled_list:list = []
        
    @property
    def ticktime(self)->int:
        """Get the tick time of the elevator.

        Returns:
            int: The tick time of the elevator in seconds.
        """
        return self.__ticktime
    
    @property
    def weight(self)->int:
        """Get the weight of the elevator.

        Returns:
            int: The weight of the elevator in kg.
        """
        return self.__weight
    
    @property
    def total_weight(self)->int:
        """Calculate the total weight of the elevator including passengers.

        Returns:
            int: The total weight of the elevator in kg.
        """
        return self.__weight + self.__num_people * 70
    
    @property
    def capacity(self)->int:
        """Get the capacity of the elevator.

        Returns:
            int: The capacity of the elevator in number of people.
        """
        return self.__capacity
    
    @property
    def curr_floor(self)->int:
        """Get the current floor of the elevator.

        Returns:
            int: The current floor of the elevator.
        """
        return self.__curr_floor
    
    @property
    def dest_floor(self)->int:
        """Get the destination floor of the elevator.

        Returns:
            int: The destination floor of the elevator.
        """
        return self.__dest_floor
    
    @property
    def scheduling_win_size(self)->int:
        """Get the scheduling window size of the elevator.

        Returns:
            int: The scheduling window size of the elevator in seconds.
        """
        return self.__scheduling_win_size
    
    @property
    def debug(self)->bool:
        """Get the debug mode of the elevator.

        Returns:
            bool: True if debug mode is enabled, False otherwise.
        """
        return self.__debug
    
    @property
    def curr_direction(self)->Direction:
        """Get the current direction of the elevator.

        Returns:
            Direction: The current direction of the elevator.
        """
        return self.__curr_direction
    
    @property
    def prev_direction(self)->Direction:
        """Get the previous direction of the elevator.

        Returns:
            Direction: The previous direction of the elevator.
        """
        return self.__prev_direction
    
    @property
    def num_people(self)->int:
        """Get the number of people inside the elevator.

        Returns:
            int: The number of people inside the elevator.
        """
        return self.__num_people
    
    @property
    def in_pending(self)->list:
        """Get the number of people waiting to get out on each floor.
        
        Returns:
            list: The number of people waiting to get out on each floor.
        """
        return self.__in_pending
    
    @property
    def scheduled_list(self)->list:
        """Get the scheduled list of the elevator.

        Returns:
            list: The scheduled list of the elevator.
        """
        return self.__scheduled_list
    
    @property
    def energy_comsumption(self)->float:
        """Get the energy consumption of the elevator.

        Returns:
            float: The energy consumption of the elevator in Joules.
        """
        return self.__energy_comsumption
    
    @property
    def motor(self)->Motor:
        """Get the motor of the elevator.

        Returns:
            Motor: The motor of the elevator.
        """
        return self.__motor
    
    @property
    def accu_ticktime(self)->int:
        """Get the accumulated tick time of the elevator.

        Returns:
            int: The accumulated tick time of the elevator in seconds.
        """
        return self.__accu_ticktime
    
    @property
    def last_scheduled_list(self)->list:
        """Get the last scheduled list of the elevator.

        Returns:
            list: The last scheduled list of the elevator.
        """
        return self.__last_scheduled_list
    
    def set_scheduled_list(self, scheduled_list:list)->None:
        """set the scheduled list of the elevator.
        
        Args:
            scheduled_list (list): The scheduled list of the elevator.
        """
        self.__scheduled_list = scheduled_list
        
    def set_dest_floor(self, dest_floor:int, num_floors:int)->None:
        """Set the destination floor of the elevator.
        
        Args:
            dest_floor (int): The destination floor of the elevator.
        """
        if dest_floor < 0 or dest_floor >= num_floors:
            raise ValueError("Invalid destination floor.")
        
        if self.__curr_floor != dest_floor:
            self.__energy_comsumption += self.__motor.startup_energy_loss
            
        self.__dest_floor = dest_floor
        
    def set_accu_ticktime(self, ticktime:int)->None:
        """Set the accumulated tick time of the elevator.
        
        Args:
            ticktime (int): The accumulated tick time of the elevator in seconds.
        """
        self.__accu_ticktime = ticktime
    
    def set_curr_direction(self, direction:Direction)->None:
        """Set the current direction of the elevator.
        
        Args:
            direction (Direction): The current direction of the elevator.
        """
        self.__curr_direction = direction
    
    def set_prev_direction(self, direction:Direction)->None:
        """Set the previous direction of the elevator.
        
        Args:
            direction (Direction): The previous direction of the elevator.
        """
        self.__prev_direction = direction
    
    def move(self)->None:
        """Move the elevator to the destination floor.
        """
        self.__energy_comsumption += self.__motor.energy_consumption(0, 1, self.__floor_height, self.total_weight) - self.__motor.startup_energy_loss
        if self.__curr_floor < self.__dest_floor:
            self.__curr_direction = Direction.UP
        elif self.__curr_floor > self.__dest_floor:
            self.__curr_direction = Direction.DOWN
        else:
            self.__dest_floor = None
            self.__prev_direction = self.__curr_direction
            self.__curr_direction = Direction.OPEN
            self.__accu_ticktime = 0
        
        # Update current floor
        if self.__curr_direction == Direction.UP:
            self.__curr_floor = self.__curr_floor + 1
        elif self.__curr_direction == Direction.DOWN:
            self.__curr_floor = self.__curr_floor - 1
        
    def open_door(self, out_pending:list, num_floors:int, enter_func:callable)->list:
        """Open the elevator door and let people in/out.
        
        Args:
            out_pending (list): The number of people waiting to get out on each floor.
            num_floors (int): The total number of floors in the building.
            enter_func (callable): The function to call when a person enters the elevator.
            
        Returns:
            list: The scheduled list of the elevator.
        """
        curr_floor = self.__curr_floor
        
        if self.__in_pending[curr_floor] > 0:
            self.__num_people -= self.__in_pending[curr_floor]
            self.__in_pending[curr_floor] = 0
            
        if out_pending[curr_floor] > 0:
            flow = min(out_pending[curr_floor], self.__capacity - self.__num_people)
            self.__num_people += flow
            for _ in range(flow):
                human:Human = enter_func(curr_floor)
                human.pick_direction(num_floors)
                dest = human.pick_destination(num_floors)
                self.__in_pending[dest] += 1
                
        self.__last_scheduled_list = self.__scheduled_list[:]
        # tmp = [i for i in range(num_floors) if (self.__in_pending[i] > 0 or out_pending[i] > 0) and i != curr_floor]
        tmp = [i for i in range(num_floors) if (self.__in_pending[i] > 0 or out_pending[i] > 0)]
        for i in tmp:
            if i not in self.__scheduled_list:
                self.__scheduled_list.append(i)
        return self.__scheduled_list
    
class Building():
    def __init__(self, config:dict, schedule_func:callable, human_request:dict, debug:bool=False, ticktime:int=1, clr:bool=False)->None:
        self.__clr:bool = clr
        self.__debug = debug
        self.__ticktime:int = ticktime
        self.__human_request:dict = human_request
        self.__num_floors:int = config['num_floors']
        self.__floor_height:int = config['floor_height']
        self.__num_elevators:int = config['num_elevators']
        self.__door_open_time:int = config['door_open_time']
        self.__move_time_per_floor:int = config['move_time_per_floor']
        self.__each_floor_waiting_queue:list = [Queue() for _ in range(config['num_floors'])]
        self.__schedule_func:callable = schedule_func
        self.__elevators:list = [Elevator(ec, self.__num_floors, self.__floor_height, debug, ticktime) for ec in config['elevator_configs']]
        self.__scheduled_lists:list = [[] for _ in range(self.__num_elevators)]
        self.__ratio:int = self.__door_open_time // self.__move_time_per_floor
        self.__log = {}
    
    def __repr__(self):
        rt = "========= Building Info =========\n"
        rt += f"\nBuilding with {self.__num_floors} floors, each {self.__floor_height}m high, and {self.__num_elevators} elevators.\n"
        rt += "\n======== Elevator Info =========\n"
        for i, elevator in enumerate(self.__elevators):
            rt += f"\nElevator {i}:\n{elevator}"
        rt += "\n========== Floor Info ==========\n\n"
        for i, queue in enumerate(self.__each_floor_waiting_queue):
            rt += f"Floor {i}: {queue}\n"
        return rt
    
    @property
    def clr(self)->bool:
        """Get the clear mode of the simulation.

        Returns:
            bool: True if clear mode is enabled, False otherwise.
        """
        return self.__clr
    
    @property
    def debug(self)->bool:
        """Get the debug mode of the simulation.

        Returns:
            bool: True if debug mode is enabled, False otherwise.
        """
        return self.__debug
    
    @property
    def ticktime(self)->int:
        """Get the tick time of the simulation.

        Returns:
            int: The tick time of the simulation in seconds.
        """
        return self.__ticktime
     
    @property
    def num_floors(self)->int:
        """Get the number of floors in the building.

        Returns:
            int: The number of floors in the building.
        """
        return self.__num_floors
    
    @property
    def door_open_time(self)->int:
        """Get the door open time of the building.

        Returns:
            int: The door open time of the building in seconds.
        """
        return self.__door_open_time
    
    @property
    def move_time_per_floor(self)->int:
        """Get the move time per floor of the building.

        Returns:
            int: The move time per floor of the building in seconds.
        """
        return self.__move_time_per_floor
    
    @property
    def floor_height(self)->int:
        """Get the height of each floor in the building.

        Returns:
            int: The height of each floor in the building in meters.
        """
        return self.__floor_height
    
    @property
    def num_elevators(self)->int:
        """Get the number of elevators in the building.

        Returns:
            int: The number of elevators in the building.
        """
        return self.__num_elevators
    
    @property
    def each_floor_waiting_queue(self)->list:
        """Get the list of waiting queues for each floor.

        Returns:
            list: The list of waiting queues for each floor.
        """
        return self.__each_floor_waiting_queue
    
    @property
    def elevators(self)->list:
        """Get the list of elevators in the building. You can use this to access each elevator.

        Returns:
            list: The list of elevators in the building.
        """
        return self.__elevators
    
    @property
    def out_pending(self) -> list:
        """Get the number of people waiting to get in on each floor.

        Returns:
            list: The number of people waiting to get in on each floor.
        """
        return [len(self.__each_floor_waiting_queue[i]) for i in range(self.__num_floors)]
    
    @property
    def human_request(self)->dict:
        """Get the human request dictionary.

        Returns:
            dict: The human request dictionary.
        """
        return self.__human_request
    
    # def random_generate_human(self)->None:
    #     """Generate a random human and add it to the waiting queue of a random floor.
    #     """
    #     floor = random.randint(0, self.__num_floors - 1)
    #     human = Human(floor)
    #     human.pick_direction(self.__num_floors)
    #     self.__each_floor_waiting_queue[floor].push(human)
        
    def accumulated_comsumption(self)->float:
        """Calculate the accumulated energy consumption of the elevator system.
        
        Returns:
            float: The accumulated energy consumption of the elevator system in Joules.
        """
        energy_comsumption = 0.0
        elevator:Elevator
        for elevator in self.__elevators:
            energy_comsumption += elevator.energy_comsumption
        return energy_comsumption
        
    def print_simulation_step(self, step:int)->None:
        """Print the current state of the elevator system.
        """
        if self.__clr:
            system('cls' if os.name == 'nt' else 'clear')
        print(f"===== Simulation Step {step} =====")
        for i in range(self.__num_elevators):
            elevator = self.__elevators[i]
            print(f"Elevator {i}: [Floor {elevator.curr_floor}]")
            print(f"    - #Passengers inside: {elevator.num_people}")
            print(f"    - Pending (In elevator): {elevator.in_pending}")
            print(f"    - Destination floor: {elevator.dest_floor}")
            print(f"    - Schedule list: {elevator.scheduled_list}")
            print()
        print("Floors:")
        for floor in reversed(range(self.__num_floors)):
            marker = ''
            elevator:Elevator
            for elevator in self.__elevators:
                if elevator.curr_direction == Direction.IDLE:
                    e_marker = '[><]'
                elif elevator.curr_direction == Direction.UP:
                    e_marker = '[^^]'
                elif elevator.curr_direction == Direction.DOWN:
                    e_marker = '[vv]'
                elif elevator.curr_direction == Direction.OPEN:
                    e_marker = '[<>]'
                marker += f'{e_marker} ' if elevator.curr_floor == floor else '     '
            waiting = len(self.__each_floor_waiting_queue[floor])
            print(f"[{floor}] ⬆️  {waiting:3d} waiting {marker}")
        print()
        print(f"Energy Consumption so far: {self.accumulated_comsumption():.3f} J")
        print("=" * 30)
        
    def add_log(self, step:int)->None:
        """Add a log entry for the current simulation step.
        
        Args:
            step (int): The current simulation step.
        """
        self.__log[step] = {}
        self.__log[step]['elevators'] = []
        for i in range(self.__num_elevators):
            elevator = self.__elevators[i]
            self.__log[step]['elevators'].append({
                'curr_floor': elevator.curr_floor,
                'dest_floor': elevator.dest_floor,
                'num_people': elevator.num_people,
                'in_pending': elevator.in_pending[:],
                'scheduled_list': elevator.scheduled_list[:],
                'curr_direction': elevator.curr_direction.name,
            })
        # system('pause')
        self.__log[step]['floors'] = []
        for floor in range(self.__num_floors):
            waiting = len(self.__each_floor_waiting_queue[floor])
            self.__log[step]['floors'].append({
                'floor': floor,
                'waiting': waiting
            })
        self.__log[step]['energy_consumption'] = self.accumulated_comsumption()
        
    def enter_func(self, curr_floor:int)->Human:
        """Enter the elevator.
        
        Args:
            curr_floor (int): The current floor of the elevator.
        """
        if len(self.__each_floor_waiting_queue[curr_floor]) == 0:
            return None
        else:
            human = self.__each_floor_waiting_queue[curr_floor].pop()
            return human
        
    def set_each_floor_waiting_queue(self, waiting_queue:list)->None:
        """Set the waiting queue for each floor.
        
        Args:
            waiting_queue (list): The waiting queue for each floor.
        """
        self.__each_floor_waiting_queue = waiting_queue
        
    def append_each_floor_waiting_queue(self, waiting_queue:list)->None:
        """Append the waiting queue for each floor.
        
        Args:
            waiting_queue (list): The waiting queue for each floor.
        """
        for i in range(self.__num_floors):
            length = len(waiting_queue[i])
            for _ in range(length):
                self.__each_floor_waiting_queue[i].push(waiting_queue[i].pop())
        
    def start(self)->float:
        """Start the elevator system.
        """
        self.__scheduled_lists = [[x for x in range(self.__num_floors) if self.out_pending[x] > 0] for _ in range(self.__num_elevators)]
        print(self.__scheduled_lists)
        
        for elevator, scheduled_list in zip(self.__elevators, self.__scheduled_lists):
            elevator.set_scheduled_list(list(scheduled_list))
        
        step = 0
        while True:
            
            if step != 0 and step in list(self.__human_request['script'].keys()):
                self.append_each_floor_waiting_queue(self.__human_request['script'][step])
            
            for elevator in self.__elevators:
                elevator.set_accu_ticktime(max(0, elevator.accu_ticktime - 1))
            
            self.__scheduled_lists = self.__schedule_func(copy.deepcopy(self))
            
            for elevator, scheduled_list in zip(self.__elevators, self.__scheduled_lists):
                elevator.set_scheduled_list(scheduled_list[:])
                
            for elevator in self.__elevators:
                if len(elevator.scheduled_list) > 0 and elevator.dest_floor is None:
                    elevator.set_dest_floor(elevator.scheduled_list.pop(0), self.__num_floors)
                    
            self.add_log(step)
            if self.__debug:
                self.print_simulation_step(step)
                time.sleep(self.__ticktime)
            step += 1
            
            # system('pause')
            
            for elevator in self.__elevators:
                if elevator.accu_ticktime == 0:
                    if elevator.dest_floor is not None:
                        elevator.move()
                    else:
                        elevator.set_prev_direction(Direction.IDLE)
                        elevator.set_curr_direction(Direction.IDLE)
            
            sum_out_pending = sum(self.out_pending)
            sum_pending = sum_out_pending
            for i in range(self.__num_elevators):
                elevator:Elevator = self.__elevators[i]
                sum_in_pending = sum(elevator.in_pending)
                sum_pending += sum_in_pending + 0 if elevator.curr_direction == Direction.IDLE else 1
                if sum_out_pending + sum_in_pending > 0 and elevator.dest_floor is None:
                    self.__scheduled_lists[i] = elevator.open_door(self.out_pending, self.__num_floors, self.enter_func)
                    elevator.set_curr_direction(Direction.OPEN)
                    elevator.set_accu_ticktime(self.__ratio)
            if sum_pending == 0 and step > self.__human_request['max_tick']:
                break
        
        self.add_log(step)
        if self.__debug:
            self.print_simulation_step(step)
        
        # save log to json file
        with open('animation_log/simulation_log.json', 'w') as f:
            json.dump(self.__log, f, indent=4)
        
        return self.accumulated_comsumption()
    
class Test:
    """This class is used to run the simulation and get the energy consumption of the elevator system.  
    Do not use this class to estimate the energy consumption of the elevator system!
    """
    # _instance = None

    # def __new__(cls, *args, **kwargs):
    #     if cls._instance is None:
    #         cls._instance = super(Test, cls).__new__(cls)
    #     return cls._instance

    def __init__(self, config:dict, debug:bool = False, ticktime:int = 1, clr:bool = False):
        # if hasattr(self, "_initialized") and self._initialized:
        #     print(f"Error: It is allowed to create only one instance of Test.")
        #     sys.exit(1)
        #     return
        self.__config:dict = config
        self.__debug:bool = debug
        self.__ticktime:int = ticktime
        self.__clr:bool = clr
        self.__building:Building = None
        self._initialized = True

    @property
    def building(self) -> Building:
        return self.__building

    def run(self, human_requests:dict, strategy:callable) -> float:
        self.__building = Building(self.__config['building_config'], strategy, human_requests, self.__debug, self.__ticktime, self.__clr)
        # print(human_requests['script']['0'])
        self.__building.set_each_floor_waiting_queue(human_requests['script'][0])
        return self.__building.start()