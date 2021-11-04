FROM python:3.8.5


COPY . /autosk

WORKDIR /autosk

RUN pip3 install --upgrade pip

RUN pip3 install -r requirements.txt

ENTRYPOINT ["/bin/bash"]

CMD ["run.sh"]
