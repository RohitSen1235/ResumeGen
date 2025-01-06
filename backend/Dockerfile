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
python wait_for_db.py\n\
if [ $? -eq 0 ]; then\n\
    echo "Running database migrations..."\n\
    alembic upgrade head\n\
    echo "Database is ready, starting application..."\n\
    exec uvicorn app.main:app --host 0.0.0.0 --reload\n\
else\n\
    echo "Failed to connect to database"\n\
    exit 1\n\
fi' > /app/start.sh

RUN chmod +x /app/start.sh

CMD ["/bin/bash", "/app/start.sh"]
