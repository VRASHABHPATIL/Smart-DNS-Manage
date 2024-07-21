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

