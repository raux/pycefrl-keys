"""
Streamlit web interface for pycefrl-keyword.

Provides a browser-based dashboard for analysing Python source code and
visualising CEFR-inspired proficiency levels detected via regex pattern
matching.

Launch with::

    python -m streamlit run app.py
"""

import json
import os
import re
import shutil
import subprocess
import tempfile

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import psutil
import streamlit as st

from pycefrl_keyword.analyzer import analyze_directory, analyze_file, save_results

# ---------------------------------------------------------------------------
# Page configuration
# ---------------------------------------------------------------------------

st.set_page_config(
    page_title="PyCEFRL Keywords - Python Code Level Analyzer",
    layout="wide",
)

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def get_system_stats():
    """Return current CPU and RAM usage percentages."""
    cpu = psutil.cpu_percent(interval=None)
    ram = psutil.virtual_memory().percent
    return cpu, ram


def categorize_class(class_name: str) -> str:
    """Map a pattern class name to a high-level category for visualisation."""
    name = class_name.lower()
    if any(x in name for x in ["list", "tuple", "dict", "set", "array"]):
        return "Data Structures"
    if any(
        x in name
        for x in [
            "if",
            "else",
            "loop",
            "for",
            "while",
            "try",
            "except",
            "break",
            "continue",
            "pass",
        ]
    ):
        return "Control Flow"
    if any(x in name for x in ["print", "file", "open", "read", "write", "input"]):
        return "I/O"
    if any(
        x in name
        for x in [
            "function",
            "lambda",
            "class",
            "method",
            "return",
            "yield",
            "super",
            "decorator",
            "init",
            "self",
            "slots",
            "metaclass",
            "new",
            "property",
            "static",
        ]
    ):
        return "OOP & Functions"
    if any(x in name for x in ["import", "from", "module"]):
        return "Modules"
    if any(x in name for x in ["assign", "operator", "compare", "augmented"]):
        return "Operations"
    return "Other"


def results_to_dataframe(results: list[dict]) -> pd.DataFrame:
    """Convert analyser result records to a :class:`~pandas.DataFrame`."""
    if not results:
        return pd.DataFrame()
    df = pd.DataFrame(results)
    df.rename(
        columns={
            "repo": "Repo",
            "file": "File",
            "class": "Class",
            "start_line": "Start Line",
            "end_line": "End Line",
            "displacement": "Displacement",
            "level": "Level",
        },
        inplace=True,
    )
    df["Category"] = df["Class"].apply(categorize_class)
    return df


_GITHUB_URL_RE = re.compile(
    r"^https?://github\.com/([\w.-]+)/([\w.-]+?)(\.git)?/?$"
)

# Fixed output directory for analysis results — reused across runs so that
# temporary directories do not accumulate.
_OUTPUT_DIR = os.path.join(tempfile.gettempdir(), "pycefrl_keyword_output")


def clone_github_repo(url: str) -> str | None:
    """Clone a GitHub repository into a temporary directory.

    The *url* is validated against the GitHub URL pattern before being
    passed to ``git clone``.  Returns the path to the cloned directory,
    or *None* on failure.
    """
    if not _GITHUB_URL_RE.match(url.rstrip("/").rstrip(".git").rstrip("/")):
        st.error("Invalid GitHub repository URL.")
        return None

    tmp_dir = tempfile.mkdtemp(prefix="pycefrl_")
    try:
        subprocess.run(
            ["git", "clone", "--depth", "1", "--", url, tmp_dir],
            check=True,
            capture_output=True,
            text=True,
        )
        return tmp_dir
    except (subprocess.CalledProcessError, FileNotFoundError) as exc:
        st.error(f"Failed to clone repository: {exc}")
        shutil.rmtree(tmp_dir, ignore_errors=True)
        return None


# ---------------------------------------------------------------------------
# Visualisation helpers
# ---------------------------------------------------------------------------


def display_level_metrics(df: pd.DataFrame) -> None:
    """Show per-level counts as metric cards."""
    level_order = ["A1", "A2", "B1", "B2", "C1", "C2"]
    counts = df["Level"].value_counts()
    cols = st.columns(len(level_order))
    for i, level in enumerate(level_order):
        with cols[i]:
            st.metric(label=f"Level {level}", value=int(counts.get(level, 0)))


