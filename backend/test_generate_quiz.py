from app.services.quiz_generator import generate_quiz_from_text

# Chargement du texte depuis ton fichier PDF ou ici un extrait
texte_test = """
Une victime inconsciente qui respire doit être mise en position latérale de sécurité.
"""

resultat = generate_quiz_from_text(texte_test)
print(resultat)
