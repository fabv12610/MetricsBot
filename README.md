# Discord Social Media URL Info Bot

A Discord bot that extracts and displays useful information from social media URLs posted in chat.

## 🚀 Status

**Production Ready (Active Use)**

> ⚠️ Currently, only **YouTube URLs** are fully supported. Support for additional platforms is planned.

---

## ✨ Features

* Detects social media URLs in messages
* Extracts metadata from supported links
* Displays clean, readable info directly in Discord

### ✅ Supported Platforms

* YouTube (Fully Supported)

  * Video title
  * Channel name
  * View count
  * Upload date

### 🔜 Planned Support

* Instagram
* TikTok
* Twitter / X
* Spotify

---

## 🛠️ Setup

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/your-repo-name.git
cd your-repo-name
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Environment Variables

Create a `.env` file in the root directory:

```env
DISCORD_TOKEN=your_discord_bot_token
YOUTUBE_API=your_youtube_api_key
```

---

## ▶️ Running the Bot

```bash
python main.py
```

Once started, the bot will automatically monitor messages for supported URLs.

---

## 💬 Usage

Simply send a YouTube link in any channel the bot has access to.

Example:

```
https://www.youtube.com/watch?v=dQw4w9WgXcQ
```

The bot will respond with extracted video information.

---

## ⚙️ Requiremts

* Python
* discord.py
* YouTube Data API v3
* dotenv

---

## ⚠️ Limitations

* Only YouTube URLs are currently processed
* Requires a valid YouTube API key
* Rate limits depend on API usage

---

## 🤝 Contributing

Pull requests are welcome. If you want to add support for more platforms, feel free to fork the repo and submit changes.

---

## 📄 License

GNU LICENSE 3.0

---

## 📌 Notes

This bot is actively used in production environments, but still under continuous development. Expect improvements and new platform support over time.
