# scrna-pipeline

A single-cell RNA-seq ingestion, QC, and analysis pipeline, built on human diabetic kidney disease (DKD) data.

## Design

Polyglot pipeline, orchestrated as one Snakemake DAG:

- **Python** — ingestion (Cell Ranger MTX to AnnData), QC (mito%, doublet detection), provenance tracking, Snakemake orchestration.
- **R (Seurat)** — normalization, HVG selection, Harmony batch integration, Leiden clustering, marker-based annotation.

## Dataset

[GSE131882](https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE131882) — Wilson et al., PNAS 2019. Three early-DKD and three control human kidney biopsies, ~23,000 cells, 10x Chromium v2. The analysis notebook reproduces the paper's core finding: a proximal tubule injury signature in DKD versus control.

## Running it

```bash
uv sync
bash scripts/download_data.sh
snakemake --cores 4
```

QC decisions are in `notebooks/01_qc_report.ipynb`; the biological result is in `notebooks/02_biological_analysis.Rmd`.

## Not built here (roadmap)

- Bulk proteomics integration and cell-type deconvolution
- Cross-species integration (mouse to human DKD)
- Foundation-model annotation (scGPT, CellTypist)
- Automated QC triage

## Layout

```
scrna-pipeline/
├── config/config.yaml
├── Snakefile
├── src/scrna_pipeline/       # Python: ingest, qc, provenance, multimodal (stub)
├── R/                        # R: normalize, integrate, annotate
├── notebooks/
├── tests/
├── scripts/download_data.sh
├── data/                     # gitignored
└── results/                  # gitignored
```
