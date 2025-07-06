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

# Initialize conversation state
if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": "Hey! How was your day today?"}]

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
    "Great-Vibes": os.path.join("fonts", "GreatVibes-Regular.ttf")
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

# User input handling
if prompt := st.chat_input("Tell me how your day went... Type 'done' once you are done."):
    with st.chat_message("user"):
        st.markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    if prompt.lower().strip() == "done":
        st.session_state.blog_generated = True
    else:
        # Use conversation history to maintain context and ask a follow-up question or comment
        conversation_history = "\n".join([f'{msg["role"]}: {msg["content"]}' for msg in st.session_state.messages])
        
        # Add a prompt to generate a balanced response: a friendly comment or a thoughtful question
        follow_up_prompt = f"""
Based on this conversation, provide a friendly, thoughtful response. It could be an empathetic comment, an interesting observation, or a follow-up question to keep the conversation going. 

Conversation History:
{conversation_history}
"""
        # Generate the response
        response = st.session_state.chat.send_message(follow_up_prompt)

        with st.chat_message("assistant"):
            st.markdown(response.text)
        st.session_state.messages.append({"role": "assistant", "content": response.text})

# Generate the blog text based on conversation history
def clean_markdown(text):
    text = re.sub(r"^#{1,6}\s*", "", text, flags=re.MULTILINE)
    text = re.sub(r"\*\*(.*?)\*\*", r"\1", text)
    text = re.sub(r"\*(.*?)\*", r"\1", text)
    text = re.sub(r"__(.*?)__", r"\1", text)
    text = re.sub(r"_(.*?)_", r"\1", text)
    text = re.sub(r"`(.*?)`", r"\1", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()

def generate_blog_text():
    formatted = "\n".join([f'{msg["role"].capitalize()}: {msg["content"]}' for msg in st.session_state.messages])
    summary_prompt = f"""
Based on this conversation, write a first-person reflective blog post about the user's day. Make it expressive and readable:

Conversation:
{formatted}
"""
    blog = model.generate_content(summary_prompt).text
    blog = clean_markdown(blog)  # <- clean it here
    blog = f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n{blog}"
    return blog

# Generate the blog image
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

# Allow user to edit the generated blog text
if st.session_state.blog_generated:
    st.subheader("Edit Your Generated Blog Post")

    # Display the blog in a text box for editing
    editable_blog = st.text_area("Edit Your Blog Post", st.session_state.blog, height=300)

    if st.button("Generate Image"):
        # Generate image based on the modified blog text
        font_path = font_options.get(font_style, list(font_options.values())[0])
        blog_img = create_blog_image(
            text=editable_blog,
            font_path=font_path,
            font_size=font_size,
            font_color=font_color,
            bg_image=bg_image,
        )
        st.image(blog_img)

        # Allow user to download the generated image
        buf = BytesIO()
        blog_img.save(buf, format="PNG")
        byte_im = buf.getvalue()

        st.sidebar.download_button(
            label="📥 Download Blog Image",
            data=byte_im,
            file_name=f"journal_blog_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png",
            mime="image/png",
        )
