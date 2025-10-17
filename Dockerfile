ARG PYTHON_VERSION=3.12.0
FROM python:${PYTHON_VERSION}-slim as base

WORKDIR /app

ENV PYTHONPATH .

COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

COPY . .

RUN chmod +x ./app-start.sh
CMD ["./app-start.sh"]
