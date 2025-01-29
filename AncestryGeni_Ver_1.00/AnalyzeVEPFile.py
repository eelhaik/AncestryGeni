#AnalyzeVEPFile
# -*- coding: utf-8 -*-
"""
Description: This script reads a txt file created by VEP. I then keep only non-coding markers, which are idnetified by keywords contained into the descriptions. It output a SNP list that satisfy these criteria.
 
Input: VEP output .txt document
Output: SNP list

----------------------------------------------------
Created by: Eran Elhaik
Date: 22/10/23
Ver: 1.00
----------------------------------------------------
"""
import pandas as pd
import os
import re

input_dir = r'D:\My Documents\University\Elhaik Lab\SubProjects\Complex phenotypes\rs9344\SNP selection\\'
input_file = 'ihlWWAMTPGBRyHtk.txt'
input_filename = os.path.join(input_dir, input_file).replace('\\', '/')

# Read the text file into a DataFrame, assuming tab-separated values (TSV)
print('Reading VEP file...')
df = pd.read_csv(input_filename, sep='\t')

# Display the DataFrame
print(df)

# Print unique Consequences
print('Unique Consequence')
unique_consequences = set(df['Consequence'])
unique_SNPs = set(df['#Uploaded_variation'])
print('Number of unique SNPs:', len(unique_SNPs))
for consequence in unique_consequences:
    print(consequence)

# Define the keywords you want to search for
keywords = ["missense", "terminal_codon", "coding_sequence_variant", "start", "stop", "synonymous"]

# Create a regular expression pattern to match any of the keywords
pattern = re.compile(r'(?:' + '|'.join(keywords) + r')', re.IGNORECASE)

# Find strings that include the keywords
matching_strings = [s for s in unique_consequences if pattern.search(s)]

# Print the matching strings
print('Found #', len(matching_strings), 'Matching Consequence out of #', len(unique_consequences) )
for string in matching_strings:
    print(string)

# Find non-overlapping strings (strings that are in unique_consequences but not in matching_strings)
non_overlapping_strings = set(unique_consequences) - set(matching_strings)
print('Found #', len(non_overlapping_strings), 'non coding types #', len(unique_consequences) )

# Convert the non-overlapping strings set to a list
matching_strings_list = list(matching_strings)

filtered_df = df[df['Consequence'].isin(matching_strings_list)]

#Find which SNPs have coding properties
coding_SNPs = set(filtered_df['#Uploaded_variation'])
print('Number of coding SNPs:', len(coding_SNPs))

#Non coding SNPs
non_coding_SNPs = set(unique_SNPs) - set(coding_SNPs)
print('Number of non coding SNPs:', len(non_coding_SNPs))

#Save to file
df_SNPs = pd.DataFrame(non_coding_SNPs, columns=['#Uploaded_variation'])
df_SNPs.to_csv(r'D:\\NonCodingSNPs.csv', index=False)



