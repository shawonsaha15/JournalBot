import streamlit as st
import google.generativeai as genai
from datetime import datetime
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont
import textwrap
import os
import re

# ------------------ CONFIG ------------------

genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
model = genai.GenerativeModel("gemini-2.5-flash")

st.set_page_config(page_title="JournalBot", layout="centered")

# ------------------ SESSION STATE ------------------

if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Hey! How was your day today?"}
    ]

if "blog_generated" not in st.session_state:
    st.session_state.blog_generated = False

if "blog" not in st.session_state:
    st.session_state.blog = ""

if "token_count" not in st.session_state:
    st.session_state.token_count = 0

# ------------------ HELPERS ------------------

def count_total_tokens(messages):
    conversation_text = "\n".join(
        f"{m['role']}: {m['content']}" for m in messages
    )
    return model.count_tokens([conversation_text]).total_tokens


def clean_markdown(text):
    patterns = [
        (r"^#{1,6}\s*", "", re.MULTILINE),
        (r"\*\*(.*?)\*\*", r"\1"),
        (r"\*(.*?)\*", r"\1"),
        (r"__(.*?)__", r"\1"),
        (r"_(.*?)_", r"\1"),
        (r"`(.*?)`", r"\1"),
        (r"\n{3,}", "\n\n"),
    ]
    for pattern, repl, *flags in patterns:
        text = re.sub(pattern, repl, text, *(flags or []))
    return text.strip()


def generate_blog_text():
    formatted = "\n".join(
        f"{m['role'].capitalize()}: {m['content']}"
        for m in st.session_state.messages
    )

    prompt = f"""
Write a first-person reflective blog post based on this conversation.
Make it emotionally expressive, natural, and readable.

Conversation:
{formatted}
"""

    response = model.generate_content(prompt)
    blog = clean_markdown(response.text)

    return f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n{blog}"


def create_blog_image(
    text,
    font_path,
    font_size,
    font_color,
    bg_image=None,
    width=800,
    padding=40,
):
    try:
        font = ImageFont.truetype(font_path, font_size)
    except Exception:
        font = ImageFont.load_default()

    wrapper = textwrap.TextWrapper(width=70)
    paragraphs = [wrapper.wrap(p) for p in text.split("\n\n")]

    line_height = font.getbbox("A")[3] + 8
    total_lines = sum(len(p) for p in paragraphs)

    height = (
        total_lines * line_height
        + (len(paragraphs) - 1) * 12
        + padding * 2
    )

    if bg_image:
        img = bg_image.convert("RGBA").resize((width, height))
    else:
        img = Image.new("RGBA", (width, height), "white")

    draw = ImageDraw.Draw(img)
    y = padding

    for para in paragraphs:
        for line in para:
            draw.text((padding, y), line, font=font, fill=font_color)
            y += line_height
        y += 12

    return img

# ------------------ SIDEBAR ------------------

st.sidebar.header("Customize Blog Appearance")

font_options = {
    "Roboto": "fonts/Roboto-VariableFont_wdth,wght.ttf",
    "Great Vibes": "fonts/GreatVibes-Regular.ttf",
}

font_style = st.sidebar.selectbox(
    "Font Style", list(font_options.keys())
)

font_size = st.sidebar.slider("Font Size", 12, 48, 20)
font_color = st.sidebar.color_picker("Font Color", "#333333")

bg_image_file = st.sidebar.file_uploader(
    "Background Image (optional)", type=["png", "jpg", "jpeg"]
)
bg_image = (
    Image.open(bg_image_file).convert("RGBA")
    if bg_image_file
    else None
)

# ------------------ UI ------------------

st.title("JournalBot")
st.caption("Where whispers become words and silence finds meaning")

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# ------------------ CHAT INPUT ------------------

if prompt := st.chat_input("Tell me about your day — type 'done' when finished"):
    st.session_state.messages.append(
        {"role": "user", "content": prompt}
    )

    with st.chat_message("user"):
        st.markdown(prompt)

    if prompt.lower().strip() == "done":
        st.session_state.blog_generated = True
        st.session_state.blog = generate_blog_text()
        st.session_state.token_count = count_total_tokens(
            st.session_state.messages
        )
    else:
        history = "\n".join(
            f"{m['role']}: {m['content']}"
            for m in st.session_state.messages
        )

        follow_up_prompt = f"""
Respond empathetically and thoughtfully.
You may comment or ask a gentle follow-up question.

Conversation:
{history}
"""

        reply = model.generate_content(follow_up_prompt).text
        st.session_state.messages.append(
            {"role": "assistant", "content": reply}
        )

        with st.chat_message("assistant"):
            st.markdown(reply)

# ------------------ BLOG OUTPUT ------------------

if st.session_state.blog_generated:
    st.subheader("✍️ Edit Your Blog Post")

    edited_blog = st.text_area(
        "Blog Content", st.session_state.blog, height=320
    )

    if st.button("🖼️ Generate Image"):
        img = create_blog_image(
            edited_blog,
            font_options[font_style],
            font_size,
            font_color,
            bg_image,
        )

        st.image(img)

        buf = BytesIO()
        img.save(buf, format="PNG")

        st.download_button(
            "📥 Download Image",
            buf.getvalue(),
            file_name=f"journal_{datetime.now():%Y%m%d_%H%M%S}.png",
            mime="image/png",
        )

    if st.button("🔁 Start Over"):
        st.session_state.clear()
        st.rerun()

    st.markdown(
        f"### 📊 Total Tokens Used: `{st.session_state.token_count}`"
    )
