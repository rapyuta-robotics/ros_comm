# rosbag
This is a custom rosbag package which provides all the feature of [original rosbag](http://wiki.ros.org/rosbag/Commandline) with custom freq recording of topics.

## dependency
* Yaml-CPP :- https://github.com/jbeder/yaml-cpp

## how to record custom rosbag
```shell
rosbag record --file-name record.yaml
```
> this only records and throttles down the topics mentioned in record.yaml
## param 
* --file-name: file which has topics for custom recording

## services
* Split rosbag
    * service_name: split_bag
    * type: std_srvs/Empty
    * description: call the service to create a split forcefully


## example:- record.yaml
```yaml
# topic_name: freq(double)
# topic_name: -1 (it will be recorded at publish freq)
#           : 0 (it will not be recorded)
#           : -2 (for latched/[pseudo-latched](https://github.com/rapyuta-robotics/ros_comm/pull/10#issue-463244616) topics, to keep them in every bag split)
#               Note: --repeat-latched option only takes topic which has topic info latch=true it does not take pseudo-latched topics (described in above link)

# For topic name same regular expressions cli can be used: ex. "/realsense(.*)" : 0
# [used by default rosbag](http://wiki.ros.org/rosbag/Commandline)
# if there is a topic in a namespace which has been excluded using regular expressions: 
#   to record that topic put that topic before the regular expression
"/chatter": 2
"/raw_odom": 1
"/realsense_bottom/accel/sample": 1
"/realsense_bottom/depth/camera_info": 1
"/realsense_bottom/depth/color/points": 1
"/realsense_bottom/depth/image_rect_raw": 1
"/realsense_bottom/infra1/camera_info": 1
"/realsense_bottom/infra1/image_rect_raw": 1
```
