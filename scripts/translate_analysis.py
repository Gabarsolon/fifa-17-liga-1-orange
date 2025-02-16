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

language_strings_df.loc[language_strings_og_df['sourcetext'] == 'None', 'sourcetext'] = 'Niciunul'

# with open(language_strings, 'r', encoding='utf-16le') as f:
#     for line in f:
#         if line.count('\t') != 2:
#             print(line)



# language_strings_df.loc[language_strings_df['sourcetext'] == ' ', 'sourcetext'] = 'Niciunul'




language_strings_df.to_csv(language_strings, sep='\t', encoding='utf-16le', index=False)

