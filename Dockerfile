# Base Image
FROM python:3.10.17-slim-bookworm
# Define Working Dir and go into it
WORKDIR /app
# Install dependencies
RUN apt-get update && apt-get install -y libgl1
RUN apt-get update && apt-get install -y libglib2.0-0
COPY . .
# Install python dependencies
RUN pip install -r requirements.txt
# Expose port streamlit is going to run on
EXPOSE 8501
# Run App
CMD ["streamlit","run","app.py"]