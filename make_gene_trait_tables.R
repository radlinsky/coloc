#/opt/software/R/3.1.1/bin/R

# make_gene_trait_tables.R
# Caleb Matthew Radens
# cradens@mail.med.upenn.edu
# Last Update: 2016_1_19

# This is a wrapper script that runs imports a GWAS trait table and all gene tables that
#   fall within 1e6 bp of sentinal SNP regions in the GWAS table, then exports tables
#   that are a merge of the GWAS and each gene table.

# I tested this script using the PMACS R module 3.1.1
system("echo ===========================",wait=FALSE)
system("echo inside make_gene_trait_tables.R",wait=FALSE)
R_ver <- substr(version$version.string,1,15) # Get R version
system(paste("echo",R_ver),wait=FALSE)
system("echo ===========================",wait=FALSE)

if (substr(R_ver,11,15) != "3.1.1"){
  stop("Please run 'module load R-3.1.1' before initiating this script")
}

# Choose a path to load R packages from:
lp <- "/project/chrbrolab/analysis/cradens/bin/r_libs/r_module_3_1_1"

# Add your library path to the current session of R's library path variable
.libPaths(lp)

# Loads the required packages
require(data.table,lib=lp) 
source("import.R")

system("echo wrapper package and script dependencies loaded",wait=FALSE)

# Extract cmd arguments (see get_command_args in import.R for details)
# Too Long, Didn't Read: you can add trailing arguments to this function if
#  called in PMACS.. those arguments are captured by get_command_args
args <- commandArgs(trailingOnly = TRUE)
# See function description in import.R 
args <- get_command_args(args) 

print(args)

GWAS_file <- args[["file"]]
Trait <- args[["trait"]]

# Specify where the eQTL files are located
eQTL_directory <- "/project/chrbrolab/coloc/data/ivs"

# Retrieve list of genes matching the pattern below and assign filepath to each gene
pattern <- "eqtl"
genes <- get_gene_names(eQTL_directory, Pattern = pattern)
genes$filepath <- paste(eQTL_directory,genes$filename,sep="/")

# Import the GWAS table (this will be slow)
trait_table <- read_GLGC_GWAS(GWAS_file, minimum = TRUE)

# Identify the sentinal SNPs (those SNPs that are smaller than some cutoff
#   and not within range of each other) 
# By default, look for SNPs that are at least range away from each other and
# are less than or equal to 5e-8
cutoff_PV <- 1e-6
range <- 1e6
trait_table_PVs <- get_sentinal_snp_regions(trait_table, Range = range, Cutoff_PV = cutoff_PV)

# Import the microArray alignment table associated with the eQTL
microArray_alnTable_file <- "/project/chrbrolab/analysis/cradens/coloc/data/GPL4133-26578.alnTable.txt"
microArray_alnTable<-get_microArray_table(microArray_alnTable_file)

# Extract the TESs from microalignment table
g <- microArray_alnTable$gene
unique_gene_indeces <- order(g)[!duplicated(sort(g))]
microArray_alnTable <- microArray_alnTable[unique_gene_indeces,]
t <- microArray_alnTable$TES
unique_TES_indeces <- order(t)[!duplicated(sort(t))]
microArray_alnTable <- microArray_alnTable[unique_TES_indeces,]
genes <- merge(genes, microArray_alnTable, by=c("gene","chr"), all = FALSE)

# Determine which genes are within range bp of the sentinal SNPs
sig_genes <- c()
tes <- c()
for (gene_row in seq(from=1,to=length(genes$gene))){
  g_chr <- genes$chr[gene_row]
  g_tes <- genes$TES[gene_row]
  bottom<-g_tes-range
  top<-g_tes+range
  # If chromosome of gene and the top trait_PV_SNP match:
  if (TRUE%in%grepl(g_chr,trait_table_PVs$chr)){
    # Get the loci from trait_table_PV that match the chromosome of the gene
    t_pos <- trait_table_PVs$chr_loci[which(grepl(g_chr,trait_table_PVs$chr))]
    t_pos <- as.integer(matrix(unlist(strsplit(t_pos,split=":")),ncol=2,byrow=TRUE)[,2])
    # If the g_tes is within 1MB of the genome-wide significant PV:
    if (TRUE%in%(t_pos >= bottom & t_pos <= top)){
      # Add the gene to the sig_gene list if any of the trait PVs are close to the gene
      sig_genes <- c(sig_genes,genes$gene_full[gene_row])
      tes <- c(tes, g_tes)
    } 
  }
}

# Make sure there was at least 1 gene added to the sig_gene list
if (length(sig_genes) == 0){
  # If not, stop the script and write the _completed file so wrapper.R may move on2
  write.table("hello world",file=paste(Trait,"_completed",sep=""))
  stop(paste(Trait,"has no significant PVs close to the genes tested."))
}

genes_to_analyze <- data.frame(gene_full=sig_genes,
                               TES=tes,
                               stringsAsFactors=FALSE)
genes_to_analyze <- merge(genes_to_analyze, genes, by=c("gene_full","TES"))
gene_files_to_analyze <- genes_to_analyze$filepath
chromosomes_to_analyze <- genes_to_analyze$chr
n_genes_to_analyze <- length(genes_to_analyze$gene)
gene_trait_tes <- paste(genes_to_analyze$gene_full,Trait,genes_to_analyze$TES,sep="_")

for (gene_row in seq(from=1,to=n_genes_to_analyze)){

  gene_table <- read_CLI_eQTL(gene_files_to_analyze[gene_row],chromosomes_to_analyze[gene_row],unzip=FALSE)

  # Merge GWAS and eQTL table columns:
  #   only keep SNPs that have a shared hg19 position between GWAS and eQTL.
  merged_table <- merge(gene_table, 
                        trait_table, 
                        by = c("chr_loci"),
                        all = FALSE)
  write.table(merged_table, file = paste(gene_trait_tes[gene_row],"_",chromosomes_to_analyze[gene_row],"_analyze_me",sep=""))
}
write.table("hello world",file=paste(Trait,"_completed",sep=""))