FROM python:3.4

RUN apt-get update \
    && apt-get install -y cron rsyslog

ADD . /code
ADD rsyslog.conf /etc/
RUN chmod 0644 /etc/rsyslog.conf

ADD crontab /var/spool/cron/crontabs/root
RUN chmod 0600 /var/spool/cron/crontabs/root

WORKDIR /code
RUN pip install -r requirements.txt

CMD rsyslogd && cron && tail -f /var/log/syslog /var/log/cron.log
