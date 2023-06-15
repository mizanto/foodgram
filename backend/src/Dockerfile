FROM python:3.9-slim
RUN mkdir /app
COPY requirements.txt /app
RUN apt-get update \
    && apt-get -y install libpq-dev gcc \
    && pip3 install --upgrade pip \
    && pip3 install psycopg2 \
    && pip install --upgrade urllib3 chardet \
    && pip3 install -r /app/requirements.txt --no-cache-dir \
    && apt-get -y autoremove \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*
COPY . /app
COPY ../../data /data
WORKDIR /app
CMD ["gunicorn", "foodgram.wsgi:application", "--bind", "0.0.0.0:8080"]
