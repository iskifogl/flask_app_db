FROM python:3-alpine

WORKDIR /app

COPY requirements.txt .

RUN pip install -r requirements.txt

COPY . ./

EXPOSE 8085

#Kendi örneğimde flask.db.py , fakat ansible'da api.py.
ENTRYPOINT ["python3", "flask_db.py"]