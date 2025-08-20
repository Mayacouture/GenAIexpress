import os
import tempfile
from datetime import datetime
from typing import Dict, List, Optional
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.colors import HexColor

class ExportSystem:
    def __init__(self):
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()
    
    def _setup_custom_styles(self):
        """Configure les styles personnalisés pour le PDF"""
        # Style pour le titre principal
        self.styles.add(ParagraphStyle(
            name='CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=24,
            spaceAfter=30,
            alignment=TA_CENTER,
            textColor=HexColor('#2E5A88')
        ))
        
        # Style pour les sections
        self.styles.add(ParagraphStyle(
            name='SectionTitle',
            parent=self.styles['Heading2'],
            fontSize=16,
            spaceAfter=12,
            spaceBefore=20,
            textColor=HexColor('#4A90E2')
        ))
        
        # Style pour le contenu
        self.styles.add(ParagraphStyle(
            name='Content',
            parent=self.styles['Normal'],
            fontSize=11,
            spaceAfter=6,
            leading=14
        ))
        
        # Style pour les références
        self.styles.add(ParagraphStyle(
            name='Reference',
            parent=self.styles['Normal'],
            fontSize=10,
            spaceAfter=4,
            leftIndent=20,
            textColor=HexColor('#666666')
        ))
    
    def export_to_markdown(self, meditation_data: Dict, output_path: str = None) -> str:
        """
        Exporte la méditation en format Markdown
        
        Args:
            meditation_data: Dictionnaire contenant les données de la méditation
            output_path: Chemin de sortie (optionnel)
        
        Returns:
            Chemin vers le fichier Markdown généré
        """
        if output_path is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_path = f"meditation_{timestamp}.md"
        
        content = self._generate_markdown_content(meditation_data)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"Export Markdown créé: {output_path}")
        return output_path
    
    def _generate_markdown_content(self, meditation_data: Dict) -> str:
        """Génère le contenu Markdown de la méditation"""
        emotion = meditation_data.get('emotion', '')
        meditation_text = meditation_data.get('meditation_text', '')
        references = meditation_data.get('references', [])
        rag_sources = meditation_data.get('rag_sources', [])
        session_info = meditation_data.get('session_info', {})
        
        content = f"""# Lectio Divina IA - Méditation personnalisée

## Informations de session
- **Date** : {session_info.get('date', datetime.now().strftime('%d/%m/%Y %H:%M'))}
- **Émotion/Blessure** : {emotion}
- **Style** : {session_info.get('style', 'Standard')}
- **Longueur** : {session_info.get('length', 'Moyen')}

---

## Méditation

{meditation_text}

---

## Références citées

"""
        
        # Ajouter les références
        for ref in references:
            content += f"- {ref}\n"
        
        content += "\n## Sources RAG utilisées\n\n"
        
        # Ajouter les sources RAG
        for i, source in enumerate(rag_sources, 1):
            content += f"### Source {i}\n"
            content += f"- **Score** : {source.get('score', 'N/A'):.3f}\n"
            content += f"- **Source** : {source.get('source', 'Inconnue')}\n"
            if source.get('content'):
                # Tronquer le contenu pour l'affichage
                excerpt = source['content'][:200] + "..." if len(source['content']) > 200 else source['content']
                content += f"- **Extrait** : {excerpt}\n"
            content += "\n"
        
        content += f"""
---

*Généré par Lectio Divina IA - {datetime.now().strftime('%d/%m/%Y à %H:%M')}*
"""
        
        return content
    
    def export_to_pdf(self, meditation_data: Dict, output_path: str = None) -> str:
        """
        Exporte la méditation en format PDF
        
        Args:
            meditation_data: Dictionnaire contenant les données de la méditation
            output_path: Chemin de sortie (optionnel)
        
        Returns:
            Chemin vers le fichier PDF généré
        """
        if output_path is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_path = f"meditation_{timestamp}.pdf"
        
        # Créer le document PDF
        doc = SimpleDocTemplate(output_path, pagesize=A4)
        story = []
        
        # Titre principal
        story.append(Paragraph("Lectio Divina IA", self.styles['CustomTitle']))
        story.append(Paragraph("Méditation personnalisée", self.styles['CustomTitle']))
        story.append(Spacer(1, 20))
        
        # Informations de session
        emotion = meditation_data.get('emotion', '')
        session_info = meditation_data.get('session_info', {})
        
        session_text = f"""
        <b>Date :</b> {session_info.get('date', datetime.now().strftime('%d/%m/%Y %H:%M'))}<br/>
        <b>Émotion/Blessure :</b> {emotion}<br/>
        <b>Style :</b> {session_info.get('style', 'Standard')}<br/>
        <b>Longueur :</b> {session_info.get('length', 'Moyen')}
        """
        story.append(Paragraph(session_text, self.styles['Content']))
        story.append(Spacer(1, 20))
        
        # Méditation
        story.append(Paragraph("Méditation", self.styles['SectionTitle']))
        meditation_text = meditation_data.get('meditation_text', '')
        
        # Diviser le texte en sections
        sections = self._parse_meditation_sections(meditation_text)
        for section_title, section_content in sections:
            if section_title:
                story.append(Paragraph(section_title, self.styles['SectionTitle']))
            story.append(Paragraph(section_content, self.styles['Content']))
            story.append(Spacer(1, 12))
        
        story.append(PageBreak())
        
        # Références
        story.append(Paragraph("Références citées", self.styles['SectionTitle']))
        references = meditation_data.get('references', [])
        for ref in references:
            story.append(Paragraph(f"• {ref}", self.styles['Reference']))
        
        story.append(Spacer(1, 20))
        
        # Sources RAG
        story.append(Paragraph("Sources RAG utilisées", self.styles['SectionTitle']))
        rag_sources = meditation_data.get('rag_sources', [])
        
        for i, source in enumerate(rag_sources, 1):
            source_text = f"""
            <b>Source {i}</b><br/>
            <b>Score :</b> {source.get('score', 'N/A'):.3f}<br/>
            <b>Source :</b> {source.get('source', 'Inconnue')}<br/>
            """
            if source.get('content'):
                excerpt = source['content'][:150] + "..." if len(source['content']) > 150 else source['content']
                source_text += f"<b>Extrait :</b> {excerpt}"
            
            story.append(Paragraph(source_text, self.styles['Reference']))
            story.append(Spacer(1, 12))
        
        # Pied de page
        story.append(Spacer(1, 30))
        footer_text = f"Généré par Lectio Divina IA - {datetime.now().strftime('%d/%m/%Y à %H:%M')}"
        story.append(Paragraph(footer_text, self.styles['Reference']))
        
        # Générer le PDF
        doc.build(story)
        
        print(f"Export PDF créé: {output_path}")
        return output_path
    
    def _parse_meditation_sections(self, meditation_text: str) -> List[tuple]:
        """Parse le texte de méditation en sections"""
        sections = []
        lines = meditation_text.split('\n')
        current_section = ""
        current_content = []
        
        for line in lines:
            line = line.strip()
            if line.startswith('## '):
                # Nouvelle section
                if current_content:
                    sections.append((current_section, '\n'.join(current_content)))
                current_section = line[3:]  # Enlever "## "
                current_content = []
            elif line:
                current_content.append(line)
        
        # Ajouter la dernière section
        if current_content:
            sections.append((current_section, '\n'.join(current_content)))
        
        return sections
    
    def create_session_summary(self, session_data: Dict) -> str:
        """Crée un résumé de session en Markdown"""
        emotion = session_data.get('emotion', '')
        feedback_score = session_data.get('feedback_score', '')
        feedback_text = session_data.get('feedback_text', '')
        timestamp = session_data.get('timestamp', datetime.now().isoformat())
        
        summary = f"""# Résumé de session - {emotion}

**Date :** {timestamp}
**Émotion/Blessure :** {emotion}

## Feedback utilisateur
**Note :** {feedback_score}/5

**Commentaire :**
{feedback_text}

---
*Résumé généré automatiquement*
"""
        
        return summary