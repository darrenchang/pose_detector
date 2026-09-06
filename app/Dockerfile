FROM python:3.12.12-slim-trixie

RUN apt update && \
    apt install -y \
    gcc \
    make \
    git && \
    # Cleanup apt cache \
    apt autoremove --purge -y && \
    apt clean && \
    rm -rf /var/lib/apt/lists/*;

WORKDIR /app
COPY ./src ./
# Download python dependency
RUN python -m venv venv && \
    . venv/bin/activate && \
    python -m pip install setuptools>=80.9.0 && \
    python -m pip install .;

ENTRYPOINT ["/bin/sh", "-c", "entrypoint.sh"]
