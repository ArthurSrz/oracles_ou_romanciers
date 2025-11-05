import streamlit as st
import ollama
import json
import re
from wordcloud import WordCloud
import matplotlib.pyplot as plt
from collections import Counter
import pandas as pd

st.set_page_config(
    page_title="Générateur de Récits Parallèles",
    page_icon="📚",
    layout="wide"
)

st.title("📚 Générateur de Récits Parallèles")
st.markdown("*Des récits alternatifs qui émergent d'une réalité statistique construite sur les vestiges de notre passé collectif.*")

# Configuration des époques historiques
EPOCHS = {
    "Renaissance (1400-1600)": {
        "description": "Époque de renouveau artistique et scientifique en Europe",
        "keywords": ["art", "science", "humanisme", "exploration", "inventions"],
        "context": "À la Renaissance, l'Europe connaît un renouveau artistique, scientifique et culturel. Les grandes découvertes transforment la vision du monde."
    },
    "Révolution française (1789-1799)": {
        "description": "Période de bouleversements politiques et sociaux en France",
        "keywords": ["révolution", "liberté", "égalité", "fraternité", "république"],
        "context": "La Révolution française marque la fin de l'Ancien Régime et l'émergence de nouveaux idéaux démocratiques."
    },
    "Révolution industrielle (1760-1840)": {
        "description": "Transformation économique et sociale par la mécanisation",
        "keywords": ["industrie", "machines", "vapeur", "usines", "urbanisation"],
        "context": "La révolution industrielle transforme radicalement les modes de production et la société européenne."
    },
    "Belle Époque (1871-1914)": {
        "description": "Période de prospérité et d'innovations en Europe",
        "keywords": ["progrès", "innovations", "électricité", "automobile", "cinéma"],
        "context": "La Belle Époque est marquée par l'optimisme, les innovations techniques et l'épanouissement culturel."
    },
    "Années folles (1920-1929)": {
        "description": "Décennie d'euphorie et de modernité après la Grande Guerre",
        "keywords": ["jazz", "modernité", "libération", "économie", "arts"],
        "context": "Les Années folles sont une période d'effervescence culturelle et de prospérité économique."
    }
}

# Sidebar pour les paramètres
st.sidebar.header("⚙️ Paramètres de génération")

# Sélection de l'époque
selected_epoch = st.sidebar.selectbox(
    "Choisissez une époque historique :",
    list(EPOCHS.keys())
)

st.sidebar.markdown(f"**Description :** {EPOCHS[selected_epoch]['description']}")

# Paramètres de divergence
st.sidebar.subheader("🔀 Paramètres de divergence")

tech_level = st.sidebar.slider(
    "Niveau technologique alternatif",
    min_value=0,
    max_value=100,
    value=30,
    help="0 = technologies de l'époque, 100 = technologies très avancées"
)

social_change = st.sidebar.slider(
    "Changements sociaux/politiques",
    min_value=0,
    max_value=100,
    value=40,
    help="0 = société identique, 100 = société radicalement différente"
)

fantasy_elements = st.sidebar.slider(
    "Éléments fantastiques subtils",
    min_value=0,
    max_value=100,
    value=20,
    help="0 = réalisme pur, 100 = éléments magiques/fantastiques"
)

story_length = st.sidebar.selectbox(
    "Longueur du récit :",
    ["Court (100-200 mots)", "Moyen (300-500 mots)", "Long (600-800 mots)"]
)

# Fonction pour générer le prompt
def generate_prompt(epoch, tech, social, fantasy, length):
    epoch_data = EPOCHS[epoch]

    length_instruction = {
        "Court (100-200 mots)": "un court récit de 100 à 200 mots",
        "Moyen (300-500 mots)": "un récit de 300 à 500 mots",
        "Long (600-800 mots)": "un récit détaillé de 600 à 800 mots"
    }

    tech_description = ""
    if tech > 70:
        tech_description = "avec des technologies très avancées pour l'époque"
    elif tech > 40:
        tech_description = "avec quelques innovations technologiques"
    elif tech > 10:
        tech_description = "avec de légères améliorations techniques"

    social_description = ""
    if social > 70:
        social_description = "dans une société aux structures radicalement différentes"
    elif social > 40:
        social_description = "avec des changements sociaux notables"
    elif social > 10:
        social_description = "avec quelques modifications sociales"

    fantasy_description = ""
    if fantasy > 70:
        fantasy_description = "intégrant des éléments magiques subtils"
    elif fantasy > 40:
        fantasy_description = "avec des phénomènes inexpliqués"
    elif fantasy > 10:
        fantasy_description = "avec une légère touche de mystère"

    prompt = f"""Écris {length_instruction[length]} se déroulant pendant {epoch.split('(')[0].strip()}
    dans un monde parallèle où {epoch_data['context']}
    {tech_description} {social_description} {fantasy_description}.

    Le récit doit :
    - Ressembler à notre réalité historique sans s'y conformer exactement
    - Présenter une alternative plausible basée sur cette époque
    - Être écrit en français avec un style littéraire
    - Inclure des détails sur la vie quotidienne de cette époque alternative

    Commence directement par le récit sans introduction."""

    return prompt

