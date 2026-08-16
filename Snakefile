configfile: "config/config.yaml"

# Python: ingestion + QC (data engineering surface)
# R (Seurat): normalization, integration, clustering, annotation (analysis surface)

rule all:
    input:
        "results/processed/annotated.rds",
        "notebooks/01_qc_report.ipynb",
        "notebooks/02_biological_analysis.Rmd",

rule ingest:
    output:
        "results/interim/raw.h5ad",
    script:
        "src/scrna_pipeline/ingest.py"

rule qc:
    input:
        "results/interim/raw.h5ad",
    output:
        "results/interim/qc_filtered.h5ad",
    script:
        "src/scrna_pipeline/qc.py"

rule normalize:
    input:
        "results/interim/qc_filtered.h5ad",
    output:
        "results/interim/normalized.rds",
    script:
        "R/normalize.R"

rule integrate:
    input:
        "results/interim/normalized.rds",
    output:
        "results/interim/integrated.rds",
    script:
        "R/integrate.R"

rule annotate:
    input:
        "results/interim/integrated.rds",
    output:
        "results/processed/annotated.rds",
    script:
        "R/annotate.R"
