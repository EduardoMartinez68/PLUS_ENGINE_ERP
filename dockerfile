# Image base
FROM python:3.10-slim

RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    libssl-dev \
    libffi-dev \
    libxml2-dev \
    libxslt1-dev \
    zlib1g-dev \
    libjpeg-dev \
    libfreetype6-dev \
    && rm -rf /var/lib/apt/lists/*
    
# Direct work inside the container
WORKDIR /app

# Copy requirements files
COPY requirements.txt .

# Install dependencies
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

#we will to install celery with redis support
RUN pip install "celery[redis]"

# copy all the project ERP
COPY . .
COPY .env /app/.env

# Expose port
EXPOSE 8000

# Command to run the server
CMD ["sh", "-c", "python manage.py migrate --noinput && python manage.py collectstatic --noinput && python manage.py runserver 0.0.0.0:8000"]
