# turtlebot_core

ROS 2 Jazzy package containing high-level control nodes for the TurtleBot platform.

This package is responsible for generating user-level commands and behaviors, which are then consumed by lower-level bridge nodes (e.g., `uno_q_bridge`) for hardware execution.

---

## Overview

`turtlebot_core` provides simple control interfaces to validate communication between ROS 2 and the underlying hardware.

At its current stage, the package focuses on **LED control** as a minimal functional test of the system architecture:

* User interaction → ROS 2 topic
* ROS 2 topic → bridge node
* Bridge node → Arduino UNO Q (via UNIX socket)

---

## Nodes

### 1. `control_led.py`

Interactive node that allows manual control of the LED state via terminal input.

#### Behavior

* Waits for user input in a loop
* Publishes commands to the `/set_led` topic
* Terminates when the user presses `q`

#### Controls

| Key | Action       |
| --- | ------------ |
| `1` | Turn LED ON  |
| `0` | Turn LED OFF |
| `q` | Exit node    |

#### Usage

```bash
ros2 run turtlebot_core control_led
```

---

### 2. `toggle_led.py`

Autonomous node that periodically toggles the LED state.

#### Behavior

* Uses a ROS 2 timer
* Inverts the internal LED state at a fixed interval
* Publishes the updated state to `/set_led`

This node is useful for:

* Validating end-to-end communication
* Observing system responsiveness
* Testing continuous command flow

#### Usage

```bash
ros2 run turtlebot_core toggle_led
```

---

## Topics

| Topic      | Type            | Description                    |
| ---------- | --------------- | ------------------------------ |
| `/set_led` | `std_msgs/Bool` | LED state command (True/False) |

---

## Integration with uno_q_bridge

Both nodes publish to:

```bash
/set_led
```

This topic is consumed by the `uno_q_bridge` package, which translates the message into a MessagePack-RPC request and forwards it to the Arduino UNO Q.

---

## Dependencies

* `jazzy-ros-base`
* `ros-jazzy-rclpy`
* `ros-jazzy-std-msgs`
* `python3`

---

## Notes

* These nodes do not interact directly with hardware
* All hardware communication is delegated to bridge nodes
* The design follows a **layered architecture**:

  * High-level control (`turtlebot_core`)
  * Hardware interface (`uno_q_bridge`)

---

## Author

**Jesus Salvador Lopez Ortega**

Digital Systems & Robotics Engineer, graduated from [Tecnologico de Monterrey Campus Queretaro](https://tec.mx/es/queretaro/)

Software & Robotics professor at [Universidad Politecnica de Santa Rosa](https://upsrj.edu.mx/)

**Contact:**

* [LinkedIn](https://www.linkedin.com/in/jesus-salvador-lopez-ortega/)
* [GitHub](https://github.com/chucholoport)
