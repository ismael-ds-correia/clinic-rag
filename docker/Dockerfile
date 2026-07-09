FROM python:3.10-slim

WORKDIR /app

# ================ Python Requirements Zone ================
COPY ./academic/requirements.txt /scripts/requirements.txt
RUN pip install --no-cache-dir -r /scripts/requirements.txt

# ================ Auto Executable Zone ================
COPY ./docker/scripts/entrypoint.sh /scripts/entrypoint.sh
RUN chmod +x /scripts/entrypoint.sh

EXPOSE 8501

ENTRYPOINT [ "sh", "/scripts/entrypoint.sh" ]