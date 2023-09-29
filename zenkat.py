from argparse import ArgumentParser
from dataclasses import dataclass, field, asdict
import os
from datetime import datetime
from pathlib import Path
from typing import Any
import re

@dataclass
class Page:
    filename: str
    path: str
    created_at: datetime
    modified_at: datetime
    tags: set[str] = field(default_factory=set)
    # this should be unpacked when making a dataframe
    metadata: dict[str, Any] = field(default_factory=dict)
    links: set[str] = field(default_factory=set)

def get_tags(document: str):
    matches = re.findall("(?:^|\s)#([-_\w\d]+)",document)
    return set(matches)

def get_wiki_links(document : str):
    matches = re.findall("(?:^|\s)\[\[([#\/\-\w\s]+)\]\]", document)
    # might want to resolve to an absolute path
    return set(matches)
    
def get_file_data(path : str, exclude : list = []):
    pages = []
    for p in Path(path).rglob("*.md"):
        suffixes = set(p.suffixes)
        if len(suffixes.intersection(exclude)) > 0:
            continue
        
        abs = str(p.absolute())
        cur_page = Page(
            p.name,
            abs,
            datetime.fromtimestamp(os.path.getctime(abs)),
            datetime.fromtimestamp(os.path.getmtime(abs))
        )
        document = p.read_text()
        cur_page.tags = get_tags(document)
        cur_page.links = get_wiki_links(document)
        
        pages.append(cur_page)
    return pages

def get_content(page : Page):
    with open(page.path, 'r') as f:
        content = f.read()
    return content

def query(path : str, exclude : list = []):
    # recursively crawl subdirectories for .md files, output as a data structure
    pages = get_file_data(path, exclude)
    return pages

def format_list(pages : list[Page], f_str : str):
    outputs = []
    for p in pages:
        o = asdict(p)
        outputs.append(f_str.format_map(o))
    return outputs

def parse(query_str : str):
    # {LIST, TABLE, JSON, CSV} AS {txt, json, csv}
    # WHERE {condition}
    raise NotImplementedError()

def main():
    query(".")

if __name__ == "__main__":
    main()