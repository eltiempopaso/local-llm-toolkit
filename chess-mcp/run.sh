#!/bin/sh
set -eu

container_name=chess-mcp
network_name=searxng_default

if docker container inspect "$container_name" >/dev/null 2>&1; then
  running=$(docker container inspect --format '{{.State.Running}}' "$container_name")
  if [ "$running" = "true" ]; then
    if ! docker network inspect "$network_name" >/dev/null 2>&1; then
      printf "No existe la red Docker %s; no se puede conectar %s.\n" "$network_name" "$container_name" >&2
      exit 1
    fi

    network_connection=$(docker container inspect \
      --format '{{if index .NetworkSettings.Networks "searxng_default"}}connected{{end}}' \
      "$container_name")
    if [ "$network_connection" != "connected" ]; then
      docker network connect "$network_name" "$container_name"
    fi

    printf "El contenedor %s ya está en ejecución.\n" "$container_name"
    exit 0
  fi

  docker rm "$container_name"
fi

if ! docker network inspect "$network_name" >/dev/null 2>&1; then
  printf "No existe la red Docker %s; inicia primero el stack que la crea.\n" "$network_name" >&2
  exit 1
fi

docker run -d \
  --name "$container_name" \
  --network "$network_name" \
  --restart unless-stopped \
  -p 8000:8000 \
  chess-mcp