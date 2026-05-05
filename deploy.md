# 1. Instalar Docker
curl -fsSL https://get.docker.com | sh
usermod -aG docker $USER && newgrp docker

# 2. Nginx + Certbot (para emitir o cert antes do compose subir)
apt install nginx -y
snap install certbot --classic

# 3. Emitir certificado (porta 80 deve estar livre)
certbot certonly --standalone -d retroapp4l.privo.app.br
systemctl stop nginx && systemctl disable nginx  # Nginx do host não será mais usado

# 4. Clonar repositório
git clone https://github.com/diniz-prj/retroapp4l.git /opt/retroapp4l
cd /opt/retroapp4l

# 5. Criar .env.prod com os secrets reais
cp backend/.env.prod.example backend/.env.prod
nano backend/.env.prod  # preencher DJANGO_SECRET_KEY e POSTGRES_PASSWORD

# 6. Instalar o hook de renovação SSL
cp scripts/ssl-renew-hook.sh /etc/letsencrypt/renewal-hooks/deploy/
chmod +x /etc/letsencrypt/renewal-hooks/deploy/ssl-renew-hook.sh

# 7. Build e start
docker compose -f docker-compose.prod.yml up -d --build

# 8. Verificar
docker compose -f docker-compose.prod.yml logs -f
curl -I https://retroapp4l.privo.app.br/api/