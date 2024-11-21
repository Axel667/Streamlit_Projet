import pandas as pd
import streamlit as st
import plotly.express as px
from datasets import load_dataset

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
            "Model": "model_name",
            "Submission Date": "submission_date",
            "Average ⬆️": "score",
            "Precision": "precision",
            # Other columns as needed
            "IFEval": "IFEval",
            "BBH": "BBH",
            "MATH Lvl 5": "MATH Lvl 5",
            "GPQA": "GPQA",
            "MUSR": "MUSR",
            "MMLU-PRO": "MMLU-PRO",
        })

        # Ensure required columns exist
        required_columns = ["precision", "type", "model_name", "submission_date", "score"]
        benchmark_metric_columns = ["IFEval", "BBH", "MATH Lvl 5", "GPQA", "MUSR", "MMLU-PRO"]
        required_columns.extend(benchmark_metric_columns)

        missing_columns = [col for col in required_columns if col not in df.columns]
        for col in missing_columns:
            df[col] = None  # Handle missing columns appropriately

        # Convert data types
        df["submission_date"] = pd.to_datetime(df["submission_date"], errors='coerce')
        df["score"] = pd.to_numeric(df["score"], errors='coerce')
        for col in benchmark_metric_columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')

        return df
    except Exception as e:
        st.error(f"Error fetching leaderboard data: {e}")
        return pd.DataFrame()

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
            "Model": "model_name",
            "Submission Date": "submission_date",
            "Average ⬆️": "score",
            "Precision": "precision",
            # Other columns as needed
            "IFEval": "IFEval",
            "BBH": "BBH",
            "MATH Lvl 5": "MATH Lvl 5",
            "GPQA": "GPQA",
            "MUSR": "MUSR",
            "MMLU-PRO": "MMLU-PRO",
        })

        # Ensure required columns exist
        required_columns = ["precision", "type", "model_name", "submission_date", "score"]
        benchmark_metric_columns = ["IFEval", "BBH", "MATH Lvl 5", "GPQA", "MUSR", "MMLU-PRO"]
        required_columns.extend(benchmark_metric_columns)

        missing_columns = [col for col in required_columns if col not in df.columns]
        for col in missing_columns:
            df[col] = None  # Handle missing columns appropriately

        # Convert data types
        df["submission_date"] = pd.to_datetime(df["submission_date"], errors='coerce')
        df["score"] = pd.to_numeric(df["score"], errors='coerce')
        for col in benchmark_metric_columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')

        return df
    except Exception as e:
        st.error(f"Error fetching leaderboard data: {e}")
        return pd.DataFrame()

def render_benchmarks_page():
    st.markdown("<h1 class='title'>Hugging Face Open LLM Leaderboard</h1>", unsafe_allow_html=True)
    st.markdown("<p class='subtitle'>Explore benchmark data dynamically fetched from Hugging Face:</p>", unsafe_allow_html=True)

    # Fetch leaderboard data
    df = fetch_leaderboard_data()

    if not df.empty:
        # Check for required columns
        required_columns = ["precision", "type", "model_name", "submission_date", "score"]
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

        # Display filtered dataset
        st.dataframe(filtered_df)

        # Multiselect for benchmark metrics
        st.markdown("<h2 class='subtitle'>Top Benchmark Metrics Over Time</h2>", unsafe_allow_html=True)
        benchmark_metrics = benchmark_metric_columns + ["score"]
        selected_metrics = st.multiselect(
            "Select benchmark metrics to plot",
            options=benchmark_metrics,
            default=["score"]
        )

        if selected_metrics:
            # Prepare data for plotting
            plot_columns = ['submission_date', 'model_name', 'type'] + selected_metrics
            filtered_df_for_plot = filtered_df.dropna(subset=['submission_date'])[plot_columns].copy()

            # Melt the dataframe to long format
            df_melted = pd.melt(
                filtered_df_for_plot,
                id_vars=['submission_date', 'model_name', 'type'],
                value_vars=selected_metrics,
                var_name='benchmark_metric',
                value_name='metric_value'
            )

            # Remove rows with NaN metric_value
            df_melted = df_melted.dropna(subset=['metric_value'])

            if not df_melted.empty:
                # **New Code Starts Here**

                # Add before plotting
                time_interval = st.selectbox(
                    "Select time interval for aggregation",
                    options=['Daily', 'Monthly'],
                    index=1  # Default to 'Monthly'
                )

                # Map user selection to pandas frequency strings
                interval_mapping = {
                    'Daily': 'D',
                    'Monthly': 'M',
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
                # **New Code Ends Here**

            else:
                st.write("No data available for the selected benchmark metrics.")
        else:
            st.write("Please select at least one benchmark metric to plot.")

        # Plot: Model types distribution
        if "type" in filtered_df.columns:
            st.markdown("<h2 class='subtitle'>Model Types Distribution</h2>", unsafe_allow_html=True)
            fig_pie = px.pie(
                filtered_df,
                names="type",
                title="Distribution of Model Types",
                hole=0.4,
            )
            st.plotly_chart(fig_pie)

    else:
        st.error("No data available to display. Check the API connection or try again later.")