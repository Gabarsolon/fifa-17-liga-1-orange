import os
import pandas as pd
import threading
import concurrent.futures
import time
from deep_translator import GoogleTranslator

potentially_corrupted_translations = os.path.join(os.path.dirname(__file__), "..", "db", "PotentiallyCorruptedLanguageStrings.txt") 

potentially_corrupted_translations_df = pd.read_csv(potentially_corrupted_translations, sep='\t', encoding='utf-16le')

potentially_corrupted_translations_df.drop(columns=['original'], axis=1, inplace=True)

potentially_corrupted_translations_df.to_csv(potentially_corrupted_translations, sep='\t', encoding='utf-16le', index=False)

