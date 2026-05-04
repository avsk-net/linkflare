FROM python:3.12-slim AS builder
WORKDIR /app
COPY requirements.txt .
RUN pip install --user --no-cache-dir -r requirements.txt

FROM python:3.12-slim
WORKDIR /app
COPY --from=builder /root/.local /home/appuser/.local
RUN useradd -m appuser
COPY . .
RUN mkdir -p /app/data && chown -R appuser:appuser /app
USER appuser
ENV PATH=/home/appuser/.local/bin:$PATH
EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "9000"]
