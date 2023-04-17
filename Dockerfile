FROM python:3.9

COPY ./requirements.txt /requirements.txt

RUN apt-get update && apt-get upgrade -y

RUN pip3 install -r /requirements.txt
RUN pip3 install gunicorn openpyxl

COPY ./app.py /code/
RUN mkdir /code/assets
COPY ./assets/ /code/assets

WORKDIR /code/
ENV PYTHONPATH /code

ENV GUNICORN_CMD_ARGS "--bind=0.0.0.0:8000 --workers=2 --thread=4 --worker-class=gthread --forwarded-allow-ips='*' --access-logfile -"

CMD ["gunicorn", "app:server"]