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
HF_MODEL = "HuggingFaceTB/SmolLM3-3B"

# Fonction pour nettoyer les thinking tokens
def clean_thinking_tokens(text):
    """Extrait le contenu narratif français des thinking tokens"""
    import re
    if not text:
        return text

    # Chercher du contenu narratif français dans toutes les balises <think>
    story_parts = []

    # Extraire tout le contenu des balises <think>...</think>
    think_matches = re.findall(r'<think>(.*?)</think>', text, flags=re.DOTALL)

    # Si pas de balises fermées, chercher une balise ouverte
    if not think_matches:
        think_match = re.search(r'<think>(.*)', text, flags=re.DOTALL)
        if think_match:
            think_matches = [think_match.group(1)]

    # Analyser chaque bloc de thinking pour extraire UNIQUEMENT les parties narratives françaises
    for think_content in think_matches:
        lines = think_content.split('\n')
        french_started = False

        for line in lines:
            line = line.strip()

            # Détecter le début du récit français (souvent après des analyses en anglais)
            if not french_started:
                # Chercher des phrases qui commencent clairement du français
                if (len(line) > 20 and
                    (line.startswith('À ') or line.startswith('En ') or line.startswith('Dans ') or
                     line.startswith('Le ') or line.startswith('La ') or line.startswith('Les ') or
                     line.startswith('Un ') or line.startswith('Une ')) and
                    not any(eng in line.lower() for eng in ['in florence', 'check the word', 'technical aspect', 'that seems', 'need to make'])):
                    french_started = True
                    story_parts.append(line)
                continue

            # Une fois le français commencé, continuer tant qu'on est en français
            if french_started:
                # Arrêter si on retombe sur de l'anglais d'analyse
                if any(phrase in line.lower() for phrase in ['check the word', 'word count', 'technical aspect', 'that seems', 'need to make', 'fits the time']):
                    break

                # Continuer si c'est du français narratif
                if (len(line) > 10 and
                    any(word in line.lower() for word in ['dans', 'était', 'sur', 'avec', 'pour', 'une', 'le', 'la', 'les', 'des', 'du', 'de', 'mais', 'alors']) and
                    not any(phrase in line.lower() for phrase in ['i need', 'i should', 'let me', 'maybe', 'perhaps', 'i think', 'okay'])):
                    story_parts.append(line)
                elif line == '':  # Ligne vide acceptable
                    story_parts.append('')

    # Aussi chercher du contenu français en dehors des balises
    outside_think = re.sub(r'<think>.*?</think>', '', text, flags=re.DOTALL)
    outside_think = re.sub(r'<think>.*', '', outside_think, flags=re.DOTALL)

    lines = outside_think.split('\n')
    for line in lines:
        line = line.strip()
        if (len(line) > 30 and
            any(word in line.lower() for word in ['dans', 'était', 'sur', 'avec', 'pour', 'une', 'le', 'la', 'les', 'des', 'du', 'de']) and
            not any(phrase in line.lower() for phrase in ['i need', 'i should', 'let me', 'maybe', 'perhaps', 'i think', 'okay'])):
            story_parts.append(line)

    # Assembler le récit
    if story_parts:
        cleaned = '\n\n'.join(story_parts)
        # Nettoyer les espaces multiples
        cleaned = re.sub(r'  +', ' ', cleaned)
        return cleaned.strip()

    # Si rien trouvé, fallback sur l'ancien algorithme
    cleaned = re.sub(r'<think>.*?</think>', '', text, flags=re.DOTALL)
    cleaned = re.sub(r'<think>.*', '', cleaned, flags=re.DOTALL)
    return cleaned.strip()

