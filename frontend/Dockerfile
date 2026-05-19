FROM python:alpine3.21 AS build

COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt

FROM build

WORKDIR /app

COPY frontend frontend
COPY frontend-config.ini frontend-config.ini

ENV FLASK_CONFIG_PATH="/app/frontend-config.ini"

CMD [ "python3", "-m" , "flask", "--app", "frontend", "run", "--host=0.0.0.0"]