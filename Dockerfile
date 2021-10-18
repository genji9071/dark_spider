FROM genji9071/python3.7_google

USER root

RUN /bin/cp /usr/share/zoneinfo/Asia/Shanghai /etc/localtime && echo 'Asia/Shanghai' >/etc/timezone

ENV LC_ALL=en_US.utf-8
ENV LANG=en_US.utf-8

ADD requirements.txt requirements.txt

RUN pip3 install --no-cache-dir --upgrade pip

RUN pip3 install --timeout 30 --no-cache-dir -r requirements.txt -i https://mirrors.huaweicloud.com/repository/pypi/simple/

COPY . /app

WORKDIR /app
EXPOSE 9000

CMD gunicorn app:create_app --bind 0.0.0.0:9000 -k uvicorn.workers.UvicornWorker --workers 4 --max-requests 5000 --max-requests-jitter 2 --timeout 1200
