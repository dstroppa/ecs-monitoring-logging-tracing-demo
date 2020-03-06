FROM python:3.8-slim

RUN pip install boto3 flask aws_xray_sdk

ADD server.py /

CMD ["/server.py"]