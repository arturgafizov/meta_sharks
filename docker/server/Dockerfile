FROM python:3.10.5
ENV PYTHONUNBUFFERED 1

ARG GID=1000
ARG UID=1000
ARG USER=ubuntu

RUN apt-get update && \
    apt-get install gettext -y && \
    groupadd -g $GID $USER && \
    useradd  -u $UID -g $GID $USER

WORKDIR /app



COPY ./app/requirements ./app/requirements

RUN pip install -r ./app/requirements/local.txt --no-cache-dir

COPY ./app/meta /app


EXPOSE 8000

COPY ./docker/server/entrypoint.sh /
RUN chmod +x /entrypoint.sh && \
    chown -R $USER:$USER /app /entrypoint.sh

ENTRYPOINT ["/entrypoint.sh"]

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]

USER $USER