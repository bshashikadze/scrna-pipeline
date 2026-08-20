"""Cell Ranger MTX output -> structured AnnData."""
import scanpy as sc
import anndata as ad

samples = snakemake.config["dataset"]["samples"]
mtx_dir = "results/interim/samples_mtx"

adatas = []

for sample_id, meta in samples.items():
    a = sc.read_10x_mtx(f"{mtx_dir}/{sample_id}", var_names="gene_symbols")
    a.obs["sample_id"] = sample_id
    a.obs["condition"] = meta["condition"]
    a.obs["donor"] = meta["donor"]
    a.obs_names = sample_id + "_" + a.obs_names
    adatas.append(a)

adata = ad.concat(adatas, join="outer")
adata.write_h5ad(snakemake.output[0])