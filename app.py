import streamlit as st
import google.generativeai as genai
from datetime import datetime
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont
import textwrap
import os
import re

# Configure Gemini API key
genai.configure(api_key=st.secrets["GEMINI_API_KEY"])

# Initialize Gemini model
model = genai.GenerativeModel("gemini-1.5-flash")
if "chat" not in st.session_state:
    st.session_state.chat = model.start_chat(history=[])
if "messages" not in st.session_state:
    st.session_state.messages = []
if "blog_generated" not in st.session_state:
    st.session_state.blog_generated = False
if "blog" not in st.session_state:
    st.session_state.blog = None
if "output_choice" not in st.session_state:
    st.session_state.output_choice = None

# Sidebar customization
st.sidebar.header("Customize Blog Appearance")

# Font selector
font_options = {
    "Roboto": os.path.join("fonts", "Roboto-VariableFont_wdth,wght.ttf"),
    "Great-Vibes": os.path.join("fonts","GreatVibes-Regular.ttf")
    # Add more fonts here like:
    # "Lora": "fonts/Lora-Regular.ttf",
    # "Indie Flower": "fonts/IndieFlower-Regular.ttf",
}
font_style = st.sidebar.selectbox("### Font Style", list(font_options.keys()), index=0)

# --- Font preview ---
st.sidebar.markdown("### Font Preview")

try:
    preview_font = ImageFont.truetype(font_options[font_style], 24)
    preview_img = Image.new("RGB", (400, 60), "white")
    draw = ImageDraw.Draw(preview_img)
    draw.text((10, 10), f"This is {font_style}", font=preview_font, fill="black")

    buf = BytesIO()
    preview_img.save(buf, format="PNG")
    st.sidebar.image(buf.getvalue(), use_container_width=True)
except Exception as e:
    st.sidebar.warning(f"Could not load preview for {font_style}.")

font_size = st.sidebar.slider("### Font Size", 12, 48, 20)
font_color = st.sidebar.color_picker("### Font Color", "#333333")
bg_image_file = st.sidebar.file_uploader("### Upload Background Image (optional)", type=["png", "jpg", "jpeg"])

if bg_image_file is not None:
    bg_image = Image.open(bg_image_file).convert("RGBA")
else:
    bg_image = None

st.title("JournalBot")
st.markdown("Where whispers become words and silence finds meaning")

# Display chat messages
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# User input
if prompt := st.chat_input("Tell me how your day went..."):
    with st.chat_message("user"):
        st.markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    if prompt.lower().strip() == "done":
        st.session_state.blog_generated = True
    else:
        response = st.session_state.chat.send_message(prompt)
        with st.chat_message("assistant"):
            st.markdown(response.text)
        st.session_state.messages.append({"role": "assistant", "content": response.text})

def clean_markdown(text):
    # Remove markdown headers like ##, ###, etc.
    text = re.sub(r"^#{1,6}\s*", "", text, flags=re.MULTILINE)

    # Remove bold/italic markers
    text = re.sub(r"\*\*(.*?)\*\*", r"\1", text)  # bold **
    text = re.sub(r"\*(.*?)\*", r"\1", text)      # italic *
    text = re.sub(r"__(.*?)__", r"\1", text)      # bold __
    text = re.sub(r"_(.*?)_", r"\1", text)        # italic _
    text = re.sub(r"`(.*?)`", r"\1", text)        # inline code
    text = re.sub(r"\n{3,}", "\n\n", text)        # normalize extra line breaks

    return text.strip()

def generate_blog_text():
    formatted = "\n".join(
        [f'{msg["role"].capitalize()}: {msg["content"]}' for msg in st.session_state.messages]
    )
    summary_prompt = f"""
Based on this conversation, write a first-person reflective blog post about the user's day. Make it expressive and readable:

Conversation:
{formatted}
"""
    blog = model.generate_content(summary_prompt).text
    blog = clean_markdown(blog)  # <- clean it here
    blog = f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n{blog}"
    return blog

def create_blog_image(text, font_path, font_size, font_color, bg_image=None, max_width=800, padding=40):
    try:
        font = ImageFont.truetype(font_path, font_size)
    except Exception:
        font = ImageFont.load_default()

    paragraphs = text.split("\n\n")
    wrapper = textwrap.TextWrapper(width=70)

    bbox = font.getbbox("A")
    line_height = (bbox[3] - bbox[1]) + 10
    paragraph_spacing = 10

    wrapped_paragraphs = [wrapper.wrap(p) for p in paragraphs]

    total_lines = sum(len(p) for p in wrapped_paragraphs)
    img_height = line_height * total_lines + paragraph_spacing * (len(paragraphs) - 1) + 2 * padding
    img_width = max_width

    if bg_image is not None:
        bg_resized = bg_image.resize((img_width, img_height))
        img = bg_resized.copy()
    else:
        img = Image.new("RGBA", (img_width, img_height), "white")

    draw = ImageDraw.Draw(img)
    y_text = padding
    for para in wrapped_paragraphs:
        for line in para:
            draw.text((padding, y_text), line, font=font, fill=font_color)
            y_text += line_height
        y_text += paragraph_spacing

    return img

# After "done" prompt, ask user what output to generate
if st.session_state.blog_generated and st.session_state.output_choice is None:
    st.info("You typed 'done'. What do you want to generate?")
    choice = st.radio(
        "Select output:",
        ("Text only", "Image only", "Both"),
        index=0,
    )
    if st.button("Generate"):
        st.session_state.output_choice = choice
        st.session_state.blog = generate_blog_text()

# Show results based on user choice
if st.session_state.output_choice and st.session_state.blog:
    font_path = font_options.get(font_style, list(font_options.values())[0])

    if st.session_state.output_choice in ("Text only", "Both"):
        st.subheader("📖 Your Blog Post")
        st.markdown(f"```plaintext\n{st.session_state.blog}\n```")
        filename_txt = f"journal_blog_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        st.sidebar.download_button(
            label="📥 Download Blog Text",
            data=st.session_state.blog,
            file_name=filename_txt,
            mime="text/plain",
        )

    if st.session_state.output_choice in ("Image only", "Both"):
        blog_img = create_blog_image(
            text=st.session_state.blog,
            font_path=font_path,
            font_size=font_size,
            font_color=font_color,
            bg_image=bg_image,
        )
        st.image(blog_img)

        buf = BytesIO()
        blog_img.save(buf, format="PNG")
        byte_im = buf.getvalue()

        st.sidebar.download_button(
            label="📥 Download Blog Image",
            data=byte_im,
            file_name=f"journal_blog_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png",
            mime="image/png",
        )
