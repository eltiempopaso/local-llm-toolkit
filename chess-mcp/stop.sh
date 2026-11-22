#!/bin/sh
set -eu

container_name=chess-mcp

if running=$(docker container inspect --format '{{.State.Running}}' "$container_name"); then
    if [ "$running" = "true" ]; then
        docker stop "$container_name"
    else
        printf "Container %s is already stopped.\n" "$container_name"
    fi
else
    printf "Could not inspect container %s; check that Docker is available.\n" "$container_name" >&2
    exit 1
fi
