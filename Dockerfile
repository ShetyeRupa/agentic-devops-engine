FROM python:3.12-slim

WORKDIR /app

# Install pytest and passlib for password hashing
RUN pip install --no-cache-dir pytest passlib

# Copy test files (will be mounted at runtime)
COPY sandbox_source.py /app/sandbox_source.py
COPY generated_tests.py /app/generated_tests.py

# Run pytest
CMD ["pytest", "generated_tests.py", "-v", "--tb=short", "-s"]