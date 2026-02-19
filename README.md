# ros_comm (Rapyuta Fork)

Forked from [ros/ros_comm](https://github.com/ros/ros_comm) to maintain patches for ROS Noetic after its upstream EOL (May 2025).

## Patches

### Fix: roscpp PollManager busy loop on unexpected UDP traffic ([#2166](https://github.com/ros/ros_comm/issues/2166))

On Noetic (and Melodic), every roscpp node opens a UDP server socket at startup and registers it with `PollManager` for read polling. However, `TransportUDP::socketUpdate` only reads data when `read_cb_` is set — which is **not** the case for nodes that don't actively use UDPROS subscriptions.

If any unexpected UDP traffic arrives on that port, the data sits unread in the kernel buffer, causing `poll()` to return immediately on every iteration. This turns `PollManager::threadFunc` into a busy loop consuming **100% CPU** on one thread.

**Fix:** When `POLLIN` fires but no `read_cb_` is registered, the socket data is now drained and discarded, preventing the busy loop.

**Affected file:** `clients/roscpp/src/libros/transport/transport_udp.cpp`

## Building the Patched Docker Image

This repo includes a Dockerfile based on `ubuntu:focal` that installs ROS Noetic from the official apt repositories, then builds this fork's packages as an overlay — replacing the system-installed `roscpp` (and other ros_comm packages) with the patched versions.

### Prerequisites

- Docker (>= 20.10)
- Docker Compose v2

### Quick Start

```bash
# Build the image
docker compose build noetic

# Run a shell
docker compose run --rm noetic bash

# Or build directly
docker build -f docker/Dockerfile \
  --build-arg UBUNTU_DISTRO=focal \
  --build-arg ROS_DISTRO=noetic \
  -t rapyuta/ros:noetic-patched .
```

### Using as a Base Image

```dockerfile
FROM rapyuta/ros:noetic-patched

# Your ROS workspace setup here
RUN mkdir -p /catkin_ws/src
WORKDIR /catkin_ws
# ...
```

## Extending for Jammy

The Dockerfile is parameterized with `UBUNTU_DISTRO` and `ROS_DISTRO` build args. To add support for a Jammy-based image in the future:

1. Uncomment the `jammy` service in `docker-compose.yaml`.
2. Adjust `ROS_DISTRO` to the target distribution (e.g., `humble` for ROS 2, or a community Noetic port).
3. If the target ROS distro uses a different apt repository URL, update the repository setup section in `docker/Dockerfile` (consider a build-arg or conditional for the repo URL).

## CI

The GitHub Actions workflow (`.github/workflows/build-noetic.yaml`) automatically:

- **On PR:** Builds the Docker image to verify compilation.
- **On push to main:** Builds and pushes to GitHub Container Registry (`ghcr.io`) tagged as `noetic-patched`.
- **On tags (`v*`):** Pushes with semver-based tags.

## License

BSD — same as upstream ros_comm.
