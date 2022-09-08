FROM python:3.10

ENV WEB_HOME=/home/app/web

RUN mkdir -p $WEB_HOME

WORKDIR $WEB_HOME

RUN apt update && apt install python3 netcat -y

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN pip install --upgrade pip

COPY . $WEB_HOME

RUN pip install -r requirements.txt

ENV PYTHONPATH "${PYTHONPATH}:${WEB_HOME}"

RUN chmod +x /home/app/web/entrypoint.sh
ENTRYPOINT ["/home/app/web/entrypoint.sh"]