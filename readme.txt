google_news.py
    - This file is used as a web crawler to scrap google news website.
    - This file will scrap all 'economy' related (global) news.
    - It then inserts all the record in postgresql database.
    - If run multiple times, it will keep adding new records as I did not want to truncate table each time it runs.
    - Although duplicate records will increases DB size, it will not have any negative affect on the analysis (we remove any duplicates before analysis).

news_analysis.py
    - This file can be run multiple times.
    - It will read whatever is in the database and analyse data based on that.
    - Each time this is run, the result will always be the same as we are not changing DB records.