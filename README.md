# tamu-bldg-notify
Sends a Teams message if TAMU building information changes

# Edge cases considered
1) Building(s) are added and/or removed at the same time
2) Any buildings added or removed are ignored from the abbreviation check
3) Mutliple buildings changed abbreviations

# Feature to-do
1) Weekly/daily digest
2) Notify chat if API server is unreachable
3) Rotating list of engineers

# NOTE
You must add your own webhook_url.txt file to the ./data/ directory with your Teams webhook URL inside for this to work.
