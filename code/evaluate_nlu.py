import os
import sys
import json
import pandas as pd

# ============================================================
# PATHS
# ============================================================

BASE_DIR = r"C:\Users\Turyal\Desktop\CellInterpreter"

TEST_FILE = os.path.join(
    BASE_DIR,
    "CellInterpreter_NLU_150_Test_Set.csv"
)

RESULT_FILE = os.path.join(
    BASE_DIR,
    "CellInterpreter_NLU_150_Results.csv"
)

# ============================================================
# IMPORT CELINTERPRETER NLU FUNCTION
# ============================================================

# Change this path if language_layer.py is stored elsewhere.
CELLINTERPRETER_DIR = BASE_DIR

if CELLINTERPRETER_DIR not in sys.path:
    sys.path.insert(0, CELLINTERPRETER_DIR)

from language_layer import llm_to_command


# ============================================================
# HELPER FUNCTIONS
# ============================================================

def normalize_gene(value):
    """
    Normalize a single gene name.
    """
    if value is None:
        return None

    if pd.isna(value):
        return None

    value = str(value).strip().upper()

    if value == "":
        return None

    return value


def normalize_genes(value):
    """
    Convert a CSV gene field or parser gene field into
    a normalized list.

    Examples:

        FOXP3
        TP53,IL9
        ["TP53", "IL9"]
    """

    if value is None:
        return []

    if isinstance(value, float) and pd.isna(value):
        return []

    if isinstance(value, list):
        genes = value

    elif isinstance(value, tuple):
        genes = list(value)

    else:
        value = str(value).strip()

        if value == "":
            return []

        # Handle comma-separated CSV values
        genes = [
            x.strip()
            for x in value.split(",")
            if x.strip()
        ]

    return [
        str(g).strip().upper()
        for g in genes
        if str(g).strip()
    ]


def extract_predicted_genes(command):
    """
    Handle both parser formats:

        {"gene": "FOXP3"}

    and

        {"genes": ["TP53", "IL9"]}
    """

    if not isinstance(command, dict):
        return []

    # Multiple-gene format
    if "genes" in command:
        return normalize_genes(command["genes"])

    # Single-gene format
    if "gene" in command:
        gene = normalize_gene(command["gene"])

        if gene:
            return [gene]

    return []


def extract_expected_genes(row):
    """
    Read expected gene information from the benchmark.

    Current CSV uses expected_gene.

    This also supports expected_genes if you later add
    that column.
    """

    # Prefer expected_genes if available
    if "expected_genes" in row.index:
        value = row["expected_genes"]

        if not pd.isna(value) and str(value).strip():
            return normalize_genes(value)

    # Otherwise use expected_gene
    if "expected_gene" in row.index:
        return normalize_genes(row["expected_gene"])

    return []


def normalize_task(value):
    """
    Normalize task labels.
    """

    if value is None:
        return ""

    if pd.isna(value):
        return ""

    return str(value).strip()


# ============================================================
# LOAD TEST SET
# ============================================================

print("=" * 70)
print("CellInterpreter NLU Evaluation")
print("=" * 70)

print(f"\nLoading test set:")
print(TEST_FILE)

df = pd.read_csv(TEST_FILE)

print(f"\nNumber of test queries: {len(df)}")

required_columns = [
    "id",
    "query",
    "expected_task"
]

for column in required_columns:
    if column not in df.columns:
        raise ValueError(
            f"Required column missing from CSV: {column}"
        )


# ============================================================
# EVALUATION STORAGE
# ============================================================

results = []


# ============================================================
# RUN ALL QUERIES
# ============================================================

for index, row in df.iterrows():

    query_id = row["id"]
    query = str(row["query"]).strip()

    expected_task = normalize_task(
        row["expected_task"]
    )

    expected_genes = extract_expected_genes(row)

    print(
        f"\n[{index + 1}/{len(df)}] "
        f"ID={query_id}"
    )

    print(f"Query: {query}")

    # --------------------------------------------------------
    # RUN ACTUAL NLU PARSER
    # --------------------------------------------------------

    try:

        command = llm_to_command(query)

        if command is None:
            command = {}

        predicted_task = normalize_task(
            command.get("task")
        )

        predicted_genes = extract_predicted_genes(
            command
        )

        parser_error = ""

    except Exception as e:

        command = {}

        predicted_task = ""

        predicted_genes = []

        parser_error = str(e)


    # --------------------------------------------------------
    # TASK COMPARISON
    # --------------------------------------------------------

    task_correct = (
        predicted_task == expected_task
    )


    # --------------------------------------------------------
    # GENE COMPARISON
    # --------------------------------------------------------

    # Compare gene lists irrespective of whether parser
    # returned "gene" or "genes".
    #
    # Order is ignored so:
    #
    # ["TP53", "IL9"]
    #
    # and
    #
    # ["IL9", "TP53"]
    #
    # are considered equivalent.

    gene_correct = (
        sorted(predicted_genes)
        == sorted(expected_genes)
    )


    # --------------------------------------------------------
    # EXACT MATCH
    # --------------------------------------------------------

    exact_match = (
        task_correct
        and gene_correct
    )


    # --------------------------------------------------------
    # PRINT RESULT
    # --------------------------------------------------------

    print(
        f"Expected task:   {expected_task}"
    )

    print(
        f"Predicted task:   {predicted_task}"
    )

    print(
        f"Expected genes:   {expected_genes}"
    )

    print(
        f"Predicted genes:  {predicted_genes}"
    )

    print(
        f"Task correct:     {task_correct}"
    )

    print(
        f"Gene correct:     {gene_correct}"
    )

    print(
        f"Exact match:      {exact_match}"
    )


    # --------------------------------------------------------
    # STORE RESULT
    # --------------------------------------------------------

    results.append({

        "id": query_id,

        "query": query,

        "category": (
            row["category"]
            if "category" in row.index
            else ""
        ),

        "expected_task": expected_task,

        "predicted_task": predicted_task,

        "expected_genes": ",".join(
            expected_genes
        ),

        "predicted_genes": ",".join(
            predicted_genes
        ),

        "task_correct": task_correct,

        "gene_correct": gene_correct,

        "exact_match": exact_match,

        "parser_output": json.dumps(
            command,
            ensure_ascii=False
        ),

        "parser_error": parser_error
    })


