# FROM tiangolo/uvicorn-gunicorn-fastapi:python3.7

# COPY ./app /app
FROM python:3.10

RUN pip install fastapi uvicorn

EXPOSE 80

WORKDIR /code
RUN pip install --upgrade pip
COPY ./requirements.txt /code/requirements.txt
RUN pip install  --no-cache-dir -r requirements.txt
COPY . /code/


CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "80"]