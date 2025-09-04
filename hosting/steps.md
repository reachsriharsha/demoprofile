# Step 1. Run docker image

# Step 2: Install Nginx on Host

```bash
sudo apt install nginx -y
sudo systemctl start nginx
sudo systemctl enable nginx
```

# Step 3: Configure Nginx (Updated for Docker)


```bash
sudo nano /etc/nginx/sites-available/lusidlogix.com


server {
    listen 80;
    server_name lusidlogix.com www.lusidlogix.com;

    location / {
        proxy_pass http://127.0.0.1:7860;  # Your Docker container
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_buffering off;
        
        # WebSocket support for Gradio
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
}
```

Enable the site:


```bash
sudo ln -s /etc/nginx/sites-available/lusidlogix.com /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

# Step 4: Set Up HTTPS with Let's Encrypt (Same as Before)

```bash
sudo apt install snapd
sudo snap install core; sudo snap refresh core
sudo snap install --classic certbot
sudo ln -s /snap/bin/certbot /usr/bin/certbot

sudo certbot --nginx -d lusidlogix.com -d www.lusidlogix.com
Enter your email address
Agree to terms of service
Choose whether to share email with EFF
Certbot will automatically update your Nginx configuration


#Test auto-renewal:

sudo certbot renew --dry-run
```


# Alternative Approach: HTTPS Inside Docker Container

in docker-compose.yaml

```yaml
version: '3.8'
services:
  gradio-app:
    build: .
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - /etc/letsencrypt:/etc/letsencrypt:ro
    restart: unless-stopped
```