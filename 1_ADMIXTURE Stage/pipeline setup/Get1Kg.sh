#!/bin/bash
#-----------------------------------------------------------------------
# Get1Kg.sh
#-----------------------------------------------------------------------
#Program: This script reads all the .bim files from an input folder, it then extarct 1kg genotype data for those SNPs and outputs the results into an output folder
# It also filters positions that are indels.
#
# 1KG data are here: /lunarc/nobackup/projects/snic2019-34-3/shared_elhaik_lab1/SubMicrob/Res/1kg/ReferencePops/hg38
# 
# Input files: *.bim
# Output files: plink file
#
# Run it: ./Get1Kg.sh
# Notice: Update the input and output folders
#-----------------------------------------------------------------------
# Written by: Eran Elhaik
# Date: 7/9/2023
# Ver: 1.20
#-----------------------------------------------------------------------
# Ver 1.10: Now removing temp files
#	    Input file is also written to a temp file first, to avoid creating plink temp files 	
#	    Add line counts to an output file	
# New in 1.20: Using parameters file for input/output folders
#-----------------------------------------------------------------------
# Read input and output file paths from the Parameters file
Parameters_file="Parameters.txt"

while IFS= read -r line; do
    #echo "Debug: $line"
    eval "$line"

    #echo "line..."
    #echo "$line"

    if [ -n "$line" ]; then
	Input_dir="$OUTPUT_DIR"
	Output_dir="$OUTPUT_DIR_1KG"
	db_name="$DB_NAME"
	output_file="$OUTPUT_FILE"
	Output_admixture_dir="$OUTPUT_ADMIXTURE_DIR"
	admixture_reference_pops="$ADMIXTURE_REFERENCE_POPS"

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

output_filename=$Output_admixture_dir$output_file

log_file="Logfile1kg.txt"

# List all files ending with .bim in the input directory
bim_files=$(ls -1 $Input_dir*bim)

# Loop through each bim file and run the echo command
first_iteration=true
for filename in $bim_files; do

	#Get the filename without the folder	
	filename=$(basename "$filename")
	echo "Processing file: $filename"
	#read -n 1 input
	
	# Extract filename without extension
	echo "   Analyzing filenames"
	file="$Input_dir${filename%.*}"
	file_bim="$file.bim"
	echo -e "   Reading input files: $file_bim\n"
	#read -n 1 input
	
	#Output
	outputfile="$Output_dir${filename%.*.*}"
	outputfile_pos_chr="${outputfile}.pos_chr"
	echo -e "   Output file:\n $outputfile_pos_chr\n"
	#read -n 1 input
	
	#Load .bim file
	echo -e "   Running awk:\nAnalyzing .bim file: $file_bim\nWriting pos_chr data into: $outputfile_pos_chr\n\n"
	cp $file_bim temp.bim
	awk 'length($5) == 1 && length($6) == 1 { print $1, $4, $4, $4 }' temp.bim > $outputfile_pos_chr
	#read -n 1 input

	#Create a temp file for Input results
	Temp_original="${Output_dir}Temp_original"
	echo -e "   *** Plink saving results into\n$Temp_original\n\n"
	#read -n 1 input
	
	plink --bfile $file --extract $outputfile_pos_chr --range --make-bed --out $Temp_original
	echo -e "   Plink Extract run on Input file is Completed\n"
	#read -n 1 input
	
	#Run plink - get the matching SNPs from the 1kg file
	outputfile_kg="$Output_dir${filename%.*.*}"
	temp="temp"
	temp_kg="$Output_dir${temp}" 
	#echo -e "   Running plink on:\n $outputfile_kg\n"
	echo -e "   Running Extract Plink on 1KG:\n $temp_kg\n"
	#read -n 1 input
	plink --bfile $admixture_reference_pops --extract $outputfile_pos_chr --range --make-bed --out $temp_kg
	echo -e "   Plink Extract run on  on 1KG is Completed\n"
	#read -n 1 input

	#Update the sample's .bim file
	echo -e "   copying file\n $temp_kg.bim\n into\n $Temp_original.bim"
	cp $temp_kg.bim $Temp_original.bim
	#read -n 1 input

	#Run plink to merge the 1kg file with the input file	
	#Input file = file
	#1kg file = temp_kg
	echo -e "   Running plink to merge these 2 files:\n"
	echo -e "   $Temp_original\n$temp_kg\n\ninto\n$outputfile_kg "
	#read -n 1 input
	plink --bfile $Temp_original --bmerge $temp_kg.bed $temp_kg.bim $temp_kg.fam --make-bed --out $outputfile_kg  
	echo -e "   Plink Merge run is completed\n"
	#read -n 1 input
	
	#------------------------------------------------------
	#Write to a summary file the row numbers in each file
	#------------------------------------------------------
	# Use wc to count the number of lines
	line_count=$(wc -l < "$outputfile_kg.bim")
	echo -e "   Line count of $filename is $line_count\n"
	
	#Output the dataset + filename + its content on the same line
	Basic_file=$(basename "$filename" .bim)
	if [ "$first_iteration" = true ]; then
		echo -e -n "$db_name\t" > "$output_filename"
		first_iteration=false
	else
		#Output the filename and its content on the same line
		echo -e -n "$db_name\t" >> "$output_filename"
	fi

	# Write the filename
	echo -e -n "$Basic_file\t" >> "$output_filename"
	
	#Write the count
	echo -e -n "$line_count\n" >> "$output_filename"
	
	#read -n 1 input
	
done

#Clean up - remove temp files
echo -e "   Deleting Temp files\n"
find "$Output_dir" -type f -name "temp.*" -delete
find "$Output_dir" -type f -name "Temp_original.*" -delete
find "$Output_dir" -type f -name "*.nosex" -delete
find "$Output_dir" -type f -name "*.log" -delete
find "$Output_dir" -type f -name "*.pos_chr" -delete



