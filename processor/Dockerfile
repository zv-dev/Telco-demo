FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
RUN apt-get update && apt-get install -y postgresql-client
COPY . .
RUN chmod +x wait-for-postgres.sh
CMD ./wait-for-postgres.sh 