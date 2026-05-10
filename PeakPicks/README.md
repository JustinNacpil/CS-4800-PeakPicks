# PeakPicks (CS 4800 Final Project)

A desktop/web companion to the **PeakPicks** mobile app. PeakPicks is a tier-style "best picks" platform where users sign up, post their favorite items in any category (movies, games, restaurants, etc.), rank them on an S/A/B/C/D scale, and explain *why*. This repository is the Flask + MongoDB build that runs in the browser on a desktop and is deployed to AWS EC2.

> **Problem this app solves:** When there are too many options and not enough clear explanations, how do you quickly find the *best* pick? PeakPicks crowdsources ranked recommendations so the answer is one tap (or click) away.

---

## Features

- **User accounts** — registration, login, logout, hashed passwords (werkzeug), session-based auth
- **Create picks** — category, item name, image URL, tier rank (S/A/B/C/D), reasoning, tags
- **Browse & search** — filter by category, search across the community feed
- **Interactive tier lists** — drag-and-drop S/A/B/C/D rows per category
- **Social layer** — like/upvote, public user profiles, recent community feed
- **Modern UI** — dark theme, glass-morphism cards, smooth animations, responsive layout
- **REST API** — JSON endpoints for picks, categories, likes, and user profile
- **Cloud-ready** — MongoDB Atlas + AWS EC2 + GitHub Actions auto-deploy

---

## Tech Stack

| Layer        | Tooling                                                  |
| ------------ | -------------------------------------------------------- |
| Backend      | Python 3.12, Flask 3.1                                   |
| Auth         | Flask sessions + `werkzeug.security` password hashing    |
| Database     | MongoDB Atlas (`pymongo`)                                |
| Frontend     | Vanilla JS, HTML5, CSS3 (no framework)                   |
| Templating   | Jinja2                                                   |
| Hosting      | AWS EC2 (Ubuntu)                                         |
| CI/CD        | GitHub Actions (deploy on push to `main`)                |

---

## Project Structure

```
PeakPicks/
├── peakpicks_app.py        # Flask app: routes, auth, API
├── seed_data.py            # Seeds MongoDB with sample picks/users
├── mongo_test.py           # Quick connectivity check
├── requirements.txt
├── run.sh                  # EC2 launch script
├── .env                    # Local environment variables (NOT committed)
├── .github/workflows/      # CI/CD pipeline
├── static/
│   ├── style.css           # Dark theme, tier colors, animations
│   └── app.js              # API calls, drag-and-drop, toasts
└── templates/
    ├── base.html           # Master layout + navbar
    ├── index.html          # Landing / dashboard
    ├── login.html          # Login form
    ├── register.html       # Signup form
    ├── create.html         # New-pick form
    ├── browse.html         # Browse picks
    ├── picks.html          # Filtered pick list
    ├── pick_detail.html    # Single pick view
    ├── tierlist.html       # Drag-and-drop tier editor
    ├── tierlist_view.html  # Read-only tier list
    ├── profile.html        # User profile
    ├── edit_profile.html   # Profile settings
    ├── 404.html            # Not Found
    └── 500.html            # Server error
```

---

## Local Setup

### 1. Clone and create a virtual environment

```bash
git clone <YOUR_GITHUB_REPO_URL> peakpicks
cd peakpicks/PeakPicks

python -m venv .venv
# Windows:
.venv\Scripts\activate
# macOS / Linux:
source .venv/bin/activate

pip install -r requirements.txt
```

### 2. Configure environment variables

Create a `.env` file inside the `PeakPicks/` folder:

```env
MONGODB_URI=mongodb+srv://<user>:<pass>@<cluster>/
MONGODB_DB=peakpicks
SECRET_KEY=change-me-to-a-random-string
PORT=8080
```

### 3. (Optional) Seed sample data

```bash
python seed_data.py
```

### 4. Run the app

```bash
python peakpicks_app.py
```

Open [http://localhost:8080](http://localhost:8080) in your browser.

---

## API Reference

All endpoints return JSON. Routes marked **(auth)** require a logged-in session.

| Method | Endpoint                       | Description                                  |
| ------ | ------------------------------ | -------------------------------------------- |
| GET    | `/api/picks`                   | List picks (filter by `category`/`username`) |
| GET    | `/api/categories`              | List categories with pick counts             |
| POST   | `/api/picks` **(auth)**        | Create a new pick                            |
| DELETE | `/api/picks/<id>` **(auth)**   | Delete your own pick                         |
| POST   | `/api/picks/<id>/like` **(auth)** | Toggle like on a pick                     |
| GET    | `/api/user/profile` **(auth)** | Current user's profile                       |

---

## MongoDB Collections

**users**
```json
{ "_id": "ObjectId", "username": "string", "email": "string",
  "password_hash": "string", "created_at": "ISO8601 string" }
```

**picks**
```json
{ "_id": "ObjectId", "category": "string", "name": "string",
  "rank": "S|A|B|C|D", "reason": "string", "image_url": "string",
  "tags": ["string"], "created_by": "ObjectId",
  "created_by_username": "string", "created_at": "ISO8601 string" }
```

**likes**
```json
{ "_id": "ObjectId", "pick_id": "string", "user_id": "string",
  "created_at": "ISO8601 string" }
```

**tierlists** — saved drag-and-drop tier arrangements per user/category.

---

## Deployment (AWS EC2)

On a fresh Ubuntu EC2 instance:

```bash
sudo apt-get update
sudo apt-get install -y python3.12 python3.12-venv git

cd ~
git clone <YOUR_GITHUB_REPO_URL> peakpicks
cd peakpicks/PeakPicks
chmod +x run.sh

# Set environment variables
echo 'export MONGODB_URI="...your atlas uri..."' >> ~/.bashrc
echo 'export SECRET_KEY="...random secret..."'   >> ~/.bashrc
echo 'export PORT=8080'                          >> ~/.bashrc
source ~/.bashrc

./run.sh
```

Make sure your EC2 **security group** allows inbound TCP on the `PORT` you set (default `8080`).

### GitHub Actions auto-deploy

`.github/workflows/deploy.yml` rsyncs changes to your EC2 box and restarts the app on every push to `main`. Add these repository secrets:

- `EC2_HOST` — public DNS or IP
- `EC2_USER` — usually `ubuntu`
- `EC2_SSH_KEY` — private key contents for the EC2 keypair

---

## Relationship to the Mobile App

This desktop build mirrors the feature set of the Flutter mobile app (`cs4750_peakpicks`), so a user who creates a pick on their phone sees the same data when they log in on their laptop. Both clients share the same MongoDB Atlas database.

| Surface       | Repo                                  | Stack                       |
| ------------- | ------------------------------------- | --------------------------- |
| Mobile        | `cs4750_peakpicks`                    | Flutter / Dart              |
| Desktop / Web | `CS-4800-PeakPicks` *(this repo)*     | Flask + MongoDB             |

---

## Author

Justin Nacpil — CS 4800, Cal Poly Pomona
