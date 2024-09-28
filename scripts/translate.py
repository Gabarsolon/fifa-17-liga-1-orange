import os
import pandas as pd
import threading
import time
from deep_translator import GoogleTranslator

language_strings = os.path.join(os.path.dirname(__file__), "..", "db", "LanguageStrings.txt")
# language_strings_translated = os.path.join(os.path.dirname(__file__), "..", "db", "LanguageStrings_Translated.txt")

language_strings_df = pd.read_csv(language_strings, sep='\t', encoding='utf-16le')

translator = GoogleTranslator(source='en', target='ro')


import concurrent.futures

translated_dict = {}

def print_translated_dict_size():
    while True:
        translated_percent = (len(translated_dict) / len(language_strings_df)) * 100
        print(f"Translated {translated_percent:.2f}%", end='\r')
        time.sleep(5)

print_thread = threading.Thread(target=print_translated_dict_size)
print_thread.daemon = True
print_thread.start()

def translate_row(row):
    translated_dict[row[0]] = translator.translate(row[0])


with concurrent.futures.ThreadPoolExecutor(max_workers=8) as executor:
    futures = {executor.submit(translate_row, row): row for index, row in language_strings_df.iterrows()}
    for future in concurrent.futures.as_completed(futures):
        future.result()

language_strings_df.iloc[list(translated_dict.keys()), 0] = list(translated_dict.values())
language_strings_df.to_csv(language_strings, sep='\t', encoding='utf-16le', index=False)
