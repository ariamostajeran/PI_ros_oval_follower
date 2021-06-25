#! /usr/bin/env python3
import math
import matplotlib.pyplot as plt
import numpy as np
import rospy
import random
from geometry_msgs.msg import Twist
from geometry_msgs.msg import Point
from turtlesim.msg import Pose
import tf
from nav_msgs.msg import Odometry

points = [(1.5, 1.5), (1.5, -1.5), (-1.5, -1.5), (-1.5, 1.5)]
point = (0, 0)

class RndVelocityGen:
    def __init__(self):
        rospy.init_node('random_velocity')
        rospy.loginfo(
            "CTRL + C to stop the turtlebot")
        rospy.on_shutdown(self.shutdown)
        self.vel_pub = rospy.Publisher('/cmd_vel', Twist, queue_size=1)
        # self.pose_Subscriber = rospy.Subscriber('/pose', Pose, self.update_pose)
        self.pose = Pose()
        self.plot_x = []
        self.plot_y = []
        self.vel = Twist()
        self.vel.linear.x = 0.5  # m/s
        self.vel.angular.z = 0.5  # rad/s
        self.max_interval = 10
        self.start_time = rospy.get_rostime().secs
        self.tmp = 0
        self.i_error = 0
        self.counter = 0
        self.locations = self.location_finder(3, 1, 0.1)
        self.average_error = 0

    # def update_pose(self, data):
    #     self.pose = data
        # self.pose.x = round(self.pose.x, 4)
        # self.pose.y = round(self.pose.y, 4)

    def location_finder(self, a, b, ds):
        s = np.linspace(0, 2 * math.pi, int(2 * math.pi * (1 / ds)))
        x = a * np.cos(s)
        y = b * np.sin(s)
        return (x, y)

    def steering_angle(self, point):
        # print("SELF POS IN STEERING : ", (self.pose.x, self.pose.y))
        return math.atan2(point.y - self.pose.y, point.x - self.pose.x)

    def angular_error(self, point):
        # print("ANGULAR_ERROR theta :", self.pose.theta,
        #       "Steering angle", self.steering_angle(point),
        #       "Result", self.steering_angle(point) - self.pose.theta)

        return self.steering_angle(point) - self.pose.theta

    def dist(self, pos1):
        return math.sqrt(((pos1.x - self.pose.x) ** 2) + ((pos1.y - self.pose.y) ** 2))

    def set_vel(self):

        while not rospy.is_shutdown():
            while self.counter < 10:
                data_odom = None
                while data_odom is None:
                    try:
                        data_odom = rospy.wait_for_message("/odom", Odometry, timeout=1)
                        # data_twist = rospy.wait_for_message("/change", Twist, timeout=1)
                        self.pose.x = data_odom.pose.pose.position.x
                        self.pose.y = data_odom.pose.pose.position.y
                        quaternion = (data_odom.pose.pose.orientation.x, data_odom.pose.pose.orientation.y,
                                      data_odom.pose.pose.orientation.z, data_odom.pose.pose.orientation.w)

                        (roll, pitch, theta) = tf.transformations.euler_from_quaternion(quaternion)
                        print("THETA = ", theta)
                        self.pose.theta = theta
                        # print("calculated theta = ", math.atan2(self.pose.x, self.pose.y))
                        # print("DATA_ODOM : ", data_odom.pose.pose.position)
                        # print("DATA_ODOM ANGLE :", self.pose.theta)
                    except:
                        rospy.loginfo("CANT FIND ODOM")
                if rospy.is_shutdown():
                    break
                # self.pose.theta = data_odom.
                point = Pose()
                # point.x = points[self.tmp][0]
                # point.y = points[self.tmp][1]
                # goal_x = points[self.tmp][0]
                # goal_y = points[self.tmp][1]
                point.x, point.y = self.locations[0][self.tmp], self.locations[1][self.tmp]
                # goal_x, goal_y = self.locations[self.tmp][0], self.locations[self.tmp][1]

                safe_dist = 0.18
                if self.counter == 0:
                    self.plot_x.append(self.pose.x)
                    self.plot_y.append(self.pose.y)
                distance_error = self.dist(point)

                if distance_error < safe_dist:
                    if self.counter == 0:
                        self.average_error += distance_error
                        print(distance_error)
                    self.tmp += 1
                    self.i_error = 0

                if self.tmp == 61:
                    self.tmp = 1
                    self.counter += 1

                # point.x = points[self.tmp][0]
                # point.y = points[self.tmp][1]
                # goal_x = points[self.tmp][0]
                # goal_y = points[self.tmp][1]
                ds = 0.1 * self.tmp
                # print(self.locations)
                print(self.locations[0][self.tmp], self.locations[1][self.tmp])

                goal_x, goal_y = self.locations[0][self.tmp], self.locations[1][self.tmp]
                # goal_x = goal[0]
                # goal_y = goal[1]
                print("GOAL X, Y", (goal_x, goal_y))

                x_dif = goal_x - self.pose.x
                y_dif = goal_y - self.pose.y

                angular_error = self.angular_error(point)
                x_forward = 0.47
                p_constant = 1.6
                i_constant = 0.25
                angle_to_goal = math.atan2(y_dif, x_dif)
                z_counterclock = 0
                angle_to_goal = angle_to_goal - self.pose.theta
                if angle_to_goal > math.pi:
                    angle_to_goal -= 2 * math.pi
                if angle_to_goal < -math.pi:
                    angle_to_goal += 2 * math.pi
                self.i_error += angle_to_goal
                # i_adder = self.i_error
                if abs(angle_to_goal) > 0.05:
                    z_counterclock = p_constant * (angle_to_goal) + i_constant * (self.i_error)
                    # x_forward = 0
                print("Angular_error = ", angular_error)
                # if abs(angular_error) < 0.7:
                #     print("pichesh 0")
                #     z_counterclock = 0
                    # x_forward = 0.9

                print("ANGULAR Result : ", z_counterclock)

                self.vel.linear.x = x_forward
                print("linear speed", self.vel.linear.x)
                # print("ANGULAR VEL : ", self.vel.angular)
                self.vel.angular.z = z_counterclock
                print("counter ", self.counter)
                print("SELF = ", self.pose)
                print("LOCATION Follower", self.tmp)
                print("DISTANCE = ", distance_error)

                self.vel_pub.publish(self.vel)
                now = rospy.get_rostime()
                print("Time now: ", now.secs)
                next = 0.05
                rospy.loginfo("Twist: [%5.3f, %5.3f], next change in %i secs - ", self.vel.linear.x, self.vel.angular.z,
                              next)
                # print("plot x", self.plot_x)
                # plt.plot(self.plot_x, self.plot_y)
                # plt.plot(self.locations[0], self.locations[1])
                # plt.legend(["Dataset 1", "Dataset 2"])
                # plt.savefig("plots_1.pdf")

                rospy.sleep(next)
        # rospy.spin()

            self.shutdown()

    def shutdown(self):
        print("Shutdown!")

        rospy.loginfo("Stop TurtleBot")
        # print("plot x", self.plot_x)
        plt.plot(self.plot_x, self.plot_y)
        print("average error : ", self.average_error / 62)
        plt.text(1, 1.5, rf'average error = {self.average_error / len(self.locations)}',
                 fontsize=10)
        plt.plot(self.locations[0], self.locations[1])
        plt.legend(["Dataset 1", "Dataset 2"])
        plt.savefig("plots_1.pdf")

        self.vel.linear.x = 0.0
        self.vel.angular.z = 0.0
        self.vel_pub.publish(self.vel)
        rospy.sleep(1)


if __name__ == '__main__':
    try:
        generator = RndVelocityGen()
        generator.set_vel()

    except rospy.ROSInterruptException:
        pass