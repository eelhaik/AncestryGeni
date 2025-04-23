#!/bin/bash
#-----------------------------------------------------------------------
# AnalyzeFiles.sh
#-----------------------------------------------------------------------
#Program: This script reads the gzipped VCF file, uplifts the positions to GRC38, extracts only relevant SNP positions, and outputs the results to an output folder 
# The original VCF files have >1M SNPs. Here, the VCF file is first filtered for 300K SNPs of the 1KG SNPs, then liftover to grc38, which is of better quality.
# The conversion VCF->plink is done by plink. note, it may change the order of the markers from the VCF ([2 4] -> [4 2]) because it considers the minor one, not ancestral
# 
# A log file keeps the number of SNPs per file
# 
# Input files: vcf.gz
# Output files: plink files
#
# Run it: ./AnalyzeFiles.sh
# Notice: Updates the input and output folders
#-----------------------------------------------------------------------
# Written by: Eran Elhaik
# Date: 28/8/2023
# Ver: 1.40
#-----------------------------------------------------------------------
# New in 1.20: Adding documentation and comments. 
#	       Using temp file.   	
# New in 1.30: Using parameters file for input/output folders
# I also added --double-id to plink command to handle the multiple _ in the sample_ID  in the vcf file
# New in 1.40: I added a code that saves only the top 1200 rows
#-----------------------------------------------------------------------
module load libpng/1.2.59

# Read input and output file paths from the Parameters file
Parameters_file="Parameters.txt"

while IFS= read -r line; do
    #echo "Debug: $line"
    eval "$line"

    #echo "line..."
    #echo "$line"

    if [ -n "$line" ]; then
        Input_dir="$INPUT_DIR"
        Output_dir="$OUTPUT_DIR"
        ref_chr_pos="$REF_CHR_POS"
        ref_snps="$REF_SNPS"

        # Check if Input_dir is not empty
        if [ -n "$line" ]; then
            echo "Processing file: $line"
            # Continue with the rest of your script...
        else
            echo "Error: line is empty."
            # Terminate the script with an error status code
            exit 1
        fi
    else
        echo "Error: $line variable not defined in the Parameter file."
        # Terminate the script with an error status code
        exit 1
    fi

done < "$Parameters_file"

#Set the quality score
quality_score=40

log_file="Logfile.txt"

# List all files ending with vcf.gz in the input directory
vcf_files=$(ls -1 $Input_dir*vcf.gz)

# Loop through each vcf.gz file and run the echo command
first_iteration=true
for filename in $vcf_files; do

	#Get the VCF filename without the folder	
	filename=$(basename "$filename")
	echo "Processing file: $filename"
	#read -n 1 input
	
	# Extract filename without extension
	echo "   Creating filenames"
	file="$Input_dir${filename%.*.*}"
	file_bim="$file.bim"
	file_lifeover="$file_bim.lifted.bed"
	echo -e "   Creating input files: $file\n$file_bim\n$file_lifeover\n\n"
	
	#Creating Output files (temp and final)
	temp="temp"
	outputfile_temp="$Output_dir$temp"
	outputfile_temp_bim="${outputfile_temp}.bim"
	echo -e "   Creating temp output files\n1)$outputfile_temp\n2)$outputfile_temp_bim\n\n"
	
	outputfile="$Output_dir${filename%.*.*}"
	outputfile_bim="${outputfile}.bim"
	echo -e "   Creating output files: $outputfile\n$outputfile_bim\n\n"
	#read -n 1 input

	echo -e "Analyzing files: $file\n$file_bim\n\n"
	#read -n 1 input

	#Extract 1KG SNPs from vcf.gz file
	echo "   Extract 1KG SNPs from vcf.gz file..."
	#plink --vcf $Input_dir$filename --extract range $ref_chr_pos --allele1234 --make-bed --out $file  --allow-extra-chr --double-id
	
	#consdering quality
	plink --vcf $Input_dir$filename --vcf-filter 'PASS' --biallelic-only 'strict' --vcf-min-qual $quality_score --extract range $ref_chr_pos --allele1234 --make-bed --out $file  --allow-extra-chr --double-id
 	#read -n 1 input

	#Copy .bim file to a temp file & Create fake SNPs in the second column
	echo "   Copy .bim file to a temp file & Create fake SNPs in the second column..."
	mv $file_bim temp.bim
	awk -F'\t' '{print $1 "\t" $1 "_" $4 "\t" $3 "\t" $4 "\t" $5 "\t" $6}' temp.bim > $file_bim
	#read -n 1 input

	#Liftover .bim file to bim files => creates 2 files
	echo "   Liftover .bim file to bim files => creates 2 files..."
	./liftOver_hg19_to_hg38 $file_bim
	#read -n 1 input

	# ----------------------------
	#Analyze only 1,200 SNPs
	# ----------------------------
	echo "   Check if need to analyze a smaller set of SNPS..."
	if [ "$REDUCE_SNP_SET" = "1" ]; then
	#	#Keep only SNPs that were lifted in a temp file
		echo "   Keep only SNPs that were lifted in a temp file..."
		cut -f1 $file_lifeover > SNPs_temp.txt
	#	#read -n 1 input

		# Save only the top 1200 rows
		if [ -e "SNPs_temp.txt" ]; then
		    # Use the 'head' command to extract the first 1200 rows and save them to the output file
		    head -n 1200 "SNPs_temp.txt" > "SNPs.txt"
		    ref_snps=SNPs.txt
		    echo "First 1200 rows extracted and saved to SNPs.txt."
		else
		    echo "Error: Input file 'SNPs_temp.txt' not found."
		fi
	else
		echo "   Analyzing the full set of SNPS."
	fi		

	#Extract all the SNPs that were lifted into a filtered file
	echo "   Extract all the SNPS that were lifted into a filtered file..."
	plink --bfile $file --extract $ref_snps --allele1234 --make-bed --out $outputfile_temp --allow-extra-chr --double-id
	#read -n 1 input

	#Merge the two files by the SNP
	echo "   Merge the two files by the SNP..."
	awk 'NR==FNR { data[$1] = $3; next } ($2 in data) { print $1 "\t" $2 "\t" $3 "\t" data[$2] "\t" $5 "\t" $6 }' $file_lifeover $outputfile_temp_bim > output.txt
	#read -n 1 input

	#Replace the filtered file 
	echo "   Replace the filterested file..."
	cp output.txt $outputfile_bim
	#read -n 1 input

	#Run plink again, to sort the .bim file
	echo "   Run plink again, to sort the .bim file..."
	plink --bfile $outputfile_temp --make-bed --out $outputfile --double-id
	#read -n 1 input

	#Update log file
	# Count the number of lines in the input file
	line_count=$(wc -l < $outputfile_bim)

	# Check if log file exists
	if [ "$first_iteration" = true ]; then
	    echo "Creating log file: $log_file"
	    echo -e "$filename\t$line_count" > "$log_file"
	    first_iteration=false
	else
	    echo "Appending to log file: $log_file"
	    echo -e "$filename\t$line_count" >> "$log_file"
	fi

	#read -n 1 input

	#Clean up - remove plink log files and the liftover files
	find "$Input_dir" -type f -name "*.log" -delete
	find "$Input_dir" -type f -name "*.nosex" -delete
#	find "$Input_dir" -type f -name "*.bim.lifted.bed" -delete
#	find "$Input_dir" -type f -name "*.bim.unlifted.bed" -delete
done
