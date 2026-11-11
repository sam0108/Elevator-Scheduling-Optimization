# `objects.py` 說明

***請不要用 Test class 估算 energy consumption !!!***

## 類別說明

### `Direction`

電梯方向的列舉（Enum），包含四種狀態：

* `Direction.UP`: 向上移動
* `Direction.DOWN`: 向下移動
* `Direction.IDLE`: 靜止未動
* `Direction.OPEN`: 開門

---

### `Human`

表示一位在樓層等電梯的人，需要傳入的參數有：

* `curr_floor`: 當前所在樓層
* `weight`: 體重（預設為 70 公斤）
* `direction`: 希望搭乘電梯的方向

方法：

* `pick_direction(num_floors)`: 根據所在樓層隨機選擇上下方向
* `pick_destination(num_floors)`: 根據方向與樓層隨機選擇目的地樓層

---

### `Motor`

模擬電梯馬達的能量消耗，需要傳入的參數有：

* `config['startup_energy_loss']`: 電梯啟動時的能量損耗
* `energy_consumption(start_floor, dest_floor, floor_height, total_weight)`: 計算從某樓層移動到另一樓層所消耗的能量

---

### `Elevator`

模擬一部電梯的行為與狀態：

* 初始化參數：

  * `config`: 包含各種設定如 `capacity`, `weight`, `init_floor` 等
  * `schedule_func`: 排程策略函式
  * `num_floors`: 總樓層數
  * `floor_height`: 每層樓高
  * `debug`, `ticktime`: 調試與時間設定

屬性（皆為唯讀）：

* `ticktime`, `total_weight`, `capacity`, `curr_floor`, `scheduling_win_size`, `door_open_time`, `debug`, `prev_direction`, `num_people`, `in_pending`, `scheduled_list`, `energy_comsumption`, `motor`

方法：

* `set_scheduled_list(list)`: 設定排程樓層清單
* `move(dest_floor, num_floors)`: 移動至指定樓層
* `open_door(out_pending, num_floors, enter_func)`: 開門讓乘客進出

---

### `Building`

模擬整棟大樓與多部電梯的互動：

* 初始化參數：

  * `config`: 包含整棟樓與電梯配置
  * `schedule_func`: 排程策略函式
  * `debug`, `ticktime`, `clr`: 控制模擬視覺與時間

屬性：

* `clr`, `debug`, `ticktime`, `num_floors`, `floor_height`, `num_elevators`, `each_floor_waiting_queue`, `elevators`, `out_pending`

方法：

* `random_generate_human()`: 隨機在某層樓生成一名人
* `accumulated_comsumption()`: 累積整棟樓的耗能
* `print_simulation_step()`: 輸出當前模擬狀態（含每層樓等候人數與電梯位置）
* `enter_func(curr_floor)`: 模擬某層進入一位人
* `start()`: 啟動模擬流程直到結束

---

## 參數與設定說明

以下為常見在 `config` 或函式中使用的參數說明：

| 參數名稱                  | 說明                   |
| --------------------- | -------------------- |
| `capacity`            | 電梯最大載客人數             |
| `weight`              | 電梯本身的重量              |
| `init_floor`          | 初始所在樓層               |
| `scheduling_win_size` | 一次排程的時間視窗            |
| `door_open_time`      | 每次開門所需時間（秒）          |
| `motor_config`        | 提供給 `Motor` 類別的設定字典  |
| `strategy`            | 排程策略函式（回傳每部電梯應前往的樓層） |