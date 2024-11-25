# Streamlit_Projet
[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://streamlit.io)

# Hugging Face Explorer 🤗

Bienvenue dans le projet **Hugging Face Explorer**, une application interactive développée pour explorer et analyser les modèles de langage open source hébergés sur la plateforme Hugging Face. Ce projet a été conçu dans le cadre de notre projet en Open data en lien avec notre projet IA du second semestre, avec un objectif principal : identifier et analyser les modèles les plus pertinents pour un projet de fine-tuning sur des modèles de langage (LLM).

# How to Clone and Run the Project Locally

## Prerequisites
Before starting, make sure you have the following installed on your computer:
- **Python 3.8 or higher**: [Download Python](https://www.python.org/downloads/)
- **Git**: [Download Git](https://git-scm.com/downloads)
- **pip**: Comes with Python. If not available, install it using `python -m ensurepip`.

---

## Steps to Clone and Run the Project

1. **Clone the Repository**
   Open a terminal or command prompt and run the following command:
   ```bash
   git clone https://github.com/Axel667/Streamlit_Projet.git

2. **Navigate to the Project Folder**
    Move into the folder where the project was cloned:
   ```bash
    cd path

3.	**Install Dependencies**
Use pip to install the required libraries:
    ```bash
    pip install -r requirements.txt

4.	**Run the Streamlit Application**
Launch the app by running the following command:
    ```bash
    streamlit run app.py

---

## 📝 Contexte du Projet

Ce projet a pour but de fournir une plateforme intuitive et riche en données, permettant de :
- Explorer les modèles de langage open source et leurs caractéristiques (auteurs, tags, téléchargements, etc.).
- Comparer les performances des modèles sur des métriques standardisées telles que **IFEval**, **BBH**, ou encore **MATH Lvl 5**.
- Agréger et visualiser des actualités récentes sur les LLM pour rester informé des dernières tendances.

L'application est développée avec **Streamlit**, en s'appuyant sur les API et datasets disponibles sur Hugging Face et d'autres plateformes.

---

## 🚀 Fonctionnalités Principales

### 1. Catalogue des Modèles
- S'appuie sur l'API Hugging Face pour extraire des informations telles que les auteurs, les tags, les téléchargements, et les tendances de popularité.
- **Visualisations :**
  - Un graphique temporel pour afficher le modèle le plus populaire chaque mois.
  ![Modèle le plus populaire par mois](/images/1_temp.png)
  - Un camembert représentant les tags les plus fréquents parmi les modèles.
  ![Camembert des tags](/images/top_10tag.png)

### 2. Benchmarks
- Compare les performances des modèles à l'aide du dataset **Open LLM Leaderboard**.
- **Visualisations :**
  - Un graphique linéaire pour suivre l'évolution des performances des modèles par type.
  ![Évolution des performances par type de modèle](/images/perf_evol.png)
  - Un diagramme circulaire montrant la répartition des types de modèles disponibles.
  ![Répartition des types de modèles](/images/Distribution_type.png)
  - Une courbe illustrant l'empreinte carbone cumulée des modèles.
  ![Coût CO₂ cumulé au fil du temps](/images/Co2.png)
  - Un nuage de points examinant la relation entre performances, coût CO₂, et taille des paramètres.
  ![Score vs Coût CO₂](/images/score_co2.png)

### 3. Actualités
- Agrège les articles récents sur les LLM via l'API **EventRegistry**.
- **Visualisations :**
  - Une carte géographique représentant la répartition des articles par pays et leur sentiment moyen.
  ![Carte géographique des articles](/images/map.png)
  - Un graphique à double axe montrant l'évolution du nombre d'articles publiés et de leur sentiment moyen.
  ![Évolution temporelle des articles](/images/evol_article.png)
  - Un diagramme circulaire mettant en évidence les pays produisant le plus d'articles.
  ![Répartition des articles par pays](/images/repartition_article_pays.png)

---