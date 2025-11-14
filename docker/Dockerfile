FROM python:3.11.14-slim-bookworm

WORKDIR /workspace

RUN pip install --upgrade pip setuptools wheel

COPY . .

RUN pip install .

CMD [ "bash" ]