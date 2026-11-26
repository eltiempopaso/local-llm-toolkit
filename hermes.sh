#!/bin/bash
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
HERMES_DIR="$SCRIPT_DIR/hermes"

cd "$HERMES_DIR"

case "${1:-help}" in
    start)
        echo "Starting Hermes..."
        docker compose up -d
        ;;
    stop)
        echo "Stopping Hermes..."
        docker compose down
        ;;
    restart)
        echo "Restarting Hermes..."
        docker compose restart
        ;;
    pull|update)
        echo "Updating Hermes..."
        docker compose pull
        docker compose up -d
        ;;
    status)
        docker compose ps
        ;;
    logs)
        docker compose logs -f
        ;;
    build)
        docker compose build
        ;;
    shell)
        docker exec -it hermes bash
        ;;
    backup)
        mkdir -p backups
        DATE=$(date +%Y-%m-%d_%H-%M-%S)
        tar czf "backups/hermes-$DATE.tar.gz" \
            --exclude='./backups' .
        echo "Backup created: backups/hermes-$DATE.tar.gz"
        ;;
    help|*)
        echo "Hermes Docker Manager"
        echo ""
        echo "Usage: ./hermes.sh <command>"
        echo ""
        echo "Commands:"
        echo "  start       Start Hermes"
        echo "  stop        Stop Hermes"
        echo "  restart     Restart Hermes"
        echo "  status      Show container status"
        echo "  logs        Follow container logs"
        echo "  pull        Download latest image"
        echo "  update      Update and restart Hermes"
        echo "  build       Build image"
        echo "  shell       Enter container shell"
        echo "  backup      Create backup"
        echo "  help        Show this help"
        ;;
esac
