FROM python:3.10-buster as compile

WORKDIR /usr/src/app

RUN python -m venv --copies /usr/src/app/.venv

COPY ./pyproject.toml ./poetry.lock /usr/src/app/

ENV PATH=/usr/src/app/.venv/bin:$PATH \
    POETRY_VIRTUALENVS_CREATE=false

RUN python -m pip install --no-compile --upgrade pip wheel poetry
RUN poetry install --no-dev --no-root -n && \
    python -m compileall .venv
RUN python -m pip uninstall --yes --no-input poetry virtualenv

# Stuff to help debug
# RUN apt-get update && apt-get install -y vim wget curl dnsutils && \
#     echo "alias ll='ls -alh'" >> /root/.bashrc

###############################################################################
FROM python:3.10-slim-buster
ARG  APP_USERID=9000

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PATH="/usr/src/app/.venv/bin:$PATH" \
    IPYTHONDIR=/tmp

LABEL maintainer="Tim McFadden <mtik00@users.noreply.github.com>"
LABEL app="noogle"

RUN apt-get update && apt-get upgrade -y \
    && apt-get install -y tini \
    && rm -rf /var/lib/apt/lists/*

RUN useradd --uid ${APP_USERID} --no-log-init --create-home --shell /bin/bash  noogle-user \
    && echo "alias ll='ls -alh'" >> /home/noogle-user/.bashrc \
    && echo "alias noogle='python -m noogle'" >> /home/noogle-user/.bashrc \
    && echo 'PATH="/usr/src/app/.venv/bin:$PATH"' >> /home/noogle-user/.bashrc

WORKDIR /usr/src/app

RUN chown noogle-user:noogle-user /usr/src/app
COPY --from=compile --chown=noogle-user:noogle-user /usr/src/app/.venv .venv
COPY --chown=noogle-user:noogle-user ./noogle ./noogle

ENTRYPOINT [ "/usr/bin/tini", "--", "python", "-m", "noogle" ]
CMD [ "--help" ]

# Stuff to help debug (as long as you didn't remove pip above)
# RUN python -m pip install ipdb

USER noogle-user
