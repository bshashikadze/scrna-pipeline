# Notes

Running log of major decisions and gotchas. Not a full changelog — just what's worth remembering later.

## Environment

- System R (3.6.3) too old for Seurat v5 — added CRAN's apt repo, installed R 4.5.2 instead.
- Seurat install failed with a cascade of unrelated compile errors (stringi, RcppArmadillo, etc).
  Root cause: Linuxbrew was ahead of `/usr/bin` in `PATH`, so build tools (`awk`, `gfortran`) resolved
  to Linuxbrew's versions, which need a newer glibc than Ubuntu 20.04 has. Fixed by moving Linuxbrew
  to the end of `PATH` in `.bashrc`.
- Everything runs inside WSL, not the Windows R install that was already on the machine — kept
  Python and R in one Linux environment for reproducibility.
- Seurat's source install also needed several system libs apt doesn't pull in automatically:
  `libuv1-dev` (for `fs`), `libudunits2-dev` (for `units`, a geospatial dependency), and `cmake`
  (for `s2`, which compiles its own bundled Abseil since Ubuntu 20.04 has no `libabsl-dev`).
- h5ad ↔ Seurat bridge: went with `sceasy` over `SeuratDisk` — fewer compiled dependencies,
  simpler after everything above.

## Data

- GSE131882 has no 10x MTX files on GEO — only per-sample `.rds` count matrices (zUMIs
  dgecounts format), snRNA-seq not scRNA-seq. Pipeline's first step: R reads the `.rds`,
  pulls out `umicount$inex$all` (UMI-deduplicated, exon+intron — the right choice for
  snRNA-seq, since nuclear RNA is intron-rich), and writes plain 10x MTX triplets. Python's
  `ingest.py` then reads those with `scanpy.read_10x_mtx` as originally planned.
- `sceasy` (0.0.7) turned out incompatible with SeuratObject 5.4.0 — it still calls
  `GetAssayData(slot = ...)`, an argument Seurat removed entirely in v5. No version of a
  Seurat object worked around it. Dropped `sceasy` — R now writes MTX directly
  (`Matrix::writeMM` + barcodes/features tsv) instead of going through a Seurat/AnnData
  object conversion at all.
- Per-sample gene counts in the raw MTX triplets differ (e.g. one sample has ~36.8k genes,
  another ~34.1k) — zUMIs' `dgecounts` matrix only keeps genes with at least one UMI count
  in that sample, so a gene silent everywhere in a sample just isn't a row. `ingest.py`
  concatenates with `anndata.concat(..., join="outer")` so genes missing from a given
  sample get filled with zero rather than dropped from the merged object.
- `raw.h5ad` has ~126k cells, far more than the paper's ~23k — expected at this stage.
  zUMIs' raw counts include every barcode above a minimal read threshold, mostly empty
  droplets/ambient noise, not just real nuclei. Cutting that down to real cells is QC's
  job (min genes/cell, mito%, Scrublet), not ingestion's.
