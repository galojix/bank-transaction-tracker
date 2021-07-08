# Pull base image
FROM python:3.9
# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
# Set work directory
WORKDIR /btt
# Install dependencies
COPY Pipfile Pipfile.lock /btt/
RUN python -m pip install --upgrade pip && python -m pip install pipenv && pipenv install --system --dev
# Copy project
COPY . /btt/
RUN mkdir -p /btt/webserver/static
