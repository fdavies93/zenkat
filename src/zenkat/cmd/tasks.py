from zenkat import index
import zenkat.filter
import zenkat.objects
from zenkat.utils import node_tree_dft
from rich.console import Console

def tasks(args, console: Console, config: dict):
    idx = index.index(args.path, config)
    # the first filter applies to the tasks
    # the second filter applies to the page
    # all others are ignored
    filter_strs = []
    if args.filter != None:
        filter_strs = args.filter

    pages = idx.pages

    li_filter = None
    if len(filter_strs) > 0:
        li_filter = zenkat.filter.parse_filter(filter_strs[0], zenkat.objects.ListItem)
    if args.page != None:
        page_filter = zenkat.filter.parse_filter(args.page, zenkat.objects.Page)
        pages = list(filter(page_filter, pages))

    status_symbols = config["theme"]["tasks"]["symbols"]
    status_tags = config["theme"]["tasks"]["tags"]
    spacer = config["theme"]["tasks"]["spacer"]
    spacer_tag = config["theme"]["tasks"]["spacer_tag"]
    spacer_end = config["theme"]["tasks"]["spacer_end"]
    page_title_tag = config["theme"]["tasks"]["page_title_tag"]
    page_link_tag = config["theme"]["tasks"]["page_link_tag"]

    li_limit = 0
    if args.limit != None:
        li_limit = int(args.limit)
    
    li_no = 0
    li_strs = []

    def do_fn(li: zenkat.objects.ListItem):
        if li.depth < 0: return True
        if li.type != "task": return False
        if li_filter is not None and not li_filter(li):
            return False
        nonlocal li_no, li_strs
        if li_limit > 0 and li_no > li_limit: return False
        t1, t2 = "", ""
        if li.status in status_tags:
            t1, t2 = status_tags[li.status]
        sym = status_symbols.get(li.status)
        spacer_str = spacer_tag[0] + (spacer * li.depth) + spacer_end + spacer_tag[1]
        li_str = f"{spacer_str}[status]{sym}[/status] {t1}{li.text}{t2}"
        li_strs.append(li_str)
        li_no += 1

        for link in li.links:
            for key, value in link.linked_metadata.items():
                print(key, value)
        return True
        
    for p in pages:
        li_strs = []
        node_tree_dft(p.lists_tree, "children", do_fn)
        if len(li_strs) == 0: continue
        console.print(f"{page_title_tag[0]}{p.title}{page_title_tag[1]} ({page_link_tag[0]}{p.rel_path}{page_link_tag[1]})")
        for li_str in li_strs:
            console.print(li_str)