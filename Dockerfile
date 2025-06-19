# 1. Use a lightweight Python base image
FROM python:3.10-slim

# 2. Set working directory
WORKDIR /app

# 3. Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade -r requirements.txt

# 4. Copy application code
COPY . .

# 5. Expose port
EXPOSE 5000

# 6. Launch with Gunicorn, pointing to your app factory
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "app:create_app()"]
