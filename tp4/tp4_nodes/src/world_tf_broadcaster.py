#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
from geometry_msgs.msg import PoseStamped, TransformStamped
from tf2_ros import TransformBroadcaster


class WorldTfBroadcaster(Node):
    def __init__(self):
        super().__init__('world_tf_broadcaster')
        self.br = TransformBroadcaster(self)
        self.create_subscription(PoseStamped, '/pose', self.pose_callback, 10)

    def pose_callback(self, msg):
        # /pose contient les poses de tous les éléments du robot :
        # on ne garde que celle qui a le bon frame_id (cf. l'énoncé)
        if msg.header.frame_id != 'my_world':
            return

        t = TransformStamped()
        t.header.stamp = msg.header.stamp
        t.header.frame_id = 'world'            # parent
        t.child_frame_id = 'dummy_root_link'   # enfant

        t.transform.translation.x = msg.pose.position.x
        t.transform.translation.y = msg.pose.position.y
        t.transform.translation.z = msg.pose.position.z
        t.transform.rotation = msg.pose.orientation

        self.br.sendTransform(t)


def main():
    rclpy.init()
    node = WorldTfBroadcaster()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()