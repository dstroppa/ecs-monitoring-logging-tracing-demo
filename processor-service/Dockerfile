FROM python:3.8-slim

RUN pip install boto3 aws_xray_sdk

ADD processor.py /

CMD ["/processor.py"]