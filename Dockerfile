FROM python:3-slim

COPY requirements.txt
RUN apt-get update

EXPOSE 8002
COPY . /selectnium
WORKDIR /selectnium
RUN pip install -r requirements.txt

CMD ["python", "-u", "run.py"]