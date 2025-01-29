#!/bin/bash
#-----------------------------------------------------------------------
# Summarize_results_one_row.sh
#-----------------------------------------------------------------------
# Program: This script reads all the .txt files from the final folder and creates a single file with the ID and the gene pools
# It uses its filename to metadata the GPs.
# It handles files with a single admixture results. Summarize_results_two_rows.sh handles 2 rows.
#
# DO NOT USE FOR Somatic_Verdict.txt
#
# Input files: *.txt
# Output files: 1 txt file
#
# Run it: ./Summarize_results.sh
#-----------------------------------------------------------------------
# Written by: Eran Elhaik
# Date: 9/9/2023
# Ver: 1.10
#-----------------------------------------------------------------------
# New in 1.10: Using parameters file for input/output folders
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

	#Output the dataset + filename + its content on the same line
	if [ "$first_iteration" = true ]; then
		echo "   First iteration\n"
		echo -e -n "$db_name\t" > "$output_filename"
		first_iteration=false
	else
		echo "   Not First iteration\n"
		#Output the filename and its content on the same line
		echo -e -n "$db_name\t" >> "$output_filename"
	fi

	# Write the filename
	echo "   Writing the filename\n"
	echo -e -n "$file\t" >> "$output_filename"
	
	# Replace spaces with tabs in the content and append to the output file
	cat "$filename" | tr ' ' '\t' >> "$output_filename"
	
	#read -n 1 input
done

echo "End of Program: Summarize_results_one_row.sh"