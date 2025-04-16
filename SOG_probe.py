import streamlit as st
import os
import tempfile
from transformers import pipeline
from docx import Document
import torch

# Set page configuration
st.set_page_config(page_title="Document Summarizer", page_icon="📄", layout="wide")


# Initialize summarizer
@st.cache_resource
def load_summarizer():
    try:
        device = 0 if torch.cuda.is_available() else -1
        return pipeline(
            "summarization", model="sshleifer/distilbart-cnn-12-6", device=device
        )  # use GPU
    except Exception as e:
        st.error(f"Error loading model: {str(e)}")
        st.info("Try refreshing the page or contact the administrator.")
        return None


summarizer = load_summarizer()


# Functions
def extract_text_from_docx(docx_path):
    doc = Document(docx_path)
    full_text = []
    for para in doc.paragraphs:
        if para.text.strip():  # skip empty lines
            full_text.append(para.text.strip())
    return "\n".join(full_text)


def summarize_text(text, max_chunk_length=1024):
    if not text:
        return "No text to summarize."

    chunks = []
    for i in range(0, len(text), max_chunk_length):
        chunk = text[i : i + max_chunk_length]
        chunks.append(chunk)

    summaries = []
    progress_bar = st.progress(0)

    summaries = []
    for chunk in chunks:
        summary = summarizer(chunk, do_sample=False)[0]["summary_text"]
        summaries.append(summary)

    return "\n\n".join(summaries)


#
def search_in_text(text, search_term):
    if not search_term or not text:
        return text

    paragraphs = text.split("\n")
    matching_paragraphs = []

    for p in paragraphs:
        if search_term.lower() in p.lower():
            matching_paragraphs.append(p)

    if not matching_paragraphs:
        return None

    return "\n".join(matching_paragraphs)


# UI
st.title("🔥📄🚒 SOG Summarizer")
st.write("Upload a DOCX file to extract and summarize its content.")

# Sidebar for settings
with st.sidebar:
    st.header("Search")
    search_option = st.checkbox("Filter content before summarizing", False)
    search_term = st.text_input("Search term (if enabled)", "") if search_option else ""

# File upload
uploaded_file = st.file_uploader("Choose a DOCX file", type="docx")

if uploaded_file:
    # Save uploaded file to temp location
    with tempfile.NamedTemporaryFile(delete=False, suffix=".docx") as tmp_file:
        tmp_file.write(uploaded_file.getvalue())
        docx_path = tmp_file.name

    # Process file
    with st.spinner("Extracting text from document..."):
        text = extract_text_from_docx(docx_path)

    # Show text statistics
    word_count = len(text.split())
    st.write(f"Document contains approximately {word_count} words.")

    # Search functionality
    if search_option and search_term:
        with st.spinner(f'Searching for "{search_term}"...'):
            filtered_text = search_in_text(text, search_term)
            if filtered_text:
                text = filtered_text
                st.success(f"Found content containing '{search_term}'")
            else:
                st.warning(f"No content found containing '{search_term}'")
                st.stop()

    # Show tabs for text and summary
    tab1, tab2 = st.tabs(["Original Text", "Summary"])

    with tab1:
        st.subheader("Original Text")
        st.text_area("", text, height=400)

    with tab2:
        st.subheader("Summary")
        if st.button("Generate Summary"):
            summary = summarize_text(text)

            st.text_area("", summary, height=400)

            # Download option
            st.download_button(
                label="Download Summary",
                data=summary,
                file_name=f"{uploaded_file.name.split('.')[0]}_summary.txt",
                mime="text/plain",
            )

    # Clean up temp file
    os.unlink(docx_path)
else:
    st.info("Please upload a DOCX file to begin.")

# Footer
st.markdown("---")
st.caption("Document Summarizer using Hugging Face Transformers and Streamlit")
