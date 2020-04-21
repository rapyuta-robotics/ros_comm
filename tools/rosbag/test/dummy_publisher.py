from std_msgs.msg import String
from std_msgs.msg import Int32
import rospy

def topic_publisher():
    pub_string_1 = rospy.Publisher('string_1', String, queue_size=10)
    pub_string_2 = rospy.Publisher('string_2', String, queue_size=10)
    pub_int_1 = rospy.Publisher('int_1', Int32, queue_size=10)

    rospy.init_node('topic_publisher', anonymous=True)
    rate = rospy.Rate(10) # 10hz
    str_1 = "foo_1"
    str_2 = "foo_2"
    int_1 = 0
    while not rospy.is_shutdown():
        str_1 = str_1 + "_" + str(int_1)
        str_2 = str_2 + "_" + str(int_1)
        pub_string_1.publish(str_1)
        pub_string_2.publish(str_2)
        pub_int_1.publish(int_1)
        rate.sleep()
        int_1 = int_1 + 1

if __name__ == '__main__':
    try:
        topic_publisher()
    except rospy.ROSInterruptException:
        pass