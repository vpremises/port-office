ARG IMAGE_NAMESPACE=ghcr.io/vpremises
FROM ${IMAGE_NAMESPACE}/base-alpine:v3.19-p3.11.7-n18

WORKDIR /home/frappe
ENV PATH=/root/.local/pipx/venvs/frappe/bin:$PATH

RUN mkdir -p \
  /home/frappe/apps \
  /home/frappe/sites \
  /home/frappe/logs \
  /home/frappe/tools 

COPY resources/tools /home/frappe/tools

## already installed by base image
#RUN npm install -g yarn

RUN /home/frappe/tools/apps/install.sh

VOLUME [ \
  "/home/frappe/sites", \
  "/home/frappe/sites/assets", \
  "/home/frappe/logs" \
  "/home/frappe/tools" \
  ]

CMD [ \
  "/root/.local/pipx/venvs/frappe/bin/gunicorn", \
  "--chdir=/home/frappe/sites", \
  "--bind=0.0.0.0:8000", \
  "--threads=4", \
  "--workers=2", \
  "--worker-class=gthread", \
  "--worker-tmp-dir=/dev/shm", \
  "--timeout=120", \
  "--preload", \
  "frappe.app:application" \
  ]
