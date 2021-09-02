FROM python:3.8-alpine

RUN pip install flask pymongo flask-cors requests urllib3 python-dateutil bson

COPY app.py /opt/app.py

EXPOSE 5000

ENTRYPOINT FLASK_APP=/opt/app.py flask run --host=0.0.0.0
