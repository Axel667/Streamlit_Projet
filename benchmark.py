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
        st.sidebar.header("Filter Options")
        precision_filter = st.sidebar.multiselect(
            "Precision",
            options=df["precision"].dropna().unique(),
            default=df["precision"].dropna().unique()
        )
        model_type_filter = st.sidebar.multiselect(
            "Model Type",
            options=df["type"].dropna().unique(),
            default=df["type"].dropna().unique()
        )

        # Apply filters
        filtered_df = df[df["precision"].isin(precision_filter) & df["type"].isin(model_type_filter)]

        # Search box
        search_query = st.text_input("Search for a model", value="")
        if search_query:
            filtered_df = filtered_df[filtered_df["model_name"].str.contains(search_query, case=False, na=False)]

        # **Display Options**
        st.sidebar.header("Display Options")

        # Default columns to display
        default_columns = ['model_name'] + benchmark_metric_columns + ['score']

        # Additional columns (exclude default columns and internal columns)
        internal_columns = ['model_name_html', 'model_link']
        all_columns = filtered_df.columns.tolist()
        additional_columns = [col for col in all_columns if col not in default_columns and col not in internal_columns]

        additional_columns_selected = st.sidebar.multiselect(
            "Select additional columns to display",
            options=additional_columns,
            default=[]
        )

        # Combine default and selected additional columns
        display_columns = default_columns + additional_columns_selected

        # Prepare the DataFrame to display
        df_to_display = filtered_df[display_columns + ['model_link']].copy()

        # Convert 'model_name' to clickable links
        df_to_display['model_name'] = df_to_display.apply(
            lambda row: f'<a href="{row["model_link"]}" target="_blank">{row["model_name"]}</a>' if pd.notnull(row["model_link"]) else row["model_name"],
            axis=1
        )

        # Remove 'model_link' from display columns as we don't want to show the URL
        df_to_display = df_to_display.drop(columns=['model_link'])

        # Convert DataFrame to HTML
        html_table = df_to_display.to_html(escape=False, index=False)

        # Define CSS for scrollable div
        scrollable_div_style = """
        <div style='
            overflow-y: auto;
            height: 500px;
            border: 1px solid #ccc;
            padding: 10px;
        '>
        """

        # Combine the div and table
        html_content = scrollable_div_style + html_table + "</div>"

        # Display the table
        st.write(html_content, unsafe_allow_html=True)

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
                st.markdown("### Évolution temporelle des performances")
                st.markdown("Cette visualisation met en évidence les modèles les plus performants pour chaque métrique au fil du temps, permettant d'identifier les tendances et les progrès réalisés dans le domaine.")
                
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

                # Select the top performer in each group
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
                    title="Top Benchmark Metrics Over Time",
                    labels={
                        "time_period": "Time Period",
                        "metric_value": "Metric Value",
                        "benchmark_metric": "Benchmark Metric"
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
                title='Cumulative CO₂ Cost Over Time',
                labels={
                    'submission_date': 'Submission Date',
                    'cumulative_co2': 'Cumulative CO₂ Cost (kg)'
                },
                markers=True
            )
            st.plotly_chart(fig_co2)
        else:
            st.write("CO₂ cost data is not available to plot.")

        # **Performance vs. CO₂ Cost Analysis**
        st.markdown("### Analyse Performance vs Impact Environnemental")
        st.markdown("Cette visualisation permet d'explorer la relation entre les performances des modèles et leur coût environnemental, mettant en évidence le compromis entre efficacité et durabilité.")

        benchmark_options = benchmark_metric_columns + ['score']
        selected_benchmark = st.selectbox(
            "Sélectionner la métrique de performance :",
            options=benchmark_options,
            index=benchmark_options.index('score') if 'score' in benchmark_options else 0
        )

        size_options = ['params_b', 'co2_cost_kg']
        size_variable = st.selectbox(
            "Variable pour la taille des points :",
            options=size_options,
            index=0
        )

        color_options = ['precision', 'type']
        color_variable = st.selectbox(
            "Variable pour la couleur des points :",
            options=color_options,
            index=0
        )

        required_columns_for_plot = [selected_benchmark, 'co2_cost_kg', size_variable, color_variable]
        missing_columns = [col for col in required_columns_for_plot if col not in filtered_df.columns]
        if missing_columns:
            st.write(f"The following columns are missing for plotting: {', '.join(missing_columns)}")
        else:
            analysis_df = filtered_df.dropna(subset=required_columns_for_plot)
            analysis_df[size_variable] = pd.to_numeric(analysis_df[size_variable], errors='coerce')

            # Filter out non-positive or missing values in size_variable
            analysis_df = analysis_df[analysis_df[size_variable] > 0]
            analysis_df = analysis_df.dropna(subset=[size_variable])

            fig_analysis = px.scatter(
                analysis_df,
                x='co2_cost_kg',
                y=selected_benchmark,
                size=size_variable,
                color=color_variable,
                hover_name='model_name',
                title='Model Performance vs. CO₂ Cost',
                labels={
                    'co2_cost_kg': 'CO₂ Cost (kg)',
                    selected_benchmark: selected_benchmark,
                    size_variable: size_variable,
                    color_variable: color_variable
                },
                size_max=40
            )
            st.plotly_chart(fig_analysis)

    else:
        st.error("No data available to display. Check the API connection or try again later.")