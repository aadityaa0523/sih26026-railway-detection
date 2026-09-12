# CHAMP Quadruped Controller — Research for ROS 2 Humble + Gazebo Classic 11 (Ubuntu 22.04)

## Scope

This document answers seven specific questions about using the [chvmp/champ](https://github.com/chvmp/champ) quadruped controller framework on **ROS 2 Humble + Gazebo Classic 11 + Ubuntu 22.04**, for a hackathon build that may need a custom robot config before real hardware/URDF exists. All claims below are sourced directly from the `chvmp` GitHub org's repos (READMEs, source files, package manifests, issues/PRs), fetched and read directly — not from blog posts or tutorials. Every claim is tagged with its source path/URL.

---

# 1. Which Repo/Branch to Clone for ROS 2 Humble

## Answer: `chvmp/champ`, branch `ros2`. There is no separate `chvmp/champ_ros2` repo.

- `chvmp/champ` has exactly two branches: `master` (ROS1: Kinetic/Melodic) and `ros2`. Confirmed via the GitHub branches API (`api.github.com/repos/chvmp/champ/branches`): `master` and `ros2`.
- `github.com/chvmp/champ_ros2` **does not exist** (HTTP 404 on direct fetch).
- The `ros2` branch's own README states it is tested on:
  > "Ubuntu 16.04 (ROS Kinetic), Ubuntu 18.04 (ROS Melodic), Ubuntu 22.04 (ROS2 Humble)"
  — [chvmp/champ, `ros2` branch, README.md](https://github.com/chvmp/champ/blob/ros2/README.md)
- Companion repos also carry a matching `ros2` branch that must be cloned alongside:
  - `chvmp/champ_teleop` — has `master` and `ros2` branches (confirmed via branches API). The README's own clone instructions pull this branch explicitly.
  - `chvmp/robots` — also has a `ros2` branch (see §3) with per-robot config packages ported/updated for Humble (last touched Feb 2023, commit message: "modify code according to latest champ" for the mini_pupper config, PR "feature/update-mini-pupper-config-for-humble").
  - `chvmp/champ_setup_assistant` — **no `ros2` branch exists** (only `master` and `noetic`). See §4/§6.

Clone command straight from the README:
```
sudo apt install -y python3-rosdep
rosdep update

cd <your_ws>/src
git clone --recursive https://github.com/chvmp/champ -b ros2
git clone https://github.com/chvmp/champ_teleop -b ros2
cd ..
rosdep install --from-paths src --ignore-src -r -y
```
— [chvmp/champ, `ros2` branch, README.md §1.1](https://github.com/chvmp/champ/blob/ros2/README.md)

`--recursive` matters: `champ/champ/include/champ` is a **git submodule** pointing at `chvmp/libchamp` (branch `master`), per the repo's `.gitmodules` file:
```
[submodule "champ/include/champ"]
	path = champ/include/champ
	url = https://github.com/chvmp/libchamp
	branch = master
```
— [chvmp/champ, `ros2` branch, `.gitmodules`](https://github.com/chvmp/champ/blob/ros2/.gitmodules)

---

# 2. Standard Package Layout

The `ros2` branch of `chvmp/champ` is a single repo containing 8 ROS 2 packages (confirmed by listing the branch's top-level tree via the GitHub Contents API):

| Package | Purpose | Source |
|---|---|---|
| `champ` | Core C++ library wrapper (`CMakeLists.txt`, `include/`, `package.xml`); pulls in `libchamp` as a submodule for kinematics/gait/odometry/body-controller/leg-controller math | [champ/champ](https://github.com/chvmp/champ/tree/ros2/champ) |
| `champ_base` | The quadruped controller ROS node(s) — subscribes to cmd_vel, runs gait/kinematics, publishes joint commands | [champ/champ_base](https://github.com/chvmp/champ/tree/ros2/champ_base) |
| `champ_bringup` | Top-level bringup launch glue (`bringup.launch.py`) that wires description + base driver + optional rviz/gazebo args together | [champ/champ_bringup](https://github.com/chvmp/champ/tree/ros2/champ_bringup) |
| `champ_config` | **The stock/demo robot's config package** — `config/{gait,joints,links,autonomy}/*.yaml`, `launch/*.launch.py`, `worlds/`, `maps/` — this is what a `champ_setup_assistant`-generated package looks like | [champ/champ_config](https://github.com/chvmp/champ/tree/ros2/champ_config) |
| `champ_description` | URDF/xacro + meshes + rviz config for the stock demo robot (named "champ") | [champ/champ_description](https://github.com/chvmp/champ/tree/ros2/champ_description) |
| `champ_gazebo` | Gazebo Classic integration: `gazebo.launch.py`, `config/ros_control.yaml`, `config/gazebo.yaml`, worlds, a `contact_sensor` C++ node | [champ/champ_gazebo](https://github.com/chvmp/champ/tree/ros2/champ_gazebo) |
| `champ_msgs` | Custom `.msg` definitions: `Contacts`, `ContactsStamped`, `Imu`, `Joints`, `PID`, `Point`, `PointArray`, `Pose`, `Velocities` | [champ/champ_msgs/msg](https://github.com/chvmp/champ/tree/ros2/champ_msgs/msg) |
| `champ_navigation` | Nav2/RViz config for autonomous navigation demos | [champ/champ_navigation](https://github.com/chvmp/champ/tree/ros2/champ_navigation) |

Note the naming: there is **no separate `champ_gazebo` vs `champ_bringup` ambiguity** to resolve — both exist side by side and are equivalents of what the question called "champ_gazebo/champ_bringup". A generated custom-robot package (e.g. `<my_robot>_config`) mirrors the shape of `champ_config` (its own `config/`, `launch/`, `worlds/`, `maps/`, `package.xml`), not a fork of `champ_description` — the URDF stays wherever you point it.

---

# 3. Robot Configs That Ship Out of the Box

## 3.1 The actual "out of the box" demo robot

`champ_description`/`champ_config` in the `ros2` branch ship a **generic quadruped simply named "champ"** (MIT-Mini-Cheetah-styled proportions) — this is what `ros2 launch champ_config bringup.launch.py` and `gazebo.launch.py` spawn by default. There is no robot literally named "first"; that is this default/generic robot. Real numbers, pulled directly from the xacro/yaml source:

**Link lengths** — [`champ_description/urdf/properties.urdf.xacro`](https://github.com/chvmp/champ/blob/ros2/champ_description/urdf/properties.urdf.xacro):
```xml
<xacro:property name="base_to_hip_x" value="0.175" />
<xacro:property name="base_to_hip_y" value="0.105" />
<xacro:property name="hip_to_upper_leg_distance" value="0.06" />
<xacro:property name="upper_leg_to_lower_leg_distance" value="0.141" />
<xacro:property name="lower_leg_to_foot_distance" value="0.141" />

<!-- body -->
<xacro:property name="base_mass" value="2.0" />
<xacro:property name="base_x_length" value="0.5" />
<xacro:property name="base_y_length" value="0.29" />
<xacro:property name="base_z_length" value="0.130" />

<!-- hip -->
<xacro:property name="hip_mass" value="0.250" />
<xacro:property name="hip_x_length" value="0.112" />
<xacro:property name="hip_y_length" value="0.08" />
<xacro:property name="hip_z_length" value="0.130" />

<!-- upper leg -->
<xacro:property name="upper_leg_mass" value="0.125" />
<xacro:property name="upper_leg_x_length" value="0.05" />
<xacro:property name="upper_leg_y_length" value="0.03" />
<xacro:property name="upper_leg_z_length" value="0.1905" />

<!-- lower leg -->
<xacro:property name="lower_leg_mass" value="0.125" />
<xacro:property name="lower_leg_x_length" value="0.039" />
<xacro:property name="lower_leg_y_length" value="0.022" />
<xacro:property name="lower_leg_z_length" value="0.156" />
```

**DOF / joints** — 3 actuated (revolute) joints per leg × 4 legs = **12 DOF**, plus a fixed foot joint per leg. From [`champ_description/urdf/leg.urdf.xacro`](https://github.com/chvmp/champ/blob/ros2/champ_description/urdf/leg.urdf.xacro):
```xml
<joint name="${leg}_hip_joint" type="revolute">
    <axis xyz="1 0 0" />
    <limit effort="25" lower="-${pi}" upper="${pi}" velocity="1.5" />
    ...
<joint name="${leg}_upper_leg_joint" type="revolute">
    <axis xyz="0 1 0" />
    <limit effort="25" lower="-${pi}" upper="${pi}" velocity="1.5" />
    ...
<joint name="${leg}_lower_leg_joint" type="revolute">
    <axis xyz="0 1 0" />
    <limit effort="25" lower="-${pi}" upper="${pi}" velocity="1.5" />
    ...
<joint name="${leg}_foot_joint" type="fixed">
```
Effort limit 25 N·m, velocity limit 1.5 rad/s, position limits ±π on all three joints (i.e. the URDF itself imposes no real angular restriction — the gait planner is what keeps the legs in a sane range).

**Gait parameters** — [`champ_config/config/gait/gait.yaml`](https://github.com/chvmp/champ/blob/ros2/champ_config/config/gait/gait.yaml):
```yaml
gait:
  knee_orientation : ">>"
  pantograph_leg : false
  odom_scaler: 0.9
  max_linear_velocity_x : 0.5
  max_linear_velocity_y : 0.25
  max_angular_velocity_z : 1.0
  com_x_translation: 0.0
  swing_height : 0.04
  stance_depth : 0.00
  stance_duration : 0.25
  nominal_height : 0.20
```

**Joints/links maps** (semantic naming the controller relies on) — [`champ_config/config/joints/joints.yaml`](https://github.com/chvmp/champ/blob/ros2/champ_config/config/joints/joints.yaml) and [`links.yaml`](https://github.com/chvmp/champ/blob/ros2/champ_config/config/links/links.yaml): each leg maps to `[<leg>_hip_joint, <leg>_upper_leg_joint, <leg>_lower_leg_joint, <leg>_foot_joint]` for legs named `left_front`, `right_front`, `left_hind`, `right_hind` (link prefixes `lf_`, `rf_`, `lh_`, `rh_`).

## 3.2 Other robots — via the separate `chvmp/robots` repo, not bundled in `champ`

`chvmp/robots` is a **separate repo** ("zoo" of pre-generated config packages) and it also has a `ros2` branch. Its `configs/` directory on `ros2` (confirmed via Contents API) contains:

```
a1_config, aliengo_config, anymal_b_config, anymal_c_config, astro_config,
bruno_config, dkitty_config, dream_walker_config, go1_config, littledog_config,
mini_cheetah_config, mini_pupper_config, open_quadruped_config, opendog_config,
spot_config, spotmicro_config, stanford_pupper_config, stochlite_config
```
— [chvmp/robots, `ros2` branch, `configs/`](https://github.com/chvmp/robots/tree/ros2/configs)

Per the `master`-branch README (credits/attribution section — the `ros2` branch mirrors this list), the robots that actually have **confirmed Gazebo support** are: Anymal B, Anymal C, Spot, Aliengo, Go1, A1, MIT Mini Cheetah, OpenDog V2, Open Quadruped, Stochlite, Mini Pupper, Stanford Pupper. — [chvmp/robots README.md](https://github.com/chvmp/robots/blob/master/README.md)

### Mini Pupper — real numbers pulled from its config

`chvmp/robots` on `ros2` still ships each robot's original `config.json` (the file `champ_setup_assistant` itself would generate/consume — see §4). For Mini Pupper — [`configs/mini_pupper_config/config.json`](https://github.com/chvmp/robots/blob/ros2/configs/mini_pupper_config/config.json):

```json
"gait": {
  "max_linear_vel_x": 0.2, "max_linear_vel_y": 0.1, "max_angular_vel_z": 0.45,
  "nominal_height": 0.045, "swing_height": 0.008, "stance_depth": 0.0,
  "stance_duration": 0.25, "knee_orientation": ">>", "odom_scaler": 1.0
}
```
Right-front leg transform chain (meters, relative to parent frame, per the setup-assistant's own convention — see §4/§5):
```
hip:       (0.06014, -0.0235, 0.0171)
upper_leg: (0.0,     -0.0197, 0.0)
lower_leg: (0.0,     -0.00475, -0.05)
foot:      (0.0,      0.0,    -0.056)
```
i.e. Mini Pupper is a **12-DOF** (3 joints × 4 legs, same joint/link naming convention as the stock robot) miniature quadruped with an 8mm swing height and 45mm nominal standing height — roughly 1/4 the scale of the stock demo robot.

`mini_pupper_config`'s package on the `ros2` branch is a real, buildable `ament_cmake` package (`package.xml` depends on `champ_base`, `launch_ros`, `rviz2`, `gazebo_plugins`) with `bringup.launch.py`, `gazebo.launch.py`, `navigate.launch.py`, `slam.launch.py` — i.e. it's already Humble-ported, last touched via PR "feature/update-mini-pupper-config-for-humble" (merged Feb 2023). Its own README states plainly:
> "Currently this only works in a virtual environment."
— [chvmp/robots, `ros2` branch, `configs/mini_pupper_config/README.md`](https://github.com/chvmp/robots/blob/ros2/configs/mini_pupper_config/README.md)

(i.e. real-hardware/microcontroller drivers for Mini Pupper are not yet ported to ROS 2 — only the Gazebo/RViz simulation path is confirmed working.)

There is **no robot named "first"** anywhere in the `chvmp` org. Two unfamiliar names in the `ros2`-branch config list, `astro_config` and `bruno_config`, are not in the master README's attribution/credits list and are not in the "confirmed Gazebo support" list — treat them as community-contributed, unverified/no-Gazebo configs unless you inspect them directly.

---

# 4. How `champ_setup_assistant` Works

**Important ROS 2 caveat first:** `chvmp/champ_setup_assistant` has branches `master` and `noetic` only — confirmed via the branches API — **no `ros2` branch exists**, and the `champ` `ros2`-branch README explicitly lists "Setup-Assistant" and "Robot Configurations" (porting of robot description/URDF/config/launch files) under a "current state of ROS2 port" checklist with a ✗ (not done):
> "✗ Setup-Assistant. / ✗ Robots Configurations. / — ✗ Porting of robot description packages to ROS 2. / — ✗ Porting of robot URDF to ROS2 (add new ros2_control tag). / — ✗ Porting of robot configurationf to ROS2. / — ✗ Porting of robot launch Files to ROS2."
— [chvmp/champ, `ros2` branch, README.md](https://github.com/chvmp/champ/blob/ros2/README.md)

In practice this is only partially true today: `chvmp/robots`' `ros2` branch *does* contain hand-ported/updated config packages (Mini Pupper confirmed working per §3.2), maintained by community PRs rather than by re-running the tool. **The GUI tool itself is ROS 1 (catkin/`roslaunch`) only.**

## What it needs as input (from `chvmp/champ_setup_assistant`, `master` README):

Install/run (ROS 1 only):
```
sudo apt install -y python-rosdep
cd <your_ws>/src
git clone https://github.com/chvmp/champ_setup_assistant
cd .. && rosdep install --from-paths src --ignore-src -r -y
cd <your_ws> && catkin_make && source <your_ws>/devel/setup.bash

roslaunch champ_setup_assistant setup_assistant.launch
```
— [chvmp/champ_setup_assistant README.md §1–2](https://github.com/chvmp/champ_setup_assistant/blob/master/README.md)

It is an RViz-embedded Qt GUI with two input modes:

1. **From a URDF** ("BROWSE URDF" button), with hard assumptions the URDF must satisfy:
   > "There are no rotation between frames (joint's origin-rpy are all set to zero). Hip joints rotate in the X axis. Upper Leg joints rotate in the Y axis. Lower Leg joints rotate in the Y axis. Origins of actuators' meshes are located at the center of rotation. All joints at zero position will result[] the robot's legs to be fully stretched towards the ground."
   The tool then auto-parses per-leg link namespaces (e.g. Anymal's `LF_HIP`/`LH_HIP`/`RF_HIP`/`RH_HIP`) or lets you manually drag links into leg slots if auto-detection fails.
2. **Manual Joint Configuration — no URDF needed at all** (see §5 below).

Either way you then fill in the **Gait Configuration** tab (knee orientation, max linear vel X/Y, max angular vel Z, stance duration, swing/stance height, nominal walking height, CoM X translation, odometry scaler), then the **Generate Config** tab: robot name + target workspace `src/` directory → **Generate**.

## What it outputs

> "This software auto generates a configuration package containing all the files necessary to make CHAMP walk."
— [chvmp/champ_setup_assistant README.md, top](https://github.com/chvmp/champ_setup_assistant/blob/master/README.md)

Concretely (per the ROS1 champ README's description of what a generated package contains, and matching the real shape of `champ_config`/`mini_pupper_config` we inspected): a `<robot>_config` ament/catkin package with:
- URDF path reference (not the URDF itself — it points at wherever your description package lives)
- `joints.yaml` / `links.yaml` (the joint/link semantic maps)
- `gait.yaml`
- Hardware-driver and navigation params (move_base/amcl/gmapping in ROS1)
- Microcontroller header files (only relevant if targeting the lightweight/Teensy firmware path)
- Launch files (`bringup.launch`, `gazebo.launch`, `slam.launch`, `navigate.launch`)

It also writes a `config.json` (seen for real in `mini_pupper_config/config.json`, §3.2) capturing the raw leg-actuator transforms and gait numbers it was given — this is the tool's internal source-of-truth format, independent of whether a URDF existed.

---

# 5. Defining a Custom Robot Config Without a Real URDF Yet

**Yes — this is an explicitly supported first-class mode of the setup assistant**, not a workaround. Section "3.2 Manual Joint Configuration" of the setup-assistant README says:

> "This step is only required if you don't have a URDF file to use. In this step, you'll define the position of each actuator in your robot to help the controller find the relative position of each joints."
— [chvmp/champ_setup_assistant README.md §3.2](https://github.com/chvmp/champ_setup_assistant/blob/master/README.md)

The input is a **pure chain-of-offsets spec**, not a URDF: for each leg, you key in the XYZ translation of each actuator **relative to the previous link in the chain** (`base → hip → upper_leg → lower_leg → foot`):
> "x: Translation in the x axis from a reference frame. + x to the front, -x to the back. / y: ... + y to the left, -y to the right. / z: ... + z up, -z down."

You only need to fully specify the **left-front leg**; the tool then predicts (mirrors) the other three legs' offsets, which you can review/override per-leg. Then the same **Gait Configuration** tab (knee orientation, velocities, stance duration, swing/stance height, nominal height, CoM-X translation, odometry scaler) applies regardless of whether a URDF exists. Clicking **Generate** in the "Generate Config Package" tab produces the full config package from just these numbers — no mesh, no visual/collision geometry, no physical URDF required for this to work end-to-end in the sense of "the walking-gait math has everything it needs."

**Practically for Humble/Gazebo Classic** (since this GUI is ROS 1-only, see §4/§6): the same information — chain-of-offsets + gait numbers — maps directly onto the plain YAML files the `ros2` branch actually reads at runtime (`joints.yaml`, `links.yaml`, `gait.yaml`, all trivial `ros__parameters:`-style YAML, see the literal file contents quoted in §3.1), so a hand-written YAML trio in the shape of `champ_config`'s is functionally equivalent to what the GUI would generate — you're just skipping the GUI, not skipping any capability. A URDF (even a crude one built from primitive `<box>`/`<cylinder>` geometry using exactly those same offsets, no meshes needed) is still required only for Gazebo *simulation and RViz visualization* — CHAMP's own gait/kinematics/odometry math (`libchamp`) does not read the URDF at all; the ROS node layer (`champ_base`) instead consumes `joints.yaml`/`links.yaml`/`gait.yaml` directly, and only the description/Gazebo layers need the actual model geometry and `ros2_control`/`gazebo_ros2_control` tags.

---

# 6. Humble / Gazebo Classic Compatibility Gotchas

## 6.1 It is `ros2_control` + `gazebo_ros2_control`, not the ROS1-style `gazebo_ros_control`

Confirmed directly in source on the `ros2` branch:
- Each leg's URDF macro embeds a `<ros2_control>` block with `<plugin>gazebo_ros2_control/GazeboSystem</plugin>`, exposing `effort` command interface + `position`/`velocity` state interfaces per joint — [`champ_description/urdf/leg.urdf.xacro`](https://github.com/chvmp/champ/blob/ros2/champ_description/urdf/leg.urdf.xacro)
- The top-level URDF loads the Gazebo Classic plugin `libgazebo_ros2_control.so` (this is the `gazebo_ros2_control` package's bridge plugin, i.e. it runs inside **Gazebo Classic**, not Ignition/GZ Sim) —
  ```xml
  <gazebo>
      <plugin filename="libgazebo_ros2_control.so" name="gazebo_ros2_control">
      <parameters>$(find champ_gazebo)/config/ros_control.yaml</parameters>
    </plugin>
  </gazebo>
  ```
  — [`champ_description/urdf/champ.urdf.xacro`](https://github.com/chvmp/champ/blob/ros2/champ_description/urdf/champ.urdf.xacro)
- `champ_gazebo`'s manifest declares exactly the dependencies this implies: `gazebo_ros`, `gazebo_ros_pkgs`, `gazebo_plugins`, `ros2_control`, `ros2_controllers`, `gazebo_ros2_control` — [`champ_gazebo/package.xml`](https://github.com/chvmp/champ/blob/ros2/champ_gazebo/package.xml)
- `champ_gazebo/launch/gazebo.launch.py` starts **Gazebo Classic** directly via `gzserver`/`gzclient` with the classic ROS bridge plugins (`libgazebo_ros_init.so`, `libgazebo_ros_factory.so`), then spawns the robot with `gazebo_ros`'s `spawn_entity.py`, then loads controllers with `ros2 control load_controller` — [`champ_gazebo/launch/gazebo.launch.py`](https://github.com/chvmp/champ/blob/ros2/champ_gazebo/launch/gazebo.launch.py)
- The controller config (`ros_control.yaml`) defines a `joint_state_broadcaster/JointStateBroadcaster` + a `joint_trajectory_controller/JointTrajectoryController` (`joint_group_effort_controller`) over all 12 joints with `effort` command interface and PID gains per joint (`p:100, i:0.2, d:1.0`), `controller_manager` `update_rate: 250` Hz — [`champ_gazebo/config/ros_control.yaml`](https://github.com/chvmp/champ/blob/ros2/champ_gazebo/config/ros_control.yaml)

**Bottom line: this is exactly the stack your target environment needs** — `ros-humble-gazebo-ros2-control`, `ros-humble-gazebo-ros-pkgs`, `ros-humble-ros2-control`, `ros-humble-ros2-controllers` must be installed (via `rosdep install` from the README's own install steps, §1). No Ignition/GZ Sim packages are involved; this is Gazebo Classic 11 specifically, matching your target.

## 6.2 Known, already-fixed Humble issues (fixed on current `ros2` HEAD)

- **Issue [#111](https://github.com/chvmp/champ/issues/111) — "ROS2 humble load_controller error when launch gazebo.launch.py"**: error `ros2 control load_controller: error: argument --set-state: invalid choice: 'start' (choose from 'configured', 'active')`. Root cause: `gazebo.launch.py` called `--set-state start`, but Humble's `ros2_control` CLI only accepts `configured`/`active`. **Fixed** in [PR #112](https://github.com/chvmp/champ/pull/112) (merged) by changing `start` → `active`. Confirmed fixed on current `ros2` HEAD — the downloaded `gazebo.launch.py` already uses `--set-state active` for both `joint_states_controller` and `joint_group_effort_controller`.
- **PR [#109](https://github.com/chvmp/champ/pull/109) — "Fix build error on ROS 2 humble"** (merged): Humble's `rclcpp` headers require `std::variant`/`std::optional`, i.e. **C++17**; `champ_base` and `champ_gazebo` needed their C++ standard bumped to 17, plus a matching fix in the `libchamp` submodule ([chvmp/libchamp#6](https://github.com/chvmp/libchamp)). If you fork/vendor an older snapshot of `champ`, make sure `CMakeLists.txt` requests C++17 for these packages.
- **Issue [#137](https://github.com/chvmp/champ/issues/137) — "colcon build failing when approaching champ_msgs with ros2 humble working on ros2 branch"** (closed): `ModuleNotFoundError` for `rosidl_typesupport_{fastrtps_c,c,introspection_c}` while building `champ_msgs`. This is a generic rosidl/environment issue (commonly caused by a stale/partial ROS 2 install or mixed sourced environments) rather than a `champ`-specific defect; issue is closed with no separate code fix recorded in the visible thread — if hit, first suspect your ROS 2 install / sourced environments rather than `champ`'s CMake.

## 6.3 Open, unresolved signal about overall ROS 2 maturity

- **Issue [#148](https://github.com/chvmp/champ/issues/148) — "Update of champ robot"** (opened Aug 2024, **still open** as of this research): a user directly asks "is robot champ is avaible in ROS2 Humble ... It seems to me that it is not fully functional?" with no maintainer reply visible. Combined with the `ros2`-branch README's own checklist (real-robot testing ✗, code cleanup/refactor ✗, robot-configuration porting ✗ at the framework level even though `chvmp/robots`'s `ros2` branch has since done some of this by hand), **treat the `ros2` branch as community-maintained and simulation-focused**, not a polished/official release. The Gazebo-Classic simulation path (bringup + gazebo + SLAM + Nav2) is explicitly checked off as working in the README:
  > "✓ Working Gazebo empty world... ✓ Working rviz only demo. ✓ Working Gazebo with teleoperated robot. ✓ Working Gazebo demo with SLAM. ✓ Working Gazebo demo with nav2 integration."
  — [chvmp/champ, `ros2` branch, README.md](https://github.com/chvmp/champ/blob/ros2/README.md)
  Real-hardware bring-up (✗ "Testing with real robot") is explicitly **not** validated on ROS 2 yet — matches what `mini_pupper_config`'s own README says ("Currently this only works in a virtual environment", §3.2).

## 6.4 No patched fork needed for the smoke test

For a pure Gazebo-Classic walking smoke test on Humble, the stock `ros2` branch of `chvmp/champ` (post the #112 merge) plus stock `chvmp/champ_teleop` `ros2` branch is sufficient — no third-party patch/fork is required. Only reach for a fork/patch if you hit the rosidl-environment issue in §6.2 (fix your ROS 2 install) or need a robot from `chvmp/robots` beyond Mini Pupper whose Gazebo path you haven't personally verified.

---

# 7. Minimum Steps: Stock Demo Robot Walking in Gazebo Classic (Smoke Test)

All commands below are copied verbatim from [chvmp/champ, `ros2` branch, README.md](https://github.com/chvmp/champ/blob/ros2/README.md).

## 7.1 Install + build
```bash
sudo apt install -y python3-rosdep
rosdep update

cd <your_ws>/src
git clone --recursive https://github.com/chvmp/champ -b ros2
git clone https://github.com/chvmp/champ_teleop -b ros2
cd ..
rosdep install --from-paths src --ignore-src -r -y

cd <your_ws>
colcon build
. <your_ws>/install/setup.bash
```

## 7.2 RViz-only walking demo (no Gazebo, fastest sanity check)
```bash
ros2 launch champ_config bringup.launch.py rviz:=true
```
in a second terminal:
```bash
ros2 launch champ_teleop teleop.launch.py
```
(add `joy:=true` if using a physical gamepad).

## 7.3 Gazebo Classic walking demo (the actual smoke test requested)
```bash
ros2 launch champ_config gazebo.launch.py
```
This single launch file (per its own source, §6.1) starts `gzserver`+`gzclient` (Gazebo Classic), spawns the stock 12-DOF "champ" robot via `spawn_entity.py`, and loads the `joint_state_broadcaster` + `joint_group_effort_controller` (`gazebo_ros2_control`). It internally also brings up `champ_bringup`'s base driver via the `champ_config`-level `bringup.launch.py` composition shown in [`champ_config/launch/bringup.launch.py`](https://github.com/chvmp/champ/blob/ros2/champ_config/launch/bringup.launch.py) (the top-level launch chains `champ_bringup`'s bringup + `champ_gazebo`'s gazebo launch together).

Drive it with teleop (same as §7.2):
```bash
ros2 launch champ_teleop teleop.launch.py
```

## 7.4 (Optional) SLAM/Nav2 smoke test on top of the same Gazebo world
```bash
ros2 launch champ_config gazebo.launch.py
ros2 launch champ_config slam.launch.py rviz:=true
```
Then in RViz: click "2D Nav Goal", click-drag to a target — this exercises `slam_toolbox` + Nav2 integration, which the README lists as working (✓) on `ros2`. Save a map with:
```bash
cd <your_ws>/src/champ/champ_config/maps
ros2 run nav2_map_server map_saver_cli -f new_map
```
Pure navigation on a saved map:
```bash
ros2 launch champ_config gazebo.launch.py
ros2 launch champ_config navigate.launch.py rviz:=true
```

No `champ_setup_assistant` step, no custom URDF, and no real hardware are needed for this smoke test — the stock `champ_config`/`champ_description` packages that ship inside the `chvmp/champ` repo itself are the complete "out of the box" demo robot (§3.1).

---

# Summary Table — Direct Answers

| # | Question | Answer |
|---|---|---|
| 1 | Repo/branch | `chvmp/champ` branch `ros2` (+ `chvmp/champ_teleop` branch `ros2`). No `champ_ros2` repo exists. |
| 2 | Package layout | `champ`, `champ_base`, `champ_bringup`, `champ_config`, `champ_description`, `champ_gazebo`, `champ_msgs`, `champ_navigation` — all inside the one repo. |
| 3 | Stock configs | Built-in generic "champ" robot (12 DOF, 0.175m/0.105m hip offsets, listed in full in §3.1). Real named robots (Mini Pupper, Spot, Mini Cheetah, Anymal B/C, Aliengo, Go1, A1, OpenDog V2, Open Quadruped, Stochlite, Stanford Pupper — Gazebo-confirmed) live in the separate `chvmp/robots` repo, `ros2` branch. No robot named "first" exists. |
| 4 | Setup assistant | ROS 1-only GUI tool (`chvmp/champ_setup_assistant`, no `ros2` branch); takes an optional URDF (with strict axis/zero-rotation assumptions) or manual per-actuator XYZ offsets, plus gait params; outputs a `<robot>_config` package (yaml configs + launch files + `config.json`). |
| 5 | Custom config without URDF | Yes — "Manual Joint Configuration" mode is explicitly designed for exactly this: key in per-leg actuator XYZ offsets (base→hip→upper→lower→foot chain) + gait params, no URDF needed for the controller math; a URDF (can be primitive-geometry, no meshes) is only needed later for Gazebo/RViz visualization. |
| 6 | Humble/Gazebo gotchas | Uses `gazebo_ros2_control` + `ros2_control` (matches Gazebo Classic 11 target exactly, not Ignition). Known issues #111 (load_controller `start`→`active`, fixed in PR #112) and PR #109 (C++17 requirement, fixed) are already resolved on current `ros2` HEAD. Issue #148 (open) flags general ROS2-port immaturity — treat as community/simulation-focused, not hardware-validated. |
| 7 | Smoke test | `colcon build` → `ros2 launch champ_config gazebo.launch.py` (+ `ros2 launch champ_teleop teleop.launch.py` to drive it). No setup-assistant or custom URDF required. |

---

# Sources Consulted

- https://github.com/chvmp/champ (branches: `master`, `ros2`)
- https://github.com/chvmp/champ/blob/ros2/README.md
- https://github.com/chvmp/champ/tree/ros2 (champ, champ_base, champ_bringup, champ_config, champ_description, champ_gazebo, champ_msgs, champ_navigation)
- https://github.com/chvmp/champ/blob/ros2/champ_description/urdf/properties.urdf.xacro
- https://github.com/chvmp/champ/blob/ros2/champ_description/urdf/leg.urdf.xacro
- https://github.com/chvmp/champ/blob/ros2/champ_description/urdf/champ.urdf.xacro
- https://github.com/chvmp/champ/blob/ros2/champ_config/config/gait/gait.yaml
- https://github.com/chvmp/champ/blob/ros2/champ_config/config/joints/joints.yaml
- https://github.com/chvmp/champ/blob/ros2/champ_config/config/links/links.yaml
- https://github.com/chvmp/champ/blob/ros2/champ_config/launch/gazebo.launch.py
- https://github.com/chvmp/champ/blob/ros2/champ_gazebo/launch/gazebo.launch.py
- https://github.com/chvmp/champ/blob/ros2/champ_gazebo/config/ros_control.yaml
- https://github.com/chvmp/champ/blob/ros2/champ_gazebo/package.xml
- https://github.com/chvmp/champ/issues/111, /issues/137, /issues/148, /pull/109, /pull/112, /pull/113
- https://github.com/chvmp/robots (branches: `master`, `ros2`)
- https://github.com/chvmp/robots/blob/master/README.md
- https://github.com/chvmp/robots/tree/ros2/configs
- https://github.com/chvmp/robots/blob/ros2/configs/mini_pupper_config/config.json
- https://github.com/chvmp/robots/blob/ros2/configs/mini_pupper_config/package.xml
- https://github.com/chvmp/robots/blob/ros2/configs/mini_pupper_config/README.md
- https://github.com/chvmp/champ_setup_assistant (branches: `master`, `noetic` — no `ros2`)
- https://github.com/chvmp/champ_setup_assistant/blob/master/README.md
- https://github.com/chvmp/champ_teleop (branches: `master`, `ros2`)
- https://github.com/chvmp/libchamp (README + top-level structure)
- https://api.github.com/orgs/chvmp/repos (full org repo listing)
