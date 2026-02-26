import os
from datetime import datetime
from flask import Flask, render_template, request, jsonify
from pymongo import MongoClient
from bson.objectid import ObjectId

def get_mongo():
    uri = os.getenv("MONGODB_URI")
    if not uri:
        raise RuntimeError("MONGODB_URI is not set. Add it to your environment or your EC2 shell profile.")
    client = MongoClient(uri)
    db_name = os.getenv("MONGODB_DB", "peakpicks")
    col_name = os.getenv("MONGODB_COLLECTION", "picks")
    return client[db_name][col_name]

app = Flask(__name__)
collection = get_mongo()

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/picks")
def picks_page():
    # optional filter: /picks?category=Headphones
    category = request.args.get("category", "").strip()
    return render_template("picks.html", category=category)

@app.route("/create")
def create_page():
    return render_template("create.html")

@app.get("/api/picks")
def api_get_picks():
    category = request.args.get("category", "").strip()
    query = {}
    if category:
        query["category"] = category

    results = []
    for doc in collection.find(query).sort([("created_at", -1)]).limit(100):
        doc["_id"] = str(doc["_id"])
        results.append(doc)
    return jsonify(results)

@app.post("/api/picks")
def api_create_pick():
    data = request.get_json(silent=True) or request.form.to_dict()

    category = (data.get("category") or "").strip()
    name = (data.get("name") or "").strip()
    rank = (data.get("rank") or "").strip()       # ex: S / A / B / C / D
    reason = (data.get("reason") or "").strip()
    image_url = (data.get("image_url") or "").strip()
    tags_raw = (data.get("tags") or "").strip()   # comma-separated

    if not category or not name or not rank:
        return jsonify({"ok": False, "error": "category, name, and rank are required"}), 400

    tags = [t.strip() for t in tags_raw.split(",") if t.strip()]

    doc = {
        "category": category,
        "name": name,
        "rank": rank.upper(),
        "reason": reason,
        "image_url": image_url,
        "tags": tags,
        "created_at": datetime.utcnow().isoformat() + "Z",
    }

    inserted = collection.insert_one(doc)
    doc["_id"] = str(inserted.inserted_id)
    return jsonify({"ok": True, "pick": doc}), 201

@app.delete("/api/picks/<pick_id>")
def api_delete_pick(pick_id):
    # optional (not required for the assignment), but useful for cleanup
    try:
        oid = ObjectId(pick_id)
    except Exception:
        return jsonify({"ok": False, "error": "invalid id"}), 400

    res = collection.delete_one({"_id": oid})
    return jsonify({"ok": True, "deleted": res.deleted_count})

if __name__ == "__main__":
    port = int(os.getenv("PORT", "8080"))
    app.run(host="0.0.0.0", port=port)
