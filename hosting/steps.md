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

# Step 5: Configure Cloudflare Settings
1. In Cloudflare dashboard, go to SSL/TLS:
   Set SSL/TLS encryption mode to "Full (strict)"
   This ensures end-to-end encryption
2. Enable security features (recommended):
    - Under "Security" → "WAF" → Enable Web Application Firewall
    - Under "Speed" → "Optimization" → Enable Auto Minify for CSS, HTML, JS

# Step 6: Firewall Configuration

```bash
# Allow SSH, HTTP, and HTTPS
sudo ufw allow ssh
sudo ufw allow 'Nginx Full'
sudo ufw enable

# Block direct access to Gradio port (optional security measure)
sudo ufw deny 7860
```
# Verification Steps

Test your domain: Visit https://lusidlogix.com in a browser
Check SSL: Look for the padlock icon in the address bar
Test Gradio functionality: Ensure your app works as expected
Check logs if issues occur:

Nginx: sudo tail -f /var/log/nginx/error.log







```bash
root@ubuntu-s-1vcpu-1gb-blr1-01:~/demoprofile# sudo certbot --nginx -d lusidlogix.com -d www.lusidlogix.com
Saving debug log to /var/log/letsencrypt/letsencrypt.log
Enter email address or hit Enter to skip.
 (Enter 'c' to cancel): buildteam.duo@gmail.com

- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
Please read the Terms of Service at:
https://letsencrypt.org/documents/LE-SA-v1.5-February-24-2025.pdf
You must agree in order to register with the ACME server. Do you agree?
- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
(Y)es/(N)o: Y

- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
Would you be willing, once your first certificate is successfully issued, to
share your email address with the Electronic Frontier Foundation, a founding
partner of the Let's Encrypt project and the non-profit organization that
develops Certbot? We'd like to send you email about our work encrypting the web,
EFF news, campaigns, and ways to support digital freedom.
- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
(Y)es/(N)o: Y
Account registered.
Requesting a certificate for lusidlogix.com and www.lusidlogix.com

Successfully received certificate.
Certificate is saved at: /etc/letsencrypt/live/lusidlogix.com/fullchain.pem
Key is saved at:         /etc/letsencrypt/live/lusidlogix.com/privkey.pem
This certificate expires on 2025-12-03.
These files will be updated when the certificate renews.
Certbot has set up a scheduled task to automatically renew this certificate in the background.

Deploying certificate
Successfully deployed certificate for lusidlogix.com to /etc/nginx/sites-enabled/lusidlogix.com
Successfully deployed certificate for www.lusidlogix.com to /etc/nginx/sites-enabled/lusidlogix.com
Congratulations! You have successfully enabled HTTPS on https://lusidlogix.com and https://www.lusidlogix.com

- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
If you like Certbot, please consider supporting our work by:
 * Donating to ISRG / Let's Encrypt:   https://letsencrypt.org/donate
 * Donating to EFF:                    https://eff.org/donate-le
- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
```
