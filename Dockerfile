FROM python:3.11-slim

WORKDIR /app

COPY scripts/mfa_audit.py .
COPY scripts/logger.py .
COPY scripts/servicenow_api.py .
COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

CMD ["python", "mfa_audit.py"]
