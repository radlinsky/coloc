#/opt/software/R/3.1.1/bin/R

# get_coloc_summaries.R
# Caleb Matthew Radens
# cradens@mail.med.upenn.edu
# Last Update: 2016_1_5

system("echo ===========================")
R_ver <- substr(version$version.string,1,15) # Get R version
system("echo inside get_coloc_summaries")
system(paste("echo",R_ver))
system("echo ===========================")

if (substr(R_ver,11,15) != "3.1.1"){
  stop("Please run 'module load R-3.1.1' before initiating this script")
}

# Choose a path to load R packages from:
lp <- "/project/chrbrolab/analysis/cradens/bin/r_libs/r_module_3_1_1"

# Add your library path to the current session of R's library path variable
.libPaths(lp)

base <- "/project/chrbrolab/analysis/cradens/coloc_for_yoson/script/"
setwd(base)

# Get functions from import.R
source("import.R")
source("coloc_analysis.R")
require(coloc,lib=lp)

system("echo wrapper package and script dependencies loaded",wait=FALSE)

# Extract cmd argument
args <- commandArgs(trailingOnly = TRUE)
# See function description in import.R 
args <- get_command_args(args) 

merged_file <- args[["file"]]

merged_table<-read.table(merged_file,header=TRUE,stringsAsFactors = FALSE)

if(length(merged_table[,1])==0){
  write.table("hello world",file=paste(merged_file,"_completed_but_was_empty",sep=""))
  # Delete file once it has been imported
  system(paste("rm",merged_file),wait=FALSE)
  stop(paste("Table was empty:",merged_file))
}

# Delete file once it has been imported
system(paste("rm",merged_file),wait=FALSE)

cat(length(merged_table[,1])," shared SNPs to be analyzed for colocalisation ","\n",sep='')

# Build lists for coloc.abf() input
#   SNPs will be named according to their hg19 position
snp <- as.character(merged_table[,'chr_pos'])

beta_GWAS <- merged_table[,'beta_GWAS']
names(beta_GWAS) <- snp

beta_eQTL <- merged_table[,'beta_eQTL']
names(beta_eQTL) <- snp

varbeta_eQTL <- merged_table[,'varbeta_eQTL']
names(varbeta_eQTL) <- snp

varbeta_GWAS <- merged_table[,'varbeta_GWAS']
names(varbeta_GWAS) <- snp

MAF <- merged_table[,'MAF']
names(MAF) <- snp

N_eQTL <- merged_table[,'N_eQTL']
names(N_eQTL) <- snp

N_GWAS <- merged_table[,'N_GWAS']
names(N_GWAS) <- snp

eQTL_list <- list(beta = beta_eQTL, varbeta = varbeta_eQTL, type = "quant", N = N_eQTL, snp = snp)
GWAS_list <- list(beta = beta_GWAS, varbeta = varbeta_GWAS, type = "quant", N = N_GWAS , snp = snp)

result <- coloc.abf(dataset1 = eQTL_list, dataset2 = GWAS_list, MAF = MAF)

summary<- result$summary

summary<-data.frame(nsnps=summary[1],
                    hyp0=summary[2],
                    hyp1=summary[3],
                    hyp2=summary[4],
                    hyp3=summary[5],
                    hyp4=summary[6],
                    stringsAsFactors = FALSE)
write.table(summary,paste(merged_file,"_summary",sep=""),row.names=FALSE)

write.table("hello world",file=paste(merged_file,"_completed",sep=""))

split_underscores <- unlist(strsplit(merged_file,split="_"))
chr <- matrix(split_underscores,ncol=length(split_underscores))[,length(split_underscores)-2]
gene <- matrix(split_underscores,ncol=length(split_underscores))[,length(split_underscores)-5]
trait <- matrix(split_underscores,ncol=length(split_underscores))[,length(split_underscores)-4]
gene_trait <- paste(gene,trait,sep="_")

bedified <- bedify_coloc(result, chr, gene_trait)

write.table(bedified,file=paste(gene_trait,"_BEDIFIED",sep=""),row.names=FALSE,col.names=FALSE)
