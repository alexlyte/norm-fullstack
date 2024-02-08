# Setup

```
# Install Requirements
pip install -r requirements.txt

# Download Apache Tika
wget https://dlcdn.apache.org/tika/2.9.1/tika-app-2.9.1.jar > tika-app-2.9.1.jar

# Start the server
cd app
uvicorn main:app --reload
```

# Usage
```
curl --location 'http://127.0.0.1:8000/query' \
--header 'Content-Type: application/json' \
--data '{"item_query" : "what happens if I steal?"}'
```
