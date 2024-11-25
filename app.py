import streamlit as st
import pandas as pd
import requests
import plotly.express as px
import plotly.graph_objects as go
import numpy as np

@st.cache_data(ttl=3600)
def fetch_models_data():
    response = requests.get(
        "https://huggingface.co/api/models",
        params={"limit": 10000, "full": "True", "config": "True"}
    )
    if response.status_code == 200:
        data = response.json()
        models_data = []
        for model in data:
            models_data.append({
                "ID": model.get("id"),
                "Auteur": model.get("author"),
                "Gated": model.get("gated"),
                "Inference": model.get("inference"),
                "Dernière modification": model.get("lastModified"),
                "Likes": model.get("likes"),
                "Trending Score": model.get("trendingScore"),
                "Privé": model.get("private"),
                "Téléchargements": model.get("downloads"),
                "Tags": model.get("tags"),
                "Library": model.get("library_name"),
                "Date de création": model.get("createdAt"),
            })
        return pd.DataFrame(models_data)
    else:
        st.error(f"Erreur de chargement des données ({response.status_code})")
        return pd.DataFrame()

def render_datasets_page():
    # Titre principal
    st.markdown("<h1 style='text-align: center; color: #FFD700;'>Catalogue des Modèles Hugging Face</h1>", unsafe_allow_html=True)
    st.markdown(
        "Ce tableau de bord utilise l'API de Hugging Face pour extraire des informations sur les modèles hébergés. "
        "Vous pouvez explorer cette API [ici](https://huggingface.co/spaces/enzostvs/hub-api-playground).",
        unsafe_allow_html=True
    )

    df = fetch_models_data()
    if not df.empty:
        df['Likes'] = pd.to_numeric(df['Likes'], errors='coerce')
        df['Téléchargements'] = pd.to_numeric(df['Téléchargements'], errors='coerce')
        df['Date de création'] = pd.to_datetime(df['Date de création'], errors='coerce')

        # Metrics Section
        col1, col2, col3 = st.columns(3)  # Suppression d'une colonne
        with col1:
            st.metric("Nombre de Modèles", f"{len(df):,}")
        with col2:
            st.metric("Nombre d'Auteurs", f"{df['Auteur'].nunique():,}")  # Nouveau calcul pour les auteurs uniques
        with col3:
            st.metric("Total Téléchargements", f"{df['Téléchargements'].sum():,}")

        # Sidebar filters
        st.sidebar.markdown("### Filtres")
        auteur_filter = st.sidebar.multiselect("Auteur", options=df['Auteur'].dropna().unique())
        tags_filter = st.sidebar.multiselect("Tags", options=pd.Series([tag for sublist in df['Tags'].dropna() for tag in sublist]).unique())

        # Apply Filters
        filtered_df = df.copy()
        if auteur_filter:
            filtered_df = filtered_df[filtered_df['Auteur'].isin(auteur_filter)]
        if tags_filter:
            filtered_df = filtered_df[filtered_df['Tags'].apply(lambda x: any(tag in tags_filter for tag in (x or [])))]

        # Search Bar
        search_query = st.text_input("Rechercher un modèle", value="", placeholder="Par exemple : GPT, LLAMA, MISTRAL ...")
        if search_query:
            filtered_df = filtered_df[filtered_df['ID'].str.contains(search_query, case=False, na=False)]

        # Titre visualisation
        st.markdown("<h2 style='color: #FFD700;'>Modèle le Plus Populaire par Mois</h2>", unsafe_allow_html=True)
        st.markdown("Ce graphique montre le modèle le plus liké chaque mois.")

        # Préparation des données
        timeline_df = filtered_df.copy()
        timeline_df['Mois'] = pd.to_datetime(timeline_df['Date de création']).dt.to_period('M')
        
        # Trouver le top modèle par mois
        top_monthly = timeline_df.sort_values('Likes', ascending=False).groupby('Mois').first().reset_index()
        top_monthly['Mois'] = top_monthly['Mois'].astype(str)
        
        # Créer la visualisation
        fig = go.Figure()
        
        # Ajouter les points pour les top modèles
        fig.add_trace(go.Scatter(
            x=pd.to_datetime(top_monthly['Mois']),
            y=top_monthly['Likes'],
            mode='markers+text',
            marker=dict(
                color='#FFD700',
                size=8,
                symbol='circle',
            ),
            text=top_monthly['ID'].apply(lambda x: x.split('/')[-1]),  # Juste le nom du modèle
            textposition="top center",
            hovertemplate="<b>%{text}</b><br>" +
                         "Likes: %{y}<br>" +
                         "Date: %{x|%B %Y}<br>" +
                         "<extra></extra>"
        ))
        
        # Ajouter des lignes entre les points
        fig.add_trace(go.Scatter(
            x=pd.to_datetime(top_monthly['Mois']),
            y=top_monthly['Likes'],
            mode='lines',
            line=dict(color='#FFD700', width=1, dash='dot'),
            hoverinfo='skip'
        ))
        
        # Mise en page
        fig.update_layout(
            title="Modèle le Plus Populaire par Mois",
            xaxis_title="Date",
            yaxis_title="Nombre de Likes",
            template="plotly_dark",
            showlegend=False,
            height=400,
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            yaxis=dict(gridcolor='rgba(128,128,128,0.2)'),
            xaxis=dict(gridcolor='rgba(128,128,128,0.2)'),
            hoverlabel=dict(
                bgcolor="black",
                font_size=12
            )
        )
        
        # Afficher le graphique
        st.plotly_chart(fig, use_container_width=True)

        # Tags Word Cloud
        st.markdown("<h2 style='color: #FFD700;'>Camembert des Tags</h2>", unsafe_allow_html=True)
        st.markdown("Cette visualisation représente les tags les plus fréquents dans les modèles.")

        tags_series = pd.Series([tag for sublist in filtered_df['Tags'].dropna() for tag in sublist])
        if not tags_series.empty:
            tag_counts = tags_series.value_counts().reset_index(name="count")
            fig_tags = px.pie(
                tag_counts.head(10),
                names="index",
                values="count",
                title="Top 10 Tags",
                color_discrete_sequence=px.colors.sequential.Sunset
            )
            st.plotly_chart(fig_tags, use_container_width=True)
            st.markdown("**Interprétation :** Ce camembert montre les thèmes dominants parmi les modèles disponibles.")

        # Liste des modèles
        st.markdown("<h2 style='color: #FFD700;'>Liste des Modèles</h2>", unsafe_allow_html=True)
        st.markdown("Ce tableau affiche les modèles disponibles après application des filtres et critères de recherche.")
        st.dataframe(filtered_df[[
            "ID", "Auteur", "Gated", "Inference", "Dernière modification",
            "Likes", "Trending Score", "Téléchargements", "Tags", "Library", "Date de création"
        ]])  # Suppression de la colonne "Privé"
    else:
        st.error("Aucune donnée disponible.")


if __name__ == "__main__":
    from accueil import main
    main()