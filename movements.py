# move.py
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
import argparse


class Move(Node):
    def __init__(self,args, lin_vel, ang_vel):
        super().__init__('simple_mover')
        self.publisher_ = self.create_publisher(Twist, '/cmd_vel', 10)
        timer_period = 0.1
        self.timer = self.create_timer(timer_period, self.move)
        self.linear_vel = lin_vel
        self.angular_vel = ang_vel
        self.start_time= self.get_clock().now()
        timer_period=0.1
        self.timer=self.create_timer(timer_period,self.move)

    def move(self):
        elapsed=(self.get_clock().now() - self.start_time).nanoseconds * 1e-9
        if elapsed<5.0:
            msg = Twist()
            msg.linear.x = self.linear_vel
            msg.angular.z = self.angular_vel
            self.publisher_.publish(msg)
            self.get_logger().info('Publishing: Forward move command')
        else:
            msg = Twist()
            msg.linear.x = 0.0
            msg.angular.z = 0.0
            self.publisher_.publish(msg)
            self.get_logger().info('Publishing: Forward move command')
            self.timer.cancel()

# stop.py

class Stop(Node):
    def __init__(self,args):
        super().__init__('simple_mover')
        self.publisher_ = self.create_publisher(Twist, '/cmd_vel', 10)
        timer_period = 0.1
        self.timer = self.create_timer(timer_period, self.stop)

    def stop(self):
        msg = Twist()
        msg.linear.x = 0.0
        msg.angular.z = 0.0
        self.publisher_.publish(msg)
        self.get_logger().info('Publishing: Stop move command')

'''def main(args=None):
    rclpy.init(args=args)
    parser = argparse.ArgumentParser(description='Machine Control')
    parser.add_argument('--linear_vel', type=float, default=0.01)
    parser.add_argument('--angular_vel', type=float, default=0.0)
    parsed_args, unknown = parser.parse_known_args()
    mover = Move(parsed_args)
    rclpy.spin(mover)
    mover.destroy_node()
    rclpy.shutdown()
'''


#if _name_ == '_main_':
#    main()

