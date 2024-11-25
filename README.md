# Streamlit Projet

Bienvenue dans le projet **Hugging Face Explorer**, une application interactive développée pour explorer et analyser les modèles de langage open source hébergés sur la plateforme Hugging Face. Ce projet a été conçu dans le cadre de notre projet Open Data en lien avec notre projet IA du second semestre, avec un objectif principal : identifier et analyser les modèles les plus pertinents pour un projet de fine-tuning sur des modèles de langage (LLM).

---

## Contexte du Projet

Ce projet a pour but de fournir une plateforme intuitive et riche en données, permettant de :
- Explorer les modèles de langage open source et leurs caractéristiques (auteurs, tags, téléchargements, etc.).
- Comparer les performances des modèles sur des métriques standardisées telles que **IFEval**, **BBH**, ou encore **MATH Lvl 5**.
- Agréger et visualiser des actualités récentes sur les LLM pour rester informé des dernières tendances.

L'application est développée avec **Streamlit**, en s'appuyant sur les API et datasets disponibles sur Hugging Face et d'autres plateformes.

---

## Fonctionnalités Principales

### 1. Catalogue des Modèles
- S'appuie sur l'[API Hugging Face](https://huggingface.co/spaces/enzostvs/hub-api-playground) pour extraire des informations telles que les auteurs, les tags, les téléchargements, et les tendances de popularité.
- **Visualisations :**
  - Un graphique temporel pour afficher le modèle le plus populaire chaque mois.
    <img src="/images/1_temp.png" alt="Modèle le plus populaire par mois" width="600">
  - Un camembert représentant les tags les plus fréquents parmi les modèles.
    <img src="/images/top_10tag.png" alt="Camembert des tags" width="600">

### 2. Benchmarks
- Compare les performances des modèles à l'aide du [dataset Open LLM Leaderboard](https://huggingface.co/spaces/open-llm-leaderboard/open_llm_leaderboard).
- **Visualisations :**
  - Un graphique linéaire pour suivre l'évolution des performances des modèles par type.
    <img src="/images/perf_evol.png" alt="Évolution des performances par type de modèle" width="600">
  - Un diagramme circulaire montrant la répartition des types de modèles disponibles.
    <img src="/images/Distribution_type.png" alt="Répartition des types de modèles" width="600">
  - Une courbe illustrant l'empreinte carbone cumulée des modèles.
    <img src="/images/Co2.png" alt="Coût CO₂ cumulé au fil du temps" width="600">
  - Un nuage de points examinant la relation entre performances, coût CO₂, et taille des paramètres.
    <img src="/images/score_co2.png" alt="Score vs Coût CO₂" width="600">

### 3. Actualités
- Agrège les articles récents sur les LLM via l'[API EventRegistry](https://newsapi.ai/documentation?tab=introduction).
- **Visualisations :**
  - Une carte géographique représentant la répartition des articles par pays et leur sentiment moyen.
    <img src="/images/map.png" alt="Carte géographique des articles" width="600">
  - Un graphique à double axe montrant l'évolution du nombre d'articles publiés et de leur sentiment moyen.
    <img src="/images/evol_article.png" alt="Évolution temporelle des articles" width="600">
  - Un diagramme circulaire mettant en évidence les pays produisant le plus d'articles.
    <img src="/images/repartition_article_pays.png" alt="Répartition des articles par pays" width="600">

---

## Comment cloner et exécuter le projet localement

### Prérequis
Avant de commencer, assurez-vous d'avoir installé les éléments suivants sur votre ordinateur :
- **Python 3.8 ou version supérieure** : [Télécharger Python](https://www.python.org/downloads/)
- **Git** : [Télécharger Git](https://git-scm.com/downloads)
- **pip** : Inclut avec Python. Si ce n'est pas disponible, installez-le avec la commande `python -m ensurepip`.

---

### Étapes pour cloner et exécuter le projet

1. **Cloner le dépôt**
   Ouvrez un terminal ou une invite de commande et exécutez la commande suivante :
   ```bash
   git clone https://github.com/Axel667/Streamlit_Projet.git

1. **Naviguer dans le dossier du projet**
    Déplacez-vous dans le dossier où le projet a été cloné :
    ```bash
    cd path

3.	**Installer les dépendances**
    Utilisez pip pour installer les bibliothèques nécessaires : 
    ```bash
    pip install -r requirements.txt

4.	**Lancer l’application Streamlit**
    Lancez l’application en exécutant la commande suivante :    ```bash
    streamlit run app.py

---