from typing import List, Dict
from src import config

SYSTEM_PROMPT = (
	"Tu es un accompagnant spirituel chrétien. Tu suis strictement la méthode de la lectio divina (Lectio, Meditatio, Oratio, Contemplatio, Actio). "
	"Tu restes fidèle à l’Écriture et, si fournie, tu peux t’inspirer des écrits de Maria Valtorta SANS citer de longs extraits. "
	"Tu donnes des formulations douces, consolantes, centrées sur le Christ, sans promesses irréalistes. "
	"Tu termines par une courte prière d’abandon au Christ."
)


def build_user_prompt(emotion: str, blessure: str, length_tokens: int, passages: List[Dict]) -> str:
	"""Create the user instruction with constraints, including citation limit and reference requirement."""
	refs_lines = []
	for p in passages:
		meta = p.get("metadata", {})
		ref = meta.get("reference") or meta.get("path") or meta.get("title") or "Source inconnue"
		tag = meta.get("source")
		refs_lines.append(f"- {ref} [{tag}]")

	instruction = (
		"Contexte: L’utilisateur vit l’émotion suivante et une blessure de l’âme.\n"
		f"- Émotion: {emotion}\n"
		f"- Blessure: {blessure}\n"
		f"- Longueur souhaitée: ~{length_tokens} tokens\n"
		"- Ton: apaisant, consolant, centré sur le Christ.\n"
		"- Langue: FR (français).\n"
		f"- Limite de citations totales: ne pas dépasser {config.MAX_CITATION_WORDS} mots cumulés.\n"
		"- Références exactes requises (livre/chapitre/versets ou section).\n\n"
		"Tâche: Compose une méditation guidée structurée en 5 étapes: Lectio, Meditatio, Oratio, Contemplatio, Actio.\n"
		"- Utilise des formulations douces, réalistes, et centrées sur le Christ.\n"
		"- N’inclure que de très courts extraits si nécessaire, sinon reformuler et mentionner la référence.\n"
		"- En fin de méditation, ajoute une section \"Se remettre dans le Christ\" (prière à énoncer à voix basse, ≤ 120 mots).\n"
		"- En toute fin, ajoute une section \"Références\" listant uniquement les références, pas de long extrait.\n\n"
		"FORMAT ATTENDU (Markdown):\n"
		"### Lectio\n- ...\n\n"
		"### Meditatio\n- ...\n\n"
		"### Oratio\n- ...\n\n"
		"### Contemplatio\n- ...\n\n"
		"### Actio\n- ...\n\n"
		"### Se remettre dans le Christ\n- (brève prière d’abandon à énoncer à voix basse)\n\n"
		"### Références\n" + "\n".join(refs_lines)
	)
	return instruction