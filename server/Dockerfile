FROM python:3.9 
#AS backend

WORKDIR /app/backend
COPY backend/requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
COPY backend ./

ENV DB_HOST your_db_host
ENV DB_PORT your_db_port
ENV DB_NAME your_db_name
ENV DB_USER your_db_user
ENV DB_PASSWORD your_db_password

EXPOSE 8000

CMD ["python", "server.py"]