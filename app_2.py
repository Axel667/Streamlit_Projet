import requests
import pandas as pd
import streamlit as st
import plotly.express as px
from pyspark import SparkConf, SparkContext

# Charger le CSS personnalisé
with open("style.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# Afficher le logo Hugging Face
st.image("https://huggingface.co/front/assets/huggingface_logo-noborder.svg", width=50)

# Titre principal
st.markdown("<h1 class='title'>Catalogue des Modèles Hugging Face</h1>", unsafe_allow_html=True)
st.markdown("<p class='subtitle'>Ce tableau présente les informations principales de chaque modèle :</p>", unsafe_allow_html=True)

# Couleur personnalisée pour les graphiques
couleur_principale = "#ffcc00"

# Configuration de Spark
conf = SparkConf().setAppName("HuggingFaceDatasets").setMaster("local[*]")
sc = SparkContext(conf=conf)

# Fonction pour récupérer les données à un offset donné
def fetch_data(offset):
    limit = 1000
    response = requests.get(
        "https://huggingface.co/api/datasets",
        params={"limit": limit, "full": "True", "config": "True", "offset": offset},
        headers={}
    )
    if response.status_code == 200:
        data = response.json()
        models_data = []
        for model in data:
            model_info = {
                "ID": model.get("id"),
                "Auteur": model.get("author"),
                "Dernière modification": model.get("lastModified"),
                "Date de création": model.get("createdAt"),
                "Likes": model.get("likes"),
                "Téléchargements": model.get("downloads"),
                "Tags": model.get("tags"),
                "Description": model.get("description"),
                "Langues": model.get("cardData", {}).get("language"),
                "Taille des catégories": model.get("cardData", {}).get("size_categories")
            }
            models_data.append(model_info)
        return models_data
    else:
        return []

# Déterminer le nombre total de jeux de données (optionnel)
# Vous pouvez définir une estimation ou récupérer ce nombre via une requête si l'API le permet

total_datasets = 100000  # Par exemple, si vous savez qu'il y a environ 5000 jeux de données
limit = 1000
offsets = list(range(0, total_datasets, limit))

# Créer une RDD des offsets
offset_rdd = sc.parallelize(offsets)

# Appliquer la fonction fetch_data à chaque offset en parallèle
all_models_data = offset_rdd.flatMap(fetch_data).collect()

# Arrêter le SparkContext
sc.stop()

# Convertir la liste de dictionnaires en DataFrame
df = pd.DataFrame(all_models_data)

# Convertir la colonne 'Date de création' en format datetime et gérer les valeurs invalides
df['Date de création'] = pd.to_datetime(df['Date de création'], errors='coerce')
df = df.dropna(subset=['Date de création'])

# Grouper par mois et compter les modèles créés chaque mois
df['Mois'] = df['Date de création'].dt.to_period('M')
monthly_counts = df.groupby('Mois').size().reset_index(name='Nombre de modèles')
monthly_counts['Mois'] = monthly_counts['Mois'].dt.to_timestamp()

# Afficher le graphique de tendance des modèles créés par mois avec la couleur principale
st.markdown("<h2 class='subtitle'>Nombre de modèles créés par mois</h2>", unsafe_allow_html=True)
fig_time_series = px.line(
    monthly_counts,
    x='Mois',
    y='Nombre de modèles',
    title="Nombre de modèles créés par mois",
    labels={"Mois": "Date", "Nombre de modèles": "Nombre de modèles créés"},
    color_discrete_sequence=[couleur_principale]
)
fig_time_series.update_traces(line=dict(color=couleur_principale))
st.plotly_chart(fig_time_series)

# Générer le violon plot pour la colonne 'Likes' avec la couleur principale
st.markdown("<h2 class='subtitle'>Distribution des Likes</h2>", unsafe_allow_html=True)
fig_likes = px.violin(df, y="Likes", box=True, points="all", title="Distribution des Likes")
fig_likes.update_traces(marker_color=couleur_principale, line_color=couleur_principale)
st.plotly_chart(fig_likes)