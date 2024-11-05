FROM python:3.12.6-alpine3.20

RUN apk add --no-cache \
        gcc \
        musl-dev \
        postgresql-dev \
        curl \
        git

# Install Poetry
RUN curl -sSL https://install.python-poetry.org | python3 - && \
    ln -s /root/.local/bin/poetry /usr/local/bin/poetry

# Set the working directory
WORKDIR /usr/src/app

# Copy pyproject.toml and poetry.lock files to the container
COPY pyproject.toml poetry.lock* ./
COPY . /usr/src/app/

# Install the dependencies using Poetry
RUN poetry config virtualenvs.create false && poetry install --no-interaction --no-ansi --no-root

# Copy the current directory into the container
COPY . .

COPY wait_for_db.sh /usr/src/app/wait_for_db.sh
RUN chmod +x /usr/src/app/wait_for_db.sh

EXPOSE 8080

# Run migrations, create superuser, and start the Django server
CMD ["sh", "-c", "./wait_for_db.sh && \
    poetry run python manage.py makemigrations && \
    poetry run python manage.py migrate && \
    poetry run python manage.py createsuperuser --noinput && \
    poetry run python manage.py runserver 0.0.0.0:8080"]