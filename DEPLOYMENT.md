# OpenPath Deployment Runbook

End-to-end guide to running OpenPath in production on a single DigitalOcean
droplet: Docker Compose behind nginx, over HTTPS, on your own domain. Follow it
top to bottom for a clean first deploy, then use the last section to redeploy
after code changes.

## What you get

- Postgres with a named volume, so data survives restarts and reboots.
- FastAPI served by gunicorn with uvicorn workers (not the dev server).
- The React app served as a static production build by nginx.
- HTTPS via Let's Encrypt, HTTP redirected to HTTPS, certificates auto-renewed.
- The backend kept off the public internet; only nginx (ports 80 and 443) is exposed.
- Everything restarts automatically after a crash or droplet reboot.

## Architecture on the droplet

```
Internet
  |  :80  -> redirect to :443 (except the ACME challenge path)
  |  :443 -> nginx (TLS termination, serves the SPA)
  v
[ frontend container: nginx ]
  |  /api/  -> proxied over the internal Docker network
  v
[ backend container: gunicorn + uvicorn workers ]  <- not published to the host
  v
[ db container: postgres ]  -> named volume postgres_data

[ certbot container ]  -> renews certs into a shared volume every 12h
```

## Prerequisites

- A DigitalOcean account.
- A domain name you control (any registrar).
- A Gemini API key (optional; the app degrades to mock responses without one).

---

## 1. Create the droplet

Recommended size: **Basic, Regular SSD, 2 GB RAM / 1 vCPU / 50 GB** (about $12/mo).
This is the smallest size that comfortably runs Postgres, the backend, and nginx
together and can run the frontend `npm run build` during image builds without the
build being killed for running out of memory.

The $6/mo 1 GB droplet can work, but the frontend build will likely be OOM-killed
unless you add swap (step 3) or build the image somewhere else. See "Cost and
durability" at the end.

Steps:
1. Create Droplets -> Ubuntu 24.04 LTS -> Basic -> Regular SSD -> 2 GB.
2. Choose a datacenter region near your users.
3. Authentication: add your SSH key (do not use password auth).
4. Create the droplet and note its public IPv4 address.

Optional but recommended: assign a **Reserved IP** (Networking -> Reserved IPs)
and point DNS at that instead of the raw droplet IP. It is free while attached and
lets you rebuild the droplet later without changing DNS.

---

## 2. Point your domain at the droplet

In your domain registrar's DNS settings, create two A records pointing at the
droplet's public IP (or Reserved IP):

| Type | Host / Name | Value            |
|------|-------------|------------------|
| A    | `@`         | droplet IP       |
| A    | `www`       | droplet IP       |

Both are needed because the TLS certificate and nginx config cover the apex domain
and `www`. DNS can take a few minutes to a few hours to propagate. Verify with:

```bash
dig +short your-domain.com
dig +short www.your-domain.com
```

Both must return your droplet IP before you request certificates in step 8.

---

## 3. First login and swap file

SSH in as root:

```bash
ssh root@your-droplet-ip
```

Add a 2 GB swap file. This is cheap insurance against out-of-memory kills during
image builds and traffic spikes, and it survives reboots:

```bash
fallocate -l 2G /swapfile
chmod 600 /swapfile
mkswap /swapfile
swapon /swapfile
echo '/swapfile none swap sw 0 0' >> /etc/fstab
```

Confirm:

```bash
free -h    # the Swap row should show 2.0Gi
```

---

## 4. Install Docker and the Compose plugin

```bash
apt-get update
apt-get install -y ca-certificates curl git
install -m 0755 -d /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg -o /etc/apt/keyrings/docker.asc
chmod a+r /etc/apt/keyrings/docker.asc
echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.asc] https://download.docker.com/linux/ubuntu $(. /etc/os-release && echo "$VERSION_CODENAME") stable" > /etc/apt/sources.list.d/docker.list
apt-get update
apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
```

Verify:

```bash
docker --version
docker compose version
```

Docker's service is enabled by default, so the daemon restarts automatically after
a reboot. Combined with the `restart: unless-stopped` policy on every service, the
whole stack comes back on its own after a reboot.

---

## 5. Clone the repository

```bash
cd /opt
git clone <your-repo-url> openpath
cd openpath
```

---

## 6. Configure secrets

Copy the template and fill in real values:

```bash
cp .env.example .env
nano .env
```

Set at minimum:

- `GEMINI_API_KEY` - your key, or leave the placeholder to run on mock responses.
- `ENVIRONMENT` - set to `production`.
- `JWT_SECRET_KEY` - generate a strong value, do not reuse a guessable one:
  ```bash
  python3 -c "import secrets; print(secrets.token_hex(32))"
  ```
