from flask import Flask, request, jsonify
from neo4j import GraphDatabase
from datetime import datetime
import os

app = Flask(__name__)

# === 環境變數讀取 ===
NEO4J_URI = os.getenv("NEO4J_URI")
NEO4J_USER = os.getenv("NEO4J_USER")
NEO4J_PASS = os.getenv("NEO4J_PASS")
PORT = int(os.getenv("PORT", 8000))

# === Neo4j 連線建立 ===
driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASS))

# === Telegram Webhook 接收 ===
@app.route("/webhook/telegram", methods=["POST"])
def webhook():
    data = request.get_json()
    print("📥 收到 Telegram 訊息：", data)

    if "message" in data:
        user_id = data["message"]["from"]["id"]
        text = data["message"]["text"]

        print(f"✍️ 來自使用者 {user_id} 的訊息：{text}")

        if text.startswith("/note "):
            note_content = text[6:].strip()
            save_note(user_id, note_content)

    return jsonify({"status": "ok"})

# === 寫入筆記到 Neo4j ===
def save_note(user_id, content):
    print(f"📝 正在儲存筆記：user_id={user_id}, content={content}")
    try:
        with driver.session() as session:
            session.run("""
                CREATE (n:Note {
                    user: $user_id,
                    content: $content,
                    created_at: datetime()
                })
            """, user_id=str(user_id), content=content)
        print("✅ 筆記儲存成功")
    except Exception as e:
        print("❌ 儲存筆記時發生錯誤：", e)

# === 啟動 Flask App ===
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=PORT)
