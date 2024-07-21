# Smart DNS Manager

Smart DNS Manager is a project aimed at enhancing DNS performance on a local machine using Docker and Unbound DNS server configuration. It includes scripts to monitor and adjust DNS cache settings based on cache hit rates.

## Prerequisites

Before you begin, ensure you have met the following requirements:
- You are using an Ubuntu machine.
- You have installed the following dependencies:
  - `apt-transport-https`
  - `curl`
  - `docker-ce`

## Installation

1. Update your package list and upgrade your system:
    ```bash
    sudo apt update
    sudo apt upgrade
    ```

2. Install necessary dependencies:
    ```bash
    sudo apt install apt-transport-https ca-certificates curl software-properties-common
    ```

3. Add Docker’s official GPG key:
    ```bash
    curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg
    ```

4. Add the Docker APT repository:
    ```bash
    echo "deb [arch=amd64 signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
    ```

5. Update your package list again:
    ```bash
    sudo apt update
    ```

6. Install Docker:
    ```bash
    sudo apt install docker-ce
    ```

7. Verify Docker installation:
    ```bash
    sudo systemctl status docker
    sudo docker run hello-world
    ```

8. Run the DNS performance monitoring tool using Docker:
    ```bash
    sudo docker run --rm -it --net=host --cap-add NET_RAW --cap-add NET_ADMIN --name dnsmonitor ghcr.io/mosajjal/dnsmonster:latest --devName lo --stdoutOutputType=1 > /path/to/dns.out
    ```

## Scripts

### `catch-hit.py`

This script is responsible for analyzing DNS cache hit rates. Ensure you have Python installed on your machine to execute this script.

### `memoryadjust.sh`

This bash script adjusts the DNS cache size based on the cache hit rate. The script reads the output of `catch-hit.py` and modifies the Unbound DNS server configuration accordingly.

```bash
#!/bin/bash

cache_hit_rate=$(python3 catch-hit.py | grep "Cache Hit Rate" | awk '{print $4}')

if (( $(echo "$cache_hit_rate < 0.5" | bc -l) )); then
    sudo sed -i '/^server:/,/^forward-zone:/ s/^    cache-min-ttl:.*/    cache-min-ttl: 3500/' /etc/unbound/unbound.conf
    echo "Cache size decreased."
elif (( $(echo "$cache_hit_rate > 0.8" | bc -l) )); then
    sudo sed -i '/^server:/,/^forward-zone:/ s/^    cache-man-ttl:.*/    cache-min-ttl: 90000/' /etc/unbound/unbound.conf
    echo "Cache size increased."
else
    echo "Cache size optimal."
fi
