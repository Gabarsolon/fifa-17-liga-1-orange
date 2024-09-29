import os
import pandas as pd
import threading
import concurrent.futures
import time
from deep_translator import GoogleTranslator

language_strings = os.path.join(os.path.dirname(__file__), "..", "db", "LanguageStrings.txt")
# potentially_corrupted_translations = os.path.join(os.path.dirname(__file__), "..", "db", "PotentiallyCorruptedLanguageStrings.txt")

language_strings_df = pd.read_csv(language_strings, sep='\t', encoding='utf-16le')
# not_translated_language_strings_df = pd.read_csv(language_strings, sep='\t', encoding='utf-16le')
# not_translated_language_strings_df = not_translated_language_strings_df[not_translated_language_strings_df['translated'] == False]
# potentially_corrupted_translations_df = pd.DataFrame(columns=['original', 'translated'])


translator = GoogleTranslator(source='en', target='ro')

translated_counter = language_strings_df[language_strings_df['translated'] == True].shape[0]
lock = threading.Lock()
stop_saving_tsv_lock = threading.Lock()
potentially_corrupted_translations_lock = threading.Lock()
save_translation_lock = threading.Lock()
stop_saving_tsv = False


def translate_with_google():
    if 'translated' not in language_strings_df.columns:
        language_strings_df['translated'] = False
    language_strings_df['to_debug'] = False

    translated_counter = language_strings_df[language_strings_df['translated'] == True].shape[0]
    lock = threading.Lock()
    stop_saving_tsv_lock = threading.Lock()
    stop_saving_tsv = False

    def print_translated_dict_size():
        global potentially_corrupted_translations_lock
        global translated_counter
        global save_translation_lock
        
        while True:
            translated_percent = (translated_counter / len(language_strings_df)) * 100
            with stop_saving_tsv_lock:
                if stop_saving_tsv:
                    print("Execution finished")
                    return
            with save_translation_lock:
                language_strings_df.to_csv(language_strings, sep='\t', encoding='utf-16le', index=False)
            # with potentially_corrupted_translations_lock:
            #     potentially_corrupted_translations_df.to_csv(potentially_corrupted_translations, sep='\t', encoding='utf-16le', index=False)
            print(f"Translated {translated_percent:.2f}%", end='\r')
        
            time.sleep(5)

    print_thread = threading.Thread(target=print_translated_dict_size)
    print_thread.daemon = True
    print_thread.start()
    

    def translate_rows(start_index, end_index):
        global stop_saving_tsv
        global save_translation_lock
        try:
            global translated_counter
            for index, row in language_strings_df.iloc[start_index:end_index].iterrows():
                if language_strings_df.iloc[index, 3] or not isinstance(row.iloc[0], str) or len(row.iloc[0]) > 5000 or language_strings_df.iloc[index, 2] == 'txt_quotation':
                    continue
                translated_string = translator.translate(row.iloc[0])
                if translated_string is None or len(translated_string) == 0:
                    continue
                # with potentially_corrupted_translations_lock:
                #     potentially_corrupted_translations_df.loc[len(potentially_corrupted_translations_df)] = {'original': row.iloc[0], 'translated': translated_string}
                with save_translation_lock:
                    language_strings_df.iloc[index, 0] = translated_string
                    language_strings_df.iloc[index, 3] = True
                    language_strings_df.iloc[index, 4] = True
                with lock:
                    translated_counter += 1
        except Exception as e:
            print(e)
            
    num_threads = 8
    rows_per_thread = len(language_strings_df) // num_threads

    with concurrent.futures.ThreadPoolExecutor(max_workers=num_threads) as executor:
        futures = [
            executor.submit(translate_rows, i * rows_per_thread, (i+1) * rows_per_thread)
            for i in range(num_threads)
        ]
        print_thread.start()
        for future in concurrent.futures.as_completed(futures):
            future.result()
            


    with stop_saving_tsv_lock:
        stop_saving_tsv = True
    print_thread.join()
    

    
def drop_translation_status_column():
    language_strings_df.drop(columns=['translated'], inplace=True)
    language_strings_df.drop(columns=['to_debug'], inplace=True)
    language_strings_df.to_csv(language_strings, sep='\t', encoding='utf-16le', index=False)

def translate_rows():
    try:
        for index, row in language_strings_df.iterrows():
            print(row.iloc[0])
            if language_strings_df.iloc[index, 3] or not isinstance(row.iloc[0], str) or len(row.iloc[0]) > 5000:
                continue
            print(row.iloc[0])
            language_strings_df.iloc[index, 0] = translator.translate(row.iloc[0])
            language_strings_df.iloc[index, 3] = True
            print(language_strings_df.iloc[index, 0])
    except Exception as e:
        print(e)
    language_strings_df.to_csv(language_strings, sep='\t', encoding='utf-16le', index=False)
    
    
def print_menu():
    print("\n")
    print("FIFA 17 LIGA 1 ORANGE TRANSLATOR")
    print("----------------------------")
    print("1. Translate LanguageStrings.txt multi-threaded")
    print("2. Translate LanguageStrings.txt single-threaded")
    print("3. Drop translation status column")
    print("----------------------------")
    print("Enter your choice: ")


    choice = input()
    if choice == "1":
        translate_with_google()
    elif choice == "2":
        translate_rows()
    elif choice == "3":
        drop_translation_status_column()
    else:
        print("Invalid choice. Please try again.")
        print_menu()

print_menu()