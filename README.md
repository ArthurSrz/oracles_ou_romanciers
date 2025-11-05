# 📚 Générateur de Récits Parallèles

*"Des récits alternatifs qui émergent d'une réalité statistique construite sur les vestiges de notre passé collectif."*

## Description

Cette application Streamlit génère des histoires alternatives en prenant des événements historiques réels comme point de départ et en créant des variations "parallèles" avec des règles légèrement différentes. Inspirée par l'idée de romanciers qui écrivent dans un monde parallèle dont les lois ressemblent aux nôtres sans jamais tout à fait s'y conformer.

## Fonctionnalités

- **Sélection d'époque historique** : Renaissance, Révolution française, Révolution industrielle, Belle Époque, Années folles
- **Paramètres de divergence** :
  - Niveau de technologie alternative
  - Changements sociaux/politiques
  - Éléments fantastiques subtils
- **Génération de récits** : Utilisation d'Ollama pour créer des nouvelles courtes
- **Analyse du texte** :
  - Comptage de mots et fréquences
  - Score de "divergence" par rapport à la réalité
  - Visualisation avec nuage de mots
- **Sauvegarde** : Export des récits générés

## Installation

### Prérequis

1. **Ollama** doit être installé sur votre machine avec un modèle français (recommandé: `llama3.2`)
   ```bash
   # Installation d'Ollama
   curl -fsSL https://ollama.ai/install.sh | sh

   # Téléchargement du modèle
   ollama pull llama3.2
   ```

2. **Python 3.8+**

### Installation des dépendances

```bash
git clone git@github.com:ArthurSrz/oracles_ou_romanciers.git
cd oracles_ou_romanciers
pip install -r requirements.txt
```

## Utilisation

1. Assurez-vous qu'Ollama est en cours d'exécution :
   ```bash
   ollama serve
   ```

2. Lancez l'application Streamlit :
   ```bash
   streamlit run app.py
   ```

3. Ouvrez votre navigateur à l'adresse indiquée (généralement `http://localhost:8501`)

4. Configurez les paramètres dans la barre latérale :
   - Choisissez une époque historique
   - Ajustez les curseurs de divergence
   - Sélectionnez la longueur du récit

5. Cliquez sur "Générer un récit parallèle" et découvrez votre histoire alternative !

## Structure du projet

```
oracles_ou_romanciers/
├── app.py              # Application Streamlit principale
├── requirements.txt    # Dépendances Python
├── README.md          # Documentation
└── recits/            # Dossier pour les récits sauvegardés (créé automatiquement)
```

## Concept

L'application explore l'idée que l'IA, entraînée sur des données historiques, peut créer des alternatives plausibles qui illustrent parfaitement le concept de "réalité statistique construite sur les vestiges de notre passé". Chaque récit généré propose un "possible" qui émerge de notre histoire collective tout en s'en écartant subtilement.

## Technologies utilisées

- **Streamlit** : Interface web interactive
- **Ollama** : Génération de texte avec modèles locaux
- **WordCloud** : Visualisation des mots-clés
- **Matplotlib** : Graphiques et visualisations
- **Pandas** : Manipulation de données

## Contribution

Les contributions sont les bienvenues ! N'hésitez pas à ouvrir des issues ou des pull requests pour :
- Ajouter de nouvelles époques historiques
- Améliorer les algorithmes d'analyse
- Proposer de nouvelles fonctionnalités

## Licence

Projet open source - voir LICENSE pour plus de détails.