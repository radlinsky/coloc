#/opt/software/R/3.1.1/bin/R

# make_gene_trait_tables.R
# Caleb Matthew Radens
# cradens@mail.med.upenn.edu
# Last Update: 2016_1_26

# This is a wrapper script that runs imports a GWAS trait table and all eQTL tables that
#   fall within 1e6 bp of sentinal SNP regions in the GWAS table, then exports tables
#   that are a merge of the GWAS and each eQTL table.

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
require(data.table,lib=lp) # eQTL_directory <- "/project/chrbrolab/coloc/data/ivs"

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
eQTL_directory <- args[["eQTL_dir"]]

# Specify where the eQTL files are located
# eQTL_directory <- "/project/chrbrolab/coloc/data/ivs/"

# Retrieve list of genes matching the pattern below and assign filepath to each gene
genes <- get_gene_names(directory= eQTL_directory, Pattern=".txt")

# Import the GWAS table (this will be slow)
trait_table <- read_GWAS(File_path=GWAS_file,
                         Columns=11,
                         Skip=1,
                         Sep="\t",
                         Chr_col=3,
                         Chr_pos_col=2,
                         Rsid_col=1, 
                         Pos_col=4,
                         MAF_col=8,
                         #N_col,            # Using beta and varbeta, not N and PV
                         #PV_col,           # Using beta and varbeta, not N and PV
                         Beta_col=9,
                         Varbeta_col=10,
                         Var_is_SE = TRUE)

# Identify the sentinal SNPs (those SNPs that are smaller than some cutoff
#   and not within range of each other) 
# By default, look for SNPs that are at least range away from each other and
# are less than or equal to 5e-8
cutoff_PV <- 5e-8
range <- 1e5
trait_table_PVs <- get_sentinal_snp_regions(trait_table, Range = range, Cutoff_PV = cutoff_PV)

# Import the microArray alignment table associated with the eQTL
microArray_alnTable_file <- "/project/chrbrolab/analysis/cradens/coloc/data/GPL4133-26578.alnTable.txt"
microArray_alnTable<-get_microArray_table(microArray_alnTable_file)

# Extract the TESs from microalignment table
# g <- microArray_alnTable$gene
# unique_gene_indeces <- order(g)[!duplicated(sort(g))]
# microArray_alnTable <- microArray_alnTable[unique_gene_indeces,]
# t <- microArray_alnTable$TEScolClasses[Pos_col]
# unique_TES_indeces <- order(t)[!duplicated(sort(t))]
# microArray_alnTable <- microArray_alnTable[unique_TES_indeces,]
genes <- merge(genes, microArray_alnTable, by=c("gene","chr"), all = FALSE)
unique_genes <- unique(genes$gene)


# Determine which genes are within range bp of the sentinal SNPs
sig_genes <- c()
tss <- c()
for (Gene in unique_genes){
  
  gene_data <- genes[which(genes$gene==Gene),]
  g_chr <- unique(gene_data$chr)
  if (length(g_chr>1)){
    stop(paste("More than 1 chr associated with:",Gene))
  }
  # Use the mode of the gene TSS from the table (if equal numbers of different TSSs,
  #   it picks one TSS at randon, I think)
  u_gene_tss <- unique(gene_data$TSS)
  g_tss <- u_gene_tss[which.max(tabulate(match(gene_data$TSS, u_gene_tss)))]
  # Calculate the range to search for P-values
  bottom<-g_tss-range
  top<-g_tss+range
  # If chromosome of gene and the top GWAS PV_SNP match:
  if (TRUE%in%grepl(g_chr,trait_table_PVs$chr)){
    # Get the loci from trait_table_PV that match the chromosome of the gene
    t_pos <- trait_table_PVs$chr_pos[which(grepl(g_chr,trait_table_PVs$chr))]
    t_pos <- as.integer(matrix(unlist(strsplit(t_pos,split="_")),ncol=2,byrow=TRUE)[,2])
    # If the g_tss is within 1MB of the genome-wide significant PV:
    if (TRUE%in%(t_pos >= bottom & t_pos <= top)){
      # Add the gene to the sig_gene list if any of the trait PVs are close to the gene
      sig_genes <- c(sig_genes,Gene)
      tss <- c(tss, g_tss)
    } 
  }
}

# Make sure there was at least 1 gene added to the sig_gene list
if (length(sig_genes) == 0){
  # If not, stop the script and write the _completed file so wrapper.R may move on2
  write.table("hello world",file=paste(Trait,"_completed",sep=""))
  stop(paste(Trait,"has no significant PVs close to the genes tested."))
}

genes_to_analyze <- data.frame(gene=sig_genes,
                               TSS=tss,
                               stringsAsFactors=FALSE)
genes_to_analyze <- merge(genes_to_analyze, genes, by=c("gene","TSS"))
gene_files_to_analyze <- genes_to_analyze$filepath
chromosomes_to_analyze <- genes_to_analyze$chr
n_genes_to_analyze <- length(genes_to_analyze$gene)
gene_trait_tss <- paste(genes_to_analyze$gene,Trait,genes_to_analyze$TSS,sep="_")

for (gene_row in seq(from=1,to=n_genes_to_analyze)){

  gene_table <- read_eQTL(File_path=gene_files_to_analyze[gene_row],
                          Columns=11,
                          Skip=1,
                          Sep="\t",
                          Chr_col=3,
                          Rsid_col=2,
                          Pos_col=4,
                          #N_col,       # Using beta and varbeta
                          #PV_col,      # Using beta and varbeta
                          Beta_col=9,
                          Varbeta_col=10,
                          Var_is_SE = TRUE)
  # Merge GWAS and eQTL table columns:
  #   only keep SNPs that have a shared hg19 position between GWAS and eQTL.
  merged_table <- merge(gene_table, 
                        trait_table, 
                        by = c("chr_pos"),
                        all = FALSE)
  write.table(merged_table, file = paste(gene_trait_tss[gene_row],"_",chromosomes_to_analyze[gene_row],"_analyze_me",sep=""))
}
write.table("hello world",file=paste(Trait,"_completed",sep=""))