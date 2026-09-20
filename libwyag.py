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

class GitRepository(object):
    worktree = None # Worktree is the directory where files which live in the VCS are stored
    gitdir = None # Directory for metadata for git
    conf = None # config file of git repo, access some properties about it

    def __init__(self, path, force=False):
        self.worktree = path
        self.gitdir = os.path.join(path, ".git")

        # Check if the given path is a Git repository
        if not (force or os.path.isdir(self.gitdir)):
            raise Exception(f"Not a Git repository {path}") 

        # Read configuration file in .git/config
        self.conf = configparser.ConfigParser()
        cf = repo_file(self, "config")

        # Check if config file exists
        if cf and os.path.exists(cf):
            self.conf.read([cf])
        elif not force:
            raise Exception("Configuration file missing")

        # Check if the repo format is 0
        if not force:
            vers = int(self.conf.get("core", "repositoryformatversion"))
            if vers != 0:
                raise Exception(f"Unsupported repositoryformatversion: {vers}")

# Asterisk makes the function variadic, which means multiple args can be passed as path. Function receives a list
def repo_path(repo, *path):
    """Compute path under repo's gitdir."""
    return os.path.join(repo.gitdir, *path)

def repo_file(repo, *path, mkdir=False):
    """Same as repo_path, but create dirname(*path) if absent.  For
    example, repo_file(r, \"refs\", \"remotes\", \"origin\", \"HEAD\") will create
    .git/refs/remotes/origin."""

    if repo_dir(repo, *path[:-1], mkdir=mkdir):
        return repo_path(repo, *path)
    
def repo_dir(repo, *path, mkdir=False):
    """Same as repo_path, but mkdir *path if absent if mkdir."""

    path = repo_path(repo, *path)

    if os.path.exists(path):
        if (os.path.isdir(path)):
            return path
        else:
            raise Exception(f"Not a directory {path}")

    if mkdir:
        os.makedirs(path)
        return path
    else:
        return None


def repo_default_config():
    """Return the default configuration for a newly created repository."""

    ret = configparser.ConfigParser()
    ret.add_section("core")
    ret.set("core", "repositoryformatversion", "0")
    ret.set("core", "filemode", "false")
    ret.set("core", "bare", "false")
    return ret


def repo_create(path):

    repo = GitRepository(path, True)
    # First, we make sure the path either doesn't exist or is an
    # empty dir.

    if os.path.exists(repo.worktree):
        if not os.path.isdir(repo.worktree):
            raise Exception (f"{path} is not a directory!")
        if os.path.exists(repo.gitdir) and os.listdir(repo.gitdir):
            raise Exception (f"{path} is not empty!")
    else:
        os.makedirs(repo.worktree)

    print(repo.worktree, repo.gitdir)

    assert repo_dir(repo, "branches", mkdir=True)
    assert repo_dir(repo, "objects", mkdir=True)
    assert repo_dir(repo, "refs", "tags", mkdir=True)
    assert repo_dir(repo, "refs", "heads", mkdir=True)

    # .git/description
    with open(repo_file(repo, "description"), "w") as f:
        f.write("Unnamed repository; edit this file 'description' to name the repository.\n")

    # .git/HEAD
    with open(repo_file(repo, "HEAD"), "w") as f:
        f.write("ref: refs/heads/master\n")

    # .git/config
    with open(repo_file(repo, "config"), "w") as f:
        config = repo_default_config()
        config.write(f)

    return repo


            
# MAIN - ARG PARSING AND DISPATCHING
argparser = argparse.ArgumentParser(description="A simple Git-like version control system.")

# Subparser is a parser in a parser, used to parse specific arguments within a perser. Allows us to enforce use of commands
argsubparsers = argparser.add_subparsers(title="commands", dest="command", required=True) # Dest means that the arg is stored in a field called "command", accessible by args.command

# Subparser for init, we add an optional argument for path to initialize repo in
argsp = argsubparsers.add_parser("init", help="Initialize a new, empty repository.")
argsp.add_argument("path",
                   metavar="directory",
                   nargs="?",
                   default=".",
                   help="Where to create the repository.")

# BRIDGE FUNCTIONS
def cmd_init(args):
    repo_create(args.path)

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