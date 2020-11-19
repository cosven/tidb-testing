FROM python:3.8.6

RUN pip install slack_sdk click --no-cache-dir

ADD notify.py /notify.py
ENTRYPOINT [ "python", "/notify.py" ]
