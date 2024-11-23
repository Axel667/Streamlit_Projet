import pandas as pd
import re
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from eventregistry import *
import matplotlib.pyplot as plt
import seaborn as sns
import matplotlib.dates as mdates

def render_actu_page():
    # Titre avec le style Hugging Face
    st.markdown("<h1 style='text-align: center; color: #FFD700;'>Actualités des LLMs</h1>", unsafe_allow_html=True)
    
    # Configuration de l'API Key
    api_key = "6d15fe13-b16a-4080-bbff-dc81f97f3d0d"

    # Fonction pour récupérer les articles
    @st.cache_data
    def get_articles():
        er = EventRegistry(apiKey=api_key)

        # Colonnes à inclure
        columns_to_include = [
            'lang', 'url', 'sentiment', 'date', 'relevance', 'title', 'location', 'isDuplicate', 'sim'
        ]

        articles = []
        q = QueryArticlesIter(keywords=QueryItems.AND(["LLM", "model"]), lang="eng")

        # Exécuter la requête et récupérer tous les résultats
        for art in q.execQuery(er,
                               returnInfo=ReturnInfo(
                                   articleInfo=ArticleInfoFlags(
                                       concepts=True, 
                                       categories=True, 
                                       location=True, 
                                       image=True, 
                                       links=True, 
                                       videos=True
                                   ))):
            article_data = {col: art.get(col, None) for col in columns_to_include}
            articles.append(article_data)
        
        return pd.DataFrame(articles)

    # Charger les articles
    df_articles = get_articles()

    # Prétraitement des données
    df_articles['date'] = pd.to_datetime(df_articles['date'])
    
    def extract_country_from_object(location_entry):
        if isinstance(location_entry, dict):
            return location_entry.get('country', {}).get('label', {}).get('eng', None)
        elif isinstance(location_entry, str):
            match = re.search(r"'country': \{.*?'label': \{'eng': '(.*?)'\}", location_entry)
            if match:
                return match.group(1)
        return None

    df_articles['country'] = df_articles['location'].apply(extract_country_from_object)
    df_articles.drop(columns=['location'], inplace=True)
    df_articles = df_articles.dropna(subset=['country'])
    df_articles_llm = df_articles.copy()

    # Metrics Section
    st.markdown("### 📰 Aperçu des Articles")
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Articles", f"{len(df_articles_llm):,}")
    with col2:
        st.metric("Pays Couverts", f"{df_articles_llm['country'].nunique():,}")
    with col3:
        avg_sentiment = df_articles_llm['sentiment'].mean()
        st.metric("Sentiment Moyen", f"{avg_sentiment:.2f}")
    with col4:
        recent_articles = df_articles_llm[df_articles_llm['date'] >= (pd.Timestamp.now() - pd.Timedelta(days=7))].shape[0]
        st.metric("Articles (7 derniers jours)", f"{recent_articles:,}")

    # Sidebar filters
    st.sidebar.markdown("### 🔍 Filtres")
    
    # Filtres existants avec style mis à jour
    countries = df_articles_llm['country'].dropna().unique()
    selected_countries = st.sidebar.multiselect(
        "Pays",
        options=countries,
        default=countries,
        help="Sélectionner un ou plusieurs pays"
    )

    min_date = df_articles_llm['date'].min()
    max_date = df_articles_llm['date'].max()
    selected_dates = st.sidebar.date_input(
        "Période",
        [min_date, max_date],
        help="Sélectionner une période"
    )

    sentiment_range = st.sidebar.slider(
        "Sentiment",
        min_value=-1.0,
        max_value=1.0,
        value=(-1.0, 1.0),
        help="Filtrer par score de sentiment"
    )

    # Appliquer les filtres
    df_filtered = df_articles_llm[
        (df_articles_llm['country'].isin(selected_countries)) &
        (df_articles_llm['date'] >= pd.to_datetime(selected_dates[0])) &
        (df_articles_llm['date'] <= pd.to_datetime(selected_dates[1])) &
        (df_articles_llm['sentiment'] >= sentiment_range[0]) &
        (df_articles_llm['sentiment'] <= sentiment_range[1])
    ]

    # Champ de recherche dans les titres
    search_query = st.sidebar.text_input("Recherche dans les titres")
    if search_query:
        df_filtered = df_filtered[df_filtered['title'].str.contains(search_query, case=False, na=False)]

    # Rest of visualizations with updated styling
    st.markdown("### 🗺️ Distribution Géographique")
    st.markdown("Cette carte montre la quantité et le sentiment global des articles sur les LLM dans le monde.")

    # Calcul du nombre d'articles et du sentiment moyen par pays
    country_stats = df_filtered.groupby('country').agg(
        num_articles=('country', 'size'),
        avg_sentiment=('sentiment', 'mean')
    ).reset_index()

    # Définir une échelle de couleurs personnalisée basée sur les valeurs réelles de avg_sentiment
    color_scale = px.colors.sequential.YlGn  # Gradient du jaune au vert

    # Créer le graphique avec des cercles représentant le nombre d'articles et le sentiment moyen
    fig_map = px.scatter_geo(
        country_stats,
        locations='country',
        locationmode='country names',
        hover_name='country',
        size='num_articles',
        size_max=40,
        color='avg_sentiment',
        color_continuous_scale=color_scale,
        title=False
    )

    # Ajuster la barre de couleurs pour afficher les valeurs réelles du sentiment moyen
    fig_map.update_coloraxes(
        colorbar=dict(
            title='Sentiment Moyen',
        )
    )

    # Activer les interactions de zoom et de pan
    fig_map.update_layout(
        geo=dict(
            projection_scale=1,
            center=dict(lat=0, lon=0),
        ),
        margin={"r":0,"t":50,"l":0,"b":0}  # Ajusté le haut pour le titre
    )

    # Configuration pour activer le zoom et le pan
    config = {
        'scrollZoom': True,     # Active le zoom avec la molette de la souris
        'doubleClick': 'reset', # Active le zoom sur double-clic
        'displayModeBar': True, # Affiche la barre de mode
        'staticPlot': False     # Permet toutes les interactions
    }

    st.plotly_chart(fig_map, use_container_width=True, config=config)

    st.markdown("### 📈 Tendances Temporelles")
    st.markdown("Ce graphique montre le nombre d'articles et le sentiment moyen au cours du temps.")

    time_stats = df_filtered.groupby('date').agg(
        num_articles=('sentiment', 'size'),
        avg_sentiment=('sentiment', 'mean')
    ).reset_index().sort_values('date')

    fig_time = go.Figure()

    # Nombre d'articles
    fig_time.add_trace(go.Bar(
        x=time_stats['date'],
        y=time_stats['num_articles'],
        name='Nombre d\'articles',
        marker_color='skyblue',
        yaxis='y1'
    ))

    # Sentiment moyen
    fig_time.add_trace(go.Scatter(
        x=time_stats['date'],
        y=time_stats['avg_sentiment'],
        name='Sentiment Moyen',
        marker_color='firebrick',
        yaxis='y2',
        mode='lines+markers'
    ))

    # Mise à jour des axes
    fig_time.update_layout(
        xaxis=dict(title='Date'),
        yaxis=dict(
            title='Nombre d\'articles',
            titlefont=dict(color='skyblue'),
            tickfont=dict(color='skyblue'),
            anchor='x',
            side='left'
        ),
        yaxis2=dict(
            title='Sentiment Moyen',
            titlefont=dict(color='firebrick'),
            tickfont=dict(color='firebrick'),
            overlaying='y',
            side='right'
        ),
        legend=dict(x=0.1, y=1.1, orientation='h'),
        title=False,
        hovermode='x unified'
    )

    st.plotly_chart(fig_time, use_container_width=True)

    st.markdown("### 🥧 Répartition par Pays")
    st.markdown("Ce graphique montre quel pays produit le plus d'articles sur les LLM dans notre base.")

    # Calculer le nombre d'articles par pays
    country_counts = df_filtered['country'].value_counts().reset_index()
    country_counts.columns = ['country', 'num_articles']

    # Créer le camembert avec une palette de couleurs qualitative
    fig_pie = px.pie(
        country_counts,
        names='country',
        values='num_articles',
        title= False,
        hole=0.4,  # Optionnel : crée un "donut chart"
        color_discrete_sequence=px.colors.qualitative.Set3  # Palette qualitative avec des couleurs différenciées
    )

    # Personnaliser le style du camembert
    fig_pie.update_traces(textposition='inside', textinfo='percent+label')

    st.plotly_chart(fig_pie, use_container_width=True)

    # Data display with improved styling
    st.markdown("### 📋 Articles Détaillés")
    st.dataframe(
        df_filtered.style.format({
            'sentiment': '{:.2f}',
            'date': lambda x: x.strftime('%Y-%m-%d')
        })
    )

    # Download button with Hugging Face style
    csv = df_filtered.to_csv(index=False)
    st.download_button(
        label="📥 Télécharger les Données (CSV)",
        data=csv,
        file_name='articles_llm.csv',
        mime='text/csv',
        help="Télécharger les données filtrées au format CSV"
    )

if __name__ == "__main__":
    from accueil import main
    main()