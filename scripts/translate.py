import os
import pandas as pd
import threading
import concurrent.futures
import time
from deep_translator import GoogleTranslator

language_strings = os.path.join(os.path.dirname(__file__), "..", "db", "LanguageStrings.txt")

language_strings_df = pd.read_csv(language_strings, sep='\t', encoding='utf-16le')
not_translated_language_strings_df = pd.read_csv(language_strings, sep='\t', encoding='utf-16le')
not_translated_language_strings_df = not_translated_language_strings_df[not_translated_language_strings_df['translated'] == False]

translator = GoogleTranslator(source='en', target='ro')

def translate_rows():
    try:
        for index, row in not_translated_language_strings_df.iterrows():
            print(row.iloc[0])
            if language_strings_df.iloc[index, 3] or not isinstance(row.iloc[0], str) or len(row.iloc[0]) > 5000:
                continue
            print(row.iloc[0])
            language_strings_df.iloc[index, 0] = translator.translate(row.iloc[0])
            language_strings_df.iloc[index, 3] = True
            print(language_strings_df.iloc[index, 0])
    except Exception as e:
        print(e)

translate_rows()
language_strings_df.to_csv(language_strings, sep='\t', encoding='utf-16le', index=False)


def translate_with_google():


    
    if 'translated' not in language_strings_df.columns:
        language_strings_df['translated'] = False

    translated_counter = language_strings_df[language_strings_df['translated'] == True].shape[0]
    lock = threading.Lock()
    stop_saving_tsv_lock = threading.Lock()
    stop_saving_tsv = False

    def print_translated_dict_size():
        global translated_counter
        while True:
            translated_percent = (translated_counter / len(language_strings_df)) * 100
            with stop_saving_tsv_lock:
                if stop_saving_tsv:
                    print("Execution finished")
                    return
            language_strings_df.to_csv(language_strings, sep='\t', encoding='utf-16le', index=False)
            print(f"Translated {translated_percent:.2f}%", end='\r')
        
            time.sleep(5)

    print_thread = threading.Thread(target=print_translated_dict_size)
    print_thread.daemon = True
    print_thread.start()

    def translate_rows(start_index, end_index):
        global stop_saving_tsv
        try:
            global translated_counter
            for index, row in not_translated_language_strings_df.iloc[start_index:end_index].iterrows():
                if language_strings_df.iloc[index, 3] or not isinstance(row.iloc[0], str) or len(row.iloc[0]) > 5000:
                    continue
                language_strings_df.iloc[index, 0] = translator.translate(row.iloc[0])
                language_strings_df.iloc[index, 3] = True
                with lock:
                    translated_counter += 1
        except Exception as e:
            print(e)
            
    num_threads = 8
    rows_per_thread = len(not_translated_language_strings_df) // num_threads

    with concurrent.futures.ThreadPoolExecutor(max_workers=num_threads) as executor:
        futures = [
            executor.submit(translate_rows, i * rows_per_thread, (i+1) * rows_per_thread)
            for i in range(num_threads)
        ]
        for future in concurrent.futures.as_completed(futures):
            future.result()
            


    with stop_saving_tsv_lock:
        stop_saving_tsv = True
    print_thread.join()