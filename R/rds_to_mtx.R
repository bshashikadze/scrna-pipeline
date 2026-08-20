# Reads one GEO .rds (zUMIs dgecounts) file, writes a 10x MTX triplet.
library(Matrix)

sample_id <- snakemake@wildcards[["sample"]]

rds_file <- list.files(
  file.path("data", "raw"),
  pattern = paste0("^", sample_id, "_.*\\.rds$"),
  full.names = TRUE
)
stopifnot(length(rds_file) == 1)

x <- readRDS(rds_file)
counts <- x$umicount$inex$all

out_dir <- dirname(snakemake@output[["matrix"]])
if (!dir.exists(out_dir)) dir.create(out_dir, recursive = TRUE)

matrix_path <- sub("\\.gz$", "", snakemake@output[["matrix"]])
writeMM(counts, matrix_path)
system(paste("gzip -f", matrix_path))

writeLines(colnames(counts), gzfile(snakemake@output[["barcodes"]]))

features <- data.frame(
  id = rownames(counts),
  symbol = rownames(counts),
  type = "Gene Expression"
)
write.table(
  features,
  gzfile(snakemake@output[["features"]]),
  sep = "\t",
  row.names = FALSE,
  col.names = FALSE,
  quote = FALSE
)
