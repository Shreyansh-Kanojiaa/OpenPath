#!/usr/bin/env bash
# One-time TLS bootstrap for the OpenPath production stack.
#
# Chicken-and-egg problem: nginx will not start if the certificate it references
# does not exist yet, but certbot needs nginx running to answer the ACME HTTP-01
# challenge. This script breaks the cycle: it drops in a throwaway self-signed
# cert so nginx can start, then replaces it with a real Let's Encrypt cert.
#
# Usage:
#   DOMAIN=your-domain.com EMAIL=you@example.com ./scripts/init-letsencrypt.sh
#
# Set STAGING=1 to hit Let's Encrypt's staging environment first (untrusted certs,
# but no rate limits) while you are still testing DNS. Re-run without STAGING once
# it succeeds.
set -euo pipefail

: "${DOMAIN:?Set DOMAIN, e.g. DOMAIN=example.com}"
: "${EMAIL:?Set EMAIL, e.g. EMAIL=you@example.com}"
STAGING="${STAGING:-0}"

# Both the apex and www are requested; make sure both have A records (see DEPLOYMENT.md).
DOMAIN_ARGS="-d ${DOMAIN} -d www.${DOMAIN}"
CERT_PATH="/etc/letsencrypt/live/${DOMAIN}"

COMPOSE="docker compose -f docker-compose.yml -f docker-compose.prod.yml"

echo "### Creating a temporary self-signed certificate for ${DOMAIN} ..."
$COMPOSE run --rm --entrypoint sh certbot -c "\
  mkdir -p ${CERT_PATH} && \
  openssl req -x509 -nodes -newkey rsa:2048 -days 1 \
    -keyout ${CERT_PATH}/privkey.pem \
    -out ${CERT_PATH}/fullchain.pem \
    -subj '/CN=localhost'"

echo "### Starting nginx with the temporary certificate ..."
$COMPOSE up -d frontend

echo "### Deleting the temporary certificate ..."
$COMPOSE run --rm --entrypoint sh certbot -c "rm -rf /etc/letsencrypt/live/${DOMAIN} /etc/letsencrypt/archive/${DOMAIN} /etc/letsencrypt/renewal/${DOMAIN}.conf"

echo "### Requesting the real Let's Encrypt certificate ..."
STAGING_ARG=""
if [ "${STAGING}" != "0" ]; then
  STAGING_ARG="--staging"
  echo "    (using STAGING environment; certs will be untrusted by browsers)"
fi

$COMPOSE run --rm --entrypoint certbot certbot certonly \
  --webroot -w /var/www/certbot \
  ${STAGING_ARG} \
  --email "${EMAIL}" \
  ${DOMAIN_ARGS} \
  --rsa-key-size 2048 \
  --agree-tos \
  --non-interactive

echo "### Reloading nginx with the real certificate ..."
$COMPOSE exec frontend nginx -s reload

echo "### Done. https://${DOMAIN} should now serve a trusted certificate."
