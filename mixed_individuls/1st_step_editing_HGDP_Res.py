import pandas as pd

# Define the file path (update this with the actual file path if necessary)
file_path = 'HGDP_Res.xlsx'

# Load the Excel file
excel_data = pd.ExcelFile(file_path)

# Load the "Data" sheet
data_sheet = excel_data.parse('Data')

# Define the function to update regions based on the mapping
def update_region(row):
    # Handle specific regions first
    if row['Region'] in [' Subsaharian Africa', 'North Africa']:
        return 'Africa'
    if row['Region'] == 'Middle Est':
        return 'Europe'
    if row['Region'] == 'Oceania':
        return 'Central Asia'
    
    # Split "Asia" into "East Asia" and "Central Asia"
    if row['Region'] == 'Asia':
        east_asia_pops = [
            'Cambodians', 'Japanese', 'Han', 'Tujia', 'Yizu', 'Miaozu', 'Oroqen', 'Daur',
            'Mongola', 'Hezhen', 'Xibo', 'Dai', 'Lahu', 'She', 'Naxi', 'Tu'
        ]
        east_asia_countries = ['Cambodia', 'Japan', 'China']
        if row['Pop'] in east_asia_pops or row['Country'] in east_asia_countries:
            return 'East Asia'
        else:
            return 'Central Asia'
    
    # Return the region unchanged if no mapping applies
    return row['Region']

# Apply the mapping to the "Region" column
data_sheet['Region'] = data_sheet.apply(update_region, axis=1)

# Save the updated Data sheet back to a new Excel file
updated_file_path = 'HGDP_Res_Updated.xlsx'
with pd.ExcelWriter(updated_file_path, engine='openpyxl') as writer:
    data_sheet.to_excel(writer, index=False, sheet_name='Data')

print(f"Updated file saved at: {updated_file_path}")
