FROM python:3.13.3-slim-bookworm

COPY requirements.txt .

RUN python -m venv /app/venv && \
    . /app/venv/bin/activate && \
    pip install --no-cache-dir -r requirements.txt
ENV PATH="/app/venv/bin:$PATH"

COPY main.py .
CMD ["python", "main.py"]
