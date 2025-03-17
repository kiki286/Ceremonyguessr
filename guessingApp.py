from flask import Flask, render_template, request, jsonify
import random
import json

app = Flask(__name__)

# Load dataset (replace 'table.json' with your scraped data file)
with open("cerv_ceremonies.json", "r", encoding="utf-8") as f:
    data = json.load(f)

# Sample game state (in-memory, resets on reload)
game_state = {
    "current_item": random.choice(data),
    "revealed_chars": [],
    "revealed_hints": set(),
    "points": 100,
}

@app.route("/reveal", methods=["POST"])
def reveal():
    title = game_state["current_item"]["Name"]
    available_indices = [i for i, c in enumerate(title) if c.isalpha() and i not in game_state["revealed_chars"]]
    
    if available_indices:
        game_state["revealed_chars"].append(random.choice(available_indices))
    
    return jsonify({"masked_title": mask_title(title, game_state["revealed_chars"])});


def mask_title(title, revealed_chars):
    """Mask title except for revealed characters."""
    masked = []
    for i, char in enumerate(title):
        if char.isalpha() and (i in revealed_chars or i == 0 or title[i - 1] == ' '):
            masked.append(char)
        elif char == ' ':
            masked.append(' ')
        else:
            masked.append('_')
    return ''.join(masked)

def get_hint(hint_type):
    """Return a specific hint based on the hint type."""
    item = game_state["current_item"]
    hints = {
        "magnitude": item.get("Magnitude", "Unknown"),
        "type": item.get("Type", "Unknown"),
    }
    return hints.get(hint_type, "Invalid hint")

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/hint", methods=["POST"])
def hint():
    hint_type = request.json.get("hint_type")
    hint_value = get_hint(hint_type)
    game_state["revealed_hints"].add(hint_type)
    return jsonify({"hint_type": hint_type, "hint_value": hint_value})

@app.route("/guess", methods=["POST"])
def guess():
    user_guess = request.json.get("guess").strip().lower()
    correct = user_guess == game_state["current_item"]["Name"].strip().lower()
    return jsonify({"correct": correct})

if __name__ == "__main__":
    app.run(debug=True)
