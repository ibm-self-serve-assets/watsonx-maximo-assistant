FROM python:3.9-slim

WORKDIR /app

COPY . /app
COPY ./app/woExamples.txt /app/woExamples.txt
RUN pip install -r requirements.txt
ENV FLASK_ENV production

EXPOSE 3001

CMD ["python", "-u", "./app/main.py"]
