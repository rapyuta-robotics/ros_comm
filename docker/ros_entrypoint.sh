#!/bin/bash
set -e

# Source the ROS setup
source "/opt/ros/${ROS_DISTRO}/setup.bash"

exec "$@"
