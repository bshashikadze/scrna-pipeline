"""QC metrics and Scrublet-based doublet detection."""
import scanpy as sc

from scrna_pipeline.provenance import stamp

qc_cfg = snakemake.config["qc"]
input_path = snakemake.input[0]

adata = sc.read_h5ad(input_path)

adata.var["mt"] = adata.var_names.str.startswith("MT-")
sc.pp.calculate_qc_metrics(adata, qc_vars=["mt"], percent_top=None, log1p=False, inplace=True)

sc.pp.filter_cells(adata, min_genes=qc_cfg["min_genes_per_cell"])
adata = adata[adata.obs["pct_counts_mt"] < qc_cfg["max_pct_mito"]].copy()
sc.pp.filter_genes(adata, min_cells=qc_cfg["min_cells_per_gene"])

# Scrublet needs a reduced gene set to stay memory-safe on this environment, and
# its own doublet score is computed on that subset only.
adata_hvg = adata.copy()
sc.pp.highly_variable_genes(adata_hvg, n_top_genes=2000, flavor="seurat_v3")
adata_subset = adata_hvg[:, adata_hvg.var["highly_variable"]].copy()

sc.pp.scrublet(adata_subset, expected_doublet_rate=qc_cfg["expected_doublet_rate"])
adata.obs["doublet_score"] = adata_subset.obs["doublet_score"]

# Scrublet's automatic threshold detection failed on this dataset (the observed
# and simulated doublet-score distributions don't separate into a clean bimodal
# shape here, plausibly because snRNA-seq nuclei carry less complexity than
# whole cells) — it picked a threshold above every observed score, calling zero
# doublets. Falling back to a quantile cut at the configured expected rate.
threshold = adata.obs["doublet_score"].quantile(1 - qc_cfg["expected_doublet_rate"])
adata.obs["predicted_doublet"] = adata.obs["doublet_score"] >= threshold

adata = adata[~adata.obs["predicted_doublet"]].copy()

stamp(adata, "qc", qc_cfg, input_path=input_path)
adata.write_h5ad(snakemake.output[0])
