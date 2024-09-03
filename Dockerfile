FROM python:3.10-slim

WORKDIR /codegen

COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

COPY ./src .
COPY ./configs ./configs
COPY ./metadata ./metadata

CMD ["streamlit", "run", "/codegen/Home.py", "--server.port=8080", "--server.address=0.0.0.0"]
