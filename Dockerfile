# Multi-stage Dockerfile for Python Flask application
FROM python AS lint-stage

WORKDIR /code

# Create virtual environment
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Activate the virtual environment
RUN . /opt/venv/bin/activate

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies in virtual environment
RUN pip install -r requirements.txt

# Install pylint
RUN pip install --no-cache-dir pylint pylint-pytest

# Copy application code
COPY src/ .

# Copy configuration files
COPY config /config

# Run pylint
COPY .pylintrc .
RUN pylint .


# Stage 2: Test stage - Build environment with virtual environment and run tests
#FROM python AS test-stage
FROM lint-stage as test-stage

WORKDIR /code

# Activate the virtual environment
RUN . /opt/venv/bin/activate

# Set the database host environment variable
ENV DATABASE_URL=sqlite:///:memory:

# Run tests
RUN python -m pytest tests_in_memory_database.py -v

# Stage 3: Production stage
FROM python

WORKDIR /code

# Create virtual environment
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Activate the virtual environment
RUN . /opt/venv/bin/activate

# Copy application code
COPY --from=test-stage /code/* .

# Install Python dependencies in virtual environment
RUN pip install -r requirements.txt

# Set environment variables
ENV FLASK_APP=app.py
ENV FLASK_ENV=production
ENV DATABASE_URL=mysql://root:password@host.docker.internal/coffees

# Run the application
CMD [ "python", "app.py" ]
