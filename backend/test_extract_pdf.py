from backend.app.utils.pdf_utils import extract_clean_sections

pdf_path = "backend/data.pdf"  # ← c’est le bon chemin relatif
sections = extract_clean_sections(pdf_path)

for title, content in sections.items():
    print(f"--- {title} ---")
    print(content[:500])  # affiche un aperçu du contenu extrait
    print("\n\n")
