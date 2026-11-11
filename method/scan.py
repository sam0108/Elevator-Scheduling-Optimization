from utils.objects import Building, Direction, Elevator
import random

def scan_algorithm(building:Building) -> list:
    """
    This function implements a simple scanning algorithm.
    It scans through a list of numbers and returns the sum of all even numbers.
    """
    dest_picked = [x.dest_floor for x in building.elevators]
    scheduled_lists = []
    
    elevator:Elevator
    for elevator in building.elevators:
        
        scheduled_list = elevator.scheduled_list[:]
        
        if elevator.curr_floor in scheduled_list and elevator.curr_direction == Direction.OPEN:
            scheduled_list.remove(elevator.curr_floor)
        
        for i in dest_picked:
            if i in scheduled_list and elevator.in_pending[i] == 0:
                scheduled_list.remove(i)
                
        if (elevator.dest_floor != None and elevator.curr_floor != elevator.dest_floor) or len(scheduled_list) <= 1:
            scheduled_lists.append(scheduled_list)
            continue
        
        scheduled_list.sort()
    
        # flag == True -> go up
        # flag == False -> go down
        if elevator.curr_floor == 0:
            flag = True
        elif elevator.curr_floor == building.num_floors:
            flag = False
        elif elevator.prev_direction == Direction.UP:
            flag = True
        elif elevator.prev_direction == Direction.DOWN:
            flag = False
        else:
            random.seed(42)
            flag = random.choice([True, False])
            
        tmp = scheduled_list[:]
        tmp.append(elevator.curr_floor)
        tmp = sorted(tmp, reverse=(not flag))
        idx = tmp.index(elevator.curr_floor)
        scheduled_list = tmp[idx+1:] + sorted(tmp[:idx], reverse=flag)
        
        dest_picked.append(scheduled_list[0])
        
        scheduled_lists.append(scheduled_list)
    
    return scheduled_lists