FROM python:3.12

WORKDIR /app

COPY requirements.txt requirements.txt

RUN pip install -r requirements.txt

COPY . .

CMD ["streamlit", "run", "app.py"]

ENV PROTOCOL_BUFFERS_PYTHON_IMPLEMENTATION=python

