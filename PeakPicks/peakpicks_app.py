import os
import secrets
from datetime import datetime
from flask import Flask, render_template, request, jsonify, session, redirect, url_for, flash
from pymongo import MongoClient
from bson.objectid import ObjectId
from werkzeug.security import generate_password_hash, check_password_hash

# ---------------------------------------------------------------------------
# Load .env file automatically (no extra packages needed)
# ---------------------------------------------------------------------------
def _load_dotenv():
    env_path = os.path.join(os.path.dirname(__file__), ".env")
    if not os.path.exists(env_path):
        return
    with open(env_path) as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, _, val = line.partition("=")
            key = key.strip()
            val = val.strip().strip('"').strip("'")
            if key and val and key not in os.environ:
                os.environ[key] = val

_load_dotenv()

# ---------------------------------------------------------------------------
# MongoDB
# ---------------------------------------------------------------------------
def get_mongo():
    uri = os.getenv("MONGODB_URI", "")
    if not uri or uri == "YOUR_MONGODB_CONNECTION_STRING_HERE":
        raise RuntimeError(
            "MONGODB_URI is not set. Open the .env file in your project folder "
            "and paste your MongoDB Atlas connection string."
        )
    client = MongoClient(uri)
    return client[os.getenv("MONGODB_DB", "peakpicks")]

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", secrets.token_hex(32))

db = get_mongo()
users_col     = db["users"]
picks_col     = db["picks"]
likes_col     = db["likes"]
tierlists_col = db["tierlists"]

# ---------------------------------------------------------------------------
# Auth helpers
# ---------------------------------------------------------------------------
def get_current_user():
    uid = session.get("user_id")
    if not uid:
        return None
    try:
        doc = users_col.find_one({"_id": ObjectId(uid)})
    except Exception:
        return None
    return doc

def login_required_api(f):
    from functools import wraps
    @wraps(f)
    def decorated(*args, **kwargs):
        if not get_current_user():
            return jsonify({"ok": False, "error": "Login required"}), 401
        return f(*args, **kwargs)
    return decorated

@app.context_processor
def inject_user():
    user = get_current_user()
    return dict(current_user=user)

# ---------------------------------------------------------------------------
# Page routes
# ---------------------------------------------------------------------------
@app.route("/")
def index():
    user = get_current_user()
    uid_str = str(user["_id"]) if user else None
    stats = {
        "total_tierlists": tierlists_col.count_documents({"is_draft": {"$ne": True}}),
        "user_tierlists": tierlists_col.count_documents({"created_by": uid_str, "is_draft": {"$ne": True}}) if uid_str else 0,
        "categories": len(tierlists_col.distinct("category", {"is_draft": {"$ne": True}})),
    }
    recent = list(tierlists_col.find({"is_draft": {"$ne": True}}).sort("created_at", -1).limit(12))
    for r in recent:
        r["_id"] = str(r["_id"])
        r["likes"] = likes_col.count_documents({"tierlist_id": r["_id"]})
    return render_template("index.html", stats=stats, recent_tierlists=recent)

