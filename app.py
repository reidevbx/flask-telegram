from flask import Flask, request, jsonify
from neo4j import GraphDatabase
from datetime import datetime
import os

app = Flask(__name__)

# 環境變數讀取
NEO4J_URI = os.getenv("NEO4J_URI")
NEO4J_USER = os.getenv("NEO4J_USER")
NEO4J_PASS = os.getenv("NEO4J_PASS")
PORT = int(os.getenv("PORT", 8000))

driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASS))

@app.route("/webhook/telegram", methods=["POST"])
def webhook():
    data = request.json
    if "message" in data:
        user = data["message"]["from"]["id"]
        text = data["message"]["text"]
        if text.startswith("/note "):
            save_note(str(user), text[6:])
    return jsonify({"status": "ok"})

def save_note(user_id, content):
    with driver.session() as session:
        session.run("""
            CREATE (n:Note {
                user: $user_id,
                content: $content,
                created_at: datetime()
            })
        """, user_id=user_id, content=content)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=PORT)
