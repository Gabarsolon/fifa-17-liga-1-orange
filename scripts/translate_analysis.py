import os
import pandas as pd
import threading
import concurrent.futures
import time
from deep_translator import GoogleTranslator

language_strings = os.path.join(os.path.dirname(__file__), "..", "db", "LanguageStrings.txt")
language_strings_df = pd.read_csv(language_strings, sep='\t', encoding='utf-16le')

print(language_strings_df[language_strings_df.to_debug == True])


# language_strings_df.loc[20375, ['sourcetext', 'stringid']] = ['Nici unul', 'None']

# language_strings_df.to_csv(language_strings, sep='\t', encoding='utf-16le', index=False)
