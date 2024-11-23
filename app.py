import streamlit as st
from benchmark import render_benchmarks_page
import requests
import pandas as pd
import plotly.express as px


def render_datasets_page():
    """
    Render the datasets page in Streamlit.
    """
    st.markdown("<h1 class='title'>Catalogue des Modèles Hugging Face</h1>", unsafe_allow_html=True)
    st.markdown("<p class='subtitle'>Ce tableau présente les informations principales de chaque modèle :</p>", unsafe_allow_html=True)

    couleur_principale = "#ffcc00"

    # Fetch datasets from Hugging Face API
    response = requests.get(
        "https://huggingface.co/api/models",
        params={"limit": 10000, "full": "True", "config": "True"},
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
                "Taille des catégories": model.get("cardData", {}).get("size_categories"),
            }
            models_data.append(model_info)

        df = pd.DataFrame(models_data)
        df['Date de création'] = pd.to_datetime(df['Date de création'], errors='coerce')
        df = df.dropna(subset=['Date de création'])

        # Plot datasets trends
        df['Mois'] = df['Date de création'].dt.to_period('M')
        monthly_counts = df.groupby('Mois').size().reset_index(name='Nombre de modèles')
        monthly_counts['Mois'] = monthly_counts['Mois'].dt.to_timestamp()

        st.markdown("<h2 class='subtitle'>Nombre de modèles créés par mois</h2>", unsafe_allow_html=True)
        fig_time_series = px.line(
            monthly_counts,
            x='Mois',
            y='Nombre de modèles',
            title="Nombre de modèles créés par mois",
            labels={"Mois": "Date", "Nombre de modèles": "Nombre de modèles créés"},
            color_discrete_sequence=[couleur_principale],
        )
        st.plotly_chart(fig_time_series)

        st.markdown("<h2 class='subtitle'>Distribution des Likes</h2>", unsafe_allow_html=True)
        fig_likes = px.violin(df, y="Likes", box=True, points="all", title=False)
        st.plotly_chart(fig_likes)
    else:
        st.error(f"Erreur lors de la requête : {response.status_code}")


# Main function
def main():
    # Initialize session state for active page
    if "active_page" not in st.session_state:
        st.session_state.active_page = "datasets"  # Default to datasets page

    # Sidebar Menu
    st.sidebar.title("Menu")
    pages = {
        "datasets": "Datasets",
        "benchmarks": "Benchmarks",
    }

    # Render the menu buttons
    for page_key, page_name in pages.items():
        if st.sidebar.button(page_name):
            st.session_state.active_page = page_key

    # Highlight the active page
    active_page = st.session_state.active_page
    if active_page == "benchmarks":
        render_benchmarks_page()
    elif active_page == "datasets":
        render_datasets_page()


if __name__ == "__main__":
    main()