- `POSTGRES_PASSWORD` - a strong password. Avoid `@` and other characters that
  would break the database connection string.
- `CORS_ORIGINS` - `https://your-domain.com,https://www.your-domain.com`.

`.env` is gitignored and stays only on the droplet. Never commit it.

---

## 7. Plug in your domain (nginx)

Edit `docker/nginx.prod.conf` and replace every `your-domain.com` with your real
domain (there are `server_name` lines and two `ssl_certificate` paths):

```bash
sed -i 's/your-domain.com/your-real-domain.com/g' docker/nginx.prod.conf
```

Double-check the result:

```bash
grep -n 'your-real-domain.com' docker/nginx.prod.conf
```

So there is no ambiguity, the domain lives in exactly two places: this file and
`CORS_ORIGINS` in `.env`.

---

## 8. First boot and TLS

Build the images and issue the certificate. The bootstrap script starts nginx with
a temporary self-signed cert, then replaces it with a real Let's Encrypt one:

```bash
# Build images and start db + backend (nginx is started by the script).
docker compose -f docker-compose.yml -f docker-compose.prod.yml build
docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d db backend

# Issue the certificate. Use STAGING=1 first if you want to test without hitting
# Let's Encrypt rate limits, then re-run without it.
DOMAIN=your-real-domain.com EMAIL=you@example.com ./scripts/init-letsencrypt.sh
```

Then bring the full stack up so the certbot renewal sidecar is running:

```bash
docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d
```

Verify:

```bash
docker compose -f docker-compose.yml -f docker-compose.prod.yml ps   # all healthy/running
curl -I https://your-real-domain.com                                 # HTTP/2 200
curl -I http://your-real-domain.com                                  # 301 to https
```

Open `https://your-real-domain.com` in a browser and confirm the padlock is valid.

---

## 9. How auto-renewal works

The `certbot` service runs `certbot renew` every 12 hours. Renewal is a no-op until
a certificate is within 30 days of expiry, then it reissues over the ACME challenge
served on port 80. The `frontend` service reloads nginx every 6 hours to pick up any
renewed certificate. Certificates are valid for 90 days, so the schedule gives about
60 days of retry headroom before expiry is a risk.

Renewal needs two things to keep working: port 80 reachable from the internet, and
the A records still pointing at the droplet. If you ever move the domain or firewall
off port 80, renewals fail silently.

Force a renewal manually if needed:

```bash
docker compose -f docker-compose.yml -f docker-compose.prod.yml run --rm --entrypoint certbot certbot renew --force-renewal
docker compose -f docker-compose.yml -f docker-compose.prod.yml exec frontend nginx -s reload
```

---

## 10. Redeploy after a code change

> Deploys are now **automatic** on every push to `main` — see section 13
> (Continuous deployment). The manual steps below remain valid as a fallback or
> for a first bring-up.

From `/opt/openpath` on the droplet:

```bash
git pull
docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d --build
```

Compose rebuilds only what changed and recreates those containers. The Postgres
volume is untouched, so data is preserved. Database schema changes are applied
automatically on backend startup (`migrate_db.py`).

Roll back by checking out the previous commit and running the same up command:

```bash
git checkout <previous-commit-sha>
docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d --build
```

---

## 11. Operations cheat sheet

Set an alias so you do not retype the compose flags:

```bash
alias dc='docker compose -f docker-compose.yml -f docker-compose.prod.yml'
```

- Logs: `dc logs -f backend` (or `frontend`, `db`, `certbot`).
- Status: `dc ps`.
- Restart one service: `dc restart backend`.
- Stop everything: `dc down` (the Postgres volume survives).
- Database backup:
  ```bash
  dc exec db pg_dump -U openpath openpath_db > backup-$(date +%F).sql
  ```
- Database restore:
  ```bash
  cat backup-YYYY-MM-DD.sql | dc exec -T db psql -U openpath -d openpath_db
  ```

Schedule the backup with cron for durability, for example daily at 03:00:

```bash
echo '0 3 * * * cd /opt/openpath && docker compose -f docker-compose.yml -f docker-compose.prod.yml exec -T db pg_dump -U openpath openpath_db > /opt/openpath/backup-$(date +\%F).sql' | crontab -
```

---

## 12. Firewall (recommended)

Restrict inbound traffic to SSH and web:

```bash
ufw allow OpenSSH
ufw allow 80/tcp
ufw allow 443/tcp
ufw enable
```

Keep port 80 open; certificate renewal depends on it.

