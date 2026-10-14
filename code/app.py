import streamlit as st

from backend import (
    get_disease_list,
    get_gene_list,
    get_deg_gene_list,
    get_celltype_list,
    get_deg_dotplot_celltype_list,
    build_gene_statistics,
    plot_expression,
    compare_diseases,
    plot_umap,
    plot_dotplot,
    plot_tsne,
    plot_deg_dotplot,
    plot_violin,
    plot_topN_gene_venn,
    wilcoxon_vs_normal,
    get_expression,
    get_umap_summary,
    get_expression_summary,
    get_disease_summary,
    get_venn_summary,
    get_dotplot_summary,
    get_deg_celltype_list,
    plot_deg,
    get_deg_summary,
    get_wilcoxon_summary
)

from language_layer import (
    check_ollama,
    llm_to_command,
    generate_llm_explanation
)

# ======================================================
# PAGE CONFIG
# ======================================================

st.set_page_config(
    page_title="CellInterpreter",
    layout="wide"
)


# ======================================================
# CUSTOM CSS — CLEAN BLACK-AND-WHITE THEME
# ======================================================

st.markdown(
    """
    <style>

    /* Main application background and default text */
    .stApp {
        background: #f2f2f2 !important;
        color: #333333 !important;
    }

    /* Main content typography */
    .main-title {
        text-align: center;
        color: #404040 !important;
        font-size: 52px;
        font-weight: 800;
        margin-bottom: 0px;
    }

    .subtitle {
        text-align: center;
        color: #666666 !important;
        font-size: 22px;
        margin-top: -10px;
        margin-bottom: 30px;
    }

    .query-title {
        color: #404040 !important;
        font-size: 28px;
        font-weight: 700;
        margin-top: 20px;
    }

    /* Main text and headings */
    .stApp h1,
    .stApp h2,
    .stApp h3,
    .stApp p,
    .stApp label,
    .stApp .stMarkdown {
        color: #404040;
    }

    .stTextInput label {
        color: #4a4a4a !important;
        font-size: 18px !important;
        font-weight: 600 !important;
    }

    /* Main-page query input: dark-gray background */
    section[data-testid="stMain"]
    div[data-testid="stTextInput"] div[data-baseweb="input"] {
        background-color: #404040 !important;
        border-color: #404040 !important;
        border-radius: 8px !important;
    }

    section[data-testid="stMain"]
    div[data-testid="stTextInput"] div[data-baseweb="base-input"] {
        background-color: #404040 !important;
    }

    /* Query input text and cursor */
    section[data-testid="stMain"]
    div[data-testid="stTextInput"] input {
        background-color: #404040 !important;
        color: #ffffff !important;
        -webkit-text-fill-color: #ffffff !important;
        caret-color: #ffffff !important;
    }

    /* Query input placeholder */
    section[data-testid="stMain"]
    div[data-testid="stTextInput"] input::placeholder {
        color: #ffffff !important;
        -webkit-text-fill-color: #cccccc !important;
        opacity: 1 !important;
    }

    /* Main buttons */
    div.stButton > button {
        width: 100%;
        background-color: #404040 !important;
        color: #ffffff !important;
        border-radius: 8px !important;
        border: 1px solid #ffffff !important;
        height: 45px !important;
        font-size: 16px;
        font-weight: 600 !important;
        transition: background-color 0.2s ease;
    }

    div.stButton > button:hover {
        background-color: #404040 !important;
        border-color: #ffffff !important;
        color: #ffffff !important;
    }

    /* Sidebar background */
    section[data-testid="stSidebar"] {
        background-color: #404040 !important;
    }

    /* Sidebar text */
    section[data-testid="stSidebar"] h1,
    section[data-testid="stSidebar"] h2,
    section[data-testid="stSidebar"] h3,
    section[data-testid="stSidebar"] p,
    section[data-testid="stSidebar"] label,
    section[data-testid="stSidebar"] span,
    section[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] {
        color: #ffffff !important;
    }

    /* Sidebar buttons */
    section[data-testid="stSidebar"] div.stButton > button {
        background-color: #222222 !important;
        color: #ffffff !important;
        border-radius: 8px !important;
        border: 1px solid #222222 !important;
        height: 42px !important;
        font-weight: 600 !important;
    }

    section[data-testid="stSidebar"] div.stButton > button:hover {
        background-color: #444444 !important;
        color: #ffffff !important;
    }

    /* White content cards with subtle gray borders */
    .content-card {
        background: #ffffff !important;
        padding: 30px;
        border-radius: 12px;
        border: 1px solid #dddddd;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
        margin-top: 10px;
        color: #000000 !important;
    }

    .content-card * {
        color: #000000 !important;
    }

    /* Navigation container: remove the outer rectangle */
    .nav-bar {
        background-color: transparent !important;
        border-radius: 10px;
        padding: 12px;
        margin-bottom: 20px;
        border: none !important;
        box-shadow: none !important;
        outline: none !important;
    }

    .nav-bar-title {
        color: #000000 !important;
        text-align: center;
        font-size: 14px;
    }

    /* Keep button text white, including nested text elements */
    .stApp div.stButton > button,
    .stApp div.stButton > button * {
        color: #ffffff !important;
    }

    /* Keep text white during hover, focus, and click */
    .stApp div.stButton > button:hover,
    .stApp div.stButton > button:hover *,
    .stApp div.stButton > button:focus,
    .stApp div.stButton > button:focus *,
    .stApp div.stButton > button:active,
    .stApp div.stButton > button:active * {
        color: #ffffff !important;
    }

    /* Hide Streamlit menu, header, and footer */
    #MainMenu {
        visibility: hidden;
    }

    footer {
        visibility: hidden;
    }

    header {
        visibility: hidden;
    }

    </style>
    """,
    unsafe_allow_html=True
)

