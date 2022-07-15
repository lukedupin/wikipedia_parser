#!/usr/bin/python3

import os, sys
from html.parser import HTMLParser

class FoxParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.found_article = False
        self.depth = 0
        self.data = None

    def handle_starttag(self, tag, attrs):
        if self.found_article:
            ws = ''.join(['    ' for _ in range(self.depth)])
            #print(f"{ws}[START {tag}]")

            if tag not in ('img', 'source'):
                self.depth += 1

        else:
            for attr in attrs:
                if attr[0] == 'class' and attr[1] == 'article-body':
                    self.found_article = True
                    self.depth = 0
                    #print("**** Found start of artcle")


    def handle_endtag(self, tag):
        if self.found_article:
            if tag not in ('img', 'source'):
                self.depth -= 1
            if self.depth < 0:
                self.found_article = False

            else:
                ws = ''.join(['    ' for _ in range(self.depth)])
                #print(f"{ws}[END {tag}]")

    def handle_data(self, data):
        if self.found_article:
            self.data = data

    def get_data(self):
        return self.data

#Program begins here, if running standalone
if __name__ == '__main__':

    if len(sys.argv) == 1:
        print(" # Example usage")
        print("wget https://www.foxbusiness.com/economy/inflation-surges-june-hitting-new-40-year-high")
        print(f"Usage: {sys.argv[0]} inflation-surges-june-hitting-new-40-year-high")
        exit()

    with open(sys.argv[1]) as handle:
        content = handle.read()
        parser = FoxParser()
        parser.feed( content )





    # <div class="article-body">
