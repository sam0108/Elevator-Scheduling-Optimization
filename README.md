# Elevator_Power_Minimization

[![Python](https://img.shields.io/badge/Python-3776AB.svg?logo=python&logoColor=white)](https://www.python.org/)
[![HTML](https://img.shields.io/badge/HTML5-E34F26.svg?logo=html5&logoColor=white)](https://developer.mozilla.org/en-US/docs/Web/HTML)
[![CSS](https://img.shields.io/badge/CSS3-1572B6.svg?logo=css3&logoColor=white)](https://developer.mozilla.org/en-US/docs/Web/CSS)
[![JavaScript](https://img.shields.io/badge/JavaScript-F7DF1E.svg?logo=javascript&logoColor=black)](https://developer.mozilla.org/en-US/docs/Web/JavaScript)  

**Project Goal:** Simulate and minimize power consumption of elevators through various scheduling strategies.

This project provides an extensible platform that allows collaborators to develop and test different elevator scheduling algorithms in a simulated environment.

## Table of Contents
- [Usage](#usage)
- [Arguments](#arguments)
- [Available Strategies](#available-strategies)
- [Config Format](#config-format)
- [How to Add a New Strategy](#how-to-add-a-new-strategy)
- [License](#license)

## Usage

```console
python run_test.py <config_file_path> [options]
```

### Example:

```console
python run_test.py config/tools/config_sample.json -hr config/human/human_config.json -d -s scan -t 1
```

This command will:
- Use `config/tools/config_sample.json`
- Enable debug mode
- Use the `scan` strategy
- Set the simulation tick time to 1

## Arguments

| Argument | Description |
|:---------|:------------|
| `<config_file_path>` | **Required**. Path to the configuration file (`.json`) |
| `-hr`, `--human_requests <human_config_file_path>` | **Required**. Path to the human configuration file (`.json`) |
| `-d`, `--debug` | **Optional**. Enable debug mode to show more detailed output |
| `-clr`, `--clear` | **Optional**. Clear the terminal after each simulation step |
| `-s`, `--strategy <strategy>` | **Optional**. Specify the scheduling strategy to use (see [Available Strategies](#available-strategies)) |
| `-t`, `--ticktime <ticktime>` | **Optional**. Set the tick time interval for the simulation |

---

## Available Strategies

Currently supported strategies:

- `scan`: Implemented in `method/scan.py` as `scan_algorithm`.
- `scan_plus`: Implemented in `method/scan_plus.py` as `scan_plus_algorithm`.

> Note: Any new strategy must be registered in the `strategy_map` inside [`run_test.py`](run_test.py).

## Config Format

- Please refer to [Config Tool Usage](config/README.md) for format specifications.
- If the config file already specifies a `strategy`, the `-s` option is not required. However, the strategy name must still match one of those registered in `strategy_map`.

## How to Add a New Strategy

1. **Create your strategy implementation**

    Add a new Python file in the `method/` folder. For example:

    ```console
    method/my_new_strategy.py
    ```

    Then define your strategy function:

    ```python
    def my_new_strategy(test_object):
        # Your scheduling logic here
        return
    ```

2. **Register the strategy in `run_test.py`**

    Open `run_test.py` and add your strategy to the `strategy_map`:

    ```python
    from method.my_new_strategy import my_new_strategy

    strategy_map = {
        'scan': scan_algorithm,
        'my_new_strategy': my_new_strategy,
    }
    ```

    Now you can run your strategy using:

    ```console
    python run_test.py <config_path> -s my_new_strategy -hr <human_config_path>
    ```

3. **Update the strategy list in `README.md`**

    To help other collaborators stay up to date, please remember to also update the [Available Strategies](#available-strategies) section in this README.