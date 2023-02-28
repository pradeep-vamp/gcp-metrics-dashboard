FROM python:3.9
LABEL maintainer "Pradeep Shankar <pradeep@vamp.me>"
USER root

ENV PYTHONUNBUFFERED True
RUN apt update && apt upgrade -y && pip install --upgrade pip


ENV APP_HOME /app
COPY requirements.txt /

# COPY ./ $APP_HOME
WORKDIR $APP_HOME

# Install production dependencies.
RUN pip install -r /requirements.txt

COPY ./ ./
EXPOSE 8080
CMD ["python", "./application.py"]

# docker build . -t metrics
# docker run -it -v $PWD:/app -p 8080:8080 --env-file=.env metrics
