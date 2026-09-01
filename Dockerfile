FROM python:3.14-slim

RUN apt-get update && \
	apt-get install -y --no-install-recommends sqlite3 && \
	rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY pyproject.toml uv.lock README.md ./
COPY src ./src

# Copy entrypoint scripts expected by CMD
COPY init_db.py ./init_db.py
COPY app.py ./app.py

# Install project dependencies
RUN pip install --no-cache-dir --upgrade pip && \
	pip install --no-cache-dir .

EXPOSE 8000

CMD ["sh", "-c", "python init_db.py && python app.py"]
