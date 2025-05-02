FROM python:3.13.3-slim-bookworm

WORKDIR /application

COPY application/requirements.txt .

RUN python -m venv /app/venv && \
    . /app/venv/bin/activate && \
    pip install --no-cache-dir -r requirements.txt

ENV PATH="/app/venv/bin:$PATH"

COPY application/ .

CMD ["python", "api.py"]
