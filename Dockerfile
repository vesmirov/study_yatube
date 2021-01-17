FROM python:3.8-slim

VOLUME /var/lib/django-db
ENV DATABASE_URL sqlite:////var/lib/django-db/db.sqlite

RUN apt-get update && \
    apt-get install -y --no-install-recommends build-essential && \
    rm -rf /var/lib/apt/lists/*

RUN pip install uwsgi==2.0.18
RUN mkdir /code
ADD requirements.txt /code
RUN pip install --no-cache-dir -r /code/requirements.txt

COPY . /code
WORKDIR /code
CMD ./manage.py migrate && \
    ./manage.py collectstatic --no-input && \
    uwsgi --http :8000 --wsgi-file /code/yatube/wsgi.py --master --process 4 --threads 2