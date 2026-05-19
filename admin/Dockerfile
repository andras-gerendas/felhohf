FROM python:alpine3.21 AS build

COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt

FROM build

WORKDIR /app

COPY admin admin
COPY admin-config.ini admin-config.ini

ENV FLASK_CONFIG_PATH="/app/admin-config.ini"

CMD [ "python3", "-m" , "flask", "--app", "admin", "run", "--host=0.0.0.0"]