# Use for local dev
FROM python:3.8
LABEL maintainer "Daniel Stratti <daniels@vamp.me>"

WORKDIR /app

# Install server
# RUN apt update

COPY requirements.txt /
RUN pip install -r /requirements.txt

COPY ./ ./

EXPOSE 8080
#EXPOSE 443

CMD ["python", "./application.py"]

# docker build . -t metrics
# docker run -it -v $PWD:/app -p 8080:8080 --env-file=.env metrics
