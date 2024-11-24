import pandas as pd
import streamlit as st
import plotly.express as px
from datasets import load_dataset
from bs4 import BeautifulSoup

def fetch_leaderboard_data():
    """
    Fetches data from the Hugging Face Open LLM Leaderboard dataset.
    """
    try:
        dataset = load_dataset("open-llm-leaderboard/contents", split="train")
        df = dataset.to_pandas()

        # Rename columns to match expected names
        df = df.rename(columns={
            "Type": "type",
            "Model": "model_name_html",
            "Submission Date": "submission_date",
            "Average ⬆️": "score",
            "Precision": "precision",
            # Other columns as needed
            "IFEval": "IFEval",
            "BBH": "BBH",
            "CO₂ cost (kg)": "co2_cost_kg",
            "#Params (B)": "params_b",
            "MATH Lvl 5": "MATH Lvl 5",
            "GPQA": "GPQA",
            "MUSR": "MUSR",
            "MMLU-PRO": "MMLU-PRO",
        })

        # Process 'model_name_html' to extract link and display text
        def extract_model_info(html):
            soup = BeautifulSoup(html, 'html.parser')
            first_link = soup.find('a')
            if first_link:
                model_link = first_link['href']
                model_text = first_link.get_text()
                return model_text, model_link
            else:
                return html, ''  # Return the original text if no link found

        df['model_name'], df['model_link'] = zip(*df['model_name_html'].apply(extract_model_info))
        
        # Simplify model names to only show the last part after the last slash
        df['model_name'] = df['model_name'].apply(lambda x: x.split('/')[-1] if isinstance(x, str) and '/' in x else x)

        # Ensure required columns exist
        required_columns = ["precision", "type", "model_name", "submission_date", "score", "model_link", "co2_cost_kg", "params_b"]
        benchmark_metric_columns = ["IFEval", "BBH", "MATH Lvl 5", "GPQA", "MUSR", "MMLU-PRO"]
        required_columns.extend(benchmark_metric_columns)

        missing_columns = [col for col in required_columns if col not in df.columns]
        for col in missing_columns:
            df[col] = None  # Handle missing columns appropriately

        # Convert data types
        df["submission_date"] = pd.to_datetime(df["submission_date"], errors='coerce')
        df["score"] = pd.to_numeric(df["score"], errors='coerce')
        df["co2_cost_kg"] = pd.to_numeric(df["co2_cost_kg"], errors='coerce')
        df["params_b"] = pd.to_numeric(df["params_b"], errors='coerce')

        for col in benchmark_metric_columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')

        return df
    except Exception as e:
        st.error(f"Error fetching leaderboard data: {e}")
        return pd.DataFrame()

