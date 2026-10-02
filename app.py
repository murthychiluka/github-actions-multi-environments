from flask import Flask
import os

app = Flask(__name__)

@app.route("/")
def home():
    environment = os.getenv("APP_ENV", "local")
    return f"Hello from Murthy - {environment}"

@app.route("/health")
def health():
    return {
        "status": "ok",
        "environment": os.getenv("APP_ENV", "local")
    }

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)