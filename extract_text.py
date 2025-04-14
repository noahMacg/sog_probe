from docx import Document


def extract_text_from_docx(docx_path):
    doc = Document(docx_path)
    full_text = []

    for para in doc.paragraphs:
        if para.text.strip():  # skip empty lines
            full_text.append(para.text.strip())

    return "\n".join(full_text)


if __name__ == "__main__":
    path = "/home/noah-macgillivray/Documents/Code/Python1_CIS1250/sog_probe/AFR_SOGs/format_docx"
    text = extract_text_from_docx(path)
    print(text[:1000])  # Preview first 1000 characters
