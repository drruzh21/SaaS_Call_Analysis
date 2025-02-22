FROM ghcr.io/br3ndonland/inboard:fastapi-0.68-python3.11

WORKDIR /app/
COPY ./app/ /app/

ENV HATCH_ENV_TYPE_VIRTUAL_PATH=.venv
RUN hatch env prune && hatch env create production
RUN pip install --upgrade pip
RUN pip install --upgrade setuptools
RUN pip install psycopg2-binary

# PostgreSQL environment variables
ENV POSTGRES_SERVER=${POSTGRES_SERVER:-db}
ENV POSTGRES_USER=${POSTGRES_USER}
ENV POSTGRES_PASSWORD=${POSTGRES_PASSWORD}
ENV POSTGRES_DB=${POSTGRES_DB:-app}
ENV POSTGRES_PORT=${POSTGRES_PORT:-5432}

# Make prestart.sh executable
RUN chmod +x /app/prestart.sh

# /start Project-specific dependencies
# RUN apt-get update && apt-get install -y --no-install-recommends \
#  && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*	
# WORKDIR /app/
# /end Project-specific dependencies

# For development, Jupyter remote kernel
# Using inside the container:
# jupyter lab --ip=0.0.0.0 --allow-root --NotebookApp.custom_display_url=http://127.0.0.1:8888

RUN bash -c "pip install argon2_cffi"

ARG BACKEND_APP_MODULE=app.main:app
ARG BACKEND_PRE_START_PATH=/app/prestart.sh
ARG BACKEND_PROCESS_MANAGER=gunicorn
ARG BACKEND_WITH_RELOAD=false
ENV APP_MODULE=${BACKEND_APP_MODULE} \
    PRE_START_PATH=${BACKEND_PRE_START_PATH} \
    PROCESS_MANAGER=${BACKEND_PROCESS_MANAGER} \
    WITH_RELOAD=${BACKEND_WITH_RELOAD}
