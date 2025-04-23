#FilterPFile
# -*- coding: utf-8 -*-
"""
Created on Wed Oct 25 00:08:25 2023

@author: erane
"""
'''
Loading a p file and a SNP list. Filtering the p-file according to sum of rows or STD. It doesn't work. 
'''


import pandas as pd
import os
import re

input_dir = r'D:\My Documents\University\Elhaik Lab\SubProjects\Complex phenotypes\rs9344\SNP selection\\'
input_file = 'merged.12.P'
input_filename = os.path.join(input_dir, input_file).replace('\\', '/')

input_SNP_file = 'SNP_list.txt'
input_SNP_filename = os.path.join(input_dir, input_SNP_file).replace('\\', '/')

print('Reading SNP file...')
df_SNPs = pd.read_csv(input_SNP_filename, sep='\s')

# Read the text file into a DataFrame, assuming tab-separated values (TSV)
print('Reading VEP file...')
df = pd.read_csv(input_filename, sep='\s')

#Calculate the sum of rows
#row_sums = df.sum(axis=1)
#print(row_sums)

row_std = df.std(axis=1)
print(row_std)


# Assuming 'row_sums' is your Series
top_10_percent = row_std.nsmallest(int(len(row_std) * 0.20))

# Print the top 10% highest values
print(top_10_percent)

df_SNPs = df_SNPs[row_std>max(top_10_percent)]
df_SNPs.to_csv(r'D:\\NonCodingSNPs_Clean.csv', index=False)

