FROM python:3.11-slim

WORKDIR /code

# Copy requirements first for better caching
COPY ./requirements.txt /code/requirements.txt

# Install dependencies
RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

# Copy application code
COPY ./app /code/app
COPY ./.env /code/.env
COPY ./student-wellness-backend-firebase-adminsdk-fbsvc-7e2af33cd7.json /code/

# Expose port
EXPOSE 8000

# Run the application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
