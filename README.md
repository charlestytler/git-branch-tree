# git-branch-tree

![Example printout with color formatting](https://github.com/user-attachments/assets/a1229f62-4e24-4b5f-820b-81554113f7cc)

Executing git-tree.py from within a git repository will query all git branches and print them to the terminal in a hierarchical tree format, according to their upstream branch mapping, and displays Github PR status for each.

This is particularly useful if you work with a lot of chained PRs. If a branch does not have a local branch listed as its upstream it will assume the main branch is upstream of it and show this relation with a dashed yellow line.
Use `git branch -u <parent_branch>` to link a branch to its parent.

## Dependencies
This script relies on the github CLI tool (gh) to be installed and configured for authentication.
See https://cli.github.com/

## Installation
Install the git-tree.py and (optionally) git-delete.py scripts (requires Python3 installed) and set it as a git alias to `git tree`:
```
curl -sL -o ~/.git-tree.py https://raw.githubusercontent.com/charlestytler/git-branch-tree/refs/heads/master/git-tree.py && chmod +x ~/.git-tree.py && git config --global alias.tree '!~/.git-tree.py'
```
(Optional) Create alias `git del` to run `git-delete.py`:
```
curl -sL -o ~/.git-delete.py https://raw.githubusercontent.com/charlestytler/git-branch-tree/refs/heads/master/git-delete.py && chmod +x ~/.git-delete.py && git config --global alias.del '!~/.git-delete.py'
```
or with git clone:
```
git clone https://github.com/charlestytler/git-branch-tree.git /tmp/git-branch-tree &&\
cp /tmp/git-branch-tree/git-tree.py ~/.git-tree.py &&\
git config --global alias.tree '!~/.git-tree.py'
git config --global alias.del '!~/.git-delete.py'
```

## Usage
When in a git repository run the command `git tree`  
This will show a tree of all branches installed.  
Note that when creating branches you should be assigning their upstream branch, i.e. `git branch --set-upstream <parent_branch>` or `git branch -u <parent_branch>`.

## Example

### Default git branch terminal output
```
❯ git br -vv
  assume_master_upstream           0174303 [origin/assume_master_upstream] Assume main branch to be upstream of branch if no upstream linked
  assumed_upstream_special_display 62c4f60 [master: ahead 3] Yellow dashed lines for branches assumed to be linked to main branch added
  gh_integration                   821da4b [master: ahead 5] Apply reviewer suggestions
  highlight_flag                   db1b463 [master: ahead 1, behind 1] Highlight branch specified by --highlight flag
* hyperlinks                       392fa2c [gh_integration: ahead 4, behind 1] Extend header underline to allow for 3 digit PR numbers to fall under, ok if PRs are bigger
  master                           8188a13 [origin/master] Hide deltas for branches assumed to have main as their upstream (#16)
```
  
### Script branch output
Executing `git-tree.py` will show the image at the top of the page.

### Git branch deletion based on PR status
Executing `git-delete.py` will delete all local branches with the PR status "MERGED" (with confirmation from user first).

Deletion based on different statuses can be performed using the `-s/--status` flag

