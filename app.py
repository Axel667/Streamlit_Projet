import requests
import pandas as pd
import streamlit as st
import plotly.express as px

#streamlit run app.py

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

# Faire la requête à l'API
response = requests.get(
    "https://huggingface.co/api/models",
    params={"limit": 10000, "full": "True", "config": "True"},
    headers={}
)

# Vérifier que la requête est réussie
if response.status_code == 200:
    data = response.json()  # Récupérer le contenu JSON de la réponse
    
    # Extraire les informations principales de chaque modèle dans une liste de dictionnaires
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
            
    # Convertir la liste de dictionnaires en DataFrame
    df = pd.DataFrame(models_data)
    
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

else:
    st.error(f"Erreur lors de la requête : {response.status_code}")