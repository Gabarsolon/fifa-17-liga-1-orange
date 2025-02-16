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
with open(language_strings, 'r+', encoding='utf-16le') as file:
    lines = file.readlines()
    file.seek(0)
    for index, line in enumerate(lines):
        columns = line.strip().split('\t')
        if len(columns) != 3:
            first_number_index = next((i for i, c in enumerate(line) if c.isdigit()), None)
            if first_number_index is not None:
                line = line[:first_number_index] + '\t' + line[first_number_index:]
            else:
                print(f"Line {index}: {line.strip()}")
            if not line.strip().endswith('\t'):
                line += '\t'
        file.write(line)
    file.truncate()



# language_strings_df.loc[language_strings_df['sourcetext'] == ' ', 'sourcetext'] = 'Niciunul'


# print(language_strings_og_df[language_strings_og_df['sourcetext'] == 'None'].index)

# def translate_og_strings(start_index, end_index):
#     for index, row in language_strings_og_df.iloc[start_index:end_index].iterrows():
#         if isinstance(row['sourcetext'], str) and row['stringid'].startswith('TeamName'):
#             language_strings_df.loc[index, 'sourcetext'] = row['sourcetext']

# with concurrent.futures.ThreadPoolExecutor(max_workers=8) as executor:
#     futures = []
#     for i in range(0, len(language_strings_og_df), len(language_strings_og_df)//8):
#         futures.append(executor.submit(translate_og_strings, i, i + len(language_strings_og_df)//8))
#     for future in concurrent.futures.as_completed(futures):
#         future.result()

# language_strings_df.to_csv(language_strings, sep='\t', encoding='utf-16le', index=False)

