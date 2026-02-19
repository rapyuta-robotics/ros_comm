# =============================================================================
# Dockerfile: Build ROS Noetic (or future distros) from ubuntu base with
# patched ros_comm overlay from this fork.
#
# Build args:
#   UBUNTU_DISTRO  - Ubuntu release codename (default: focal)
#   ROS_DISTRO     - ROS distribution name    (default: noetic)
#
# Usage:
#   docker build -f docker/Dockerfile \
#     --build-arg UBUNTU_DISTRO=focal --build-arg ROS_DISTRO=noetic \
#     -t rapyuta/ros:noetic-patched .
#
# Extend for Jammy in the future by changing the build args.
# =============================================================================

ARG UBUNTU_DISTRO=focal
FROM ubuntu:${UBUNTU_DISTRO}

# Re-declare after FROM so it's available in subsequent stages
ARG UBUNTU_DISTRO=focal
ARG ROS_DISTRO=noetic

ENV DEBIAN_FRONTEND=noninteractive
ENV ROS_DISTRO=${ROS_DISTRO}
ENV LANG=C.UTF-8
ENV LC_ALL=C.UTF-8

SHELL ["/bin/bash", "-o", "pipefail", "-c"]

# ---------------------------------------------------------------------------
# 1. Install base dependencies & set up ROS apt repository
# ---------------------------------------------------------------------------
RUN apt-get update && apt-get install -y --no-install-recommends \
        ca-certificates \
        curl \
        gnupg2 \
        lsb-release \
        software-properties-common \
    && rm -rf /var/lib/apt/lists/*

# Add the ROS apt key and repository
RUN curl -sSL https://raw.githubusercontent.com/ros/rosdistro/master/ros.asc | apt-key add - \
    && echo "deb http://packages.ros.org/ros/ubuntu ${UBUNTU_DISTRO} main" \
        > /etc/apt/sources.list.d/ros-latest.list

# ---------------------------------------------------------------------------
# 2. Install ROS base packages & build tooling
# ---------------------------------------------------------------------------
# Install ROS base, build tools, and ros_comm build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
        ros-${ROS_DISTRO}-ros-base \
        build-essential \
        cmake \
        python3-catkin-tools \
        python3-catkin-pkg \
        python3-rosdep \
        python3-rosinstall \
        python3-rosinstall-generator \
        python3-pip \
        python3-setuptools \
        python3-vcstool \
        python3-empy \
        python3-nose \
        python3-numpy \
        libboost-all-dev \
        libbz2-dev \
        liblz4-dev \
        libgpgme-dev \
        libssl-dev \
        liblog4cxx-dev \
        libyaml-cpp-dev \
    && rm -rf /var/lib/apt/lists/*

# Initialize rosdep (if not already initialized)
RUN if [ ! -f /etc/ros/rosdep/sources.list.d/20-default.list ]; then \
        rosdep init; \
    fi \
    && rosdep update --rosdistro ${ROS_DISTRO}

# ---------------------------------------------------------------------------
# 3. Copy fork source into an overlay catkin workspace
# ---------------------------------------------------------------------------
ENV OVERLAY_WS=/opt/ros_comm_ws
RUN mkdir -p ${OVERLAY_WS}/src
COPY . ${OVERLAY_WS}/src/ros_comm

# Install any missing dependencies via rosdep
WORKDIR ${OVERLAY_WS}
RUN . /opt/ros/${ROS_DISTRO}/setup.sh \
    && rosdep install --from-paths src --ignore-src -r -y 2>/dev/null || true

# ---------------------------------------------------------------------------
# 4. Build the overlay — install directly into /opt/ros/${ROS_DISTRO} so
#    patched libraries (e.g. libroscpp.so) replace the distro versions.
#    Downstream images just need to source /opt/ros/${ROS_DISTRO}/setup.bash.
# ---------------------------------------------------------------------------
RUN . /opt/ros/${ROS_DISTRO}/setup.sh \
    && catkin_make_isolated \
        --install \
        --install-space /opt/ros/${ROS_DISTRO} \
        -DCMAKE_BUILD_TYPE=Release \
    && rm -rf ${OVERLAY_WS}/build_isolated ${OVERLAY_WS}/devel_isolated

# ---------------------------------------------------------------------------
# 5. Entrypoint
# ---------------------------------------------------------------------------
COPY docker/ros_entrypoint.sh /ros_entrypoint.sh
RUN chmod +x /ros_entrypoint.sh

ENTRYPOINT ["/ros_entrypoint.sh"]
CMD ["bash"]
