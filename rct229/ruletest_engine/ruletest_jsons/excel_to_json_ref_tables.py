import pandas as pd
import json
import math

from rct229.ruletest_engine.ruletest_jsons.json_generation_utilities import *

# Choose reference table and the table name (tab in the excel)
table_file = '1_ltg_tables_clean.xlsx'
table_tag = 'G3.7'

# Pull out TCDs from spreadsheet
master_df = pd.read_excel('90.1_ltg_tables_clean.xlsx', sheet_name=table_tag)

# Name of resulting JSON file
file_name = 'ref_table_' + table_tag + '.json'
file_name = 'test_ltg_table_G3.7.json'

# Begin putting together dictionary for JSON
json_dict_values = {}
row_array = master_df.to_dict(orient='records')

# Enter the column header to be used as the key
key_tag = 'Lighting Space Type'

for line in row_array:
    key_item = line.pop(key_tag)
    json_dict_values[key_item] = line

# Pack with the table number
json_dict = {}
table_dict = {}
table_dict['description'] = 'Performance Rating Method Lighting Power Density Allowances and Occupancy Sensor Reductions Using the Space-by-Space Method'
table_dict[key_tag] = json_dict_values
json_dict[table_tag] = table_dict

# Dump JSON to string for writing
json_string = json.dumps(json_dict,indent=4)

# Write JSON string to file
with open(file_name, 'w') as json_file:
    json_file.write(json_string)
    print("JSON complete and written to file: " + file_name)



