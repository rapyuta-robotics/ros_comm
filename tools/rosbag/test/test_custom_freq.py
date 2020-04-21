#!/usr/bin/env python
import unittest
import tempfile
import rosbag
import os
import time
import logging
import rospy
import subprocess

from std_msgs.msg import Int32

BAG_DIR = tempfile.mkdtemp(prefix='rosbag_tests')

def fname(name):
        return os.path.join(BAG_DIR, name)

def callback(data):
    print("callback")

def run_cmd(step, cmd):
    rospy.loginfo('[%s] %s', step, cmd)
    process = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)
    process.wait()
    if process.returncode == 0:
        rospy.loginfo('[%s] Success', step)
        return True
    else:
        rospy.logerr('[%s] Failed: %s', step, process.returncode)
        return False

cmd = "roscore &"
run_cmd("roscore", cmd)

while (True) :
    try:
        rospy.get_published_topics()
        break;
    except:
        print("Waiting for rosmaster")
        time.sleep(1)

cmd = "python $(rospack find rosbag)/test/topic_publisher.py & "
run_cmd("bag_write", cmd)



file = fname("custom_record_freq.bag")
cmd = "rosbag record -f $(rospack find rosbag)/config/test_custom_freq.yaml -O " + file + " -a --duration 5s"
run_cmd("bag", cmd)

class TestCustomFreq(unittest.TestCase):
    def test_custom_freq(self):
        with rosbag.Bag(file) as bag:
            int_1 = list(bag.read_messages('/int_1'))
            string_1 = list(bag.read_messages('/string_1'))
            string_2 = list(bag.read_messages('/string_2'))

        self.assertGreater(len(int_1), 40)
        self.assertEqual(len(string_1), 5)
        self.assertEqual(len(string_2), 0)

cmd = "rosnode kill -a"
run_cmd("kill", cmd)

cmd = "pkill roscore"
run_cmd("kill", cmd)