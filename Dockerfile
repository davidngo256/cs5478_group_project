# A Linux environment for the study, for a machine where the native install is not an option (macOS, Windows):
# Ubuntu 24.04, the C++ compiler PyBullet needs, uv and the locked packages. See "Docker" in README.md.
FROM ubuntu:24.04

RUN apt-get update \
    && apt-get install -y --no-install-recommends build-essential ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

COPY --from=ghcr.io/astral-sh/uv:0.13.1 /uv /usr/local/bin/uv

WORKDIR /repo
COPY pyproject.toml uv.lock .python-version ./
RUN uv sync --locked --no-cache
# The environment is complete, so `uv run` uses it as it is and needs no network.
ENV UV_NO_SYNC=1

COPY . .

CMD ["uv", "run", "pytest"]
