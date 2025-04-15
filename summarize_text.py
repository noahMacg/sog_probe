import os
from transformers import pipeline
from docx import Document

summarizer = pipeline("summarization", model="facebook/bart-large-cnn")


def extract_text_from_docx(docx_path):
    doc = Document(docx_path)
    full_text = []

    for para in doc.paragraphs:
        if para.text.strip():  # skip empty lines
            full_text.append(para.text.strip())

    return "\n".join(full_text)


def summarize_text(text, max_chunk_length=1024):

    chunks = []
    for i in range(0, len(text), max_chunk_length):
        chunk = text[i : i + max_chunk_length]
        chunks.append(chunk)

    summaries = []
    for chunk in chunks:
        summary = summarizer(chunk, max_length=150, min_length=40, do_sample=False)[0][
            "summary_text"
        ]
        summaries.append(summary)

    return "\n\n".join(summaries)


def search_and_summarize(docx_path, search_term):
    paragraphs = extract_text_from_docx(docx_path, search_term)
    matching_paragraphs = []
    for p in paragraphs:
        if search_term.lower() in p.lower():
            matching_paragraphs.append(p)

    if not matching_paragraphs:
        return None

    text = "\n".join(matching_paragraphs)
    return summarize_text(text)


if __name__ == "__main__":
    # Directory of files to be processed
    directory_path = "/home/noah-macgillivray/Documents/Code/Python1_CIS1250/sog_probe/AFR_SOGs/format_docx"

    summary_dir = os.path.join(directory_path, "summaries")
    os.makedirs(summary_dir, exist_ok=True)

    # Process each DOCX file in the directory
    for filename in os.listdir(directory_path):
        if filename.endswith(".docx"):
            docx_path = os.path.join(directory_path, filename)
            print(f"Processing {filename}...")

            # Extract text
            text = extract_text_from_docx(docx_path)

            # Summarize text
            summary = summarize_text(text)

            # Save summary
            summary_filename = os.path.splitext(filename)[0] + "_summary.txt"
            summary_path = os.path.join(summary_dir, summary_filename)

            with open(summary_path, "w") as f:
                f.write(summary)

            print(f"Summary saved to {summary_path}")