# ---- Auth pages ----------------------------------------------------------
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        if request.is_json:
            data = request.get_json()
        else:
            data = request.form.to_dict()

        username = (data.get("username") or "").strip()
        email    = (data.get("email") or "").strip()
        password = data.get("password", "")
        confirm  = data.get("password_confirm") or data.get("passwordConfirm") or ""

        errors = []
        if not username or not email or not password:
            errors.append("All fields are required.")
        if password != confirm:
            errors.append("Passwords do not match.")
        if len(password) < 6:
            errors.append("Password must be at least 6 characters.")
        if not errors and users_col.find_one({"username": username}):
            errors.append("Username already taken.")
        if not errors and users_col.find_one({"email": email}):
            errors.append("Email already registered.")

        if errors:
            err_msg = " ".join(errors)
            if request.is_json:
                return jsonify({"ok": False, "error": err_msg}), 400
            flash(err_msg, "error")
            return render_template("register.html")

        result = users_col.insert_one({
            "username": username,
            "email": email,
            "password_hash": generate_password_hash(password),
            "bio": "",
            "avatar_color": "",
            "created_at": datetime.utcnow().isoformat() + "Z",
        })
        session["user_id"] = str(result.inserted_id)

        if request.is_json:
            return jsonify({"ok": True, "redirect": "/"}), 200
        return redirect(url_for("index"))

    return render_template("register.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        if request.is_json:
            data = request.get_json()
        else:
            data = request.form.to_dict()

        username = (data.get("username") or "").strip()
        password = data.get("password", "")

        if not username or not password:
            err = "Username and password are required."
            if request.is_json:
                return jsonify({"ok": False, "error": err}), 400
            flash(err, "error")
            return render_template("login.html")

        user_doc = users_col.find_one({"username": username})
        if not user_doc or not check_password_hash(user_doc["password_hash"], password):
            err = "Invalid username or password."
            if request.is_json:
                return jsonify({"ok": False, "error": err}), 401
            flash(err, "error")
            return render_template("login.html")

        session["user_id"] = str(user_doc["_id"])

        if request.is_json:
            return jsonify({"ok": True, "redirect": "/"}), 200
        return redirect(url_for("index"))

    return render_template("login.html")

@app.route("/logout")
def logout():
    session.pop("user_id", None)
    return redirect(url_for("index"))

# ---- Content pages -------------------------------------------------------
@app.route("/browse")
def browse_page():
    category = request.args.get("category", "").strip()
    return render_template("browse.html", category=category)

@app.route("/picks")
def picks_page():
    return redirect(url_for("browse_page"))

@app.route("/create")
def create_page():
    return render_template("create.html")

@app.route("/profile/<username>")
def profile_page(username):
    user_doc = users_col.find_one({"username": username})
    if not user_doc:
        return render_template("404.html"), 404
    user_doc["_id"] = str(user_doc["_id"])
    return render_template("profile.html", profile_user=user_doc)

@app.route("/edit-profile", methods=["GET", "POST"])
def edit_profile():
    user = get_current_user()
    if not user:
        return redirect(url_for("login"))

    if request.method == "POST":
        if request.is_json:
            data = request.get_json()
        else:
            data = request.form.to_dict()

        bio = (data.get("bio") or "").strip()[:500]
        avatar_color = (data.get("avatar_color") or "").strip()
        new_username = (data.get("username") or "").strip()

        errors = []
        if new_username and new_username != user["username"]:
            if len(new_username) < 3:
                errors.append("Username must be at least 3 characters.")
            elif users_col.find_one({"username": new_username}):
                errors.append("Username already taken.")

        if errors:
            if request.is_json:
                return jsonify({"ok": False, "error": " ".join(errors)}), 400
            flash(" ".join(errors), "error")
            return render_template("edit_profile.html", user=user)

        updates = {"bio": bio}
        if avatar_color:
            updates["avatar_color"] = avatar_color
        if new_username and new_username != user["username"]:
            updates["username"] = new_username
            # Also update tierlist username references
            tierlists_col.update_many(
                {"created_by": str(user["_id"])},
                {"$set": {"created_by_username": new_username}}
            )

        users_col.update_one({"_id": user["_id"]}, {"$set": updates})

        if request.is_json:
            updated_user = users_col.find_one({"_id": user["_id"]})
            return jsonify({"ok": True, "redirect": f"/profile/{updated_user['username']}"})

        updated_user = users_col.find_one({"_id": user["_id"]})
        return redirect(url_for("profile_page", username=updated_user["username"]))

    return render_template("edit_profile.html", user=user)

@app.route("/view/<tierlist_id>")
def view_tierlist(tierlist_id):
    try:
        doc = tierlists_col.find_one({"_id": ObjectId(tierlist_id)})
    except Exception:
        return render_template("404.html"), 404
    if not doc:
        return render_template("404.html"), 404
    doc["_id"] = str(doc["_id"])
    doc["likes"] = likes_col.count_documents({"tierlist_id": doc["_id"]})
    user = get_current_user()
    if user:
        doc["liked_by_user"] = bool(likes_col.find_one({"tierlist_id": doc["_id"], "user_id": str(user["_id"])}))
    else:
        doc["liked_by_user"] = False
    return render_template("tierlist_view.html", tierlist=doc)

@app.route("/tierlist/<category>")
def tierlist_page(category):
    return render_template("tierlist.html", category=category)

@app.route("/pick/<pick_id>")
def pick_detail_page(pick_id):
    try:
        doc = picks_col.find_one({"_id": ObjectId(pick_id)})
    except Exception:
        return render_template("404.html"), 404
    if not doc:
        return render_template("404.html"), 404
    doc["_id"] = str(doc["_id"])
    doc["likes"] = likes_col.count_documents({"pick_id": doc["_id"]})
    related = list(picks_col.find({"category": doc["category"], "_id": {"$ne": ObjectId(pick_id)}}).limit(6))
    for r in related:
        r["_id"] = str(r["_id"])
    return render_template("pick_detail.html", pick=doc, related=related)

@app.route("/seed")
def seed_route():
    from seed_data import seed
    count = seed()
    return jsonify({"ok": True, "message": f"Seeded {count} tier lists."})

# ---------------------------------------------------------------------------
# Tierlists API
# ---------------------------------------------------------------------------
@app.get("/api/tierlists")
def api_get_tierlists():
    category = request.args.get("category", "").strip()
    username = request.args.get("username", "").strip()
    include_drafts = request.args.get("drafts", "false").lower() == "true"

    query = {}
    if not include_drafts:
        query["is_draft"] = {"$ne": True}
    if category:
        query["category"] = category

    user = get_current_user()
    if username:
        u = users_col.find_one({"username": username})
        if u:
            query["created_by"] = str(u["_id"])
        else:
            query["created_by_username"] = username
        # If getting own drafts
        if include_drafts and user and str(u["_id"]) == str(user["_id"]):
            pass  # already filtered above

    results = []
    for doc in tierlists_col.find(query).sort("created_at", -1).limit(100):
        doc["_id"] = str(doc["_id"])
        doc["likes"] = likes_col.count_documents({"tierlist_id": doc["_id"]})
        if user:
            doc["liked_by_user"] = bool(likes_col.find_one({"tierlist_id": doc["_id"], "user_id": str(user["_id"])}))
        else:
            doc["liked_by_user"] = False
        results.append(doc)
    return jsonify(results)

@app.get("/api/tierlists/<tierlist_id>")
def api_get_tierlist(tierlist_id):
    try:
        doc = tierlists_col.find_one({"_id": ObjectId(tierlist_id)})
    except Exception:
        return jsonify({"ok": False, "error": "Invalid ID"}), 400
    if not doc:
        return jsonify({"ok": False, "error": "Not found"}), 404
    doc["_id"] = str(doc["_id"])
    doc["likes"] = likes_col.count_documents({"tierlist_id": doc["_id"]})
    user = get_current_user()
    if user:
        doc["liked_by_user"] = bool(likes_col.find_one({"tierlist_id": doc["_id"], "user_id": str(user["_id"])}))
    else:
        doc["liked_by_user"] = False
    return jsonify(doc)

@app.post("/api/tierlists")
def api_create_tierlist():
    data = request.get_json(silent=True) or {}
    title     = (data.get("title") or "").strip()
    category  = (data.get("category") or "").strip()
    scale_type = (data.get("scale_type") or "classic").strip()
    theme     = (data.get("theme") or "classic").strip()
    layout    = (data.get("layout") or "rows").strip()
    items     = data.get("picks", [])
    is_draft  = bool(data.get("is_draft", False))

    if not category:
        return jsonify({"ok": False, "error": "Category is required"}), 400
    if not title:
        title = f"{category} Tier List"

    user = get_current_user()
    doc = {
        "title": title,
        "category": category,
        "scale_type": scale_type,
        "theme": theme,
        "layout": layout,
        "picks": items,
        "is_draft": is_draft,
        "created_by": str(user["_id"]) if user else "guest",
        "created_by_username": user["username"] if user else "Guest",
        "created_at": datetime.utcnow().isoformat() + "Z",
        "updated_at": datetime.utcnow().isoformat() + "Z",
    }
    inserted = tierlists_col.insert_one(doc)
    doc["_id"] = str(inserted.inserted_id)
    doc["likes"] = 0
    doc["liked_by_user"] = False

    if not user:
        session["guest_tierlists"] = session.get("guest_tierlists", 0) + 1

    return jsonify({
        "ok": True,
        "tierlist": doc,
        "guest_tierlists": session.get("guest_tierlists", 0)
    }), 201

@app.put("/api/tierlists/<tierlist_id>")
def api_update_tierlist(tierlist_id):
    try:
        oid = ObjectId(tierlist_id)
    except Exception:
        return jsonify({"ok": False, "error": "Invalid ID"}), 400

    user = get_current_user()
    tl = tierlists_col.find_one({"_id": oid})
    if not tl:
        return jsonify({"ok": False, "error": "Not found"}), 404

    # Auth check: owner or guest
    if tl.get("created_by") != "guest":
        if not user or str(tl.get("created_by")) != str(user["_id"]):
            return jsonify({"ok": False, "error": "Unauthorized"}), 403

    data = request.get_json(silent=True) or {}
    updates = {}
    for field in ["title", "picks", "theme", "layout", "is_draft", "scale_type"]:
        if field in data:
            updates[field] = data[field]
    updates["updated_at"] = datetime.utcnow().isoformat() + "Z"

    tierlists_col.update_one({"_id": oid}, {"$set": updates})
    updated = tierlists_col.find_one({"_id": oid})
    updated["_id"] = str(updated["_id"])
    return jsonify({"ok": True, "tierlist": updated})

@app.delete("/api/tierlists/<tierlist_id>")
@login_required_api
def api_delete_tierlist(tierlist_id):
    try:
        oid = ObjectId(tierlist_id)
    except Exception:
        return jsonify({"ok": False, "error": "Invalid ID"}), 400

    user = get_current_user()
    tl = tierlists_col.find_one({"_id": oid})
    if not tl:
        return jsonify({"ok": False, "error": "Not found"}), 404
    if str(tl.get("created_by")) != str(user["_id"]):
        return jsonify({"ok": False, "error": "Unauthorized"}), 403

    tierlists_col.delete_one({"_id": oid})
    likes_col.delete_many({"tierlist_id": tierlist_id})
    return jsonify({"ok": True})

@app.post("/api/tierlists/<tierlist_id>/like")
def api_like_tierlist(tierlist_id):
    user = get_current_user()
    if not user:
        return jsonify({"ok": False, "error": "Login to like tier lists"}), 401
    try:
        tl = tierlists_col.find_one({"_id": ObjectId(tierlist_id)})
    except Exception:
        return jsonify({"ok": False, "error": "Invalid ID"}), 400
    if not tl:
        return jsonify({"ok": False, "error": "Not found"}), 404

    uid = str(user["_id"])
    existing = likes_col.find_one({"tierlist_id": tierlist_id, "user_id": uid})
    if existing:
        likes_col.delete_one({"_id": existing["_id"]})
        liked = False
    else:
        likes_col.insert_one({
            "tierlist_id": tierlist_id,
            "user_id": uid,
            "created_at": datetime.utcnow().isoformat() + "Z"
        })
        liked = True
    count = likes_col.count_documents({"tierlist_id": tierlist_id})
    return jsonify({"ok": True, "liked": liked, "likes_count": count})

# ---------------------------------------------------------------------------
# Categories API
# ---------------------------------------------------------------------------
@app.get("/api/categories")
def api_get_categories():
    cats = list(tierlists_col.aggregate([
        {"$match": {"is_draft": {"$ne": True}}},
        {"$group": {"_id": "$category", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}}
    ]))
    return jsonify(cats)

@app.get("/api/user/stats")
def api_user_stats():
    user = get_current_user()
    if not user:
        return jsonify({"ok": False, "error": "Not logged in"}), 401
    uid_str = str(user["_id"])
    count = tierlists_col.count_documents({"created_by": uid_str, "is_draft": {"$ne": True}})
    return jsonify({"ok": True, "tierlist_count": count})

# ---------------------------------------------------------------------------
# Legacy Picks API (kept for backward compatibility with seeded data)
# ---------------------------------------------------------------------------
@app.get("/api/picks")
def api_get_picks():
    category = request.args.get("category", "").strip()
    username = request.args.get("username", "").strip()
    query = {}
    if category:
        query["category"] = category
    if username:
        u = users_col.find_one({"username": username})
        if u:
            query["created_by"] = u["_id"]
        else:
            query["created_by_username"] = username

    user = get_current_user()
    results = []
    for doc in picks_col.find(query).sort("created_at", -1).limit(200):
        doc["_id"] = str(doc["_id"])
        doc["likes"] = likes_col.count_documents({"pick_id": doc["_id"]})
        if user:
            doc["liked_by_user"] = bool(likes_col.find_one({"pick_id": doc["_id"], "user_id": str(user["_id"])}))
        else:
            doc["liked_by_user"] = False
        results.append(doc)
    return jsonify(results)

@app.get("/api/picks/<pick_id>")
def api_get_pick(pick_id):
    try:
        doc = picks_col.find_one({"_id": ObjectId(pick_id)})
    except Exception:
        return jsonify({"ok": False, "error": "Invalid ID"}), 400
    if not doc:
        return jsonify({"ok": False, "error": "Not found"}), 404
    doc["_id"] = str(doc["_id"])
    doc["likes"] = likes_col.count_documents({"pick_id": doc["_id"]})
    return jsonify(doc)

@app.post("/api/picks")
def api_create_pick():
    data = request.get_json(silent=True) or request.form.to_dict()
    category  = (data.get("category") or "").strip()
    name      = (data.get("name") or "").strip()
    rank      = (data.get("rank") or "").strip().upper()
    reason    = (data.get("reason") or "").strip()
    image_url = (data.get("image_url") or "").strip()
    tags_raw  = (data.get("tags") or "").strip()
    theme     = (data.get("theme") or "classic").strip()
    layout    = (data.get("layout") or "rows").strip()

    if not category or not name or not rank:
        return jsonify({"ok": False, "error": "Category, name, and rank are required."}), 400
    if rank not in ("S", "A", "B", "C", "D"):
        return jsonify({"ok": False, "error": "Rank must be S, A, B, C, or D."}), 400

    tags = [t.strip() for t in tags_raw.split(",") if t.strip()]
    user = get_current_user()
    doc = {
        "category": category, "name": name, "rank": rank, "reason": reason,
        "image_url": image_url, "tags": tags, "theme": theme, "layout": layout,
        "created_by": str(user["_id"]) if user else "guest",
        "created_by_username": user["username"] if user else "Guest",
        "created_at": datetime.utcnow().isoformat() + "Z",
    }
    inserted = picks_col.insert_one(doc)
    doc["_id"] = str(inserted.inserted_id)
    doc["likes"] = 0
    doc["liked_by_user"] = False
    if not user:
        session["guest_picks"] = session.get("guest_picks", 0) + 1
    return jsonify({"ok": True, "pick": doc, "guest_picks": session.get("guest_picks", 0)}), 201

@app.delete("/api/picks/<pick_id>")
@login_required_api
def api_delete_pick(pick_id):
    try:
        oid = ObjectId(pick_id)
    except Exception:
        return jsonify({"ok": False, "error": "Invalid ID"}), 400
    user = get_current_user()
    pick = picks_col.find_one({"_id": oid})
    if not pick:
        return jsonify({"ok": False, "error": "Pick not found"}), 404
    if str(pick.get("created_by")) != str(user["_id"]):
        return jsonify({"ok": False, "error": "Unauthorized"}), 403
    picks_col.delete_one({"_id": oid})
    likes_col.delete_many({"pick_id": pick_id})
    return jsonify({"ok": True})

@app.post("/api/picks/<pick_id>/like")
def api_like_pick(pick_id):
    user = get_current_user()
    if not user:
        return jsonify({"ok": False, "error": "Login to like picks"}), 401
    try:
        pick = picks_col.find_one({"_id": ObjectId(pick_id)})
    except Exception:
        return jsonify({"ok": False, "error": "Invalid ID"}), 400
    if not pick:
        return jsonify({"ok": False, "error": "Pick not found"}), 404
    uid = str(user["_id"])
    existing = likes_col.find_one({"pick_id": pick_id, "user_id": uid})
    if existing:
        likes_col.delete_one({"_id": existing["_id"]})
        liked = False
    else:
        likes_col.insert_one({"pick_id": pick_id, "user_id": uid, "created_at": datetime.utcnow().isoformat() + "Z"})
        liked = True
    count = likes_col.count_documents({"pick_id": pick_id})
    return jsonify({"ok": True, "liked": liked, "likes_count": count})

# ---------------------------------------------------------------------------
if __name__ == "__main__":
    port = int(os.getenv("PORT", "8080"))
    app.run(host="0.0.0.0", port=port, debug=True)
