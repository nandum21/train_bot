from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse

app = Flask(__name__)

ROUTES = {
    ("secunderabad", "lingampally"): {
        "interchange": "Ameerpet",
        "train1": "MMTS Secunderabad – Falaknuma",
        "train2": "MMTS Lingampally – Medchal"
    },
    ("irrummanzil", "tarnaka"): {
        "interchange": "Ameerpet",
        "train1": "Catch Towards Miyapur",
        "train2": "Catch Towards Nagole"
    },
    ("secunderabad", "falaknuma"): {
        "interchange": "Direct",
        "train1": "MMTS Secunderabad – Falaknuma"
    }
}

@app.route("/whatsapp", methods=["POST"])
def whatsapp_bot():
    msg = request.form.get("Body", "").lower().strip()
    resp = MessagingResponse()

    if "to" not in msg:
        resp.message("❌ Format:\nStation1 to Station2")
        return str(resp)

    src, dest = [x.strip() for x in msg.split("to", 1)]

    route = ROUTES.get((src, dest)) or ROUTES.get((dest, src))

    if not route:
        resp.message("❌ Route not found")
        return str(resp)

    if route["interchange"] == "Direct":
        reply = f"""
🚆 Local Train Guide

➡ Board: {route['train1']}
✅ Direct train
"""
    else:
        reply = f"""
🚆 Local Train Guide

➡ First Train: {route['train1']}
🔁 Interchange at: {route['interchange']}
➡ Second Train: {route['train2']}
"""

    resp.message(reply)
    return str(resp)

