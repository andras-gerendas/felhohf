FROM python:alpine3.21 AS build

RUN apk update && apk add --no-cache --update tesseract-ocr tesseract-ocr-data-eng tesseract-ocr-data-deu
COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt

FROM build

WORKDIR /app

COPY app.py app.py

CMD [ "python3", "-m" , "flask", "run", "--host=0.0.0.0"]
