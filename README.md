# wikipedia_parser
Download Wikipedia, run this to break out the articles

https://meta.wikimedia.org/wiki/Data_dump_torrents#English_Wikipedia

# Run the program

qmake && make && ./Wikipedia article.xml

# Parse foxnews

Find the article you want. Download with wget. Run the fox_parse on the article

```
wget https://www.foxbusiness.com/economy/inflation-surges-june-hitting-new-40-year-high
./fox_parser.py inflation-surges-june-hitting-new-40-year-high
```

#Parse list of fox URL's in CSV file

```
python parse_urls.py path/to/urls.csv --type fox --dump /path/to/data/dump/file.txt
```