# ============================================================
# CREATE RESULTS DATAFRAME
# ============================================================

results_df = pd.DataFrame(results)


# ============================================================
# OVERALL METRICS
# ============================================================

total = len(results_df)

task_accuracy = (
    results_df["task_correct"].mean()
    if total > 0
    else 0
)

gene_accuracy = (
    results_df["gene_correct"].mean()
    if total > 0
    else 0
)

exact_match_accuracy = (
    results_df["exact_match"].mean()
    if total > 0
    else 0
)


# ============================================================
# PRINT OVERALL RESULTS
# ============================================================

print("\n")
print("=" * 70)
print("OVERALL RESULTS")
print("=" * 70)

print(
    f"\nTotal queries:       {total}"
)

print(
    f"Task accuracy:       {task_accuracy:.4f}"
    f"  ({task_accuracy * 100:.2f}%)"
)

print(
    f"Gene accuracy:       {gene_accuracy:.4f}"
    f"  ({gene_accuracy * 100:.2f}%)"
)

print(
    f"Exact-match accuracy:{exact_match_accuracy:.4f}"
    f"  ({exact_match_accuracy * 100:.2f}%)"
)


# ============================================================
# RESULTS BY CATEGORY
# ============================================================

if "category" in results_df.columns:

    print("\n")
    print("=" * 70)
    print("RESULTS BY CATEGORY")
    print("=" * 70)

    category_results = (
        results_df
        .groupby("category")
        .agg(
            queries=("id", "count"),
            task_accuracy=("task_correct", "mean"),
            gene_accuracy=("gene_correct", "mean"),
            exact_match_accuracy=("exact_match", "mean")
        )
        .reset_index()
    )

    category_results[
        "task_accuracy"
    ] *= 100

    category_results[
        "gene_accuracy"
    ] *= 100

    category_results[
        "exact_match_accuracy"
    ] *= 100

    print(
        category_results.to_string(
            index=False,
            float_format=lambda x: f"{x:.2f}"
        )
    )


# ============================================================
# SHOW INCORRECT CASES
# ============================================================

incorrect = results_df[
    ~results_df["exact_match"]
]

print("\n")
print("=" * 70)
print("INCORRECT QUERIES")
print("=" * 70)

print(
    f"\nIncorrect queries: "
    f"{len(incorrect)} / {total}"
)

if len(incorrect) > 0:

    for _, row in incorrect.iterrows():

        print("\n" + "-" * 70)

        print(
            f"ID: {row['id']}"
        )

        print(
            f"Query: {row['query']}"
        )

        print(
            f"Expected task: "
            f"{row['expected_task']}"
        )

        print(
            f"Predicted task: "
            f"{row['predicted_task']}"
        )

        print(
            f"Expected genes: "
            f"{row['expected_genes']}"
        )

        print(
            f"Predicted genes: "
            f"{row['predicted_genes']}"
        )

        print(
            f"Parser output: "
            f"{row['parser_output']}"
        )


# ============================================================
# SAVE RESULTS
# ============================================================

results_df.to_csv(
    RESULT_FILE,
    index=False,
    encoding="utf-8-sig"
)

print("\n")
print("=" * 70)

print(
    f"Detailed results saved to:"
)

print(
    RESULT_FILE
)

print("=" * 70)

# ============================================================
# FINAL NLU EVALUATION STATISTICS
# ============================================================

total = len(results)

# ------------------------------------------------------------
# Separate supported and out-of-scope queries
# ------------------------------------------------------------

def get_category(result):
    """
    Safely retrieve category as a lowercase string.
    Handles empty CSV cells / NaN values.
    """
    category = result.get("category", "")

    if category is None:
        return ""

    return str(category).strip().lower()


