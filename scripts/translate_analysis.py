import os
import pandas as pd
import threading
import concurrent.futures
import time
from deep_translator import GoogleTranslator

language_strings = os.path.join(os.path.dirname(__file__), "..", "db", "LanguageStrings.txt")
language_strings_df = pd.read_csv(language_strings, sep='\t', encoding='utf-16le')

language_strings_og = os.path.join(os.path.dirname(__file__), "..", "db", "original_tables", "LanguageStrings.txt")
language_strings_og_df = pd.read_csv(language_strings_og, sep='\t', encoding='utf-16le', na_filter=False)

# for index, row in language_strings_og_df.iterrows():
#     if row['stringid'].startswith('TeamName_Abbr3'):
#         language_strings_df.loc[index, 'sourcetext'] = row['sourcetext']

for index, row in language_strings_og_df.iterrows():
    if row['stringid'].startswith('nationname_abbr3'):
        language_strings_df.loc[index, 'sourcetext'] = row['sourcetext']


# print(language_strings_og_df[language_strings_og_df['stringid'] == 'None'])

# for index, row in language_strings_og_df.iterrows():
#     if row['sourcetext'] == 'None':
#         language_strings_df.loc[index, 'sourcetext'] = 'Nici unul'

# for index, row in language_strings_df.iterrows():
#     print(f"{index}: {row['sourcetext']} -> {row['hashid']} -> {row['stringid']}\n")


language_strings_df.to_csv(language_strings, sep='\t', encoding='utf-16le', index=False)

