import os
from flask import Flask, request, jsonify
import requests
from linebot import LineBotApi, WebhookHandler
from linebot.models import MessageEvent, TextMessage, TextSendMessage

# สร้างตัวแปร LINE BOT API
LINE_CHANNEL_ACCESS_TOKEN = "UiQb94tyD1whY/1I2iAaVIUSijxvvNqAVjCnJwEZNiO1LEtYqeQBkdmcNL3qSCHDS7JCsDDM3n94o/t/htF0ygUmuD5bzZtyCqpMLFjuxGHaQ/0n0t83Y5DaPAo64ZHX6WKMs+yg4rE76ypEbfMEfAdB04t89/1O/w1cDnyilFU="  # ใส่ Channel Access Token
LINE_CHANNEL_SECRET = "f7e1f9937eca9cc402164890b24b0d3d"  # ใส่ Channel Secret
line_bot_api = LineBotApi(LINE_CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(LINE_CHANNEL_SECRET)

# ThingSpeak API endpoint
THINGSPEAK_CHANNEL_ID = "2743926"  # ใส่ Channel ID ของคุณ
THINGSPEAK_READ_API_KEY = "E963HNR4SUJWS8YO"  # ใส่ Read API Key ของ ThingSpeak

# สร้าง Flask App
app = Flask(__name__)

@app.route("/webhook", methods=['POST'])
def webhook():
    signature = request.headers['X-Line-Signature']
    body = request.get_data(as_text=True)

    try:
        # ตรวจสอบว่าเป็นข้อความที่ส่งมาจาก LINE BOT หรือไม่
        handler.handle(body, signature)
    except Exception as e:
        return "Error", 400
    return 'OK', 200

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    message = event.message.text.strip().lower()

    if message == "pm2.5":
        # ดึงข้อมูล PM1, PM2.5, PM10 จาก ThingSpeak
        url = f"https://api.thingspeak.com/channels/{THINGSPEAK_CHANNEL_ID}/feeds.json?api_key={THINGSPEAK_READ_API_KEY}&results=1"
        response = requests.get(url)
        data = response.json()

        if data.get("feeds"):
            pm1 = data["feeds"][0].get("field1", "N/A")
            pm2_5 = data["feeds"][0].get("field2", "N/A")
            pm10 = data["feeds"][0].get("field3", "N/A")
            message = f"ค่า PM 2.5 ณ เวลานี้ คือ\nPM1: {pm1} ug/m3\nPM2.5: {pm2_5} ug/m3\nPM10: {pm10} ug/m3"
        else:
            message = "ไม่สามารถดึงข้อมูลได้จาก ThingSpeak"

        # ส่งข้อความกลับไปยังผู้ใช้
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=message)
        )

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=5000)
