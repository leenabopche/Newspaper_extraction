import zipfile
from pathlib import Path
from PyPDF2 import PdfReader, PdfWriter, PdfMerger

# Keywords to look for
KEYWORDS = ["opinion", "editorial", "op-ed", "letters to the editor"]

def text_has_keywords(text):
    if not text:
        return False
    text = text.lower()
    return any(k in text for k in KEYWORDS)

def extract_opinion_pages(pdf_path, out_folder):
    reader = PdfReader(pdf_path)
    writer = PdfWriter()
    found = []
    for i, page in enumerate(reader.pages):
        text = page.extract_text() or ""
        if text_has_keywords(text):
            writer.add_page(page)
            found.append(i+1)
    if found:
        out_file = out_folder / f"{pdf_path.stem}_opinions.pdf"
        with open(out_file, "wb") as f:
            writer.write(f)
        print(f"Extracted from {pdf_path.name}: pages {found}")
        return out_file
    return None

def extract_text_from_pdfs(pdf_files, output_txt="merged_opinions.txt"):
    import pdfplumber
    from pathlib import Path

    all_text = []
    for pdf_file in pdf_files:
        with pdfplumber.open(pdf_file) as pdf:
            for page in pdf.pages:
                text = page.extract_text()
                if text:
                    all_text.append(text)
    Path(output_txt).write_text("\n\n--- PAGE BREAK ---\n\n".join(all_text), encoding="utf-8")
    print(f"Extracted text -> {output_txt}")

def main():
    # adjust if your zip has a different name
    zip_path = Path("C:/Users/Asus/OneDrive/Desktop/NEWSPAPER/newspapers.zip")
    work_dir = Path("temp_pdfs")
    work_dir.mkdir(exist_ok=True)

    # unzip
    with zipfile.ZipFile(zip_path, 'r') as zf:
        zf.extractall(work_dir)

    # process PDFs
    extracted_files = []
    for pdf in work_dir.rglob("*.pdf"):
        # skip already extracted _opinions files
        if pdf.name.endswith("_opinions.pdf"):
            continue
        out = extract_opinion_pages(pdf, work_dir)
        if out:
            extracted_files.append(out)

    if not extracted_files:
        print("No opinion/editorial pages found.")
        return

    # merge
    merger = PdfMerger()
    for f in extracted_files:
        merger.append(str(f))
    merger.write("merged_opinions.pdf")
    merger.close()
    print("Merged output -> merged_opinions.pdf")

    # extract text
    extract_text_from_pdfs(extracted_files, "merged_opinions.txt")

    # cleanup temp _opinions.pdf files
    for f in extracted_files:
        try:
            f.unlink()
        except Exception as e:
            print(f"Could not delete {f}: {e}")

if __name__ == "__main__":
    main()

