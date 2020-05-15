#!/usr/bin/env python
import unittest
import tempfile
import os
import sys
import time
import logging
import subprocess

import rosbag
import rospy
import rostest

from std_msgs.msg import Int32

BAG_DIR = tempfile.mkdtemp(prefix='rosbag_tests')

class TestCustomFreq(unittest.TestCase):

    def fname(self, name):
        return os.path.join(BAG_DIR, name)

    def callback(self, data):
        print("callback")

    def run_cmd(self, step, cmd):
        rospy.loginfo('[%s] %s', step, cmd)
        process = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)
        process.wait()
        if process.returncode == 0:
            rospy.loginfo('[%s] Success', step)
            return True
        else:
            rospy.logerr('[%s] Failed: %s', step, process.returncode)
            return False


    def test_custom_freq(self):
        cmd = "roscore &"
        self.run_cmd("roscore", cmd)

        while (True) :
            try:
                rospy.get_published_topics()
                break;
            except:
                print("Waiting for rosmaster")
                time.sleep(1)

        cmd = "python $(rospack find rosbag)/test/topic_publisher.py & "
        self.run_cmd("topic_publisher", cmd)

        file = self.fname("custom_record_freq.bag")
        cmd = "rosbag record -f $(rospack find rosbag)/config/test_custom_freq.yaml -O " + file + " -a --duration 5s"
        self.run_cmd("bag", cmd)

        cmd = "rosnode kill -a"
        self.run_cmd("kill node", cmd)

        cmd = "pkill roscore"
        self.run_cmd("kill roscore", cmd)

        with rosbag.Bag(file) as bag:
            int_1 = list(bag.read_messages('/int_1'))
            string_1 = list(bag.read_messages('/string_1'))
            string_2 = list(bag.read_messages('/string_2'))

        self.assertGreater(len(int_1), 40)
        self.assertGreaterEqual(len(string_1), 4)
        self.assertLessEqual(len(string_1), 6)
        self.assertEqual(len(string_2), 0)

if __name__ == '__main__':
    rostest.rosrun('test_rosbag', 'test_custom_freq', TestCustomFreq, sys.argv)