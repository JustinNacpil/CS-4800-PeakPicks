# PeakPicks (CS4800)

**Problem:** How can people quickly choose the best option when there are too many choices and not enough clear explanations?

PeakPicks is a simple tier-style "best picks" web app. You can add a pick (category, item name, rank, and reason) and then view picks by category.

## Tech
- Backend: Flask (Python)
- Frontend: HTML/CSS/JS (templates + fetch API)
- Database: MongoDB Atlas (cloud)
- Deployment: AWS EC2 + GitHub Actions (deploy on push to `main`)

## Local Setup
1) Create a virtual env and install deps:
```bash
python -m venv .venv
# Windows: .venv\Scripts\activate
source .venv/bin/activate
pip install -r requirements.txt
```

2) Set your MongoDB connection string:
```bash
export MONGODB_URI="mongodb+srv://<user>:<pass>@<cluster>/..."
# optional:
export MONGODB_DB="peakpicks"
export MONGODB_COLLECTION="picks"
```

3) Run:
```bash
python peakpicks_app.py
```
Open:
- http://localhost:8080/

## EC2 Setup (matches the demo repo structure)
On your EC2 instance:
```bash
# Example:
sudo apt-get update
sudo apt-get install -y python3.12 python3.12-venv git

cd ~
git clone <YOUR_GITHUB_REPO_URL> peakpicks
cd peakpicks
chmod +x run.sh

# Set environment variables (simple approach)
echo 'export MONGODB_URI="...your atlas uri..."' >> ~/.bashrc
echo 'export PORT=8080' >> ~/.bashrc
source ~/.bashrc

./run.sh
```

Make sure your EC2 security group allows inbound TCP **8080** (or whatever PORT you set).

## GitHub Actions (CI/CD)
Add these secrets in your GitHub repo:
- `EC2_HOST` (your public IPv4 DNS or IP)
- `EC2_USER` (usually `ubuntu` on Ubuntu AMIs)
- `EC2_SSH_KEY` (private key contents for your EC2 keypair)

Workflow file: `.github/workflows/deploy.yml`
