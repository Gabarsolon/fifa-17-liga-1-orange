import os
import pandas as pd
import threading
import time
from deep_translator import GoogleTranslator

language_strings = os.path.join(os.path.dirname(__file__), "..", "db", "LanguageStrings.txt")
# language_strings_translated = os.path.join(os.path.dirname(__file__), "..", "db", "LanguageStrings_Translated.txt")

language_strings_df = pd.read_csv(language_strings, sep='\t', encoding='utf-16le')
language_strings_original_df = pd.read_csv(language_strings, sep='\t', encoding='utf-16le')

translator = GoogleTranslator(source='en', target='ro')
BATCH_SIZE = 100

import concurrent.futures

translated_counter = 0
lock = threading.Lock()

language_strings_df['translated'] = False

def translate_rows(start_index, end_index):
    batch = []
    for index, row in language_strings_df.iloc[start_index:end_index].iterrows():
        if language_strings_df.iloc[index, 3] or not isinstance(row.iloc[0], str) or len(row.iloc[0]) > 5000:
            continue
        batch.append(row.iloc[0])
    translated_batch = translator.translate_batch(batch)
    for i, translation in enumerate(translated_batch):
        language_strings_df.iloc[start_index + i, 0] = translation
        language_strings_df.iloc[start_index + i, 3] = True
    with lock:
        translated_counter += len(batch)

def print_translated_dict_size():
    global translated_counter
    while True:
        translated_percent = (translated_counter / len(language_strings_df)) * 100
        print(f"Translated {translated_percent:.2f}%", end='\r')
        language_strings_df.to_csv(language_strings, sep='\t', encoding='utf-16le', index=False)
        time.sleep(5)

print_thread = threading.Thread(target=print_translated_dict_size)
print_thread.daemon = True
print_thread.start()

# def translate_rows(start_index, end_index):
#     global translated_counter
#     batch = {}
#     for index, row in language_strings_df.iloc[start_index:end_index].iterrows():
#         if language_strings_df.iloc[index, 3] or not isinstance(row.iloc[0], str) or len(row.iloc[0]) > 5000:
#             continue
#         batch[index] = row.iloc[0]
#         if len(batch) == BATCH_SIZE:
#             for index, translation in translator.translate_batch(batch.values()).items():
#                 language_strings_df.iloc[index, 0] = translation
#             batch = {}
#             translated_counter += BATCH_SIZE
#             with lock:
#                 translated_counter += 1
#         language_strings_df.iloc[index, 0] = translator.translate(row.iloc[0])
#         language_strings_df.iloc[index, 3] = True
#         with lock:
        

num_threads = 500
rows_per_thread = len(language_strings_df) // num_threads

with concurrent.futures.ThreadPoolExecutor(max_workers=num_threads) as executor:
    futures = [
        executor.submit(translate_rows, i * rows_per_thread, (i+1) * rows_per_thread)
        for i in range(num_threads)
    ]
    for future in concurrent.futures.as_completed(futures):
        future.result()
        
language_strings_df.to_csv(language_strings, sep='\t', encoding='utf-16le', index=False)
