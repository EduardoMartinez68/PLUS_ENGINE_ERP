# Image base
FROM python:3.10-slim

# Direct work inside the container
WORKDIR /app

# Copy requirements files
COPY requirements.txt .

# Install dependencies
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# copy all the project ERP
COPY . .

# Expose port
EXPOSE 8000

# Command to run the server
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
