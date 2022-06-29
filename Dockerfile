FROM python:3.10

RUN pip install bencode.py==4.0.0
RUN pip install rpyc==5.1.0
RUN pip install bitstring==3.1.9
RUN mkdir -p /home/app
COPY . /home/app
RUN cd /home/app

CMD [ "/bin/sh" ]
