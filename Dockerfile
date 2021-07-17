# syntax=docker/dockerfile:1
FROM python:slim
ENV PYTHONUNBUFFERED=1
WORKDIR /bot
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
