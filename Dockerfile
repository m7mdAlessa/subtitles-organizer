FROM python:alpine3.8
COPY requirements.txt .
COPY /src /app
RUN pip install -r requirements.txt
CMD python ./app/main.py
