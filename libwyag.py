import argparse # Library to parse CLI arguments
import configparser # Library to read configuration files like Git has
from datetime import datetime # Library to do some date/time manipulation
try:
    import pwd, grp # To read user and groups database on Unix
except ModuleNotFoundError: 
    pass # Module is not available on Windows
from fnmatch import fnmatch # Library to match file names with wildcards
import hashlib # Git use SHA-1 function, which this library exposes
from math import ceil
import os # Library to do some OS stuff like file manipulation
import re # Library to use regexes
import sys # Library to access real CLI arguments
import zlib # Git uses this for compression

argparser = argparse.ArgumentParser(description="A simple Git-like version control system.")

# Subparser is a parser in a parser, used to parse specific arguments within a perser. Allows us to enforce use of commands
argsubparsers = argparser.add_subparsers(title="commands", dest="command", required=True) # Dest means that the arg is stored in a field called "command", accessible by args.command


def main(argv=sys.argv[1:]):
    args = argparser.parse_args(argv)

    # Dispatch to bridge function, which process the arguments and then calls the actual function 
    match args.command:
        case "add"          : cmd_add(args)
        case "cat-file"     : cmd_cat_file(args)
        case "check-ignore" : cmd_check_ignore(args)
        case "checkout"     : cmd_checkout(args)
        case "commit"       : cmd_commit(args)
        case "hash-object"  : cmd_hash_object(args)
        case "init"         : cmd_init(args)
        case "log"          : cmd_log(args)
        case "ls-files"     : cmd_ls_files(args)
        case "ls-tree"      : cmd_ls_tree(args)
        case "rev-parse"    : cmd_rev_parse(args)
        case "rm"           : cmd_rm(args)
        case "show-ref"     : cmd_show_ref(args)
        case "status"       : cmd_status(args)
        case "tag"          : cmd_tag(args)
        case _              : print("Bad command.")