# ======================================================
# HEADER
# ======================================================

st.markdown(
    '<div class="main-title">🧬 CellInterpreter</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="subtitle">Interactive Single-Cell RNA-seq Analysis Platform</div>',
    unsafe_allow_html=True
)

# ======================================================
# TOP NAVIGATION
# ======================================================

st.markdown("""
<style>

.nav-bar{
    background-color: rgba(10,20,40,0.90);
    border-radius: 18px;
    padding: 12px;
    margin-bottom: 20px;
    border: 1px solid rgba(183,215,240,0.30);
}

.nav-bar-title{
    color:white;
    text-align:center;
    font-size:14px;
}

</style>
""", unsafe_allow_html=True)

nav_container = st.container(border=True)

with nav_container:

    nav1, nav2, nav3, nav4 = st.columns([1,1,1.5,1])

    with nav1:
        home_btn = st.button(
            "🏠 Home",
            key="home_btn"
        )

    with nav2:
        about_btn = st.button(
            "🧬 About",
            key="about_btn"
        )

    with nav3:
        why_btn = st.button(
            "⭐ Why CellInterpreter",
            key="why_btn"
        )

    with nav4:
        contact_btn = st.button(
            "📩 Contact",
            key="contact_btn"
        )

# Default page
if "page" not in st.session_state:
    st.session_state.page = "home"

if home_btn:
    st.session_state.page = "home"

if about_btn:
    st.session_state.page = "about"

if why_btn:
    st.session_state.page = "why"

if contact_btn:
    st.session_state.page = "contact"

page = st.session_state.page

# ======================================================
# NATURAL LANGUAGE QUERY
# ======================================================
user_query = None
if page == "home":
 st.markdown(
    '<div class="query-title">User Query Assistant</div>',
    unsafe_allow_html=True
 )

 user_query = st.text_input(
    "Ask a biological question",
    placeholder=(
        "Examples:\n"
        "- Show UMAP of AAAS gene\n"
        "- Compare diseases for AAMP\n"
        "- Show violin plot of TP53"
    )
 )

