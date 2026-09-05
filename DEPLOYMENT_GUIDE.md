# 🚀 ORCA Deployment Guide

This guide details how to deploy the **ORCA Marine Intelligence Platform** to the cloud for free with zero configuration headaches.

---

## 🌟 Option 1: 1-Click Deploy on Render (Recommended — Easiest & Free)

Render runs both the React frontend and FastAPI backend inside a single unified container. You don't have to worry about CORS, multiple URLs, or separate builds.

### Steps:
1. Push your latest code to GitHub:
   ```bash
   git add .
   git commit -m "Add production deployment configuration"
   git push origin main
   ```
2. Log in to [Render](https://dashboard.render.com/) (free account).
3. Click **"New +"** and choose **"Web Service"**.
4. Connect your GitHub repository: `Amanakgec/orca-marine`.
5. Render will automatically detect the **Dockerfile**:
   - **Name:** `orca-marine` (or any name you like)
   - **Language / Runtime:** `Docker`
   - **Instance Type:** `Free`
6. (Optional) Add Environment Variables if you want Gemini AI LLM mode:
   - `MOCK_MODE`: `false` (default is `true` if unset)
   - `GOOGLE_API_KEY`: `<your-gemini-api-key>`
7. Click **"Deploy Web Service"**.

Once deployment finishes (usually 2-3 minutes), Render gives you a live public URL like:
👉 `https://orca-marine.onrender.com`

---

## 🚆 Option 2: Deploy on Railway

Railway also natively builds and runs the `Dockerfile`.

### Steps:
1. Log in to [Railway](https://railway.app/).
2. Click **"New Project"** → **"Deploy from GitHub repo"**.
3. Select `orca-marine`.
4. Railway will automatically pick up the `Dockerfile` and start the build.
5. In the service settings, click **"Generate Domain"** under Networking to get your public HTTPS URL.

---

## ⚡ Option 3: Decoupled Deploy (Vercel Frontend + Render Backend)

If you prefer using Vercel's global edge network for the React frontend:

### 1. Deploy Backend to Render:
- Create a **Web Service** on Render.
- Root Directory: `backend`
- Runtime: `Python 3`
- Build Command: `pip install -r requirements.txt`
- Start Command: `uvicorn app:app --host 0.0.0.0 --port $PORT`
- Copy your deployed backend URL (e.g. `https://orca-backend.onrender.com`).

### 2. Deploy Frontend to Vercel:
- Import repository on [Vercel](https://vercel.com/).
- Set **Root Directory** to `frontend`.
- Add Environment Variable:
  - Key: `VITE_API_URL`
  - Value: `https://orca-backend.onrender.com` (your backend URL, no trailing slash).
- Click **"Deploy"**.

---

## 🐳 Option 4: Local or VPS Docker Run

To run the unified container locally or on any Linux VPS:

```bash
# 1. Build Docker image
docker build -t orca-marine .

# 2. Run container on port 8000
docker run -d -p 8000:8000 --name orca orca-marine

# 3. Test in browser
# Visit http://localhost:8000
```
