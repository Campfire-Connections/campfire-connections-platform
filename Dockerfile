FROM python:3.13-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV DJANGO_SETTINGS_MODULE=campfire_connections.settings.local

WORKDIR /app

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        build-essential \
        libjpeg-dev \
        zlib1g-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt requirements.local.txt ./
COPY core ./core
COPY organization ./organization
COPY facility ./facility
COPY faction ./faction
COPY course ./course
COPY enrollment ./enrollment
COPY reports ./reports
COPY pages ./pages
COPY user ./user
RUN pip install --no-cache-dir -r requirements.local.txt

COPY . .

EXPOSE 8000

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