if user_query:

    if not check_ollama():

        st.error(
            "Ollama is not running."
        )

    else:

        try:

            command = llm_to_command(
                user_query
            )
            st.markdown(
                "<h4 style='color:#404040;'>Structured Command</h4>",
                unsafe_allow_html=True
            )

            st.json(command)

            if "error" in command:

                st.error(
                    command["error"]
                )

            else:

                task = command.get("task")
                gene = command.get("gene")

                # ==================================================
                # UMAP
                # ==================================================

                if task == "plot_umap":

                   with st.spinner("Generating UMAP..."):

                       plot_umap(gene=gene)

                   if check_ollama():

                       with st.spinner(
                          "Generating AI interpretation..."
                   ):

                        summary = get_umap_summary(gene)

                        context = {
                             "gene": gene,
                             "plot_type": "umap",
                             "summary": summary
                        }

                        explanation = (
                             generate_llm_explanation(
                                context
                             )
                        )

                        st.subheader(
                            "Biological Interpretation"
                        )

                        st.write(explanation)
                # ==================================================
                # DOT PLOT
                # ==================================================
                elif task == "plot_dotplot":

                    genes = command["genes"]

                    with st.spinner("Generating Dot Plot..."):

                        plot_dotplot(genes)

                    if check_ollama():

                        with st.spinner(
                    "Generating AI interpretation..."
                    ):

                         summary = get_dotplot_summary(genes)

                         context = {
                         "genes": genes,
                         "plot_type": "dotplot",
                         "summary": summary
                        }

                         explanation = (
                            generate_llm_explanation(
                            context
                            )
                        )

                        st.subheader(
                            "Biological Interpretation"
                        )

                        st.write(explanation)
                # ==================================================
                # DIFFERENTIAL EXPRESSION
                # ==================================================

                elif task == "plot_deg":

                    cell_type = command.get(
                        "cell_type"
                    )

                    direction = command.get(
                        "direction",
                        "both"
                    )

                    top_n = command.get(
                        "top_n",
                        20
                    )

                    with st.spinner(
                        "Generating DEG analysis..."
                    ):

                        plot_deg(
                            cell_type=cell_type,
                            direction=direction,
                            top_n=top_n
                        )

                    if check_ollama():

                        with st.spinner(
                            "Generating biological interpretation..."
                        ):

                            summary = get_deg_summary(
                                cell_type=cell_type,
                                direction=direction,
                                top_n=top_n
                            )

                            context = {

                                "plot_type": "deg",

                                "cell_type":
                                    cell_type,

                                "comparison":
                                    "B18_M vs B18_C",

                                "direction":
                                    direction,

                                "summary":
                                    summary
                            }

                            explanation = (
                                generate_llm_explanation(
                                    context
                                )
                            )

                        st.subheader(
                            "Biological Interpretation"
                        )

                        st.write(
                            explanation
                        )
                # ==================================================
                # VIOLIN
                # ==================================================

                elif task == "plot_violin":

                    plot_violin(gene=gene)

                    stats = build_gene_statistics(
                        gene
                    )

                    context = {
                        "gene": gene,
                        "plot_type": "violin",
                        "summary":
                            f"Violin distribution of {gene}",
                        "group_stats": stats
                    }

                    explanation = (
                        generate_llm_explanation(
                            context
                        )
                    )

                    st.subheader(
                        "Biological Interpretation"
                    )

                    st.write(explanation)

                # ==================================================
                # EXPRESSION HISTOGRAM
                # ==================================================

                elif task == "plot_expression":

                    plot_expression(gene=gene)
                    if check_ollama():
                    
                                           with st.spinner(
                                              "Generating AI interpretation..."
                                       ):
                    
                                            summary = get_expression_summary(gene)
                    
                                            context = {
                                                 "gene": gene,
                                                 "plot_type": "expression",
                                                 "summary": summary
                                            }
                    
                                            explanation = (
                                                 generate_llm_explanation(
                                                    context
                                                 )
                                            )
                    
                                            st.subheader(
                                                "Biological Interpretation"
                                            )
                    
                                            st.write(explanation)


                # ==================================================
                # WILCOXON
                # ==================================================

                elif task == "wilcoxon":

                    results = wilcoxon_vs_normal(
                        gene
                    )
                    if check_ollama():
                                        
                                            with st.spinner(
                                            "Generating AI interpretation..."
                                        ):
                                        
                                             summary = get_wilcoxon_summary(gene)
                                     
                                            context = {
                                                "gene": gene,
                                                "plot_type": "wilcoxon",
                                                "summary": summary
                                            }
                                        
                                            explanation = (
                                                generate_llm_explanation(
                                                  context
                                                )
                                            )
                                        
                                            st.subheader(
                                                "Biological Interpretation"
                                            )
                                        
                                            st.write(explanation)
                    

                    st.json(results)

                else:

                    st.warning(
                        "Task not supported yet."
                    )

        except Exception as e:

            st.error(str(e))

