import streamlit as st
import pandas as pd
import requests
import plotly.express as px
import plotly.graph_objects as go

# Set page configuration
st.set_page_config(
    page_title="Catalogue des Modèles Hugging Face",
    layout="wide",
    page_icon="🤗"
)

# Main function
def main():
    # Sidebar with Hugging Face branding
    st.sidebar.markdown("<h1 style='color: #FFD700;'>🤗 Hugging Face</h1>", unsafe_allow_html=True)
    st.sidebar.markdown("<p style='color: #FFD700;'>Explorez les modèles et benchmarks.</p>", unsafe_allow_html=True)
    
    pages = {"Modèles": render_datasets_page, "Benchmarks": render_benchmarks_page}
    selected_page = st.sidebar.radio("Navigation", options=list(pages.keys()))

    # Display the selected page
    pages[selected_page]()

@st.cache_data(ttl=3600)
def fetch_models_data():
    # Fetch data from Hugging Face API
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
                "Licence": model.get("cardData", {}).get("license"),
                "Langues": model.get("cardData", {}).get("language", ""),
                "Likes": model.get("likes"),
                "Téléchargements": model.get("downloads"),
                "Tâches": model.get("pipeline_tag"),
                "Date de création": model.get("createdAt")
            })
        return pd.DataFrame(models_data)
    else:
        st.error(f"Erreur de chargement des données ({response.status_code})")
        return pd.DataFrame()

def render_datasets_page():
    st.markdown("<h1 style='text-align: center; color: #FFD700;'>Catalogue des Modèles Hugging Face</h1>", unsafe_allow_html=True)

    # Fetch data
    df = fetch_models_data()
    if not df.empty:
        # Data transformation
        df['Likes'] = pd.to_numeric(df['Likes'], errors='coerce')
        df['Téléchargements'] = pd.to_numeric(df['Téléchargements'], errors='coerce')
        df['Date de création'] = pd.to_datetime(df['Date de création'], errors='coerce')

        # Metrics
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Modèles", value=f"{len(df):,}")
        with col2:
            st.metric("Total Likes", value=f"{df['Likes'].sum():,}")
        with col3:
            st.metric("Total Téléchargements", value=f"{df['Téléchargements'].sum():,}")

        # Sidebar filters
        st.sidebar.markdown("### Filtres")
        auteur_filter = st.sidebar.multiselect("Auteur", options=df['Auteur'].dropna().unique())
        langue_filter = st.sidebar.multiselect("Langues", options=df['Langues'].dropna().unique())
        task_filter = st.sidebar.multiselect("Tâches", options=df['Tâches'].dropna().unique())

        # Filter data
        filtered_df = df.copy()
        if auteur_filter:
            filtered_df = filtered_df[filtered_df['Auteur'].isin(auteur_filter)]
        if langue_filter:
            filtered_df = filtered_df[filtered_df['Langues'].str.contains('|'.join(langue_filter), na=False)]
        if task_filter:
            filtered_df = filtered_df[filtered_df['Tâches'].isin(task_filter)]

        # Display table
        st.dataframe(filtered_df[['ID', 'Auteur', 'Licence', 'Langues', 'Tâches', 'Likes', 'Téléchargements']])

        # Visualizations
        st.markdown("### Visualisations")
        col1, col2 = st.columns(2)

        with col1:
            fig = px.pie(filtered_df, names="Langues", title="Répartition par Langue", color_discrete_sequence=["#FFD700"])
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            task_counts = filtered_df['Tâches'].value_counts().reset_index()
            fig = px.bar(task_counts, x='index', y='Tâches', title="Top Tâches", color_discrete_sequence=["#FFD700"])
            st.plotly_chart(fig, use_container_width=True)
    else:
        st.error("Aucune donnée disponible.")

def render_benchmarks_page():
    st.markdown("<h1 style='text-align: center; color: #FFD700;'>Benchmarks des Modèles</h1>", unsafe_allow_html=True)
    st.write("Cette section est en cours de développement.")

if __name__ == "__main__":
    main()