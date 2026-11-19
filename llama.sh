#!/bin/bash

# Uso: ./llama.sh [config] [action]
# Ejemplo: ./llama.sh nvidia-rtx3060-qwen3-14b-q4 start

# Verificar que se pasen 0 o 2 argumentos
if [ "$#" -eq 0 ]; then
  echo "Configuraciones válidas:"
    for file in $( dirname "${BASH_SOURCE[0]}" )/llama.cpp/*.yaml; do
        echo "$(basename "$file" .yaml)"
    done
  exit 0
elif [ "$#" -ne 2 ]; then
  echo "Uso: $0 <nombre_configuracion> <accion>"
  echo "Acciones válidas: start, stop, status, logs"
  exit 1
fi

CONFIG_NAME="$1"
ACTION="$2"

# Construir la ruta del archivo YAML
YAML_PATH="$( dirname "${BASH_SOURCE[0]}" )/llama.cpp/"
YAML_FILE="${YAML_PATH}${CONFIG_NAME}.yaml"

# Verificar que el archivo YAML exista
if [ ! -f "$YAML_FILE" ]; then
  echo "Error: El archivo $YAML_FILE no existe."
  exit 1
fi

# Ejecutar según la acción
case "$ACTION" in
  start)
    echo "Iniciando configuración: $CONFIG_NAME"
    docker compose -f "$YAML_FILE" up -d
    ;;
  stop)
    echo "Deteniendo configuración: $CONFIG_NAME"
    docker compose -f "$YAML_FILE" down
    ;;
  status)
    echo "Estado de la configuración: $CONFIG_NAME"
    docker compose -f "$YAML_FILE" ps
    ;;
  logs)
    echo "Mostrando logs de la configuración: $CONFIG_NAME"
    docker compose -f "$YAML_FILE" logs -f
    ;;
  *)
    echo "Acción desconocida: $ACTION. Use: start, stop, status, logs."
    exit 1
    ;;
esac

exit 0