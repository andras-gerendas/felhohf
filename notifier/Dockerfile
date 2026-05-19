FROM python:alpine3.21 AS build

COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt

FROM build

WORKDIR /app

COPY notifier notifier
COPY schema.sql schema.sql

CMD [ "python3", "-m" , "flask", "--app", "notifier", "run", "--host=0.0.0.0"]