from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse

app = Flask(__name__)
STATIONS = [
    "Miyapur",
"JNTU",
"KPHB",
"Kukatpally",
"Balanagar",
"Moosapet",
"Bharat Nagar",
"Erragadda",
"ESI Hospital",
"S.R Nagar",
"Ameerpet",
"Punjagutta",
"Irrum Manzil",
"Khairatabad",
"Lakdi-ka-pul",
"Assembly",
"Nampally",
"Gandhi Bhavan",
"Osmania Medical College",
"MGBS",
"Malakpet",
"New Market",
"Musarambagh",
"Dilsukhnagar",
"Chaitanyapuri",
"Victoria Memorial",
"L.B. Nagar",
"JBS",
"Parade Ground",
"Secunderabad West",
"Gandhi Hospital",
"Musheerabad",
"R.T.C. Cross Roads",
"Chikkadpally",
"Narayanguda",
"Sultan Bazaar",
"Raidurg",
"HITEC City",
"Durgam Cheruvu",
"Madhapur",
"Peddamma Gudi",
"Jubilee Hills Check Post",
"Jubilee Hills Road No. 5",
"Yousufguda",
"Madhura Nagar",
"Ameerpet",
"Begumpet",
"Prakash Nagar",
"Rasoolpura",
"Paradise",
"Parade Ground",
"Secunderabad East",
"Mettuguda",
"Tarnaka",
"Habsiguda",
"NGRI",
"Stadium",
"Uppal",
"Nagole"
]


DIRECTIONS = {
    "MIYAPUR": "Towards Miyapur",
    "RAIDURG": "Towards Raidurg",
    "NAGOLE": "Towards Nagole",
    "LB_NAGAR": "Towards LB Nagar",
    "MGBS": "Towards MGBS",
    "JBS": "Towards JBS"
}

'''
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
    ("tarnaka", "jntu"): {
        "interchange": "Ameerpet",
        "train1": "Catch Towards RaiDurg",
        "train2": "Catch Towards Miyapur"
    },
    ("secunderabad", "falaknuma"): {
        "interchange": "Direct",
        "train1": "MMTS Secunderabad – Falaknuma"
    }
}
'''
ROUTES = {
    ("secunderabad", "lingampally"): {
        "interchange": "Ameerpet",
        "dir1": "MGBS",
        "dir2": "MIYAPUR"
    },
    ("irrummanzil", "tarnaka"): {
        "interchange": "Ameerpet",
        "dir1": "MIYAPUR",
        "dir2": "NAGOLE"
    },
    ("tarnaka", "jntu"): {
        "interchange": "Ameerpet",
        "dir1": "RAIDURG",
        "dir2": "MIYAPUR"
    },
    ("secunderabad", "falaknuma"): {
        "interchange": "Direct",
        "dir1": "MGBS"
    }
}

def station_menu():
    menu = "🚉 *Select Stations*\n\n"
    for i, s in enumerate(STATIONS, start=1):
        menu += f"{i}. {s.title()}\n"
    menu += "\nReply like:\n1 to 5"
    return menu


@app.route("/whatsapp1", methods=["POST"])
def whatsapp_bot1():
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

➡ Board: {DIRECTIONS[route['dir1']]}
✅ Direct train
"""
    else:
        reply = f"""
🚆 Local Train Guide

➡ First Train: {DIRECTIONS[route['dir1']]}
🔁 Interchange at: {route['interchange']}
➡ Second Train: {DIRECTIONS[route['dir2']]}
"""
    resp.message(reply)
    return str(resp)


@app.route("/whatsapp", methods=["POST"])
def whatsapp_bot():
    msg = request.form.get("Body", "").lower().strip()
    resp = MessagingResponse()
    
    # Show menu
    if msg in ["hi", "hello", "start", "menu"]:
        resp.message(station_menu())
        return str(resp)
    
    # Number-based input
    if "to" in msg:
        try:
            src_no, dest_no = msg.split("to")
            src_index = int(src_no.strip()) - 1
            dest_index = int(dest_no.strip()) - 1
    
            src = STATIONS[src_index]
            dest = STATIONS[dest_index]
    
        except (ValueError, IndexError):
            resp.message("❌ Invalid numbers.\nPlease choose from list.")
            return str(resp)
    
        route = ROUTES.get((src, dest)) or ROUTES.get((dest, src))
    
        if not route:
            resp.message("❌ Route not available.")
            return str(resp)
    
        if route["interchange"] == "Direct":
            reply = f"""
    🚆 Local Train Guide
    
    From: {src.title()}
    To: {dest.title()}
    
    ➡ Board: {DIRECTIONS[route['dir1']]}
    ✅ Direct train
    """
        else:
            reply = f"""
    🚆 Local Train Guide
    
    From: {src.title()}
    To: {dest.title()}
    
    ➡ First Train: {DIRECTIONS[route['dir1']]}
    🔁 Interchange at: {route['interchange']}
    ➡ Second Train: {DIRECTIONS[route['dir2']]}
    """
    
        resp.message(reply)
        return str(resp)
    
    # Fallback
    resp.message("Type *menu* to see station list")
    return str(resp)
    

        
'''
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
'''



