FROM python:3.12.4
WORKDIR /app
COPY requirements.txt /app/requirements.txt

RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

COPY parser.py /app/parser.py 




CMD ["python", "parser.py"]
