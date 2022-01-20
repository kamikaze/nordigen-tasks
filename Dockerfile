FROM python:3.10-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /code
COPY requirements.txt /code/
RUN apt-get update \
     && apt-get upgrade -y \
     && apt-get install -y libpq-dev gcc
RUN python3 -m pip install -U setuptools pip wheel
RUN python3 -m pip install -U -r requirements.txt
COPY src /code/
