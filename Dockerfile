FROM python:3.10

ENV PYTHONUNBUFFERED=TRUE

EXPOSE 8050

WORKDIR /app
COPY ./requirements.txt /app

RUN pip install -r requirements.txt

COPY ./src /app

CMD ["gunicorn", "-c", "gunicorn.conf.py", "app:server"]
