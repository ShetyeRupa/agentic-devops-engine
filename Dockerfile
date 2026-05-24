FROM python:3.12-slim

WORKDIR /app

# Install pytest and passlib for password hashing
RUN pip install --no-cache-dir pytest passlib

# Create a script that will run the tests
RUN echo '#!/bin/bash\n\
if [ -f /app/generated_tests.py ]; then\n\
    echo "Found test file, running pytest..."\n\
    pytest /app/generated_tests.py -v --tb=short -s\n\
else\n\
    echo "ERROR: No test file found at /app/generated_tests.py"\n\
    echo "Contents of /app:"\n\
    ls -la /app/\n\
    exit 1\n\
fi' > /app/run_tests.sh && chmod +x /app/run_tests.sh

# The source files will be mounted as volumes at runtime
# We create empty placeholders so the container has something to start with
RUN touch /app/sandbox_source.py /app/generated_tests.py

# Run the test script
CMD ["/app/run_tests.sh"]