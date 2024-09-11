FROM python:3.12
WORKDIR /usr/src/app
COPY requirements.txt /usr/src/app/
RUN pip install -r requirements.txt
COPY app.py /usr/src/app/
ENTRYPOINT [ "python", "/usr/src/app/app.py" ]
