import os
import pandas as pd
import threading
import concurrent.futures
import time
from deep_translator import GoogleTranslator

language_strings = os.path.join(os.path.dirname(__file__), "..", "db", "LanguageStrings.txt")
language_strings_df = pd.read_csv(language_strings, sep='\t', encoding='utf-16le', keep_default_na=False)

language_strings_og = os.path.join(os.path.dirname(__file__), "..", "db", "original_tables", "LanguageStrings.txt")
language_strings_og_df = pd.read_csv(language_strings_og, sep='\t', encoding='utf-16le', keep_default_na=False)

with open(language_strings, 'r+', encoding='utf-16le') as f, open(language_strings_og, 'r', encoding='utf-16le') as og_f:
    lines = f.readlines()
    og_lines = og_f.readlines()
    for i, og_line in enumerate(og_lines):
        og_fields = og_line.split('\t')
        line_fields = lines[i].split('\t')
        if og_fields[-1] != line_fields[-1]:
            print(i, og_fields[-1], line_fields[-1])
            lines.insert(i, og_line)
    f.seek(0)
    f.writelines(lines)
    f.truncate()



# for index, row in language_strings_og_df.iterrows():
#     if(language_strings_df.loc[index, 'stringid'] != row['stringid']):
#         print(language_strings_df.loc[index, 'stringid'], row['stringid'])

# language_strings_df.loc[language_strings_og_df['sourcetext'] == 'None', 'sourcetext'] = 'Niciunul'
# language_strings_df.to_csv(language_strings, sep='\t', encoding='utf-16le', index=False)

# for index, row in language_strings_df.iterrows():
#     if len(row['sourcetext'].strip()) == 0:
#         language_strings_df.loc[index, 'sourcetext'] = language_strings_og_df.loc[index, 'sourcetext']

# language_strings_df.to_csv(language_strings, sep='\t', encoding='utf-16le', index=False)

# for index, row in language_strings_og_df.iterrows():
#     if row['sourcetext'] == 'None':
#         language_strings_df.loc[index, 'sourcetext'] = 'Niciunul'
        
# language_strings_df.to_csv(language_strings, sep='\t', encoding='utf-16le', index=False)

# for index, row in language_strings_df.iterrows():
#     if 'TeamName' in row['stringid']:
#         language_strings_df.loc[index, 'sourcetext'] = language_strings_og_df.loc[index, 'sourcetext']
        
# language_strings_df.to_csv(language_strings, sep='\t', encoding='utf-16le', index=False)

# with open(language_strings, 'r', encoding='utf-16le') as f, open(language_strings_og, 'r', encoding='utf-16le') as og_f:
#     lines = f.readlines()
#     og_lines = og_f.readlines()
    
# with open('language_strings_playername.txt', 'w', encoding='utf-16le') as f:
#     for index, line in enumerate(lines):
#         if 'player' in line.lower() and 'player' not in og_lines[index].lower():
#             f.write(lines[index])

# total_lines = 0    
    
# with open(language_strings, 'w', encoding='utf-16le') as f:
#     for index, line in enumerate(lines):
#         if 'player' in line.lower() and 'player' not in og_lines[index].lower():
#             lines[index] = og_lines[index]
#             total_lines += 1
#     f.writelines(lines)
# print("Total number of lines:", total_lines)




# language_strings_df.loc[language_strings_df['sourcetext'] == ' ', 'sourcetext'] = 'Niciunul'