# ======================================================
# About Button
# ======================================================
elif page == "about":

    st.markdown(
    """
    <div class="content-card">

    <h2>🧬 About CellInterpreter</h2>

    <p>
    CellInterpreter is an AI-powered platform designed to simplify
    single-cell RNA-seq interpretation for biomedical researchers.
    </p>

    <h3>Our Mission</h3>

    <p>
    Enable rapid interpretation of single-cell RNA-seq through AI
    for precision medicine and biomedical research.
    </p>

    <h3>How It Works</h3>

    <ol>
    <li>Upload single-cell RNA-seq datasets</li>
    <li>Explore genes interactively</li>
    <li>Generate UMAP, t-SNE, violin plots, and statistical analyses</li>
    <li>Receive AI-generated biological interpretations</li>
    <li>Accelerate discovery through natural-language interaction</li>
    </ol>

    <h3>Target Applications</h3>

    <ul>
    <li>Allergy and Immunology Research</li>
    <li>Precision Medicine</li>
    <li>Translational Genomics</li>
    <li>Cell Atlas Exploration</li>
    <li>Disease Biomarker Discovery</li>
    </ul>

    </div>
    """,
    unsafe_allow_html=True
    )

# ======================================================
# WHY CellInterpreter Page
# ======================================================
elif page == "why":

    st.markdown(
    """
    <div class="content-card">

    <h2>⭐ Why CellInterpreter?</h2>

    <h3>⚡ Faster Insights</h3>
    AI accelerates analysis from weeks to minutes.

    <h3>🧬 User Friendly</h3>
    Designed for biologists, not just bioinformaticians.

    <h3>☁️ Scalable</h3>
    Handle datasets of any size with cloud-ready infrastructure.

    <h3>🔒 Secure & Private</h3>
    Your data stays yours with enterprise-grade security.

    <h3>💰 Cost Effective</h3>
    Reduce computational costs and manual effort.

    </div>
    """,
    unsafe_allow_html=True
    )

# ======================================================
# Contact Us
# ======================================================
elif page == "contact":

    st.markdown(
    """
    <div class="content-card">

    <h2>📩 Contact Us</h2>

    <h3>Dr. Muhammad Turyalai Khan</h3>

    <p>
    AI Researcher • Machine Learning • Single-Cell Genomics
    </p>

    <p>
    📧 muhammadturyalaikhan@gmail.com
    </p>

    <p>
    For collaborations, partnerships, licensing opportunities,
    or investor inquiries, please contact us directly.
    </p>

    </div>
    """,
    unsafe_allow_html=True
    )

# ======================================================
# LOAD DATA
# ======================================================

GENES = get_gene_list()
DISEASES = get_disease_list()
CELLTYPES = get_celltype_list()

