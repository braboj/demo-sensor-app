# Grafana for the Render free tier.
#
# The free tier has no persistent disk, so the provisioned datasource and
# dashboards are baked into the image (they reload on every boot — the same
# files docker-compose mounts as a volume). A thin entrypoint binds Render's
# $PORT and derives the datasource connection from DATABASE_URL.
#
# Pinned to match the compose stack (docker-compose.yml grafana service).
FROM grafana/grafana:11.4.0

# COPY lands files as root; switch back to the grafana user to run.
USER root

# Bake the as-code provisioning into the default provisioning path.
COPY provisioning /etc/grafana/provisioning

COPY render-entrypoint.sh /render-entrypoint.sh
RUN chmod +x /render-entrypoint.sh

USER grafana

ENTRYPOINT ["/render-entrypoint.sh"]
