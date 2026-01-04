from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse

app = Flask(__name__)

INTERCHANGES = {
    ("RED", "BLUE"): "Ameerpet",
    ("RED", "GREEN"): "MGBS",
    ("BLUE", "GREEN"): "Parade Ground"
}


LINES = {
    "BLUE": [
        "Raidurg", "HITEC City", "Durgam Cheruvu", "Madhapur",
        "Peddamma Gudi", "Jubilee Hills Check Post",
        "Jubilee Hills Road No. 5", "Yousufguda",
        "Madhura Nagar", "Ameerpet", "Begumpet",
        "Prakash Nagar", "Rasoolpura", "Paradise",
        "Parade Ground", "Secunderabad East", "Mettuguda",
        "Tarnaka", "Habsiguda", "NGRI",
        "Stadium", "Uppal", "Nagole"
    ],
    "RED": [
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
"L.B. Nagar"
    ],

    "GREEN": [
        "JBS Parade Ground",
        "Secunderabad West (Gandhi Hospital)",
        "Musheerabad",
        "RTC X Roads",
        "Chikkadpally",
        "Narayanguda",
        "Sultan Bazaar",
        "MG Bus Station (MGBS)"
    ]
}


# -----------------------------
# 1. STATIONS (number-based)
# -----------------------------
STATIONS1 = {
    1: {"name": "Miyapur", "lines": ["RED"]},
    2: {"name": "JNTU", "lines": ["RED"]},
    3: {"name": "KPHB", "lines": ["RED"]},
    4: {"name": "Kukatpally", "lines": ["RED"]},
    5: {"name": "Balanagar", "lines": ["RED"]},
    6: {"name": "Moosapet", "lines": ["RED"]},
    7: {"name": "Bharat Nagar", "lines": ["RED"]},
    8: {"name": "Erragadda", "lines": ["RED"]},

    20: {"name": "Ameerpet", "lines": ["RED", "BLUE"]},
    21: {"name": "Parade Grounds", "lines": ["BLUE", "GREEN"]},

    30: {"name": "Nagole", "lines": ["BLUE"]},
    31: {"name": "Raidurg", "lines": ["BLUE"]},

    40: {"name": "JBS", "lines": ["GREEN"]},
    41: {"name": "MGBS", "lines": ["GREEN"]}
}

# -----------------------------
# 2. LINE DIRECTIONS
# -----------------------------
LINE_DIRECTIONS = {
    "RED": ("Miyapur", "LB Nagar"),
    "BLUE": ("Nagole", "Raidurg"),
    "GREEN": ("JBS", "MGBS")
}

# -----------------------------
# 3. LINE GRAPH (max 2 interchanges)
# -----------------------------
LINE_GRAPH = {
    "RED": ["BLUE"],
    "BLUE": ["RED", "GREEN"],
    "GREEN": ["BLUE"]
}


STATION_LINES = {}

for line, stations in LINES.items():
    for st in stations:
        STATION_LINES.setdefault(st, []).append(line)
    STATIONS = STATION_LINES

# -----------------------------
# 4. HELPERS
# -----------------------------
def station_menu():
    text = "🚉 *Select Stations*\n\n"
    for i in sorted(STATIONS):
        text += f"{i}. {STATIONS[i]['name']}\n"
    text += "\nReply like:\n1 to 5"
    return text


def find_interchange(line1, line2):
    for s in STATIONS.values():
        if line1 in s["lines"] and line2 in s["lines"]:
            return s["name"]
    return None


def get_direction(line, src, dest):
    stations = LINES[line]
    return f"Towards {stations[-1]}" if stations.index(src) < stations.index(dest) \
           else f"Towards {stations[0]}"


def find_line_path(src_lines, dest_lines):
    # 0 interchange
    for l in src_lines:
        if l in dest_lines:
            return [l]

    # 1 interchange
    for sl in src_lines:
        for dl in dest_lines:
            if dl in LINE_GRAPH.get(sl, []):
                return [sl, dl]

    # 2 interchanges
    for sl in src_lines:
        for mid in LINE_GRAPH.get(sl, []):
            for dl in dest_lines:
                if dl in LINE_GRAPH.get(mid, []):
                    return [sl, mid, dl]

    return None

# -----------------------------
# 5. WHATSAPP BOT
# -----------------------------
@app.route("/whatsapp", methods=["POST"])
def whatsapp_bot():
    msg = request.form.get("Body", "").strip().lower()
    resp = MessagingResponse()

    if msg in ["hi", "hello", "start", "menu"]:
        resp.message(station_menu())
        return str(resp)

    if "to" not in msg:
        resp.message("❌ Invalid format\nType *menu* to see station list")
        return str(resp)

    try:
        src_no, dest_no = map(int, msg.split("to"))
        src = STATIONS[src_no]
        dest = STATIONS[dest_no]
    except Exception:
        resp.message("❌ Invalid station numbers\nType *menu* again")
        return str(resp)

    path = find_line_path(src["lines"], dest["lines"])

    if not path:
        resp.message("❌ Route not supported (max 2 interchanges)")
        return str(resp)

    reply = f"""
🚆 *Local Train Guide*

From: {src['name']}
To: {dest['name']}
"""

    # Build instructions
    if len(path) == 1:
        reply += f"\n➡ Board: {get_direction(path[0], src_no, dest_no)}\n✅ Direct train"

    elif len(path) == 2:
        i1 = find_interchange(path[0], path[1])
        reply += f"""
➡ First Train: {get_direction(path[0], src_no, dest_no)}
🔁 Interchange at: {i1}
➡ Second Train: {get_direction(path[1], src_no, dest_no)}
"""

    else:  # 2 interchanges
        i1 = find_interchange(path[0], path[1])
        i2 = find_interchange(path[1], path[2])
        reply += f"""
➡ First Train: {get_direction(path[0], src_no, dest_no)}
🔁 Interchange at: {i1}
➡ Second Train: {get_direction(path[1], src_no, dest_no)}
🔁 Interchange at: {i2}
➡ Third Train: {get_direction(path[2], src_no, dest_no)}
"""

    resp.message(reply.strip())
    return str(resp)


if __name__ == "__main__":
    app.run()