def display_bar_chart(df: pd.DataFrame) -> None:
    """Bar chart of element counts per level."""
    level_order = ["A1", "A2", "B1", "B2", "C1", "C2"]
    counts = df["Level"].value_counts().reindex(level_order, fill_value=0)
    fig = go.Figure(
        data=go.Bar(
            x=counts.index.tolist(),
            y=counts.values.tolist(),
            marker_color=["#1f77b4", "#2ca02c", "#ff7f0e", "#d62728", "#9467bd", "#8c564b"],
        )
    )
    fig.update_layout(
        xaxis_title="Level",
        yaxis_title="Count",
        title="Elements per Level",
        height=400,
    )
    st.plotly_chart(fig, use_container_width=True)


def display_bubble_chart(df: pd.DataFrame) -> None:
    """Bubble chart: Category vs Level (size = frequency)."""
    bubble = df.groupby(["Category", "Level"]).size().reset_index(name="Count")
    if bubble.empty:
        st.info("No data available for bubble chart.")
        return
    level_order = ["A1", "A2", "B1", "B2", "C1", "C2"]
    fig = go.Figure(
        data=go.Scatter(
            x=bubble["Category"],
            y=bubble["Level"],
            mode="markers",
            marker=dict(
                size=bubble["Count"],
                sizemode="area",
                sizeref=2.0 * max(bubble["Count"]) / (50.0**2),
                sizemin=5,
                color=bubble["Count"],
                colorscale="Viridis",
                showscale=True,
                colorbar=dict(title="Count"),
            ),
            text=bubble.apply(lambda row: f"Count: {row['Count']}", axis=1),
            hovertemplate="<b>%{x}</b><br>Level: %{y}<br>%{text}<extra></extra>",
        )
    )
    fig.update_layout(
        xaxis=dict(title="Category"),
        yaxis=dict(title="Level", categoryorder="array", categoryarray=level_order),
        height=600,
        margin=dict(l=50, r=50, t=50, b=50),
    )
    st.plotly_chart(fig, use_container_width=True)


def display_file_heatmap(df: pd.DataFrame) -> None:
    """Heatmap of file vs level count."""
    if "File" not in df.columns or "Level" not in df.columns:
        st.info("Not enough data for heatmap.")
        return
    pivot = df.pivot_table(index="File", columns="Level", aggfunc="size", fill_value=0)
    fig = go.Figure(
        data=go.Heatmap(
            z=pivot.values,
            x=pivot.columns.tolist(),
            y=pivot.index.tolist(),
            colorscale="Viridis",
        )
    )
    fig.update_layout(height=max(400, len(pivot) * 25))
    st.plotly_chart(fig, use_container_width=True)


def display_treemap(df: pd.DataFrame) -> None:
    """Treemap: Level → Category → Element."""
    if not {"Level", "Category", "Class"}.issubset(df.columns):
        st.info("Not enough data for treemap.")
        return
    color_map = {
        "A1": "#1f77b4",
        "A2": "#2ca02c",
        "B1": "#ff7f0e",
        "B2": "#d62728",
        "C1": "#9467bd",
        "C2": "#8c564b",
    }
    fig = px.treemap(
        df,
        path=["Level", "Category", "Class"],
        color="Level",
        color_discrete_map=color_map,
    )
    fig.update_layout(height=600)
    st.plotly_chart(fig, use_container_width=True)


# ---------------------------------------------------------------------------
# Results display
# ---------------------------------------------------------------------------