---

## 13. Continuous deployment (CI/CD)

Pushing to `main` deploys to this droplet automatically. The pipeline lives in
`.github/workflows/ci.yml`:

1. **Test** — backend `pytest` and a frontend `npm run build` (these also run on PRs).
2. **Build & push** — builds the backend and frontend Docker images and pushes them
   to GitHub Container Registry (GHCR), each tagged with the commit SHA and `latest`.
3. **Deploy** — SSHes into this droplet, fast-forwards `/opt/openpath` to the new
   commit, pulls the two images by SHA, and runs `docker compose … up -d --no-build`.
   A final step polls `https://open-path.dev` until it returns 200.

Only a green test run reaches the build and deploy stages, so broken code never ships.
The Postgres volume is never touched, and schema changes still auto-apply on backend
startup (`migrate_db.py`).

### One-time setup

**a. A deploy SSH key.** On your laptop, create a keypair dedicated to CI (no
passphrase) and authorise it on the droplet:

```bash
ssh-keygen -t ed25519 -f ~/.ssh/openpath_deploy -N "" -C "github-actions-deploy"
ssh-copy-id -i ~/.ssh/openpath_deploy.pub root@<droplet-ip>
# (or append ~/.ssh/openpath_deploy.pub to /root/.ssh/authorized_keys on the droplet)
```

**b. GitHub repository secrets** — Settings → Secrets and variables → Actions:

| Secret | Value |
|--------|-------|
| `DEPLOY_HOST` | droplet public IP (e.g. `168.144.22.61`) or `open-path.dev` |
| `DEPLOY_USER` | `root` (or your deploy user) |
| `DEPLOY_SSH_KEY` | the **private** key: `cat ~/.ssh/openpath_deploy` |
| `GOOGLE_CLIENT_ID` | your Google OAuth client ID (baked into the frontend bundle) |

The droplet authenticates to GHCR during the deploy using the workflow's own
`GITHUB_TOKEN`, so no registry password is stored on the server.

**c. Droplet prerequisites** (already true if you followed sections 1–8):

- `/opt/openpath` is a clean checkout of `main`. The deploy fast-forwards it and
  **preserves** your local edit of `docker/nginx.prod.conf` (the real domain). Keep
  any other server-only settings in `.env` (gitignored), not in tracked files.
- Docker + the compose plugin are installed and `.env` is present.

### First automated deploy

Push a commit to `main` and watch it under the repo's **Actions** tab. The first run
switches the droplet from locally-built images to GHCR images; every run after that
just pulls the new tag.

### Rollback

Fastest — revert the bad commit and push; CI redeploys the previous good state:

```bash
git revert <bad-sha> && git push
```

Or pin the droplet to an older image by hand (every pushed commit is a tag):

```bash
cd /opt/openpath
IMAGE_TAG=<older-sha> docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d
```

### If a deploy fails

- **Tests red** → nothing was built or deployed; fix and push again.
- **`git merge --ff-only` aborts** → `/opt/openpath` has diverging local commits or a
  conflicting edit to a tracked file. SSH in, reconcile, re-run the job.
- **Smoke check fails** → containers came up but the site isn't returning 200. Check
  `docker compose … logs backend frontend` on the droplet and roll back.

---

## Cost and durability

- **Droplet**: the only guaranteed recurring cost. On DigitalOcean credits it is
  free; when credits end, the 2 GB droplet is about $12/mo, or $6/mo for 1 GB with
  swap. Nothing in this stack requires a paid managed service.
- **Postgres**: runs in a container with a named volume, so it costs nothing beyond
  the droplet. The trade-off is that backups are your responsibility. Use the
  `pg_dump` cron job above. There is no managed database bill.
- **Let's Encrypt**: free, and auto-renews. No cost, but see section 9 for what
  keeps renewal healthy.
- **Gemini API**: billed per use above Google's free tier. The app degrades to mock
  responses if the key is unset or the API errors, so it never hard-fails on cost.
- **Domain**: renews annually at your registrar; the one external cost this repo
  cannot avoid.
- **Things that silently cost money on DigitalOcean and are NOT required here**:
  droplet snapshots, managed databases, load balancers, and additional Reserved IPs
  beyond the one attached to your droplet. Do not enable them unless you decide to.

## Local development is unchanged

None of the above affects local work:

```bash
docker compose up --build          # full stack locally over plain HTTP
```

or the non-Docker workflow from the project README (backend via uvicorn, frontend
via `npm run dev`). The dev compose overlay (`docker-compose.override.yml`) loads
automatically and never touches the production overlay.
