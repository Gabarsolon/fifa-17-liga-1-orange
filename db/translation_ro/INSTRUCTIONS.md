# Task: translate FIFA 17 UI/news strings from English to Romanian

Input batch: `db/translation_ro/in/NNNN.json` = `[{"id": 1, "ctx": "<stringid>", "en": "<text>"}]`
Output: write `db/translation_ro/out/NNNN.json` = `[{"id": 1, "ro": "<translation>"}]`, same ids, same order, one entry per input entry, valid UTF-8 JSON.
Translate every entry yourself. Do NOT use a script, API or machine-translation library to produce the Romanian text. Read the entries and write the translations.

`ctx` is the string id: it tells you where the text is used (news_title_*, news_body_*, TalkToPress_*, SM_* = social media, OSDK_* = menus, FUT_*, CM_* = career mode, SUB_*_VO_* = spoken subtitles, TXT_* = UI labels). Use it to pick the right register and meaning (football, not literal).

## Hard rules (a validator checks them; a failing entry is discarded)
1. Keep these tokens EXACTLY as written, no spaces inside, same count: `<TeamName>`, `<TeamName1>`, `<PlayerName>`, `<FullPlayerName2>`, `<ManagerName>`, `<UserName>`, `<PlayerAge>`, `<PreferredPos1>`, `<CompetitionName>`, `<0>`, `<1>` (anything in `<...>`), `%1`, `%2`, ... (also `%1s`), `{C:NAME}` speaker tags, `{0.11-5.06}` timing marks, and the two-character sequence backslash + `n` (`\n`).
2. `{C:NAME}` and `{t-t}` tags stay in the same order. Translate only the words between them. Do not translate NAME.
3. If the English text starts and ends with a double quote, the translation does too. Inside such text a quote is written doubled (`""`); keep that.
4. No real line breaks and no tabs inside a translation: single line only.
5. Romanian letters: use cedilla `ş ţ Ş Ţ` and `ă â î Ă Â Î`. NEVER use the comma-below letters `ș ț`.
6. Never translate player, team, city, manager or competition names that appear literally in the text (e.g. "Pochettino", "Spurs", "White Hart Lane").
7. A token stands for a name that will be inserted. You cannot inflect it: do not add endings to it (no `<TeamName>-ul`). Rephrase so the bare name works ("echipa <TeamName>", "fanii echipei <TeamName>", "jucătorul <PlayerName>").
8. Keep roughly the same length as the English where possible (UI space is limited). Short labels (2-4 letters, buttons, positions) must stay short; if an abbreviation is standard, keep or adapt it (GK -> GR is wrong here: leave position codes like LB, RB, CM, ST as they are).
9. If the text is not translatable (a code, a URL, a number, ".com", an abbreviation with no Romanian form), return it unchanged.

## Style and glossary
- Natural Romanian football commentary/press tone, not word-for-word. Address the user as "tu"/"tău" in menus, impersonal in news.
- manager = antrenor (career mode "manager" = antrenor); club = club; squad = lot; transfer = transfer; loan = împrumut; kick-off = repriză/începerea meciului (menus: "Start meci"); match = meci; draw = egal; win = victorie; defeat/loss = înfrângere; goal = gol; assist = pasă decisivă; yellow/red card = cartonaş galben/roşu; offside = ofsaid; penalty = penalty; free kick = lovitură liberă; corner = corner; substitute = rezervă / schimbare; formation = formaţie; tactics = tactică; fixture = meci / program; league = ligă; cup = cupă; promotion = promovare; relegation = retrogradare; scout = observator; youth academy = academie; wage = salariu; budget = buget; contract = contract; board = conducerea clubului; fans = suporteri.
- FUT / Ultimate Team terms: keep "Ultimate Team", "FUT", "Coins" -> "Monede", "pack" -> "pachet", "chemistry" -> "chimie", "squad" -> "echipă".
- Do not add explanations, notes or extra entries. Output only the JSON file.

## Club names (important)
Club/team names are proper names: NEVER translate them word by word. "Young Boys" stays "Young Boys" (not "Băieţi Tineri"), "Red Bull Salzburg", "Real Madrid", "Manchester United", "Newcastle United", "Bayern Munich" (keep as written in the English text), etc. This includes names that look like ordinary words (United, City, Rovers, Wanderers, Athletic, Sporting, Boys, Stars). Same for stadiums, competitions' official names and nicknames of clubs (Spurs, Red Devils): keep them literal. Only translate the plain Romanian words around them. A validator compares against the full club-name list and discards entries where a club name from the English text is missing in the Romanian one.
