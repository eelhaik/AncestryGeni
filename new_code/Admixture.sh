#!/bin/bash
#-----------------------------------------------------------------------
# Admixture.sh
#-----------------------------------------------------------------------
#Program: This script reads all the .bim files from an input folder, to know which files are there.
# Then it runs supervised admixture and saves the results in an output file. 
#
# Input files: *.bim
# Output files: txt file
#
# Run it: ./Admixture.sh
#
#-----------------------------------------------------------------------
# Written by: Eran Elhaik
# Date: 9/9/2023
# Ver: 1.10
#-----------------------------------------------------------------------
# New in 1.10: Using parameters file for input/output folders
#	       I also adjusted the .pop file to handle 1/2 spaced lines based on num_of_lines
#-----------------------------------------------------------------------
# Read input and output file paths from the Parameters file
Parameters_file="Parameters.txt"

while IFS= read -r line; do
    #echo "Debug: $line"
    eval "$line"

    echo "line..."
    echo "$line"

    if [ -n "$line" ]; then
        Input_dir="$OUTPUT_DIR_1KG"
        Output_dir="$OUTPUT_DIR_FINAL"
        Output_admixture_dir="$OUTPUT_ADMIXTURE_DIR"
        num_of_lines=$(expr "$NUM_OF_LINES" + 0)

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

log_file="LogfileAdmixture.txt"

# List all files ending with .bim in the input directory
bim_files=$(ls -1 $Input_dir*bim)

# Loop through each bim file and run the echo command
for filename in $bim_files; do

	# Extract the basic file name without extension
	file=$(basename "$filename" .bim)
	file_bed="$Input_dir$file.bed"
	file_pop="$Input_dir$file.pop"
	admixture_dir="$ADMIXTURE_DIR"
	
	echo -e "   Input files: $file\n"
	#read -n 1 input

	#Report what is filename
	echo "   Now analyzing filename: $filename"
	#read -n 1 input
	
	#Output
	outputfile="$Output_dir$file.txt"
	echo -e "   Output file: $outputfile\n"
	#read -n 1 input
	
	#Calling Admixture
	admixture_input="$Input_dir$file_bed"
	echo -e "   Running Admixture: $file_bed\n"
	
	# Copying .pop file
	if [ $num_of_lines -eq 1 ]; then
	    Zombies_pop="${Output_admixture_dir}Zombies1.pop"
	else
	    Zombies_pop="${Output_admixture_dir}Zombies2.pop"
	fi

	cp "$Zombies_pop" "$file_pop"
	
	$admixture_dir $file_bed -F 12 -j21
	#read -n 1 input

	#Extracting the first line from the output admixture file
	echo -e "   Copying Admixture output file to:\n $outputfile\n"
	#read -n 1 input
	output_admixture_filenameQ="$Output_admixture_dir${file}.12.Q"
	output_admixture_filenameP="$Output_admixture_dir${file}.12.P"
	echo -e "   Extracting first line from: $output_admixture_filenameQ\n"
	
	#Read 2 lines, not 1
	echo -e "   Copying the first $num_of_lines lines\n"
	head -n $num_of_lines $output_admixture_filenameQ > $outputfile
	#read -n 1 input
	
	echo -e "   Moving output files\n"
	#Move admixture file to output folder
	#mv $output_admixture_filenameQ $Output_dir
	#mv $output_admixture_filenameP $Output_dir
	#rm $output_admixture_filenameQ
	#rm $output_admixture_filenameP
	echo -e "   Done moving files...\n"
#	read -n 1 input
done

echo "End of Program: Admixture.sh"