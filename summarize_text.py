from transformers import pipeline
from extract_text import extract_text_from_docx


def summarize_text(text, max_chunk_length=1024):
    summarizer = pipeline("summarization", model="facebook/bart-large-cnn")

    chunks = [
        text[i : i + max_chunk_length] for i in range(0, len(text), max_chunk_length)
    ]

    summaries = []
    for chunk in chunks:
        summary = summarizer(chunk, max_length=150, min_length=40, do_sample=False)[0][
            "summary_text"
        ]
        summaries.append(summary)

    return "\n\n".join(summaries)


if __name__ == "__main__":
    text = extract_text_from_docx("sog_example.docx")
    summary = summarize_text(text)

    with open("sog_summary.txt", "w") as f:
        f.write(summary)

    print("Summary saved to sog_summary.txt")
