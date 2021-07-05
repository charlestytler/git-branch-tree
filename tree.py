#!/usr/bin/env python

import subprocess
from collections import defaultdict

class GitBranch:
    def __init__(self, branch_printout):
        branch_details = branch_printout.decode('ASCII')
        # Parse details of form "<*> <name> <commit> ([<upstream_info>]) <commit_details>"
        self.active_branch = branch_details.startswith("*")
        self.name, branch_details = branch_details.lstrip("* ").split(" ", maxsplit=1)
        self.commit, branch_details = branch_details.lstrip().split(" ", maxsplit=1)
        try:
            self.upstream_branch = subprocess.check_output(["git","rev-parse","--abbrev-ref",self.name+"@{u}"], stderr=subprocess.STDOUT).decode('ASCII').strip(" \n")
        except subprocess.CalledProcessError:
            self.upstream_branch = None
        self.ahead = 0
        self.behind = 0
        if self.upstream_branch is not None:
            upstream_info, branch_details = branch_details.lstrip(" [").split("]", maxsplit=1)
            self._parse_upstream_info(upstream_info)
        self.commit_description = branch_details.lstrip()

    def _parse_upstream_info(self, upstream_info):
        # Parse upstream_info of form "<upstream_branch>: (ahead #), (behind #)"
        upstream_branch_with_deltas = upstream_info.split(":")
        if len(upstream_branch_with_deltas) > 1:
            deltas_from_upstream = upstream_branch_with_deltas[1].split(",")
            for delta in deltas_from_upstream:
                if delta.strip().startswith("ahead"):
                    self.ahead = int(delta.strip("ahead "))
                elif delta.strip().startswith("behind"):
                    self.ahead = int(delta.strip("behind "))


def parse_branches():
    git_br_output = subprocess.check_output(["git", "branch", "-vv"])
    git_br_output_lines = git_br_output.splitlines()
    
    tree = defaultdict(list)
    branches = {}
    for line in git_br_output_lines:
        branch = GitBranch(line)
        branches[branch.name] = branch
    
        # Build tree contents of the form {"parent": "child"}.
        if branch.upstream_branch is not None:
            if "origin/" in branch.upstream_branch:
                tree["root"].append(branch.upstream_branch)
            tree[branch.upstream_branch].append(branch.name)
        else:
            tree["root"].append(branch.name)

    return branches, tree

def print_children_recursive(branches, tree, node, curr_depth):
    for child in tree[node]:
        if "origin/" in child:
            print(child)
        else:
            """
            # │   │   ├──
            #  │   └──
            """
            branch = branches[child]
            if curr_depth > 0:
                print("   " * (curr_depth - 1), end='')
                print("└──", end='')
            print(f"{branch.name} Commit: {branch.commit} +{branch.ahead}:-{branch.behind}  {branch.commit_description}")
        print_children_recursive(branches, tree, child, curr_depth + 1)


branches, tree = parse_branches()
print_children_recursive(branches, tree, "root", 0)




