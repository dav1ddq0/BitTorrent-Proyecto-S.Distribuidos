FROM python:3.10

RUN pip install rpyc
RUN mkdir -p /home/app
COPY . /home/app
RUN cd /home/app
RUN python server_test.py

CMD [ "/bin/sh" ]
