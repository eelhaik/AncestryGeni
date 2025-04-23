#!/bin/bash
#-----------------------------------------------------------------------
# Summarize_results_two_rows.sh
#-----------------------------------------------------------------------
# Program: This script reads all the .txt files from the final folder and creates a single file with the ID and the gene pools
# It uses its filename to metadata the GPs
# This script handles files with 2 samples, unlike Summarize_results_one_row.sh which handles files with 1 sample.
# USE ONLY FOR Somatic_Verdict.txt
#
# Input files: *.txt
# Output files: 1 txt file
#
# Run it: ./Summarize_results_two_rows.sh
#-----------------------------------------------------------------------
# Written by: Eran Elhaik
# Date: 9/9/2023
# Ver: 1.30
#-----------------------------------------------------------------------
# Based on Summarize_results_one_row.sh, but handles files with 2 admixture results
#-----------------------------------------------------------------------
# Ver 1.20: Improving documentaiton
#-----------------------------------------------------------------------
# New in 1.30: Using parameters file for input/output folders
#-----------------------------------------------------------------------
# Read input and output file paths from the Parameters file
Parameters_file="Parameters.txt"

while IFS= read -r line; do
    #echo "Debug: $line"
    eval "$line"

    #echo "line..."
    #echo "$line"

    if [ -n "$line" ]; then
        Input_dir="$OUTPUT_DIR_FINAL"
        db_name="$DB_NAME"
        output_file="$OUTPUT_FILE_TABLE"
        Output_admixture_dir="$OUTPUT_ADMIXTURE_DIR"

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

# List all files ending with .txt in the input directory
res_files=$(ls -1 $Input_dir*txt)

# Loop through each bim file and run the echo command
first_iteration=true
for filename in $res_files; do

	# Extract the basic file name without extension
	file=$(basename "$filename" .txt)
	echo -e "\n   Input file: $file\n"
	#read -n 1 input

	#Report what is filename
	echo "   Now analyzing filename: $filename\n"
	#read -n 1 input

	# Read the file line by line from "$filename"
	echo "Enter while loop\n"
	while read -r line; do

		echo "   Printing the dataset name"
		if [ "$first_iteration" = true ]; then
			# Print the database name and filename
			echo -e -n "$db_name\t" > "$output_filename"
			first_iteration=false
		else
			# Print the database name and filename
			echo -e -n "$db_name\t" >> "$output_filename"
		fi

		#echo "This is the file name"
		echo -e -n "$file\t" >> "$output_filename"

		# Replace spaces with tabs in the content and append to the output file
		#This is the admxiture file
		echo -e "$line" | tr ' ' '\t' >> "$output_filename"
		
	done < "$filename"

	#read -n 1 input
done

echo "End of Program: Summarize_results_two_row.sh"