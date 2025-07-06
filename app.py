import streamlit as st
import google.generativeai as genai
from datetime import datetime
import base64

# Function to encode local image to base64
def get_base64_image(image_path):
    with open(image_path, "rb") as img_file:
        encoded = base64.b64encode(img_file.read()).decode()
    return f"data:image/jpg;base64,{encoded}"

# Apply custom CSS with notebook-style background for blog
notebook_image = get_base64_image("notebook-bg.jpg")
st.markdown(
    f"""
    <style>
    .blog-background {{
        background-image: url("{notebook_image}");
        background-size: contain;
        background-repeat: repeat;
        padding: 2rem;
        border-radius: 10px;
        box-shadow: 0 0 10px rgba(0,0,0,0.1);
        margin-top: 2rem;
        white-space: pre-wrap;
        color: #000000;
    }}
    </style>
    """,
    unsafe_allow_html=True
)

# Set your Gemini API key (use Streamlit Secrets in production)
genai.configure(api_key=st.secrets["GEMINI_API_KEY"])

# Initialize Gemini chat model
model = genai.GenerativeModel("gemini-1.5-flash")
if "chat" not in st.session_state:
    st.session_state.chat = model.start_chat(history=[])
if "messages" not in st.session_state:
    st.session_state.messages = []
if "blog_generated" not in st.session_state:
    st.session_state.blog_generated = False

st.title("📝 JournalBot")
st.markdown("A reflective journaling chatbot powered by Gemini.")

# Display chat messages
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# Handle user input
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

# Generate blog post
if st.session_state.blog_generated and "blog" not in st.session_state:
    with st.spinner("Compiling your journal into a blog post..."):
        formatted = "\n".join(
            [f'{msg["role"].capitalize()}: {msg["content"]}' for msg in st.session_state.messages]
        )
        summary_prompt = f"""
Based on this conversation, write a first-person reflective blog post about the user's day. Make it expressive and readable:

Conversation:
{formatted}
"""
        blog = model.generate_content(summary_prompt).text
        st.session_state.blog = blog

# Display blog post with background
if "blog" in st.session_state:
    st.subheader("📖 Your Blog Post")
    st.markdown(
        f'<div class="blog-background">{st.session_state.blog}</div>',
        unsafe_allow_html=True
    )

    # Download button
    filename = f"journal_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
    st.download_button("📥 Download Blog", st.session_state.blog, file_name=filename)
