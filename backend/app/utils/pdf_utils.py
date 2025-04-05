import fitz  # PyMuPDF

def extract_text_from_pdf(pdf_path):
    """
    Lit le PDF et extrait le texte de chaque page.
    Retourne une liste : une entrée = texte d’une page.
    """
    doc = fitz.open(pdf_path)
    content_by_page = [page.get_text() for page in doc]
    doc.close()
    return content_by_page


def extract_clean_sections(pdf_path):
    """
    Découpe les pages extraites en sections par titres détectés.
    Exemple de découpage : Hémorragies, Arrêt cardiaque, etc.
    """
    pages = extract_text_from_pdf(pdf_path)
    sections = {}
    current_title = "Introduction"
    sections[current_title] = ""

    for page in pages:
        lines = page.split("\n")
        for line in lines:
            if line.isupper() and len(line.strip()) > 4:
                # Suppose que les titres sont en majuscules
                current_title = line.strip()
                sections[current_title] = ""
            else:
                sections[current_title] += line + "\n"

    return sections
