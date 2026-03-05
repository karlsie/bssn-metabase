## Deploy Metabase

Reference: https://www.metabase.com/docs/latest/installation-and-operation/running-metabase-as-service

## Create an unprivileged user to run Metabase

```bash
# Create a "metabase" group
sudo groupadd -r metabase

# Create a "metabase" user, with a home directory at /home/metabase
sudo useradd -m -r -s /bin/false -g metabase metabase
```

## Download Metabase JAR

```bash
sudo -u metabase wget -O /home/metabase/metabase.jar https://downloads.metabase.com/enterprise/latest/metabase.jar
```

## Set environment variables

Environment variables let you configure and customize your Metabase instance.

## Create Metabase service

Every service needs a configuration file that tells systemd how to manage it and what capabilities it supports. 

```bash
sudo cat << EOF > /etc/systemd/system/metabase.service
[Unit]
Description=Metabase server
After=network.target

[Service]
WorkingDirectory=~
ExecStart=/usr/bin/java --add-opens java.base/java.nio=ALL-UNNAMED -jar /home/metabase/metabase.jar
EnvironmentFile=/home/metabase/.env
User=metabase
Type=simple
SuccessExitStatus=143
TimeoutStopSec=120
Restart=always

[Install]
WantedBy=multi-user.target
EOF
```

The best part of setting up Metabase as a systemd service is that it will start up at every system boot, and get restarted automatically if it crashes. We only have a few more quick steps to finish registering our service and having Metabase up and running.

## Ensure database is ready

If you’re running a PostgreSQL application database, make sure you’ve created a database for Metabase, as well as a user that can access that database.
These values should match what you’ve set in your Metabase config for the `MB_DB_TYPE`, `MB_DB_DBNAME`, `MB_DB_USER`, and `MB_DB_PASS` environment variables. 
If you don’t have your database properly configured, Metabase won’t be able to start.

## Installing nginx

```bash
sudo apt update
sudo apt install nginx
```

## Configure nginx

enable nginx to start at boot
```bash
sudo systemctl enable nginx
```

create a nginx config file
```bash
sudo cat << EOF > /etc/nginx/sites-enabled/default/nginx.conf
server {
  listen 80;
  listen [::]:80;
  server_name _;
  location / {
    proxy_pass http://127.0.0.1:3000;
  }
}
EOF
```

restart nginx
```bash
sudo systemctl restart nginx
```

## Register Metabase service

Now, it’s time to register our Metabase service with systemd so it will start up at system boot:

```bash
sudo systemctl daemon-reload
sudo systemctl start metabase.service
sudo systemctl status metabase.service
```

Once we are OK here, enable the service to start up during boot:

```bash
sudo systemctl enable metabase.service
```

## Start, Stop and Restart Metabase

Now, whenever you need to restart, stop, or start Metabase, all you need to do is:

```bash
sudo systemctl restart metabase.service
sudo systemctl stop metabase.service
sudo systemctl start metabase.service
```

To print the live Metabase service logs, you can run:

```bash
journalctl -fxeu metabase.service
```
