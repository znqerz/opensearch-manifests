
FROM python:3.10-slim

COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt; \
    ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone;

RUN set -eux; \
	apt-get update; \
	apt-get upgrade -y --no-install-recommends; \
	rm -rf /var/lib/apt/lists/*; \
    adduser --uid 1000 worker


USER worker

ENV HOME_PATH /home/worker

WORKDIR ${HOME_PATH}

COPY --chown=worker:worker . .

CMD [ "python3", "demo.py"]