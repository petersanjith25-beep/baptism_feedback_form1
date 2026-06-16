# 💒 Baptism Feedback Website

An elegant, modern feedback web application designed for a baptism function. It features a clean **White & Gold theme** with subtle Christian accents. 

🌐 **Live Website**: [https://baptism-feedback-form.onrender.com](https://baptism-feedback-form.onrender.com)

This project is built using a **FastAPI (Python)** backend, **SQLite** for lightweight local database storage, and a **Telegram Bot** integration to notify the family instantly of any feedback submissions.

---

## ✨ Features

- **Elegant White & Gold Theme**: Visually striking, modern design with subtle shadows, metallic gradients, and premium typography.
- **Subtle Christian Accents**: Decorative cross and dove graphics conveying a blessed celebration.
- **Interactive Form Fields**:
  - Full Name input.
  - Interactive selection chips for Relationship (Friend, Relative, Church member, Neighbor).
  - Gold Star rating systems (1–5 scale) for Invitation and Function experience.
  - Choice Cards (Excellent, Good, Average, Poor) for Food rating.
  - Feedback/suggestions textarea with an active character counter.
- **Instant Telegram Notifications**: Submissions send a clean, formatted Markdown message directly to a Telegram Bot.
- **SQLite Database**: Save responses locally out-of-the-box.
- **Robust Field Validation**: Pydantic schemas validate input constraints.

---

## 🛠️ Technology Stack

1. **Frontend**: Semantic HTML5, Vanilla CSS3 (Custom grid, animations), and ES6+ JavaScript.
2. **Backend**: Python (FastAPI, Uvicorn, SQLAlchemy).
3. **Database**: SQLite (No configuration required).
4. **Third Party API**: Telegram Bot API via `httpx`.

---

## 🚀 Local Quickstart

### 1. Setup Virtual Environment
Initialize a Python virtual environment to keep your system dependencies clean:

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows (Command Prompt/PowerShell):
venv\Scripts\activate

# On macOS/Linux:
source venv/bin/activate
```

### 2. Install Dependencies
Install requirements using `pip`:

```bash
pip install -r requirements.txt
```

### 3. Run the Server
Launch the local Uvicorn development server:

```bash
uvicorn main:app --reload
```

The application will start running on [http://localhost:8000](http://localhost:8000). Open this URL in your web browser to view the form!

---

## 🤖 Telegram Bot Integration Setup

To get real-time notifications on Telegram when a guest submits feedback:

1. **Create a Telegram Bot**:
   - Open Telegram and search for the user [@BotFather](https://t.me/BotFather).
   - Start a chat and send the command `/newbot`.
   - Follow the instructions to choose a name and username for your bot.
   - Copy the generated HTTP API **Bot Token** (e.g., `123456789:ABCdefGhIJKlmNoPQRsTUVwxyZ`).

2. **Get your Chat ID**:
   - Search for the bot [@userinfobot](https://t.me/userinfobot) on Telegram.
   - Start a chat with it. It will immediately reply with your **Id** (a sequence of numbers, e.g., `987654321`).
   - *Note: You must also open your newly created bot and click **Start** so it has permission to message you.*

3. **Configure Environment Variables**:
   - Duplicate the file `.env.example` and rename it to `.env`.
   - Update it with your credentials:
     ```env
     TELEGRAM_BOT_TOKEN=your_copied_bot_token_here
     TELEGRAM_CHAT_ID=your_copied_chat_id_here
     ```
   - Restart the server. Any new submission will now send a direct message to your Telegram bot.
   - *Note: If these environment variables are left unconfigured, the app will log a warning and continue saving feedback to SQLite successfully.*

---

## 💾 Database Structure
Feedback is saved inside a SQLite database file called `feedback.db`. The table `feedbacks` contains the following columns:

| Column | Type | Description |
| :--- | :--- | :--- |
| `id` | `INTEGER` | Primary Key (Auto-Incrementing) |
| `name` | `VARCHAR` | Full Name of the guest |
| `relationship` | `VARCHAR` | Relationship to family (`Friend`/`Relative`/`Church member`/`Neighbor`) |
| `invitation_rating` | `INTEGER` | Invitation rating (`1` to `5`) |
| `overall_rating` | `INTEGER` | Overall function rating (`1` to `5`) |
| `food_rating` | `VARCHAR` | Food rating (`Excellent`/`Good`/`Average`/`Poor`) |
| `improvements` | `TEXT` | Suggestion text (Optional, limit 1000 chars) |
| `created_at` | `DATETIME` | UTC timestamp of submission |

---

## ☁️ Deployment on Render

This application is ready to deploy directly onto [Render.com](https://render.com):

1. Push your repository to your GitHub account.
2. Log in to Render and click **New +** > **Web Service**.
3. Link your GitHub repository.
4. Configure the Web Service settings:
   - **Runtime**: `Python`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn main:app --host 0.0.0.0 --port $PORT`
5. Go to the **Environment** tab on Render and add your variables:
   - `TELEGRAM_BOT_TOKEN`: *your bot token*
   - `TELEGRAM_CHAT_ID`: *your chat id*
6. Click **Deploy Web Service**. Render will build and serve your app.

> [!WARNING]
> Render's free tier uses ephemeral disks, meaning your SQLite `feedback.db` file will reset whenever the instance restarts (typically once a day). For permanent database storage on Render, you can either:
> 1. Attach a **Render Persistent Disk** and point `DATABASE_URL` to the mounted path (e.g. `sqlite:////opt/feedback-data/feedback.db`).
> 2. Spin up a free PostgreSQL database on Render and set `DATABASE_URL` to its connection string (SQLAlchemy supports Postgres natively!).
