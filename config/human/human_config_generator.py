import random
import json
from utils.data_structures import Queue
from utils.objects import Human

def random_generate_human(flow:int, num_floors:int)->list:
    """Generate a random huma
    """
    queues = [Queue() for _ in range(num_floors)]
    for _ in range(flow):
        floor = random.randint(0, num_floors - 1)
        human = Human(floor)
        human.pick_direction(num_floors)
        queues[floor].push(human)
    return queues

def generate(flow_range:tuple, num_floors:int)->dict:
    # rand_num_ticks = random.randint(3, 10)
    # rand_ticks = random.sample(range(50, 400), rand_num_ticks)
    rand_num_ticks = 1
    rand_ticks = []
    if 0 not in rand_ticks:
        rand_ticks.append(0)
    rand_ticks.sort()
    rt = {}
    for tick in rand_ticks:
        flow = random.randint(flow_range[0], flow_range[1])
        human_requests = random_generate_human(flow, num_floors)
        for i in range(len(human_requests)):
            human_requests[i] = human_requests[i].to_list()
            for j in range(len(human_requests[i])):
                human_requests[i][j] = human_requests[i][j].to_dict()
        rt[tick] = human_requests
    return rt

floors = [5, 10, 20]
flow_ranges = [(10, 20), (30, 50)]

# for floor in floors:
#     for flow_range in flow_ranges:
#         for i in range(3):
#             config = {}
#             script = generate(flow_range, floor)
#             max_tick = max(script.keys())
#             config['max_tick'] = max_tick
#             config['script'] = script

#             # save the config to a file
#             with open(f'config_demo/config_human/floor_{floor}/flow_{flow_range[0]}{flow_range[1]}_{i}.json', 'w') as f:
#                 json.dump(config, f, indent=4)

for i in range(3):
    config = {}
    script = generate((30, 30), 10)
    max_tick = max(script.keys())
    config['max_tick'] = max_tick
    config['script'] = script

    # save the config to a file
    with open(f'config_demo/easy.json', 'w') as f:
        json.dump(config, f, indent=4)