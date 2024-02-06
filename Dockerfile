# Use the official Python image from the Docker Hub
FROM python:3.11-slim

# Set the working directory inside the container
WORKDIR /norm-fullstack

# Copy the dependencies file to the working directory
COPY requirements.txt .

# Copy the original docs into the image
COPY docs .

# Install any dependencies
RUN pip install --no-cache-dir --upgrade -r requirements.txt
RUN pip install uvicorn

# Install Apache Tika
RUN apt-get update && apt-get install -y default-jre
RUN wget https://dlcdn.apache.org/tika/2.9.1/tika-app-2.9.1.jar
RUN mkdir parsed_docs
RUN java -jar tika-app-2.9.1.jar -x docs/laws.pdf > parsed_docs/laws.html

# API key
ENV OPENAI_API_KEY=$OPENAI_API_KEY

# Copy the content of the local src directory to the working directory
COPY ./app /norm-fullstack/app
COPY ./docs /norm-fullstack/docs

# Command to run on container start
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "80"]