FROM python:3.12.0rc2-alpine3.18

COPY . /plot-generator

WORKDIR /plot-generator

RUN apk add bash gcc musl-dev g++ util-linux

RUN pip install -r requirements.txt

RUN pip install -U python-dotenv

RUN apk add --update busybox-suid

CMD crontab /plot-generator/cron/jobs && crontab -l && python3 /plot-generator/src/main.py; crond -f
