# Deployment on AWS EC2

## Overview
This guide provides step-by-step instructions to deploy the Webhook Delivery Service on an AWS EC2 instance, set up PostgreSQL and Redis, connect the application to a custom domain, and configure Nginx for reverse proxy.

---

## Prerequisites
- An AWS account.
- A registered domain name.
- Basic knowledge of SSH and Linux commands.
- AWS CLI installed and configured on your local machine.

---

## Step 1: Launch an EC2 Instance
1. Log in to your AWS Management Console.
2. Navigate to the EC2 Dashboard and click **Launch Instance**.
3. Configure the instance:
   - **AMI**: Choose Ubuntu 22.04 LTS.
   - **Instance Type**: Select `t2.micro` (free tier eligible).
   - **Key Pair**: Create or select an existing key pair for SSH access.
   - **Security Group**: Allow the following ports:
     - `22` (SSH)
     - `80` (HTTP)
     - `443` (HTTPS)
     - `5432` (PostgreSQL)
     - `6379` (Redis)
4. Launch the instance and note the public IP address.

---

## Step 2: Connect to the Instance via SSH
1. Open a terminal and run:
   ```bash
   ssh -i /path/to/your-key.pem ubuntu@<EC2_PUBLIC_IP>
   ```
2. Update the system:
   ```bash
   sudo apt update && sudo apt upgrade -y
   ```

---

## Step 3: Install Dependencies
1. Install Docker and Docker Compose:
   ```bash
   sudo apt install -y docker.io docker-compose
   ```
2. Install PostgreSQL:
   ```bash
   sudo apt install -y postgresql postgresql-contrib
   ```
3. Install Redis:
   ```bash
   sudo apt install -y redis-server
   ```
4. Install Nginx:
   ```bash
   sudo apt install -y nginx
   ```

---

## Step 4: Configure PostgreSQL
1. Open the PostgreSQL configuration file:
   ```bash
   sudo nano /etc/postgresql/14/main/pg_hba.conf
   ```
2. Update the file to allow connections from the EC2 instance's private IP.
3. Restart PostgreSQL:
   ```bash
   sudo systemctl restart postgresql
   ```
4. Create a database and user:
   ```bash
   sudo -u postgres psql
   CREATE DATABASE webhooks;
   CREATE USER webhook_user WITH PASSWORD 'your_password';
   GRANT ALL PRIVILEGES ON DATABASE webhooks TO webhook_user;
   \q
   ```

---

## Step 5: Configure Redis
1. Open the Redis configuration file:
   ```bash
   sudo nano /etc/redis/redis.conf
   ```
2. Update the `bind` directive to allow connections from the EC2 instance's private IP.
3. Restart Redis:
   ```bash
   sudo systemctl restart redis
   ```

---

## Step 6: Deploy the Application
1. Clone the repository:
   ```bash
   git clone https://github.com/lakshya324/Webhook-Delivery-Service.git
   cd Webhook-Delivery-Service
   ```
2. Create a `.env` file with the following content:
   ```env
   DATABASE_URL=postgresql://webhook_user:your_password@localhost:5432/webhooks
   REDIS_URL=redis://localhost:6379/0
   SECRET_KEY=your-secret-key
   DEBUG=False
   ALLOWED_HOSTS=<your-domain>,<EC2_PUBLIC_IP>
   ```
3. Build and start the application using Docker Compose:
   ```bash
   sudo docker-compose up --build -d
   ```

---

## Step 7: Configure Nginx
1. Create a new Nginx configuration file:
   ```bash
   sudo nano /etc/nginx/sites-available/webhook_service
   ```
2. Add the following content:
   ```nginx
   server {
       listen 80;
       server_name <your-domain>;

       location / {
           proxy_pass http://localhost:8000;
           proxy_set_header Host $host;
           proxy_set_header X-Real-IP $remote_addr;
           proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
       }
   }
   ```
3. Enable the configuration:
   ```bash
   sudo ln -s /etc/nginx/sites-available/webhook_service /etc/nginx/sites-enabled/
   sudo nginx -t
   sudo systemctl restart nginx
   ```

---

## Step 8: Connect the Domain
1. Update your domain's DNS settings to point to the EC2 instance's public IP.
2. Verify the domain is resolving correctly by visiting `http://<your-domain>`.

---

## Step 9: Secure the Application with SSL
1. Install Certbot:
   ```bash
   sudo apt install -y certbot python3-certbot-nginx
   ```
2. Obtain an SSL certificate:
   ```bash
   sudo certbot --nginx -d <your-domain>
   ```
3. Verify the SSL setup by visiting `https://<your-domain>`.

---

## Maintenance
- Use `sudo docker-compose logs` to view application logs.
- Use `sudo systemctl status` to check the status of PostgreSQL, Redis, and Nginx.

---

**Your application is now live and accessible via your custom domain!**