# Fonction pour appeler l'API Hugging Face
def call_huggingface_api(prompt, max_retries=3):
    print(f"🔍 DEBUG: Début call_huggingface_api avec prompt: {prompt[:100]}...")

    # Utilisation du token depuis les secrets Streamlit
    api_token = st.secrets.get("HUGGINGFACE_API_TOKEN", "")
    print(f"🔍 DEBUG: Token trouvé: {bool(api_token)} (longueur: {len(api_token) if api_token else 0})")

    if not api_token:
        print("❌ DEBUG: Pas de token trouvé")
        st.error("Token Hugging Face manquant. Veuillez configurer HUGGINGFACE_API_TOKEN dans les secrets.")
        return None

    try:
        # Import Hugging Face InferenceClient
        from huggingface_hub import InferenceClient

        # Création du client Hugging Face
        client = InferenceClient(
            provider="hf-inference",
            api_key=api_token,
        )
        print(f"🔍 DEBUG: Client Hugging Face configuré avec provider hf-inference")

        for attempt in range(max_retries):
            try:
                print(f"🔍 DEBUG: Tentative {attempt + 1}/{max_retries} avec le modèle {HF_MODEL}")

                # Appel à l'API avec le client Hugging Face (non-streaming)
                # Utiliser un exemple pour "apprendre" au modèle à répondre correctement
                completion = client.chat.completions.create(
                    model=HF_MODEL,
                    messages=[
                        {
                            "role": "user",
                            "content": "Écris une courte histoire de 50 mots sur la Renaissance."
                        },
                        {
                            "role": "assistant",
                            "content": "<think>\nJe dois écrire une histoire courte sur la Renaissance. Je vais me concentrer sur un artiste à Florence.\n</think>\n\nEn cette année 1503 à Florence, Lorenzo observait son maître Leonardo peindre. Les pinceaux dansaient sur la toile, capturant la lumière comme jamais auparavant. \"L'art révèle la vérité\", murmura le maître. Lorenzo comprit alors que cette époque de renouveau transformait non seulement l'art, mais l'âme humaine elle-même."
                        },
                        {"role": "user", "content": prompt}
                    ],
                    max_tokens=1000,
                    temperature=0.7,
                    top_p=1.0,
                    stream=False
                )

                generated = completion.choices[0].message.content
                if generated:
                    # Nettoyer les thinking tokens
                    cleaned_text = clean_thinking_tokens(generated)

                    if cleaned_text and len(cleaned_text) > 20:  # Vérifier qu'il y a du contenu substantiel
                        print(f"✅ DEBUG: Texte généré: {cleaned_text[:100]}...")
                        return cleaned_text
                    else:
                        print(f"⚠️ DEBUG: Texte vide ou trop court après nettoyage, utilisation du fallback")
                        return generate_fallback_story(prompt)
                else:
                    print(f"⚠️ DEBUG: Réponse vide")

            except Exception as e:
                print(f"💥 DEBUG: Erreur tentative {attempt + 1}: {str(e)}")
                if "503" in str(e) or "loading" in str(e).lower():
                    st.warning(f"Modèle en cours de chargement... Tentative {attempt + 1}/{max_retries}")
                    time.sleep(20)
                    continue
                elif "429" in str(e) or "rate" in str(e).lower():
                    st.warning(f"Limite de taux atteinte. Tentative {attempt + 1}/{max_retries}")
                    time.sleep(30)
                    continue
                else:
                    st.warning(f"Erreur: {str(e)}")
                    if attempt == max_retries - 1:
                        break
                    time.sleep(5)

    except ImportError:
        print("❌ DEBUG: Module huggingface_hub non disponible")
        st.error("Module huggingface_hub non installé. Utilisez: pip install huggingface_hub")
        return None
    except Exception as e:
        print(f"💥 DEBUG: Erreur configuration client: {str(e)}")
        st.error(f"Erreur configuration API: {str(e)}")
        return None

    # Si tous les essais échouent, génération de fallback
    print("🔄 DEBUG: Utilisation du fallback")
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

    prompt = f"""Histoire: {length_instruction[length]} se déroulant pendant {epoch.split('(')[0].strip()} {tech_description} {social_description} {fantasy_description}.

Contexte: {epoch_data['context']}

Récit:"""

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
                print(f"🚀 DEBUG: Bouton cliqué - Génération démarrée")
                print(f"🔍 DEBUG: Paramètres - Époque: {selected_epoch}, Tech: {tech_level}, Social: {social_change}, Fantasy: {fantasy_elements}")

                prompt = generate_prompt(selected_epoch, tech_level, social_change, fantasy_elements, story_length)
                print(f"📝 DEBUG: Prompt généré: {prompt[:200]}...")

                # Appel à l'API Hugging Face ou fallback
                print("🌐 DEBUG: Appel de l'API Hugging Face...")
                generated_story = call_huggingface_api(prompt)

                if not generated_story:
                    print("⚠️ DEBUG: API a retourné None, utilisation du fallback")
                    # Si l'API échoue, utilise le fallback
                    generated_story = generate_fallback_story(prompt)
                    st.info("🎭 Histoire générée en mode hors-ligne (API Hugging Face indisponible)")
                else:
                    print(f"✅ DEBUG: Histoire générée avec succès: {len(generated_story)} caractères")

                # Stockage dans la session avec historique
                print("💾 DEBUG: Stockage dans la session...")

                # Initialiser l'historique s'il n'existe pas
                if 'story_history' not in st.session_state:
                    st.session_state.story_history = []

                # Créer l'entrée d'historique
                story_entry = {
                    'story': generated_story,
                    'epoch': selected_epoch,
                    'tech_level': tech_level,
                    'social_change': social_change,
                    'fantasy_elements': fantasy_elements,
                    'story_length': story_length,
                    'timestamp': pd.Timestamp.now(),
                    'analysis': analyze_text(generated_story)
                }

                # Ajouter au début de l'historique (le plus récent en premier)
                st.session_state.story_history.insert(0, story_entry)

                # Limiter l'historique à 10 récits pour éviter l'encombrement
                if len(st.session_state.story_history) > 10:
                    st.session_state.story_history = st.session_state.story_history[:10]

                # Garder les variables pour l'affichage principal
                st.session_state.current_story = generated_story
                st.session_state.current_analysis = analyze_text(generated_story)
                print("✅ DEBUG: Génération terminée avec succès")

            except Exception as e:
                print(f"💥 DEBUG: Exception dans le bouton: {str(e)}")
                import traceback
                print(f"📍 DEBUG: Traceback complet: {traceback.format_exc()}")

                st.error(f"Erreur lors de la génération : {str(e)}")
                # Génération de fallback en cas d'erreur
                try:
                    prompt = generate_prompt(selected_epoch, tech_level, social_change, fantasy_elements, story_length)
                    generated_story = generate_fallback_story(prompt)

                    # Initialiser l'historique s'il n'existe pas
                    if 'story_history' not in st.session_state:
                        st.session_state.story_history = []

                    # Créer l'entrée d'historique pour le fallback
                    story_entry = {
                        'story': generated_story,
                        'epoch': selected_epoch,
                        'tech_level': tech_level,
                        'social_change': social_change,
                        'fantasy_elements': fantasy_elements,
                        'story_length': story_length,
                        'timestamp': pd.Timestamp.now(),
                        'analysis': analyze_text(generated_story),
                        'is_fallback': True
                    }

                    st.session_state.story_history.insert(0, story_entry)

                    if len(st.session_state.story_history) > 10:
                        st.session_state.story_history = st.session_state.story_history[:10]

                    st.session_state.current_story = generated_story
                    st.session_state.current_analysis = analyze_text(generated_story)
                    st.info("🎭 Histoire générée en mode hors-ligne")
                    print("🔄 DEBUG: Fallback appliqué avec succès")
                except Exception as fallback_error:
                    print(f"💥 DEBUG: Erreur même dans le fallback: {str(fallback_error)}")
                    st.error(f"Erreur critique: {str(fallback_error)}")

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

    # Section d'historique des récits
    if hasattr(st.session_state, 'story_history') and st.session_state.story_history:
        st.markdown("---")
        st.header(f"📚 Historique des récits ({len(st.session_state.story_history)} récit{'s' if len(st.session_state.story_history) > 1 else ''})")

        # Boutons de gestion
        col_clear, col_info, col_spacer = st.columns([1, 2, 1])
        with col_clear:
            if st.button("🗑️ Vider l'historique"):
                st.session_state.story_history = []
                st.success("Historique vidé !")
                st.rerun()
        with col_info:
            st.info("💡 Cliquez sur un récit pour voir ses détails et paramètres")

        # Affichage de l'historique
        for i, entry in enumerate(st.session_state.story_history):
            # Créer un titre avec emoji indicateur de nouveauté
            title_emoji = "🆕" if i == 0 else "📖"
            title = f"{title_emoji} Récit {i+1} - {entry['epoch']} ({entry['timestamp'].strftime('%H:%M')})"

            with st.expander(title):
                # Affichage des paramètres avec comparaison
                st.markdown("**Paramètres utilisés :**")
                param_cols = st.columns(4)

                # Comparaison avec les paramètres actuels
                current_params = {
                    'tech': tech_level,
                    'social': social_change,
                    'fantasy': fantasy_elements,
                    'length': story_length
                }

                with param_cols[0]:
                    delta = entry['tech_level'] - current_params['tech'] if i > 0 else None
                    st.metric("Tech", entry['tech_level'], delta=delta)
                with param_cols[1]:
                    delta = entry['social_change'] - current_params['social'] if i > 0 else None
                    st.metric("Social", entry['social_change'], delta=delta)
                with param_cols[2]:
                    delta = entry['fantasy_elements'] - current_params['fantasy'] if i > 0 else None
                    st.metric("Fantasy", entry['fantasy_elements'], delta=delta)
                with param_cols[3]:
                    st.write(f"**Longueur:** {entry['story_length']}")
                    if entry['story_length'] != current_params['length']:
                        st.caption(f"(Actuel: {current_params['length']})")

                # Indicateur de source
                if entry.get('is_fallback', False):
                    st.info("🎭 Récit généré en mode hors-ligne")

                # Le récit
                st.markdown("**Récit :**")
                st.write(entry['story'])

                # Mini-analyse
                analysis = entry['analysis']
                st.markdown(f"**Analyse :** {analysis['word_count']} mots • Score de divergence : {analysis['parallel_score']:.1f}%")

                # Bouton pour recharger ce récit comme actuel
                if st.button(f"🔄 Recharger ce récit", key=f"reload_{i}"):
                    st.session_state.current_story = entry['story']
                    st.session_state.current_analysis = entry['analysis']
                    st.success("Récit rechargé dans l'affichage principal !")
                    st.rerun()

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