# ======================================================
# SIDEBAR
# ======================================================
if page == "home":

    ## st.sidebar.markdown("## 📂 Upload Dataset")

    ## uploaded_file = st.sidebar.file_uploader(
       # "Upload .h5ad file",
        # type=["h5ad"]
    #)

    #if uploaded_file is not None:

     #   with open(
      #      "./temp_uploaded.h5ad",
       #     "wb"
       # ) as f:

        #    f.write(
         #       uploaded_file.getbuffer()
          #  )

        #st.sidebar.success(
         #   "Dataset uploaded successfully."
        #)

    analysis_type = st.sidebar.selectbox(
        "Select Analysis",
        [
            "Expression Histogram",
            "Disease Comparison",
            "UMAP",
            "t-SNE",
            "Violin Plot",
            "Dot Plot",
            "Differential Expression",
            "DEG Dot Plot",
            "Venn Diagram",
            "Wilcoxon Test"
        ]
    )

    if analysis_type != "Differential Expression":
        gene = st.sidebar.selectbox(
            "Select Gene",
            GENES
    )
    else:
        gene = None

    # =============================================
    # Expression Histogram
    # =============================================

    if analysis_type == "Expression Histogram":

        disease = st.sidebar.selectbox(
            "Disease",
            DISEASES
        )

        cell_type = st.sidebar.selectbox(
            "Cell Type",
            ["All"] + CELLTYPES
        )

        generate_plot = st.sidebar.button(
            "Generate Plot",
            key="expr_plot"
        )

        if generate_plot:

            plot_expression(
                gene=gene,
                disease=disease,
                cell_type=None if cell_type == "All"
                else cell_type
            )

    # =============================================
    # Disease Comparison
    # =============================================

    elif analysis_type == "Disease Comparison":

        if st.sidebar.button(
            "Generate Plot",
            key="disease_plot"
        ):
            compare_diseases(gene)

    # =============================================
    # UMAP
    # =============================================

    elif analysis_type == "UMAP":

        mode = st.sidebar.radio(
            "UMAP Coloring",
            [
                "Gene Expression",
                "Disease Group",
                "Cell Type"
            ]
        )

        if st.sidebar.button(
            "Generate Plot",
            key="umap_plot"
        ):

            if mode == "Gene Expression":
                plot_umap(gene=gene)

            elif mode == "Disease Group":
                plot_umap(
                    color_by="diseasegroup"
                )

            else:
                plot_umap(
                    color_by="celltype"
                )

    # =============================================
    # t-SNE
    # =============================================

    elif analysis_type == "t-SNE":

        mode = st.sidebar.radio(
        "t-SNE Coloring",
        [
            "Gene Expression",
            "Disease Group",
            "Cell Type"
        ]
        )

        n_cells = st.sidebar.slider(
        "Number of Cells",
        1000,
        20000,
        5000
        )

        perplexity = st.sidebar.slider(
        "Perplexity",
        5,
        50,
        30
        )

        if st.sidebar.button(
        "Generate Plot",
        key="tsne_plot"
        ):

            if mode == "Gene Expression":

                plot_tsne(
                n_cells=n_cells,
                perplexity=perplexity,
                gene=gene
                )

            elif mode == "Disease Group":

                plot_tsne(
                n_cells=n_cells,
                perplexity=perplexity,
                color_by="diseasegroup"
                )

            else:

                plot_tsne(
                n_cells=n_cells,
                perplexity=perplexity,
                color_by="celltype"
                )

    # =============================================
    # Violin Plot
    # =============================================

    elif analysis_type == "Violin Plot":

        group_by = st.sidebar.selectbox(
            "Group By",
            [
                "diseasegroup",
                "celltype"
            ]
        )

        if st.sidebar.button(
            "Generate Plot",
            key="violin_plot"
        ):

            plot_violin(
                gene=gene,
                group_by=group_by
            )

    # =============================================
    # Dot Plot
    # =============================================

    elif analysis_type == "Dot Plot":

        selected_genes = st.sidebar.multiselect(
            "Select Genes",
            GENES,
            default=GENES[:3]
        )

        group_by = st.sidebar.selectbox(
            "Group By",
            [
                "celltype",
                "diseasegroup"
            ]
        )

        if st.sidebar.button(
            "Generate Plot",
            key="dotplot_sidebar"
        ):

            if selected_genes:

                plot_dotplot(
                    genes=selected_genes,
                    groupby=group_by
                )

            else:

                st.warning(
                    "Please select at least one gene."
                )
     # =============================================
    # DEG CSV Dot Plot
    # =============================================

    elif analysis_type == "DEG Dot Plot":

        st.sidebar.markdown(
            "### DEG CSV Dot Plot"
        )

        deg_genes = get_deg_gene_list()
        deg_celltypes = get_deg_dotplot_celltype_list()

        if not deg_genes:

            st.sidebar.warning(
                "No genes were found in the DEG CSV."
            )

        else:

            selected_deg_genes = st.sidebar.multiselect(
                "Select Genes",
                deg_genes,
                default=deg_genes[:20]
            )

            selected_deg_celltypes = st.sidebar.multiselect(
                "Select Cell Types",
                deg_celltypes,
                default=deg_celltypes
            )

            if st.sidebar.button(
                "Generate DEG Dot Plot",
                key="deg_dotplot"
            ):

                if not selected_deg_genes:

                    st.warning(
                        "Please select at least one gene."
                    )

                elif not selected_deg_celltypes:

                    st.warning(
                        "Please select at least one cell type."
                    )

                else:

                    with st.spinner(
                        "Generating DEG dot plot..."
                    ):

                        plot_deg_dotplot(
                            genes=selected_deg_genes,
                            cell_types=selected_deg_celltypes
                        )
    # =============================================
    # Venn Diagram
    # =============================================

    elif analysis_type == "Venn Diagram":

        selected_diseases = st.sidebar.multiselect(
            "Select Diseases",
            DISEASES,
            default=DISEASES[:3]
        )

        top_n = st.sidebar.slider(
            "Top N Genes",
            10,
            500,
            150
        )

        if st.sidebar.button(
            "Generate Plot",
            key="venn_plot"
        ):

            plot_topN_gene_venn(
                diseases=selected_diseases,
                top_n=top_n
            )
    # =============================================
    # Differential Expression
    # =============================================
    elif analysis_type == "Differential Expression":

        DEG_CELLTYPES = get_deg_celltype_list()

        if not DEG_CELLTYPES:

            st.sidebar.warning(
                "No DEG cell types found."
            )

        else:

            deg_cell_type = st.sidebar.selectbox(
                "Cell Type",
                DEG_CELLTYPES
            )

            deg_direction = st.sidebar.selectbox(
                "Direction",
                [
                    "Both",
                    "Upregulated",
                    "Downregulated"
                ]
            )

            deg_top_n = st.sidebar.slider(
                "Top DEGs",
                5,
                50,
                20
            )

            if st.sidebar.button(
                "Generate DEG Plot",
                key="deg_plot"
            ):

                with st.spinner(
                    "Generating DEG analysis..."
                ):

                    plot_deg(
                        cell_type=deg_cell_type,
                        direction=deg_direction,
                        top_n=deg_top_n
                    )

                # -----------------------------------------
                # Quantitative evidence
                # -----------------------------------------

                summary = get_deg_summary(
                    cell_type=deg_cell_type,
                    direction=deg_direction,
                    top_n=deg_top_n
                )

                # -----------------------------------------
                # LLM biological interpretation
                # -----------------------------------------

                if check_ollama():

                    with st.spinner(
                        "Generating biological interpretation..."
                    ):

                        context = {

                            "plot_type": "deg",

                            "cell_type":
                                deg_cell_type,

                            "comparison":
                                "B18_M vs B18_C",

                            "direction":
                                deg_direction,

                            "summary":
                                summary
                        }

                        explanation = (
                            generate_llm_explanation(
                                context
                            )
                        )

                    st.subheader(
                        "Biological Interpretation"
                    )

                    st.write(
                        explanation
                    )
    # =============================================
    # Wilcoxon Test
    # =============================================

    elif analysis_type == "Wilcoxon Test":

        if st.sidebar.button(
            "Generate Plot",
            key="wilcoxon_plot"
        ):

            results = wilcoxon_vs_normal(
                gene
            )

            st.subheader(
                "Wilcoxon Results"
            )

            st.json(results)
    st.markdown(
    """
    <style>
    .footer {
        position: fixed;
        left: 0;
        bottom: 0;
        width: 100%;
        text-align: center;
        color: #000000;
        padding: 10px;
        font-size: 14px;
        background-color: rgba(0,0,0,0.35);
        z-index: 100;
    }
    </style>

    <div class="footer">
        © 2026 Institute of Sciences in Emergency Medicine (ISEM) — All rights reserved <br>
        Developed by Dr. Muhammad Turyalai Khan
    </div>
    """,
    unsafe_allow_html=True
    )