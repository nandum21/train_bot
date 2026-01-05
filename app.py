from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse

app = Flask(__name__)

# =====================================================
# 1. METRO LINES (ORDER MATTERS)
# =====================================================
LINES = {
    "RED": [
        "Miyapur", "JNTU", "KPHB", "Kukatpally", "Balanagar",
        "Moosapet", "Bharat Nagar", "Erragadda", "ESI Hospital",
        "S.R Nagar", "Ameerpet", "Punjagutta", "Irrum Manzil",
        "Khairatabad", "Lakdi-ka-pul", "Assembly", "Nampally",
        "Gandhi Bhavan", "Osmania Medical College", "MGBS",
        "Malakpet", "New Market", "Musarambagh", "Dilsukhnagar",
        "Chaitanyapuri", "Victoria Memorial", "L.B. Nagar"
    ],

    "BLUE": [
        "Raidurg", "HITEC City", "Durgam Cheruvu", "Madhapur",
        "Peddamma Gudi", "Jubilee Hills Check Post",
        "Jubilee Hills Road No. 5", "Yousufguda",
        "Madhura Nagar", "Ameerpet", "Begumpet",
        "Prakash Nagar", "Rasoolpura", "Paradise",
        "JBS", "Secunderabad East", "Mettuguda",
        "Tarnaka", "Habsiguda", "NGRI",
        "Stadium", "Uppal", "Nagole"
    ],

    "GREEN": [
        "JBS",
        "Secunderabad West (Gandhi Hospital)",
        "Musheerabad",
        "RTC X Roads",
        "Chikkadpally",
        "Narayanguda",
        "Sultan Bazaar",
        "MGBS"
    ]
}

# =====================================================
# 2. INTERCHANGES (ONLY THESE)
# =====================================================
INTERCHANGES = {
    ("RED", "BLUE"): "Ameerpet",
    ("BLUE", "GREEN"): "JBS",
    ("RED", "GREEN"): "MGBS"
}

# =====================================================
# 3. LINE CONNECTIVITY (MAX 2 INTERCHANGES)
# =====================================================
LINE_GRAPH = {
    "RED": ["BLUE", "GREEN"],
    "BLUE": ["RED", "GREEN"],
    "GREEN": ["RED", "BLUE"]
}

# =====================================================
# 4. AUTO-GENERATE STATION NUMBERS
# =====================================================
STATIONS = {}
STATION_LINES = {}

station_id = 1
for line, stations in LINES.items():
    for st in stations:
        if st not in STATION_LINES:
            STATION_LINES[st] = []
            STATIONS[station_id] = st
            station_id += 1
        STATION_LINES[st].append(line)

# =====================================================
# 5. HELPERS
# =====================================================
def station_menu():
    text = "🚉 *Select Stations*\n\n"
    for num, name in STATIONS.items():
        text += f"{num}. {name}\n"
    text += "\nReply like:\n* src_num to dest_num(1 to 50)*"
    return text


def get_direction(line, src, dest):
    stations = LINES[line]
    return f"Towards {stations[-1]}" if stations.index(src) < stations.index(dest) \
        else f"Towards {stations[0]}"


def find_line_path(src_lines, dest_lines):
    # Direct
    for l in src_lines:
        if l in dest_lines:
            return [l]

    # One interchange
    for sl in src_lines:
        for dl in dest_lines:
            if dl in LINE_GRAPH.get(sl, []):
                return [sl, dl]

    # Two interchanges
    for sl in src_lines:
        for mid in LINE_GRAPH.get(sl, []):
            for dl in dest_lines:
                if dl in LINE_GRAPH.get(mid, []):
                    return [sl, mid, dl]

    return None


def get_interchange(l1, l2):
    return INTERCHANGES.get((l1, l2)) or INTERCHANGES.get((l2, l1))

# =====================================================
# 6. WHATSAPP BOT
# =====================================================
@app.route("/whatsapp", methods=["POST"])
def whatsapp_bot():
    msg = request.values.get("Body", "")
    msg = msg.strip().lower()

    resp = MessagingResponse()

    if msg in ["hi", "hello", "menu", "start"]:
        resp.message(station_menu())
        return str(resp)

    if "to" not in msg:
        resp.message("❌ Invalid format\nType *menu*")
        return str(resp)

    try:
        src_no, dest_no = map(int, msg.split("to"))
        src = STATIONS[src_no]
        dest = STATIONS[dest_no]
    except:
        resp.message("❌ Invalid station numbers\nType *menu*")
        return str(resp)

    src_lines = STATION_LINES[src]
    dest_lines = STATION_LINES[dest]

    path = find_line_path(src_lines, dest_lines)
    if not path:
        resp.message("❌ Route not supported (max 2 interchanges)")
        return str(resp)

    reply = f"""
🚆 *Hyderabad Metro Guide*

From: {src}
To: {dest}
"""

    if len(path) == 1:
        reply += f"\n➡ Board {get_direction(path[0], src, dest)}\n✅ Direct Train"

    elif len(path) == 2:
        i1 = get_interchange(path[0], path[1])
        reply += f"""
➡ First Train: {get_direction(path[0], src, i1)}
🔁 Change at: {i1}
➡ Second Train: {get_direction(path[1], i1, dest)}
"""

    else:
        i1 = get_interchange(path[0], path[1])
        i2 = get_interchange(path[1], path[2])
        reply += f"""
➡ First Train: {get_direction(path[0], src, i1)}
🔁 Change at: {i1}
➡ Second Train: {get_direction(path[1], i1, i2)}
🔁 Change at: {i2}
➡ Third Train: {get_direction(path[2], i2, dest)}
"""

    resp.message(reply.strip())
    return str(resp)

# =====================================================
# 7. RUN
# =====================================================
if __name__ == "__main__":
    print("Metro bot started")
    print("Total stations:", len(STATIONS))
    app.run(debug=True)
