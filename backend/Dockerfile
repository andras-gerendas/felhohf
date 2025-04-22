FROM python:alpine3.21

WORKDIR /app

COPY app.py app.py
COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt

CMD [ "python3", "-m" , "flask", "run", "--host=0.0.0.0"]