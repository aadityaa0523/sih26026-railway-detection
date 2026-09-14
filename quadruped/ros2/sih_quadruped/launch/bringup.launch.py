# sih_quadruped bringup launch. Mirrors chvmp/champ `ros2` branch
# champ_config/launch/bringup.launch.py (docs/champ-research.md #3.1/#7): includes
# champ_bringup's bringup.launch.py (reused as-is -- it runs champ_description's
# description.launch.py for robot_state_publisher + xacro, champ_base's
# quadruped_controller_node + state_estimation_node, and the two robot_localization EKFs)
# pointed at THIS package's urdf/config instead of champ_description/champ_config's.
#
# `effort_limit` (N.m) is threaded into the xacro `leg_effort_limit` arg (see
# urdf/properties.urdf.xacro) by appending "leg_effort_limit:=<value>" to the
# description_path string -- champ_description's description.launch.py runs
# `Command(["xacro ", description_path])`, and xacro's CLI accepts trailing `key:=value`
# args after the file path, so this needs no changes to any chvmp/champ package.
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
    bringup_launch_path = PathJoinSubstitution(
        [FindPackageShare('champ_bringup'), 'launch', 'bringup.launch.py']
    )

    return LaunchDescription([
        DeclareLaunchArgument(
            name='robot_name',
            default_value='',
            description='Set robot name for multi robot'
        ),
        DeclareLaunchArgument(
            name='sim',
            default_value='false',
            description='Enable use_sim_time to true'
        ),
        DeclareLaunchArgument(
            name='rviz',
            default_value='false',
            description='Run rviz'
        ),
        DeclareLaunchArgument(
            name='hardware_connected',
            default_value='false',
            description='Set to true if connected to a physical robot'
        ),
        DeclareLaunchArgument(
            name='effort_limit',
            default_value='2.4525',
            description='Leg joint effort limit, N.m (default: DS3225 stall torque at 6.8V, see urdf/properties.urdf.xacro)'
        ),

        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(bringup_launch_path),
            launch_arguments={
                "use_sim_time": LaunchConfiguration("sim"),
                "robot_name": LaunchConfiguration("robot_name"),
                "gazebo": LaunchConfiguration("sim"),
                "rviz": LaunchConfiguration("rviz"),
                "hardware_connected": LaunchConfiguration("hardware_connected"),
                "publish_foot_contacts": "true",
                "close_loop_odom": "true",
                "joint_controller_topic": "joint_group_effort_controller/joint_trajectory",
                "description_path": [description_path, " leg_effort_limit:=", LaunchConfiguration("effort_limit")],
                "joints_map_path": joints_config,
                "links_map_path": links_config,
                "gait_config_path": gait_config
            }.items(),
        )
    ])
