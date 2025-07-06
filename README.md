# JournalBot 
## Where whispers become words and silence finds meaning

Ever wanted to keep a journal but didn’t know where to begin? Or maybe you’ve found it hard to reflect clearly on your day? Whether you're an overthinker, a quiet observer, or someone who just wants to make sense of it all — **JournalBot** is here to help.

---

## What is JournalBot?

**JournalBot** is a conversational journaling assistant powered by **Google's Gemini AI**. You chat with it about your day — casually, like you're talking to a friend. When you're ready, JournalBot turns your thoughts into a beautifully written blog post, optionally styled with custom fonts and backgrounds.

But that’s not all. You can download your reflections as a **text file** or as a **styled journal image** — perfect for printing, archiving, or sharing.

---

## Why JournalBot?

Sometimes it’s hard to process everything we experience in a day. This app helps you:

* Reflect with intention
* Express thoughts clearly
* Save your experiences creatively

---

## How It Works

1.  **Talk to JournalBot**
   Open the app and tell it how your day went.

2. **Say "done"** when finished
   JournalBot will then ask what kind of output you want.

3. **Choose Your Format**

   * Generate plain text
   * Generate styled image
   * Or both!

4. **Customize the Look (optional)**

   * Select fonts
   * Set font size & color
   * Upload your favorite background image

5. **Download** your blog as `.txt` or `.png`.

---

## Features at a Glance

* **Conversational journaling experience**
* **AI-powered blog generation (Gemini-1.5-Flash)**
* **No markdown or formatting clutter — clean output**
* **Font customization + live font preview**
* **Optional image output with beautiful formatting**
* **Paragraph-aware layout (no stacked walls of text!)**
* **Download as text or image**

---

## Technologies Used

* [Streamlit](https://streamlit.io/) – for interactive UI
* [Google Generative AI (Gemini)](https://ai.google.dev/) – for blog generation
* [Pillow (PIL)](https://python-pillow.org/) – for dynamic image rendering
* [Python](https://www.python.org/) – the glue behind it all

---

## Installation

### 1. Clone the repository

```bash
git clone https://github.com/yourusername/journalbot.git
cd journalbot
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Add your Gemini API key

Create a `.streamlit/secrets.toml` file:

```toml
GEMINI_API_KEY = "your_google_api_key_here"
```

### 4. Run the app

```bash
streamlit run app.py
```

---

## 📥 Example Output

### 🖼️ Blog Image Preview

> Includes your text styled with your selected font, size, and background.

### 📄 Blog Text Preview

```plaintext
Date: 2025-07-06 22:13:45

Today was a whirlwind of emotions. I started my morning with a sense of excitement...
```

---

## 🤝 Contribute or Customize

Want to add more fonts? New AI personalities? Markdown exports?
PRs and ideas are welcome! Fork the repo and make it your own ✨

---

## 🙌 Final Thoughts

Whether you journal every day or just need a space to reflect occasionally, **JournalBot** helps you turn fleeting thoughts into meaningful reflections — one conversation at a time.

**Try it out. Make journaling yours.**

---

Would you like me to generate a badge-ready link to a **real Streamlit deployment** for this as well? Or shall I generate a `requirements.txt` for your current setup too?
