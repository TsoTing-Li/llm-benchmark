FROM python:3.10-slim-bookworm

WORKDIR /workspace

RUN pip install --upgrade pip setuptools wheel

COPY . .

RUN pip install .

CMD [ "bash" ]