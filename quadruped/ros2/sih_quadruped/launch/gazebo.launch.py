# sih_quadruped Gazebo Classic launch. Mirrors chvmp/champ `ros2` branch
# champ_config/launch/gazebo.launch.py (docs/champ-research.md #6.1/#7): includes this
# package's own bringup.launch.py (see bringup.launch.py's docstring for the effort_limit
# xacro-arg wiring) plus champ_gazebo's gazebo.launch.py (reused as-is -- gzserver/gzclient,
# spawn_entity, controller loaders, the champ_gazebo contact_sensor node), pointed at this
# package's ros_control.yaml.
#
# `headless` (new vs. stock champ_config/gazebo.launch.py, per the task spec): champ_gazebo's
# own gazebo.launch.py already exposes a `headless` arg that skips gzclient (WSL2's Mesa/
# D3D12 OGRE renderer crashes gzclient/RViz -- see the task's WSL2 note) -- stock
# champ_config/gazebo.launch.py just never forwards it. Default true here since this package
# only needs gzserver for the stand/walk test harness; pass headless:=false for a GUI run
# (with LIBGL_ALWAYS_SOFTWARE=1, per the same WSL2 note).
import os
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.substitutions import FindPackageShare


def generate_launch_description():
    this_package = FindPackageShare('sih_quadruped')
    description_path = PathJoinSubstitution(
        [this_package, 'urdf', 'sih_quadruped.urdf.xacro']
    )
    joints_config = PathJoinSubstitution(
        [this_package, 'config', 'joints', 'joints.yaml']
    )
    gait_config = PathJoinSubstitution(
        [this_package, 'config', 'gait', 'gait.yaml']
    )
    links_config = PathJoinSubstitution(
        [this_package, 'config', 'links', 'links.yaml']
    )
    ros_control_config = PathJoinSubstitution(
        [this_package, 'config', 'ros_control', 'ros_control.yaml']
    )
    bringup_launch_path = PathJoinSubstitution(
        [FindPackageShare('sih_quadruped'), 'launch', 'bringup.launch.py']
    )
    gazebo_launch_path = PathJoinSubstitution(
        [FindPackageShare('champ_gazebo'), 'launch', 'gazebo.launch.py']
    )
    default_world_path = PathJoinSubstitution(
        [FindPackageShare('champ_gazebo'), 'worlds', 'default.world']
    )

    return LaunchDescription([
        DeclareLaunchArgument('use_sim_time', default_value='true'),
        DeclareLaunchArgument('rviz', default_value='false'),
        DeclareLaunchArgument('robot_name', default_value='sih_quadruped'),
        DeclareLaunchArgument('lite', default_value='false'),
        DeclareLaunchArgument('ros_control_file', default_value=ros_control_config),
        DeclareLaunchArgument('world', default_value=default_world_path),
        DeclareLaunchArgument('gui', default_value='true'),
        DeclareLaunchArgument('headless', default_value='true',
                               description='Skip gzclient -- WSL2 Mesa/D3D12 OGRE crash workaround, see this file docstring'),
        DeclareLaunchArgument('world_init_x', default_value='0.0'),
        DeclareLaunchArgument('world_init_y', default_value='0.0'),
        DeclareLaunchArgument('world_init_z', default_value='0.30'),
        DeclareLaunchArgument('world_init_heading', default_value='0.0'),
        DeclareLaunchArgument(
            name='effort_limit',
            default_value='2.4525',
            description='Leg joint effort limit, N.m (default: DS3225 stall torque at 6.8V, see urdf/properties.urdf.xacro)'
        ),

        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(bringup_launch_path),
            launch_arguments={
                "description_path": description_path,
                "joints_map_path": joints_config,
                "links_map_path": links_config,
                "gait_config_path": gait_config,
                "use_sim_time": LaunchConfiguration("use_sim_time"),
                "robot_name": LaunchConfiguration("robot_name"),
                "sim": "true",
                "rviz": LaunchConfiguration("rviz"),
                "hardware_connected": "false",
                "effort_limit": LaunchConfiguration("effort_limit"),
            }.items(),
        ),

        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(gazebo_launch_path),
            launch_arguments={
                "use_sim_time": LaunchConfiguration("use_sim_time"),
                "robot_name": LaunchConfiguration("robot_name"),
                "world": LaunchConfiguration("world"),
                "lite": LaunchConfiguration("lite"),
                "ros_control_file": LaunchConfiguration("ros_control_file"),
                "world_init_x": LaunchConfiguration("world_init_x"),
                "world_init_y": LaunchConfiguration("world_init_y"),
                "world_init_z": LaunchConfiguration("world_init_z"),
                "world_init_heading": LaunchConfiguration("world_init_heading"),
                "gui": LaunchConfiguration("gui"),
                "headless": LaunchConfiguration("headless"),
            }.items(),
        ),
    ])
