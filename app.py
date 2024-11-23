import streamlit as st
import pandas as pd
import requests
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
from benchmark import render_benchmarks_page


# Supprimer la configuration de page ici car elle sera gérée par accueil.py
# st.set_page_config(...)

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
    st.markdown("<h1 style='text-align: center; color: #FFD700;'>Catalogue des Modèles Hugging Face</h1>", unsafe_allow_html=True)

    df = fetch_models_data()
    if not df.empty:
        df['Likes'] = pd.to_numeric(df['Likes'], errors='coerce')
        df['Téléchargements'] = pd.to_numeric(df['Téléchargements'], errors='coerce')
        df['Date de création'] = pd.to_datetime(df['Date de création'], errors='coerce')

        # Metrics Section
        st.markdown("### 🚀 Aperçu des Modèles")
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Nombre de Modèles", f"{len(df):,}")
        with col2:
            st.metric("Total Likes", f"{df['Likes'].sum():,}")
        with col3:
            st.metric("Total Téléchargements", f"{df['Téléchargements'].sum():,}")
        with col4:
            st.metric("Modèles Privés", f"{df['Privé'].sum()}")

        # Sidebar filters
        st.sidebar.markdown("### 🔍 Filtres")
        auteur_filter = st.sidebar.multiselect("Auteur", options=df['Auteur'].dropna().unique())
        tags_filter = st.sidebar.multiselect("Tags", options=pd.Series([tag for sublist in df['Tags'].dropna() for tag in sublist]).unique())

        # Apply Filters
        filtered_df = df.copy()
        if auteur_filter:
            filtered_df = filtered_df[filtered_df['Auteur'].isin(auteur_filter)]
        if tags_filter:
            filtered_df = filtered_df[filtered_df['Tags'].apply(lambda x: any(tag in tags_filter for tag in (x or [])))]

        # Search Bar
        search_query = st.text_input("Rechercher un modèle", value="")
        if search_query:
            filtered_df = filtered_df[filtered_df['ID'].str.contains(search_query, case=False, na=False)]

        # Data Display
        st.markdown("<h2 style='color: #FFD700;'>📋 Liste des Modèles</h2>", unsafe_allow_html=True)
        st.dataframe(filtered_df[[
            "ID", "Auteur", "Gated", "Inference", "Dernière modification",
            "Likes", "Trending Score", "Privé", "Téléchargements",
            "Tags", "Library", "Date de création"
        ]])

        # Visualizations
        st.markdown("### 📊 Visualisations")

        st.markdown("#### 🏆 Modèle le Plus Populaire par Mois")
        
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
                size=15,
                symbol='star',
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
            title="Modèle le Plus Liké Chaque Mois",
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
        st.markdown("### ☁️ Nuage de Tags")
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
    else:
        st.error("Aucune donnée disponible.")

# ...existing code...

def main():
    # Initialisation de session_state
    if "active_page" not in st.session_state:
        st.session_state["active_page"] = "🏠 Accueil"

    # Ajouter du CSS personnalisé pour la sidebar
    st.markdown("""
        <style>
        .sidebar-nav {
            padding: 10px;
            border-radius: 10px;
            background-color: #262730;
        }
        .nav-button {
            width: 100%;
            padding: 10px;
            margin: 5px 0;
            border: 2px solid #FFD700;
            border-radius: 5px;
            background-color: transparent;
            color: #FFD700;
            transition: all 0.3s;
        }
        .nav-button:hover, .nav-button.active {
            background-color: #FFD700;
            color: #262730;
        }
        </style>
    """, unsafe_allow_html=True)

    # Logo et titre dans la sidebar
    st.sidebar.markdown(
        "<h1 style='text-align: center; padding: 20px 0; border-bottom: 2px solid #FFD700;'>"
        "🤗 Hugging Face Explorer</h1>", 
        unsafe_allow_html=True
    )

    # Navigation améliorée
    st.sidebar.markdown("<div class='sidebar-nav'>", unsafe_allow_html=True)
    
    # Importer la fonction d'accueil
    from accueil import render_accueil_page
    
    pages = {
        "🏠 Accueil": render_accueil_page,
        "🔍 Modèles": render_datasets_page,
        "📊 Benchmarks": render_benchmarks_page
    }
    
    for page_name in pages:
        if st.sidebar.button(
            page_name, 
            key=page_name,
            help=f"Aller à {page_name}",
            use_container_width=True,
            type="primary" if st.session_state["active_page"] == page_name else "secondary"
        ):
            st.session_state["active_page"] = page_name
    
    st.sidebar.markdown("</div>", unsafe_allow_html=True)

    # Render the active page
    pages[st.session_state["active_page"]]()


if __name__ == "__main__":
    from accueil import main
    main()