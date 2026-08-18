# Reads one GEO .rds (zUMIs dgecounts) file, converts to h5ad via sceasy.
library(Seurat)
library(sceasy)
library(glue)

rds_files  <- list.files(file.path("data", "raw"))

output_dir <- file.path("results", "interim")

if (!dir.exists(output_dir)) dir.create(output_dir)

for (rds_file in rds_files) {

  rds_file_name = gsub(".rds", "", rds_file)

  x <- readRDS(file.path("data", "raw", rds_file))
  umi_inex_all <- x$umicount$inex$all
  assay_v3 <- Seurat::CreateAssayObject(counts = umi_inex_all) # otherwise getting  The `slot` argument of `GetAssayData()` was deprecated in SeuratObject 5.0.0 and is now defunct.
  umi_inex_all_seurat <- Seurat::CreateSeuratObject(assay_v3)
  convertFormat(obj = umi_inex_all_seurat, from="seurat", to="anndata", outFile=glue("{rds_file_name}.h5ad"))
}
