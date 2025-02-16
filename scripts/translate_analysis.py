import os
import pandas as pd
import threading
import concurrent.futures
import time
from deep_translator import GoogleTranslator

language_strings = os.path.join(os.path.dirname(__file__), "..", "db", "LanguageStrings.txt")
# language_strings_df = pd.read_csv(language_strings, sep='\t', encoding='utf-16le', keep_default_na=False)

language_strings_og = os.path.join(os.path.dirname(__file__), "..", "db", "original_tables", "LanguageStrings.txt")
# language_strings_og_df = pd.read_csv(language_strings_og, sep='\t', encoding='utf-16le', keep_default_na=False)

# language_strings_df.loc[language_strings_og_df['sourcetext'] == 'None', 'sourcetext'] = 'Niciunul'
# language_strings_df.to_csv(language_strings, sep='\t', encoding='utf-16le', index=False)


with open(language_strings, 'r', encoding='utf-16le') as f, open(language_strings_og, 'r', encoding='utf-16le') as og_f:
    lines = f.readlines()
    og_lines = og_f.readlines()
    
for index, line in enumerate(lines):
    if '%' in line:
        print(line)
    
# with open(language_strings, 'w', encoding='utf-16le') as f:
#     for index, line in enumerate(lines):
#         if 'TIME' in line:
#             print(line)
            # lines[index] = og_lines[index]
    # f.writelines(lines)



# language_strings_df.loc[language_strings_df['sourcetext'] == ' ', 'sourcetext'] = 'Niciunul'