# Fonction pour analyser le texte généré
def analyze_text(text):
    # Comptage des mots
    words = re.findall(r'\b\w+\b', text.lower())
    word_count = len(words)

    # Mots les plus fréquents
    word_freq = Counter(words)
    common_words = word_freq.most_common(10)

    # Détection d'éléments "parallèles" vs réalistes
    parallel_indicators = [
        'alternative', 'différent', 'inhabituel', 'étrange', 'mystérieux',
        'inexpliqué', 'nouveau', 'révolutionnaire', 'impossible', 'magique'
    ]

    parallel_score = sum(1 for word in words if word in parallel_indicators)
    parallel_percentage = (parallel_score / word_count) * 100 if word_count > 0 else 0

    return {
        'word_count': word_count,
        'common_words': common_words,
        'parallel_score': parallel_percentage
    }

# Interface principale
col1, col2 = st.columns([2, 1])

with col1:
    st.header("📖 Génération de récit")

    if st.button("🎲 Générer un récit parallèle", type="primary"):
        with st.spinner("Génération du récit en cours..."):
            try:
                prompt = generate_prompt(selected_epoch, tech_level, social_change, fantasy_elements, story_length)

                # Appel à Ollama
                response = ollama.chat(
                    model='llama3.2:3b',  # Utilise le modèle disponible
                    messages=[
                        {
                            'role': 'user',
                            'content': prompt
                        }
                    ]
                )

                generated_story = response['message']['content']

                # Stockage dans la session
                st.session_state.current_story = generated_story
                st.session_state.current_analysis = analyze_text(generated_story)

            except Exception as e:
                st.error(f"Erreur lors de la génération : {str(e)}")
                st.info("Assurez-vous qu'Ollama est installé et qu'un modèle est disponible (ex: llama3.2)")

    # Affichage du récit généré
    if hasattr(st.session_state, 'current_story'):
        st.subheader("📜 Récit généré")
        st.write(st.session_state.current_story)

        # Bouton pour sauvegarder
        if st.button("💾 Sauvegarder ce récit"):
            try:
                with open(f"/Users/arthursarazin/Documents/oracles_ou_romanciers/recit_{selected_epoch.replace(' ', '_')}_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}.txt", "w", encoding='utf-8') as f:
                    f.write(f"Époque : {selected_epoch}\n")
                    f.write(f"Paramètres : Tech={tech_level}, Social={social_change}, Fantasy={fantasy_elements}\n\n")
                    f.write(st.session_state.current_story)
                st.success("Récit sauvegardé !")
            except Exception as e:
                st.error(f"Erreur lors de la sauvegarde : {str(e)}")

with col2:
    st.header("📊 Analyse du texte")

    if hasattr(st.session_state, 'current_analysis'):
        analysis = st.session_state.current_analysis

        # Métriques
        st.metric("Nombre de mots", analysis['word_count'])
        st.metric("Score de divergence", f"{analysis['parallel_score']:.1f}%")

        # Mots les plus fréquents
        st.subheader("🔤 Mots les plus fréquents")
        for word, count in analysis['common_words'][:5]:
            st.write(f"• **{word}** : {count}")

        # Nuage de mots
        if hasattr(st.session_state, 'current_story') and len(st.session_state.current_story) > 50:
            st.subheader("☁️ Nuage de mots")
            try:
                wordcloud = WordCloud(
                    width=300,
                    height=200,
                    background_color='white',
                    colormap='viridis'
                ).generate(st.session_state.current_story)

                fig, ax = plt.subplots(figsize=(6, 4))
                ax.imshow(wordcloud, interpolation='bilinear')
                ax.axis('off')
                st.pyplot(fig)
            except Exception as e:
                st.write("Nuage de mots non disponible")

# Footer
st.markdown("---")
st.markdown("*Application développée avec Streamlit et Ollama - Exploration des mondes parallèles littéraires*")