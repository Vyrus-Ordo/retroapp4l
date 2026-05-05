#!/bin/sh
# Called by Certbot after successful certificate renewal.
# Reloads the Nginx container gracefully without downtime.
docker compose -f /opt/retroapp4l/docker-compose.prod.yml exec nginx nginx -s reload
