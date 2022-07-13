FROM python:3.9.7
ENV PYTHONUNBUFFERED 1
RUN apt-get update && \
    apt-get install gettext -y

WORKDIR /app

COPY ./app/requirements ./app/requirements

RUN pip install -r ./app/requirements/local.txt --no-cache-dir

COPY ./app/rudn /app

EXPOSE 8000

CMD python manage.py runserver 0.0.0.0:8000
