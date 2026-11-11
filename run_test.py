import argparse
import copy
import json
import os
import sys

from utils.data_structures import Queue
from utils.objects import Human, Test
from config.tools.config_validation import config_validation

# TODO: 之後可以這邊加更多 strategies 的 import
from method.scan import scan_algorithm
from method.scan_plus import scan_plus_algorithm

strategy_map = {
    # TODO: 之後要加新的 strategy，可以在這裡補
    'scan': scan_algorithm,
    'scan_plus': scan_plus_algorithm,
}

parser = argparse.ArgumentParser(description="Run test with a configuration file.")
parser.add_argument('config_file', type=str, help="Path to the config file")
parser.add_argument('-d', '--debug', action='store_true', help="Enable debug mode")
parser.add_argument('-clr', '--clear', action='store_true', help="Enable clear mode")
parser.add_argument('-s', '--strategy', type=str, choices=[name for name in strategy_map.keys()], help="Specify strategy to use")
parser.add_argument('-t', '--ticktime', type=int, help="Specify simulation tick time")
parser.add_argument('-hr', '--human_requests', type=str, help="Specify human requests file")

args = parser.parse_args()

file_path = args.config_file

try:
    with open(file_path, 'r') as config_file:
        config:dict = json.load(config_file)
except Exception as e:
    print(f"Error reading config file: {e}")
    sys.exit(1)

if not config_validation(config):
    print("Error: Invalid configuration file.")
    sys.exit(1)
print("Configuration file is valid.")

try:
    with open(args.human_requests, 'r') as human_requests_file:
        human_requests = json.load(human_requests_file)
            
except Exception as e:
    print(f"Error reading human requests file: {e}")
    sys.exit(1)
    
keys_list = list(human_requests['script'].keys())
for i in keys_list:
    # print(human_requests['script'][i])
    for j in range(len(human_requests['script'][i])):
        q = Queue()
        for k in range(len(human_requests['script'][i][j])):
            q.push(Human(**human_requests['script'][i][j][k]))
        human_requests['script'][i][j] = q
    human_requests['script'][int(i)] = human_requests['script'][i]
    human_requests['script'].pop(i)
if args.strategy:
    if args.strategy not in strategy_map:
        print(f"Error: Unknown strategy {args.strategy}")
        sys.exit(1)
    config['strategy'] = strategy_map[args.strategy]
else:
    if config['strategy'] not in strategy_map:
        print(f"Error: Unknown strategy {config['strategy']}")
        sys.exit(1)
    config['strategy'] = strategy_map[config['strategy']]
    
if args.ticktime:
    ticktime = args.ticktime
else:
    ticktime = 0
    
def run_test(test:Test):
    energy_consumption = test.run(copy.deepcopy(human_requests), config['strategy'])
    print(f"Energy consumption: {energy_consumption} J")
    new_name = f"animation_log/simulation_log_{config['strategy'].__name__}.json"
    if os.path.exists(new_name):
        os.remove(new_name)
    os.rename("animation_log/simulation_log.json", new_name)

test = Test(config, debug=args.debug, ticktime=ticktime, clr=args.clear)
run_test(test)

config['strategy'] = scan_algorithm
run_test(test)