import os
import pandas as pd
import threading
import concurrent.futures
import time
from deep_translator import GoogleTranslator

language_strings = os.path.join(os.path.dirname(__file__), "..", "db", "LanguageStrings.txt")
language_strings_df = pd.read_csv(language_strings, sep='\t', encoding='utf-16le')
language_strings_df.drop(columns=['to_debug'], inplace=True)


# for index, row in language_strings_df.iterrows():
#     print(f"{index}: {row['sourcetext']} -> {row['hashid']} -> {row['stringid']}\n")


language_strings_df.to_csv(language_strings, sep='\t', encoding='utf-16le', index=False)

