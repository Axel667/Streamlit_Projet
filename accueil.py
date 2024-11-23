import streamlit as st

# Import des fonctions de rendu après render_accueil_page pour éviter les imports circulaires
def render_accueil_page():
    st.markdown("<h1 style='text-align: center; color: #FFD700;'>Bienvenue sur HuggingFace Explorer</h1>", unsafe_allow_html=True)
    
    # Contenu de la page d'accueil
    st.markdown("""
    ### 🎯 Notre Mission
    
    Ce site a pour but d'explorer et d'analyser les modèles open source disponibles sur HuggingFace. 
    
    ### 📚 Contexte du Projet
    
    Ce projet a été développé dans le cadre de notre projet IA avec plusieurs objectifs :
    
    - 🔍 Explorer la diversité des modèles disponibles
    - 📊 Analyser les performances des différents modèles
    - 🌍 Évaluer l'impact environnemental des modèles
    - 💡 Comprendre les tendances dans le développement des LLMs
    
    ### 🚀 Fonctionnalités
    
    - **Catalogue des Modèles** : Explorez la base de données complète des modèles
    - **Benchmarks** : Analysez les performances des modèles LLM
    - **Visualisations** : Découvrez des graphiques interactifs et des analyses détaillées
    
    ### 👥 Navigation
    
    Utilisez le menu de gauche pour naviguer entre les différentes sections du site.
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
    
    from app import render_datasets_page
    from benchmark import render_benchmarks_page
    
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

    # Afficher la page active
    pages[st.session_state["active_page"]]()

if __name__ == "__main__":
    st.set_page_config(
        page_title="Hugging Face Explorer - Accueil",
        layout="wide",
        page_icon="🤗"
    )
    main()