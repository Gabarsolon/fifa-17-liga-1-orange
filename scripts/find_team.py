import os
from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'))

import pandas as pd
from dataframes import *

# Search in LanguageStrings
for row in fifa16_languagestrings_df.itertuples():
    if isinstance(row.sourcetext, str) and 'Timis' in row.sourcetext:
        print(f"Found in strings: {row.stringid} - {row.sourcetext}")
