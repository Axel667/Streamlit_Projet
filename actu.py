import pandas as pd
import re
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from eventregistry import *
import matplotlib.pyplot as plt
import seaborn as sns
import matplotlib.dates as mdates

# Charger le CSS personnalisé
with open("style.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# Afficher le logo Event Registry
st.image("https://eventregistry.org/img/er-logo-transparent.png", width=50)

# Titre principal
st.markdown("<h1 class='title'>Analyse des Articles sur les LLM</h1>", unsafe_allow_html=True)
st.markdown("<p class='subtitle'>Cette application présente une visualisation interactive des articles collectés sur les LLMs (Large Language Models).</p>", unsafe_allow_html=True)

# Configuration de l'API Key
api_key = "YOUR_API_KEY"  # Remplacez par votre propre clé API

# Collecter les articles via EventRegistry
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

# Charger les articles dans un DataFrame
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

# Copie du DataFrame
df_articles_llm = df_articles.copy()

# --- Ajout des filtres dans la barre latérale ---
st.sidebar.header("Options de Filtrage")

# Filtre par pays
countries = df_articles_llm['country'].dropna().unique()
selected_countries = st.sidebar.multiselect("Pays", options=countries, default=countries)

# Filtre par date
min_date = df_articles_llm['date'].min()
max_date = df_articles_llm['date'].max()
selected_dates = st.sidebar.date_input("Période", [min_date, max_date])

# Filtre par sentiment
sentiment_range = st.sidebar.slider("Sentiment", min_value=-1.0, max_value=1.0, value=(-1.0, 1.0))

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

# --- Carte interactive ---
st.markdown("<h2 class='subtitle'>Carte des Articles par Pays</h2>", unsafe_allow_html=True)

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
    projection='mercator',  # Changement de la projection à Mercator (projection plate)
    title="Carte des Sentiments Moyens par Pays"
)

# Ajuster la barre de couleurs pour afficher les valeurs réelles du sentiment moyen
fig_map.update_coloraxes(
    colorbar=dict(
        title='Sentiment Moyen',
    )
)

# Personnaliser le fond de la carte pour une meilleure esthétique
fig_map.update_geos(
    visible=True,
    resolution=50,
    showcountries=True, countrycolor="LightGray",
    showland=True, landcolor="rgb(240, 240, 240)",  # Couleur plus claire pour les terres
    showocean=True, oceancolor="rgb(224, 224, 224)",  # Couleur grise douce pour les océans
    showlakes=True, lakecolor="rgb(224, 224, 224)",
    showrivers=True, rivercolor="rgb(224, 224, 224)",
    projection_type='mercator'  # Assurer que la projection est bien Mercator
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

# --- Graphique temporel ---
st.markdown("<h2 class='subtitle'>Évolution du Nombre d'Articles et du Sentiment Moyen</h2>", unsafe_allow_html=True)

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
    title='Nombre d\'articles et Sentiment Moyen au fil du temps',
    hovermode='x unified'
)

st.plotly_chart(fig_time, use_container_width=True)

# --- Camembert du Nombre d'Articles par Pays ---
st.markdown("<h2 class='subtitle'>Répartition des Articles par Pays</h2>", unsafe_allow_html=True)

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

# --- Affichage du DataFrame Filtré ---
st.markdown("<h2 class='subtitle'>Données Filtrées</h2>", unsafe_allow_html=True)
st.dataframe(df_filtered)

# Bouton de téléchargement
csv = df_filtered.to_csv(index=False)
st.download_button(
    label="Télécharger les données filtrées en CSV",
    data=csv,
    file_name='donnees_filtrees.csv',
    mime='text/csv',
)