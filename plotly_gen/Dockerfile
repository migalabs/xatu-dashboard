FROM python:3.12.0rc2-alpine3.18

COPY . /plotly_gen

WORKDIR /plotly_gen

RUN apk add bash gcc musl-dev g++ util-linux

RUN pip install -r requirements.txt

RUN pip install -U python-dotenv

RUN apk add --update busybox-suid

CMD crontab /plotly_gen/cron/jobs && crontab -l && python3 /plotly_gen/main.py -t 1 2 3 4 5 6 7; crond -f
