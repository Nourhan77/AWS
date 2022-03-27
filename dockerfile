# syntax=docker/dockerfile:1.0.0-experimental
FROM mysql:latest as base

COPY ./conf.d/my.cnf /etc/mysql/conf.d/

FROM python:3.8.2-slim-buster
COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt
RUN pip3 install seqtolang numpy mysql-connector-python==8.0.11 translate boto3 jsons
COPY docker-compose.yml docker-compose.yml
COPY docker_entrypoint.py docker_entrypoint.py
COPY . .
ENTRYPOINT ["python3", "docker_entrypoint.py"]
