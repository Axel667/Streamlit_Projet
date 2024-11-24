import streamlit as st
from app import render_datasets_page
from benchmark import render_benchmarks_page
from actu import render_actu_page  # Nouvel import

def render_accueil_page():
    st.markdown("<h1 style='text-align: center; color: #FFD700;'>Bienvenue sur HuggingFace Explorer</h1>", unsafe_allow_html=True)
    
    st.markdown("<h3 style='text-align: center; color: #FFD700;'>Contexte du Projet</h3>", unsafe_allow_html=True)

    st.markdown("""
    Ce projet est en lien avec notre projet IA de finetuning de LLM. Cette app permet d'explorer les LLM en open data via leur fine-tuning, avec une analyse approfondie des modèles et des données.
    """)

    st.markdown("<h3 style='text-align: center; color: #FFD700;'>Fonctionnalités</h3>", unsafe_allow_html=True)

    # Contenu de la page d'accueil
    st.markdown("""
    - **Catalogue des Modèles** : Explorez et visualisez les modèles Hugging Face (populaires, thèmes, téléchargements).
    - **Benchmarks** : Analysez les performances des modèles via des données de référence.
    - **Actualités** : Consultez et filtrez les articles sur les LLM selon le sentiment, la période ou les pays.
    """)

def main():
    # Initialisation de session_state
    if "active_page" not in st.session_state:
        st.session_state["active_page"] = "🏠 Accueil"

    # Style de la sidebar
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

    # Navigation
    st.sidebar.markdown("<div class='sidebar-nav'>", unsafe_allow_html=True)
    
    pages = {
        "🏠 Accueil": render_accueil_page,
        "🔍 Modèles": render_datasets_page,
        "📊 Benchmarks": render_benchmarks_page,
        "📰 Actualités": render_actu_page  # Nouvelle page
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

    # Afficher la page active
    pages[st.session_state["active_page"]]()

if __name__ == "__main__":
    st.set_page_config(
        page_title="Hugging Face Explorer - Accueil",
        layout="wide",
        page_icon="🤗"
    )
    main()