FROM python:3.10-slim

WORKDIR /codegen

COPY requirements.txt requirements.txt
RUN apt-get update && apt-get install ffmpeg libsm6 libxext6 -y
RUN pip install -r requirements.txt

COPY ./src .
COPY ./configs ./configs
COPY ./metadata ./metadata

CMD ["python", "/codegen/main.py"]