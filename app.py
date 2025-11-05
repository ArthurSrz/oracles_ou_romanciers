import streamlit as st
import requests
import json
import re
from wordcloud import WordCloud
import matplotlib.pyplot as plt
from collections import Counter
import pandas as pd
import time

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

# Configuration Hugging Face
HF_API_URL = "https://api-inference.huggingface.co/models/microsoft/DialoGPT-medium"
HF_API_URL_FR = "https://api-inference.huggingface.co/models/gilf/french-camembert-postag-model"

# Fonction pour appeler l'API Hugging Face
def call_huggingface_api(prompt, max_retries=3):
    # Utilisation du token depuis les secrets Streamlit
    api_token = st.secrets.get("HUGGINGFACE_API_TOKEN", "")

    if not api_token:
        st.error("Token Hugging Face manquant. Veuillez configurer HUGGINGFACE_API_TOKEN dans les secrets.")
        return None

    headers = {"Authorization": f"Bearer {api_token}"}

    # Modèle français spécialisé
    models = [
        "OpenLLM-France/Lucie-7B"
    ]

    for model in models:
        api_url = f"https://api-inference.huggingface.co/models/{model}"

        for attempt in range(max_retries):
            try:
                data = {"inputs": prompt, "parameters": {"max_length": 500, "temperature": 0.8}}
                response = requests.post(api_url, headers=headers, json=data, timeout=30)

                if response.status_code == 200:
                    result = response.json()
                    if isinstance(result, list) and len(result) > 0:
                        return result[0].get('generated_text', prompt)
                    elif isinstance(result, dict) and 'generated_text' in result:
                        return result['generated_text']
                elif response.status_code == 503:
                    st.warning(f"Modèle {model} en cours de chargement... Tentative {attempt + 1}")
                    time.sleep(10)
                    continue
                else:
                    st.warning(f"Erreur avec le modèle {model}: {response.status_code}")
                    break

            except Exception as e:
                st.warning(f"Erreur de connexion avec {model}: {str(e)}")
                break

    # Si tous les modèles échouent, génération de fallback
    return generate_fallback_story(prompt)

# Fonction de fallback pour générer une histoire simple
def generate_fallback_story(prompt):
    epoch_stories = {
        "Renaissance": "En cette époque de renouveau, un artiste florentin découvrit dans son atelier une machine étrange, aux engrenages d'une précision inouïe. Cette invention, léguée par un mystérieux alchimiste, permettait de capturer la lumière même et de la transformer en pigments aux couleurs impossibles. Ses œuvres, d'une beauté surnaturelle, attirèrent l'attention de mécènes venus de contrées lointaines. Mais l'artiste réalisa bientôt que chaque toile peinte avec ces couleurs magiques volait un fragment de réalité au monde, créant des échos entre les dimensions.",

        "Révolution française": "Dans les rues de Paris révolutionnaire, une imprimerie clandestine produisait des pamphlets aux propriétés extraordinaires. L'encre, mélangée avec des herbes rares trouvées dans les jardins royaux abandonnés, rendait les mots littéralement convaincants - quiconque lisait ces textes se trouvait irrésistiblement poussé à agir selon leur contenu. Les révolutionnaires utilisèrent ce pouvoir avec parcimonie, conscients que leur liberté nouvellement acquise dépendait de la volonté authentique du peuple, non de la magie de l'encre.",

        "Révolution industrielle": "Les machines à vapeur de cette Manchester alternative fonctionnaient non pas au charbon, mais aux rêves collectés dans les quartiers ouvriers. Des collecteurs nocturnes parcouraient les rues, récupérant dans des fioles de cristal les songes abandonnés par les travailleurs épuisés. Ces rêves, une fois distillés, produisaient une énergie pure et inépuisable. Mais quand les ouvriers cessèrent de rêver, privés de leurs aspirations, les machines s'arrêtèrent une à une, et la société dut repenser son rapport au progrès.",

        "Belle Époque": "L'Exposition universelle de Paris accueillait cette année-là un pavillon secret, visible seulement à la tombée du jour. Les inventions exposées défiaient les lois de la physique : des automobiles volantes alimentées par la musique des cabarets, des téléphones permettant de converser avec les morts, des photographies capturant non pas les visages mais les émotions. Les visiteurs, ébahis, repartaient avec la certitude qu'un monde nouveau était né, où la science et la poésie ne faisaient qu'un.",

        "Années folles": "Dans les clubs de jazz de Montmartre, la musique avait acquis des propriétés alchimiques. Les notes de saxophone transformaient littéralement l'atmosphère, rendant l'air plus léger, permettant aux danseurs de défier la gravité quelques instants. Les musiciens, conscients de leur pouvoir, créaient des mélodies capables d'effacer temporairement les traumatismes de la Grande Guerre. Mais ils découvrirent bientôt que cette magie avait un prix : elle consumait lentement leur propre mémoire, les condamnant à rejouer éternellement les mêmes airs."
    }

    # Retourne une histoire prédéfinie selon l'époque
    for epoch_key, story in epoch_stories.items():
        if epoch_key.lower() in prompt.lower():
            return story

    return epoch_stories["Renaissance"]  # Histoire par défaut

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

                # Appel à l'API Hugging Face ou fallback
                generated_story = call_huggingface_api(prompt)

                if not generated_story:
                    # Si l'API échoue, utilise le fallback
                    generated_story = generate_fallback_story(prompt)
                    st.info("🎭 Histoire générée en mode hors-ligne (API Hugging Face indisponible)")

                # Stockage dans la session
                st.session_state.current_story = generated_story
                st.session_state.current_analysis = analyze_text(generated_story)

            except Exception as e:
                st.error(f"Erreur lors de la génération : {str(e)}")
                # Génération de fallback en cas d'erreur
                prompt = generate_prompt(selected_epoch, tech_level, social_change, fantasy_elements, story_length)
                generated_story = generate_fallback_story(prompt)
                st.session_state.current_story = generated_story
                st.session_state.current_analysis = analyze_text(generated_story)
                st.info("🎭 Histoire générée en mode hors-ligne")

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