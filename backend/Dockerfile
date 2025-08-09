FROM python:3.11-slim-bookworm

# Install system dependencies
RUN apt-get update && apt-get install -y \
    wget \
    sqlite3 \
    && rm -rf /var/lib/apt/lists/*

# Install only required LaTeX packages
RUN apt-get update && apt-get install -y \
    texlive-latex-base \
    texlive-latex-recommended \
    texlive-latex-extra \
    texlive-fonts-recommended \
    texlive-fonts-extra \
    lmodern \
    fonts-open-sans \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*
    
# Install XeTeX and fonts
RUN apt-get update && apt-get install -y \
    texlive-xetex \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/* \
    && fc-cache -f


WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Create required directories
RUN mkdir -p /app/uploads /app/output

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
