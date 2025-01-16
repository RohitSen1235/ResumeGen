FROM python:3.11-slim-bookworm

# Install full TeX Live distribution and pandoc
RUN apt-get update && apt-get install -y \
    texlive-full \
    pandoc \
    wget \
    sqlite3 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Create necessary directories
RUN mkdir -p /app/app/output /app/app/uploads && \
    chmod 777 /app/app/output /app/app/uploads

# Create a shell script to run commands
RUN echo '#!/bin/bash\n\
set -e\n\
echo "Waiting for database..."\n\
while ! python wait_for_db.py; do\n\
    echo "Database not ready, waiting..."\n\
    sleep 2\n\
done\n\
echo "Starting application..."\n\
exec uvicorn app.main:app --host 0.0.0.0 --reload\n' > /app/start.sh

RUN chmod +x /app/start.sh

CMD ["/bin/bash", "/app/start.sh"]
