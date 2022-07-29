FROM python:3.10-slim-buster

ENV TZ=Asia/Shanghai

WORKDIR /python-docker

COPY requirements.txt requirements.txt
RUN  pip install -r requirements.txt; \
    ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone; 

COPY . .

# CMD [ "python3", "-m" , "flask", "run", "--host=0.0.0.0"]
CMD [ "opentelemetry-instrument", "--traces_exporter","console", "flask", "run", "--host=0.0.0.0"]