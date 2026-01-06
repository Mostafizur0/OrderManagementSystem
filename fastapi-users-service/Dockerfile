FROM python:3.11-slim-bookworm AS build-env

RUN apt-get update && \
  apt-get install -y libpq-dev gcc && \
  apt-get clean && \
  rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY . /app

RUN python -m venv /venv && \
  /venv/bin/pip install --no-cache-dir -r requirements.txt


FROM python:3.11-slim-bookworm

RUN apt-get update && apt-get install -y libpq5 && \
  apt-get clean && \
  rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY --from=build-env /app /app
COPY --from=build-env /venv /venv
RUN chmod +x /app/start.sh

ENV PATH="/venv/bin:$PATH"

