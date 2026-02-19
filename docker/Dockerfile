# =============================================================================
# Dockerfile: Build patched ros_comm and overlay onto the slim Rapyuta
# Noetic base image.
#
# Multi-stage build:
#   Stage 1 (builder) — ubuntu:focal + build tools → compile ros_comm
#   Stage 2 (runtime) — quay.io/rapyuta/ros:noetic → overlay patched files
#
# Build args:
#   UBUNTU_DISTRO   - Ubuntu release codename         (default: focal)
#   ROS_DISTRO      - ROS distribution name            (default: noetic)
#   BASE_IMAGE      - Slim runtime base image          (default: quay.io/rapyuta/ros:noetic)
#
# Usage:
#   docker build -f docker/Dockerfile \
#     -t rapyuta/ros:noetic-patched .
#
# =============================================================================

# ---- configurable args (before any FROM so they're global) -----------------
ARG UBUNTU_DISTRO=focal
ARG ROS_DISTRO=noetic
ARG BASE_IMAGE=quay.io/rapyuta/ros:noetic

# ===========================================================================
# Stage 1: Builder — fat image with all build tools
# ===========================================================================
FROM ubuntu:${UBUNTU_DISTRO} AS builder

ARG UBUNTU_DISTRO=focal
ARG ROS_DISTRO=noetic

ENV DEBIAN_FRONTEND=noninteractive
ENV ROS_DISTRO=${ROS_DISTRO}
ENV LANG=C.UTF-8
ENV LC_ALL=C.UTF-8

SHELL ["/bin/bash", "-o", "pipefail", "-c"]

# ---------------------------------------------------------------------------
# 1. Base dependencies & ROS apt repository
# ---------------------------------------------------------------------------
RUN apt-get update && apt-get install -y --no-install-recommends \
        ca-certificates \
        curl \
        gnupg2 \
        lsb-release \
    && rm -rf /var/lib/apt/lists/*

RUN curl -sSL https://raw.githubusercontent.com/ros/rosdistro/master/ros.asc | apt-key add - \
    && echo "deb http://packages.ros.org/ros/ubuntu ${UBUNTU_DISTRO} main" \
        > /etc/apt/sources.list.d/ros-latest.list

# ---------------------------------------------------------------------------
# 2. ROS base + build tools + ros_comm build dependencies
# ---------------------------------------------------------------------------
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

RUN if [ ! -f /etc/ros/rosdep/sources.list.d/20-default.list ]; then \
        rosdep init; \
    fi \
    && rosdep update --rosdistro ${ROS_DISTRO}

# ---------------------------------------------------------------------------
# 3. Copy source & build into a clean install-space
# ---------------------------------------------------------------------------
ENV OVERLAY_WS=/opt/ros_comm_ws
RUN mkdir -p ${OVERLAY_WS}/src
COPY . ${OVERLAY_WS}/src/ros_comm

WORKDIR ${OVERLAY_WS}
RUN . /opt/ros/${ROS_DISTRO}/setup.sh \
    && rosdep install --from-paths src --ignore-src -r -y 2>/dev/null || true

# Build and install into a SEPARATE prefix so we can cherry-pick files later.
# Using /opt/ros_comm_install avoids mixing with system ros packages.
RUN . /opt/ros/${ROS_DISTRO}/setup.sh \
    && catkin_make_isolated \
        --install \
        --install-space /opt/ros_comm_install \
        -DCMAKE_BUILD_TYPE=Release \
    && rm -rf ${OVERLAY_WS}/build_isolated ${OVERLAY_WS}/devel_isolated

# ===========================================================================
# Stage 2: Runtime — slim image with only the patched overlay
# ===========================================================================
FROM ${BASE_IMAGE} AS runtime

ARG ROS_DISTRO=noetic

# Copy the entire patched install-space over the system ROS install.
# This overlays patched libraries (libroscpp.so, etc.), headers, Python
# packages, and package metadata on top of whatever the base image ships.
COPY --from=builder /opt/ros_comm_install/ /opt/ros/${ROS_DISTRO}/


ENTRYPOINT ["/ros_entrypoint.sh"]
CMD ["bash"]
