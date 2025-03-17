import os
from flask import Flask, render_template, request, jsonify, session
import random
import json

app = Flask(__name__)
app.secret_key = os.urandom(24)

# Load dataset (replace 'table.json' with your scraped data file)
with open("cerv_ceremonies.json", "r", encoding="utf-8") as f:
    data = json.load(f)

# Sample game state (in-memory, resets on reload)

@app.route("/reveal", methods=["POST"])
def reveal():
    if "revealed_chars" not in session:
        session["revealed_chars"] = []
    if "current_item" not in session:
        session["current_item"] = random.choice(data)
    title = session["current_item"]["Name"]
    available_indices = [i for i, c in enumerate(title) if c.isalpha() and i not in session["revealed_chars"]]
    
    if available_indices:
        session["revealed_chars"].append(random.choice(available_indices))
        session.modified = True  # Ensure session is marked as modified
    
    return jsonify({"masked_title": mask_title(title, session["revealed_chars"])});


def mask_title(title, revealed_chars):
    """Mask title except for revealed characters."""
    masked = []
    for i, char in enumerate(title):
        if char.isalpha() and (i in revealed_chars or i == 0 or title[i - 1] == ' '):
            masked.append(char)
        elif char == ' ':
            masked.append(' ')
        else:
            masked.append(' _ ')
    return ''.join(masked)

def get_hint(hint_type):
    """Return a specific hint based on the hint type."""
    item = session["current_item"]
    hints = {
        "magnitude": item.get("Magnitude", "Unknown"),
        "type": item.get("Type", "Unknown"),
    }
    return hints.get(hint_type, "Invalid hint")


@app.route("/")
def index():
    session["current_item"] = random.choice(data)
    

    return render_template("index.html")

@app.route("/hint", methods=["POST"])
def hint():
    hint_type = request.json.get("hint_type")
    hint_value = get_hint(hint_type)
    return jsonify({"hint_type": hint_type, "hint_value": hint_value})

@app.route("/guess", methods=["POST"])
def guess():
    user_guess = request.json.get("guess").strip().lower()
    correct = user_guess == session["current_item"]["Name"].strip().lower()
    return jsonify({"correct": correct})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