def render_benchmarks_page():
    if "active_page" not in st.session_state:
        st.session_state["active_page"] = "🏠 Accueil"

    st.markdown("<h1 class='title'>Tableau de Bord des Modèles LLM Open Source</h1>", unsafe_allow_html=True)
    st.markdown("<p class='subtitle'>Explorez les données de performance des modèles de langage :</p>", unsafe_allow_html=True)

    # Fetch leaderboard data
    df = fetch_leaderboard_data()

    if not df.empty:
        # Check for required columns
        required_columns = ["precision", "type", "model_name", "submission_date", "score", "model_link", "co2_cost_kg", "params_b"]
        benchmark_metric_columns = ["IFEval", "BBH", "MATH Lvl 5", "GPQA", "MUSR", "MMLU-PRO"]
        required_columns.extend(benchmark_metric_columns)
        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            st.error(f"Missing required columns: {', '.join(missing_columns)}")
            return

        # Sidebar for filters
        st.sidebar.header("Options de Filtrage")
        precision_filter = st.sidebar.multiselect(
            "Précision",
            options=df["precision"].dropna().unique(),
            default=df["precision"].dropna().unique()
        )
        model_type_filter = st.sidebar.multiselect(
            "Type de Modèle",
            options=df["type"].dropna().unique(),
            default=df["type"].dropna().unique()
        )

        # Apply filters
        filtered_df = df[df["precision"].isin(precision_filter) & df["type"].isin(model_type_filter)]

        # Search box with real-time filtering and multi-select
        all_models = filtered_df["model_name"].unique()
        selected_models = st.multiselect(
            "Rechercher et sélectionner des modèles",
            options=all_models,
            help="Tapez pour rechercher et sélectionner plusieurs modèles",
            placeholder="Commencez à taper pour rechercher des modèles..."
        )
        
        if selected_models:  # Only filter if models are selected
            filtered_df = filtered_df[filtered_df["model_name"].isin(selected_models)]

        # **Display Options**
        st.sidebar.header("Options d'Affichage")

        # Default columns to display
        default_columns = ['model_name'] + benchmark_metric_columns + ['score']

        # Additional columns (exclude default columns and internal columns)
        internal_columns = ['model_name_html', 'model_link']
        all_columns = filtered_df.columns.tolist()
        additional_columns = [col for col in all_columns if col not in default_columns and col not in internal_columns]

        additional_columns_selected = st.sidebar.multiselect(
            "Sélectionner des colonnes supplémentaires",
            options=additional_columns,
            default=[]
        )

        # Combine default and selected additional columns
        display_columns = default_columns + additional_columns_selected

        

        # Proceed with plotting
        if benchmark_metric_columns:
            # Prepare data for plotting
            plot_columns = ['submission_date', 'model_name', 'type'] + benchmark_metric_columns + ['score']
            filtered_df_for_plot = filtered_df.dropna(subset=['submission_date'])[plot_columns].copy()

            # Melt the dataframe to long format
            df_melted = pd.melt(
                filtered_df_for_plot,
                id_vars=['submission_date', 'model_name', 'type'],
                value_vars=benchmark_metric_columns + ['score'],
                var_name='benchmark_metric',
                value_name='metric_value'
            )

            # Remove rows with NaN metric_value
            df_melted = df_melted.dropna(subset=['metric_value'])

            if not df_melted.empty:
                st.markdown("### Évolution des Performances par Type de Modèle")
                col1, col2 = st.columns([2, 1])
                with col1:
                    st.markdown("""
                    Cette visualisation met en évidence :
                    - 📈 L'évolution des performances pour chaque métrique au fil du temps
                    - 🏆 Les types des modèles les plus performants à chaque période
                    - 📊 La progression des différentes architectures de modèles
                
                    

                    """)
                
                # Time interval selection
                time_interval = st.selectbox(
                    "Sélectionner l'intervalle de temps",
                    options=['Quotidien', 'Mensuel'],
                    index=1
                )

                # Map user selection to pandas frequency strings
                interval_mapping = {
                    'Quotidien': 'D',
                    'Mensuel': 'M',
                }

                # Use selected time interval
                df_melted['time_period'] = df_melted['submission_date'].dt.to_period(interval_mapping[time_interval])

                # Group by benchmark_metric and time_period
                grouped = df_melted.groupby(['benchmark_metric', 'time_period'])

                # Fix the syntax error here - replace curly braces with square brackets
                top_performers = grouped.apply(lambda x: x.loc[x['metric_value'].idxmax()])
                top_performers = top_performers.reset_index(drop=True)

                # Convert time_period to timestamp for plotting
                top_performers['time_period'] = top_performers['time_period'].dt.to_timestamp()

                # Create the line plot with top performers
                fig = px.line(
                    top_performers.sort_values("time_period"),
                    x="time_period",
                    y="metric_value",
                    color='benchmark_metric',
                    title=False,
                    labels={
                        "time_period": "Période",
                        "metric_value": "Valeur Métrique",
                        "benchmark_metric": "Métrique"
                    },
                    markers=True,
                )
                st.plotly_chart(fig)
            else:
                st.write("No data available for the selected benchmark metrics.")
        else:
            st.write("Please select at least one benchmark metric to plot.")

        # Plot: Model types distribution
        if "type" in filtered_df.columns:
            st.markdown("### Répartition des architectures de modèles")
            st.markdown("Ce graphique circulaire illustre la diversité des approches techniques utilisées dans le développement des modèles de langage.")
            fig_pie = px.pie(
                filtered_df,
                names="type",
                title="Distribution des Types de Modèles",
                hole=0.4,
            )
            st.plotly_chart(fig_pie)

        # **Cumulative CO₂ Cost Plot**
        st.markdown("### Coût CO₂ Cumulé au fil du temps (en kg)")
        st.markdown("Cette courbe révèle l'évolution de l'empreinte carbone totale liée à l'entraînement des modèles, soulignant l'importance des considérations environnementales dans le développement de l'IA.")

        if 'submission_date' in filtered_df.columns and 'co2_cost_kg' in filtered_df.columns:
            co2_df = filtered_df.dropna(subset=['submission_date', 'co2_cost_kg'])
            co2_df = co2_df.sort_values('submission_date')
            co2_df['cumulative_co2'] = co2_df['co2_cost_kg'].cumsum()

            fig_co2 = px.line(
                co2_df,
                x='submission_date',
                y='cumulative_co2',
                title='Coût CO₂ Cumulé au Fil du Temps',
                labels={
                    'submission_date': 'Date de Soumission',
                    'cumulative_co2': 'Coût CO₂ Cumulé (kg)'
                },
                markers=True
            )
            st.plotly_chart(fig_co2)
        else:
            st.write("Les données de coût CO₂ ne sont pas disponibles.")

        # **Performance vs. CO₂ Cost Analysis**
        st.markdown("### Analyse Performance vs Impact Environnemental")
        
        st.markdown("""
        #### 🤔 Le coût Coût CO₂ justifie-t-il les performances ?
        
        Cette visualisation révèle la relation cruciale entre performance et impact écologique :
        - 🎯 Position : Rapport performance/coût CO₂
        - 📏 Taille : Nombre de paramètres (en milliards)
        - 🎨 Couleur : Type d'architecture
        """)

        benchmark_options = benchmark_metric_columns + ['score']
        
        # Ajouter les descriptions des métriques
        metric_descriptions = {
            "IFEval": "Évalue la capacité du modèle à suivre des instructions explicites.",
            "BBH": "23 tâches complexes testant le raisonnement algorithmique et la compréhension du langage.",
            "MATH Lvl 5": "Problèmes de mathématiques de niveau compétition lycée.",
            "GPQA": "Questions expertes en sciences validées par des doctorants.",
            "MUSR": "Problèmes complexes nécessitant un raisonnement sur un long contexte.",
            "MMLU-PRO": "Test de connaissances avancées avec 10 choix multiples.",
            "score": "Score moyen global sur l'ensemble des métriques."
        }

        selected_benchmark = st.selectbox(
            "Sélectionner la métrique de performance :",
            options=benchmark_options,
            index=benchmark_options.index('score') if 'score' in benchmark_options else 0
        )

        # Afficher la description de la métrique sélectionnée
        st.markdown(f"*{metric_descriptions[selected_benchmark]}*")

        required_columns_for_plot = [selected_benchmark, 'co2_cost_kg', 'params_b', 'type']
        missing_columns = [col for col in required_columns_for_plot if col not in filtered_df.columns]
        if missing_columns:
            st.write(f"Colonnes manquantes pour le graphique : {', '.join(missing_columns)}")
        else:
            analysis_df = filtered_df.dropna(subset=required_columns_for_plot)
            analysis_df['params_b'] = pd.to_numeric(analysis_df['params_b'], errors='coerce')

            # Filter out non-positive or missing values
            analysis_df = analysis_df[analysis_df['params_b'] > 0]
            analysis_df = analysis_df.dropna(subset=['params_b'])

            fig_analysis = px.scatter(
                analysis_df,
                x='co2_cost_kg',
                y=selected_benchmark,
                size='params_b',
                color='type',
                hover_name='model_name',
                title=False,
                labels={
                    'co2_cost_kg': 'Coût CO₂ (kg)',
                    selected_benchmark: 'Performance',
                    'params_b': 'Paramètres (B)',
                    'type': 'Type de Modèle'
                },
                size_max=45,
            )

            # Update hover template to include all relevant information
            fig_analysis.update_traces(
                hovertemplate="<b>%{hovertext}</b><br>" +
                             "Performance: %{y:.2f}<br>" +
                             "CO₂: %{x:.2f} kg<br>" +
                             "Paramètres: %{marker.size:.1f}B<br>" +
                             "Type: %{marker.color}<br>" +
                             "<extra></extra>"
            )

            st.plotly_chart(fig_analysis)
            
            # Ajouter le conseil après le graphique
            st.markdown("""
            💡 **Conseil:** Observez les modèles qui se démarquent par leur efficacité énergétique 
            tout en maintenant de bonnes performances.
            """)

        # Add table section at the bottom with scrollable layout
        st.markdown("### 📋 Liste Complète des Modèles")

        # Prepare the DataFrame display
        df_to_display = filtered_df[display_columns + ['model_link']].copy()
        df_to_display['model_name'] = df_to_display.apply(
            lambda row: f'<a href="{row["model_link"]}" target="_blank">{row["model_name"]}</a>' 
            if pd.notnull(row["model_link"]) else row["model_name"],
            axis=1
        )
        df_to_display = df_to_display.drop(columns=['model_link'])

        # Convert DataFrame to HTML with custom styling
        html_table = df_to_display.to_html(escape=False, index=False, classes=['dataframe'])
        
        # Create scrollable container with fixed height
        st.markdown("""
            <div style="height: 400px; overflow-y: scroll; margin: 10px 0px">
                {}
            </div>
        """.format(html_table), unsafe_allow_html=True)

        # Après la section Liste Complète des Modèles
        st.markdown("""
        ---
        ### 📚 Documentation des Métriques d'Évaluation

        Nous évaluons les modèles sur 6 benchmarks clés utilisant le framework Eleuther AI Language Model Evaluation Harness:

        #### [IFEval](https://arxiv.org/abs/2311.07911)
        Test de la capacité du modèle à suivre des instructions explicites, en se concentrant sur le format plutôt que le contenu.

        #### [BBH (Big Bench Hard)](https://arxiv.org/abs/2210.09261)
        23 tâches complexes évaluant le raisonnement algorithmique, la compréhension du langage et les connaissances générales.

        #### [MATH](https://arxiv.org/abs/2103.03874)
        Problèmes de mathématiques de niveau compétition lycée, formatés en LaTeX avec figures en Asymptote.

        #### [GPQA](https://arxiv.org/abs/2311.12022)
        Questions expertes créées par des doctorants en biologie, physique et chimie, validées pour leur précision.

        #### [MuSR](https://arxiv.org/abs/2310.16049)
        Problèmes complexes de 1000 mots nécessitant un raisonnement multi-étapes et une analyse de contexte approfondie.

        #### [MMLU-PRO](https://arxiv.org/abs/2406.01574)
        Version améliorée du test MMLU avec 10 choix au lieu de 4, exigeant plus de raisonnement et validée par des experts.
        """)

    else:
        st.error("Aucune donnée disponible. Vérifiez la connexion API ou réessayez plus tard.")

if __name__ == "__main__":
    from accueil import main
    main()