def get_expected_task(result):
    task = result.get("expected_task", "")

    if task is None:
        return ""

    return str(task).strip().lower()


# Supported queries have an expected task.
supported_results = [
    r for r in results
    if get_expected_task(r) != ""
]

# Out-of-scope queries intentionally have no expected task.
out_of_scope_results = [
    r for r in results
    if get_expected_task(r) == ""
]

# ------------------------------------------------------------
# 1. TASK ACCURACY
#    Only supported plot queries
# ------------------------------------------------------------

if supported_results:
    task_correct_count = sum(
        bool(r.get("task_correct", False))
        for r in supported_results
    )
    task_accuracy = 100 * task_correct_count / len(supported_results)
else:
    task_correct_count = 0
    task_accuracy = 0.0

# ------------------------------------------------------------
# 2. GENE EXTRACTION ACCURACY
#    Only supported queries where a gene is expected
# ------------------------------------------------------------

gene_results = []

for r in supported_results:
    expected_genes = r.get("expected_genes", [])

    # Also support the older expected_gene field
    if not expected_genes:
        expected_gene = r.get("expected_gene", "")
        if expected_gene:
            expected_genes = [expected_gene]

    if expected_genes:
        gene_results.append(r)

if gene_results:
    gene_correct_count = sum(
        bool(r.get("gene_correct", False))
        for r in gene_results
    )
    gene_accuracy = 100 * gene_correct_count / len(gene_results)
else:
    gene_correct_count = 0
    gene_accuracy = 0.0

# ------------------------------------------------------------
# 3. EXACT-MATCH ACCURACY
#    Supported queries only
# ------------------------------------------------------------

if supported_results:
    exact_correct_count = sum(
        bool(r.get("exact_match", False))
        for r in supported_results
    )
    exact_accuracy = 100 * exact_correct_count / len(supported_results)
else:
    exact_correct_count = 0
    exact_accuracy = 0.0

# ------------------------------------------------------------
# 4. OUT-OF-SCOPE REJECTION ACCURACY
# ------------------------------------------------------------

def is_correctly_rejected(result):
    """
    Determine whether an out-of-scope query was rejected
    rather than mapped to a supported plotting task.
    """

    predicted_task = str(
        result.get("predicted_task", "")
    ).strip().lower()

    # Tasks that indicate the parser incorrectly interpreted
    # an out-of-scope request as a supported plotting command.
    supported_plot_tasks = {
        "plot_expression",
        "plot_violin",
        "plot_dotplot",
        "plot_umap",
        "plot_tsne"
    }

    # If it mapped to one of the supported plotting tasks,
    # the rejection is incorrect.
    if predicted_task in supported_plot_tasks:
        return False

    # Otherwise, consider it rejected.
    #
    # This includes outputs such as:
    # invalid, error, none, clarification, invalid_command,
    # assistant_response, etc.
    return True


if out_of_scope_results:
    rejection_correct_count = sum(
        is_correctly_rejected(r)
        for r in out_of_scope_results
    )
    rejection_accuracy = (
        100 * rejection_correct_count / len(out_of_scope_results)
    )
else:
    rejection_correct_count = 0
    rejection_accuracy = 0.0

# ------------------------------------------------------------
# 5. OVERALL ACCURACY
#
# For the 150-query benchmark:
#   - 140 supported queries
#   - 10 out-of-scope queries
#
# A query is considered correct if:
#   supported query  -> correct task
#   out-of-scope     -> correctly rejected
# ------------------------------------------------------------

overall_correct_count = (
    task_correct_count +
    rejection_correct_count
)

overall_accuracy = 100 * overall_correct_count / total

# ------------------------------------------------------------
# PRINT FINAL RESULTS
# ------------------------------------------------------------

print("\n")
print("=" * 70)
print("FINAL NLU EVALUATION RESULTS")
print("=" * 70)

print(f"Total queries evaluated       : {total}")
print(f"Supported plot queries       : {len(supported_results)}")
print(f"Out-of-scope queries         : {len(out_of_scope_results)}")

print("-" * 70)

print(
    f"Task accuracy                : "
    f"{task_accuracy:.2f}% "
    f"({task_correct_count}/{len(supported_results)})"
)

print(
    f"Gene extraction accuracy     : "
    f"{gene_accuracy:.2f}% "
    f"({gene_correct_count}/{len(gene_results)})"
)

print(
    f"Exact-match accuracy         : "
    f"{exact_accuracy:.2f}% "
    f"({exact_correct_count}/{len(supported_results)})"
)

print(
    f"Out-of-scope rejection       : "
    f"{rejection_accuracy:.2f}% "
    f"({rejection_correct_count}/{len(out_of_scope_results)})"
)

print(
    f"Overall accuracy             : "
    f"{overall_accuracy:.2f}% "
    f"({overall_correct_count}/{total})"
)

print("=" * 70)

print("\nDetailed results saved to:")
print(RESULT_FILE)