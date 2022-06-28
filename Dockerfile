FROM python:3.10

RUN pip install rpyc
RUN mkdir -p /home/app
COPY . /home/app
RUN cd /home/app

CMD [ "/bin/sh" ]
