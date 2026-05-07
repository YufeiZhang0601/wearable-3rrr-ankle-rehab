"""ROS 2 JointState publisher for the RH1 ankle rehabilitation demo."""

import os

import rclpy
from ament_index_python.packages import get_package_share_directory
from rclpy.node import Node
from sensor_msgs.msg import JointState

from rh1.ankle_rehab_control import (
    ALL_DEMO_JOINTS,
    AnkleRehabClosedLoopController,
    default_config,
    parse_revolute_joint_limits,
    write_csv,
)


class AnkleRehabJointStatePlayer(Node):
    def __init__(self):
        super().__init__("ankle_rehab_joint_state_player")

        package_share = get_package_share_directory("rh1")
        default_urdf = os.path.join(package_share, "urdf", "rh1.urdf")
        default_csv = os.path.join(
            os.getcwd(), "demo_output", "ankle_rehab_joint_state_player.csv"
        )

        config = default_config()
        self.declare_parameter("urdf_path", default_urdf)
        self.declare_parameter("csv_path", default_csv)
        self.declare_parameter("publish_rate_hz", 50.0)
        self.declare_parameter("duration_s", 60.0)
        self.declare_parameter("loop", True)
        for key, value in config.items():
            self.declare_parameter(key, value)

        self.urdf_path = self.get_parameter("urdf_path").value
        self.csv_path = self.get_parameter("csv_path").value
        self.publish_rate_hz = float(self.get_parameter("publish_rate_hz").value)
        self.duration_s = float(self.get_parameter("duration_s").value)
        self.loop = bool(self.get_parameter("loop").value)
        for key in config:
            config[key] = float(self.get_parameter(key).value)

        limits = parse_revolute_joint_limits(self.urdf_path)
        self.controller = AnkleRehabClosedLoopController(limits, config)
        self.publisher = self.create_publisher(JointState, "joint_states", 10)
        self.rows = []
        self.start_time = self.get_clock().now()
        self.last_time_s = 0.0
        self.timer = self.create_timer(1.0 / self.publish_rate_hz, self._on_timer)

        self.get_logger().info("Publishing RH1 ankle rehab JointState demo.")
        self.get_logger().info("URDF limits source: %s" % self.urdf_path)
        self.get_logger().info("CSV log: %s" % self.csv_path)

    def destroy_node(self):
        if self.rows:
            write_csv(self.csv_path, self.rows)
            self.get_logger().info("Wrote CSV log: %s" % self.csv_path)
        super().destroy_node()

    def _on_timer(self):
        elapsed = (self.get_clock().now() - self.start_time).nanoseconds * 1e-9
        if self.loop and self.duration_s > 0.0:
            t = elapsed % self.duration_s
        else:
            t = elapsed

        dt = max(1.0 / self.publish_rate_hz, t - self.last_time_s)
        self.last_time_s = t
        sample = self.controller.step(t, dt)
        self.rows.append(sample["row"])

        msg = JointState()
        msg.header.stamp = self.get_clock().now().to_msg()
        msg.name = list(ALL_DEMO_JOINTS)
        msg.position = [sample["positions"].get(joint_name, 0.0) for joint_name in msg.name]
        msg.velocity = []
        msg.effort = []
        self.publisher.publish(msg)

        if not self.loop and self.duration_s > 0.0 and elapsed >= self.duration_s:
            write_csv(self.csv_path, self.rows)
            self.get_logger().info("Demo duration complete; wrote CSV log.")
            rclpy.shutdown()


def main(args=None):
    rclpy.init(args=args)
    node = AnkleRehabJointStatePlayer()
    try:
        rclpy.spin(node)
    finally:
        if rclpy.ok():
            node.destroy_node()


if __name__ == "__main__":
    main()
