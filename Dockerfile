FROM python:3.8-alpine


RUN pip3 install docker jinja2 semver docker requests

WORKDIR /app

COPY . /app

CMD [ "python3", "build.py" ]