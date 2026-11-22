#!/bin/sh
set -eu

container_name=chess-mcp

if running=$(docker container inspect --format '{{.State.Running}}' "$container_name"); then
    if [ "$running" = "true" ]; then
        docker stop "$container_name"
    else
        printf "El contenedor %s ya está detenido.\n" "$container_name"
    fi
else
    printf "No se pudo consultar el contenedor %s; comprueba que Docker esté disponible.\n" "$container_name" >&2
    exit 1
fi