def display_results(results: list[dict], output_dir: str) -> None:
    """Render all result sections: metrics, charts, table, downloads."""
    if not results:
        st.warning("No patterns found in the analysed code.")
        return

    df = results_to_dataframe(results)

    # --- Level distribution -------------------------------------------------
    st.subheader("Level Distribution")
    display_level_metrics(df)
    display_bar_chart(df)

    # --- Visualisation tabs -------------------------------------------------
    st.subheader("Visualisations")
    tab1, tab2, tab3 = st.tabs(["Bubble Chart", "File Heatmap", "Element Treemap"])

    with tab1:
        st.write("**Category vs Level** — bubble size represents frequency")
        display_bubble_chart(df)
    with tab2:
        st.write("**File vs Level Count**")
        display_file_heatmap(df)
    with tab3:
        st.write("**Drill down**: Level → Category → Element")
        display_treemap(df)

    # --- Detailed table -----------------------------------------------------
    st.subheader("Detailed Results")
    st.dataframe(df[["Repo", "File", "Class", "Start Line", "End Line", "Level", "Category"]])

    # --- Downloads ----------------------------------------------------------
    st.subheader("Downloads")
    json_path, csv_path = save_results(results, output_dir)

    col1, col2 = st.columns(2)
    with col1:
        with open(json_path, "rb") as fh:
            st.download_button(
                "📥 Download JSON Report",
                fh,
                file_name="pycefrl_keyword_data.json",
                mime="application/json",
            )
    with col2:
        with open(csv_path, "rb") as fh:
            st.download_button(
                "📥 Download CSV Report",
                fh,
                file_name="pycefrl_keyword_data.csv",
                mime="text/csv",
            )


# ---------------------------------------------------------------------------
# Sidebar
# ---------------------------------------------------------------------------

with st.sidebar:
    st.header("Settings")
    mode = st.selectbox(
        "Select Analysis Mode",
        ["Local Directory", "GitHub Repository"],
    )

    st.divider()
    st.header("System Stats")
    cpu_metric = st.empty()
    ram_metric = st.empty()
    cpu, ram = get_system_stats()
    cpu_metric.metric("CPU Usage", f"{cpu}%")
    ram_metric.metric("RAM Usage", f"{ram}%")

# ---------------------------------------------------------------------------
# Main content
# ---------------------------------------------------------------------------

st.title("🐍 PyCEFRL Keywords — Python Code Level Analyzer")
st.markdown(
    """
This tool analyses Python source code and assigns each detected language
construct a **CEFR-inspired proficiency level** (A1 – C2) using **regex
pattern matching**.

Choose an analysis mode from the sidebar:
- 📁 **Local Directory** — analyse Python files in any local path
- 🔗 **GitHub Repository** — clone and analyse a public GitHub repository
"""
)

# --- Mode: Local Directory -------------------------------------------------
if mode == "Local Directory":
    path = st.text_input("Enter directory path", value=".", key="dir_path")

    if path and os.path.isdir(path):
        st.info(f"📂 Resolved path: `{os.path.abspath(path)}`")
    elif path:
        st.warning(f"⚠️ Path does not exist: `{path}`")

    if st.button("Analyse Directory", type="primary"):
        if path and os.path.isdir(path):
            with st.spinner("Analysing…"):
                results = analyze_directory(path)
            st.success(f"✅ Analysis complete — {len(results)} pattern match(es) found.")
            display_results(results, output_dir=_OUTPUT_DIR)
        else:
            st.error("Please enter a valid directory path.")

# --- Mode: GitHub Repository -----------------------------------------------
elif mode == "GitHub Repository":
    url = st.text_input(
        "Enter GitHub Repository URL",
        placeholder="https://github.com/username/repository",
        key="repo_url",
    )

    is_valid = False
    if url:
        if _GITHUB_URL_RE.match(url.strip().rstrip("/")):
            is_valid = True
            st.success("✓ Valid GitHub repository URL")
        else:
            st.warning(
                "⚠️ Please enter a valid GitHub repository URL "
                "(e.g., https://github.com/user/repo)"
            )

    if st.button("Analyse Repository", type="primary"):
        if url and is_valid:
            clone_url = url.strip().rstrip("/")
            if not clone_url.endswith(".git"):
                clone_url += ".git"

            with st.spinner("Cloning repository…"):
                repo_dir = clone_github_repo(clone_url)

            if repo_dir:
                try:
                    with st.spinner("Analysing…"):
                        results = analyze_directory(repo_dir)
                    st.success(
                        f"✅ Analysis complete — {len(results)} pattern match(es) found."
                    )
                    display_results(
                        results, output_dir=_OUTPUT_DIR
                    )
                finally:
                    shutil.rmtree(repo_dir, ignore_errors=True)
            # Error already shown by clone_github_repo
        elif url:
            st.error("Please enter a valid GitHub repository URL.")
        else:
            st.warning("Please enter a URL.")
