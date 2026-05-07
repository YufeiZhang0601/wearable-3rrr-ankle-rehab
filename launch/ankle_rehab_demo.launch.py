import os

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import Command, LaunchConfiguration, PathJoinSubstitution
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare
from launch.substitutions import FindExecutable


def generate_launch_description():
    package_name = "rh1"
    package_share = FindPackageShare(package=package_name)

    urdf_file = LaunchConfiguration("urdf_file")
    rviz_config_file = LaunchConfiguration("rviz_config_file")
    duration_s = LaunchConfiguration("duration_s")
    loop = LaunchConfiguration("loop")
    publish_rate_hz = LaunchConfiguration("publish_rate_hz")
    csv_path = LaunchConfiguration("csv_path")

    default_urdf = PathJoinSubstitution(
        [package_share, "urdf", "rh1_sim.urdf.xacro"]
    )
    default_rviz = PathJoinSubstitution(
        [package_share, "rviz", "ankle_rehab_demo.rviz"]
    )
    default_csv = os.path.join(
        os.getcwd(), "demo_output", "ankle_rehab_joint_state_player.csv"
    )

    robot_description = {
        "robot_description": Command([FindExecutable(name="xacro"), " ", urdf_file])
    }

    return LaunchDescription(
        [
            DeclareLaunchArgument(
                "urdf_file",
                default_value=default_urdf,
                description="Simulation Xacro/URDF used by robot_state_publisher.",
            ),
            DeclareLaunchArgument(
                "rviz_config_file",
                default_value=default_rviz,
                description="RViz config for the ankle rehab video demo.",
            ),
            DeclareLaunchArgument(
                "duration_s",
                default_value="60.0",
                description="Demo playback duration before looping.",
            ),
            DeclareLaunchArgument(
                "loop",
                default_value="true",
                description="Loop the rehab trajectory for repeated recording attempts.",
            ),
            DeclareLaunchArgument(
                "publish_rate_hz",
                default_value="50.0",
                description="JointState publish rate.",
            ),
            DeclareLaunchArgument(
                "csv_path",
                default_value=default_csv,
                description="CSV file written by the JointState player.",
            ),
            Node(
                package="robot_state_publisher",
                executable="robot_state_publisher",
                name="robot_state_publisher",
                output="screen",
                parameters=[robot_description],
            ),
            Node(
                package=package_name,
                executable="ankle_rehab_joint_state_player",
                name="ankle_rehab_joint_state_player",
                output="screen",
                parameters=[
                    {
                        "duration_s": duration_s,
                        "loop": loop,
                        "publish_rate_hz": publish_rate_hz,
                        "csv_path": csv_path,
                    }
                ],
            ),
            Node(
                package="rviz2",
                executable="rviz2",
                name="rviz2_ankle_rehab_demo",
                output="screen",
                arguments=["-d", rviz_config_file],
            ),
        ]
    )
