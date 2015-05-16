FROM python:3.4

RUN apt-get update \
    && apt-get install -y cron

ADD . /code
ADD crontab /etc/cron.d/publisher
RUN chmod 0644 /etc/cron.d/publisher

WORKDIR /code
RUN pip install -r requirements.txt

RUN touch /var/log/cron.log
CMD cron && env > /root/env.txt && tail -f /var/log/cron.log
