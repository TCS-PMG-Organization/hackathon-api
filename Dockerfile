FROM python:3.8-alpine

RUN pip uninstall pymongo bson

RUN pip install flask bson pymongo flask-cors requests urllib3 python-dateutil 

COPY app.py /opt/app.py

EXPOSE 5000

ENTRYPOINT FLASK_APP=/opt/app.py flask run --host=0.0.0.0
