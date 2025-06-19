FROM python:3.13-slim-bullseye

RUN apt-get update --fix-missing \
    && apt-get install -y --no-install-recommends --no-install-suggests \
        build-essential \
        default-libmysqlclient-dev \
        pkg-config \
    || (sleep 30 && apt-get update --fix-missing && apt-get install -y --no-install-recommends --no-install-suggests build-essential default-libmysqlclient-dev pkg-config) \
    && pip install --no-cache-dir --upgrade pip \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY ./requirements.txt /app
RUN pip install --no-cache-dir -r /app/requirements.txt
COPY . /app

EXPOSE 5000

CMD ["python", "server.py"]
