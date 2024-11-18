#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import subprocess
from collections import defaultdict


class ColorFG:
    RED = "\x1b[31m"
    GREEN = "\x1b[32m"
    DEFAULT = "\x1b[39m"


class Format:
    BOLD = "\x1b[1m"
    ITALIC = "\x1b[3m"
    RESET = "\x1b[0m"


class GitBranch:
    def __init__(self, branch_printout):
        branch_details = branch_printout.decode("ASCII")
        # Parse details of form "<*> <name> <commit> ([<upstream_info>]) <commit_details>"
        # Active branch in current worktree starts with "* ".
        # Active branch in other worktree(s) starts with "+ ".
        self.active_branch = branch_details.startswith("*")
        self.active_on_other_worktree = branch_details.startswith("+")
        self.name, branch_details = (
            branch_details.lstrip("* ").lstrip("+ ").split(" ", maxsplit=1)
        )
        self.commit, branch_details = branch_details.lstrip().split(" ", maxsplit=1)
        try:
            self.upstream_branch = (
                subprocess.check_output(
                    ["git", "rev-parse", "--abbrev-ref", self.name + "@{u}"],
                    stderr=subprocess.STDOUT,
                )
                .decode("ASCII")
                .strip(" \n")
            )
        except subprocess.CalledProcessError:
            self.upstream_branch = None
        self.ahead = 0
        self.behind = 0
        if self.active_on_other_worktree:
            other_worktree_basedir, branch_details = branch_details.lstrip(" (").split(
                ")", maxsplit=1
            )
            self.other_worktree_basedir = os.path.basename(other_worktree_basedir)
        if self.upstream_branch is not None:
            upstream_info, branch_details = branch_details.lstrip(" [").split(
                "]", maxsplit=1
            )
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
                    self.behind = int(delta.strip("behind "))


def parse_branches():
    git_br_output = subprocess.check_output(["git", "branch", "-vv"])
    git_br_output_lines = git_br_output.splitlines()

    tree = defaultdict(list)
    branches = {}
    for line in git_br_output_lines:
        branch = GitBranch(line)
        branches[branch.name] = branch

        # Build tree contents of the form {"parent": "child"}.
        if branch.upstream_branch is None or "origin/" in branch.upstream_branch:
            tree["root"].append(branch.name)
        else:
            tree[branch.upstream_branch].append(branch.name)

    return branches, tree


def collect_depth_first_print_order(tree, node, prefix, print_outs):
    for index, child in enumerate(tree[node]):
        if not prefix:
            append_curr_line = ""
            append_children = " "
        elif index < len(tree[node]) - 1:
            append_curr_line = "├──"
            append_children = "│  "
        else:
            append_curr_line = "└──"
            append_children = "   "

        print_outs.append([prefix + append_curr_line, child])
        collect_depth_first_print_order(
            tree, child, prefix + append_children, print_outs
        )


def calculate_branch_column_width(print_outs, branches):
    branch_column_widths = []
    for prefix, branch_name in print_outs:
        branch = branches[branch_name]

        worktree_width = 0
        if branch.active_on_other_worktree:
            worktree_width = len(branch.other_worktree_basedir) + 3

        branch_width = len(prefix) + len(branch_name) + worktree_width
        branch_column_widths.append(branch_width)
    return max(branch_column_widths) + 2


def print_table(print_outs, branches):
    # Print header
    first_column_width = calculate_branch_column_width(print_outs, branches)
    header = "Branch".ljust(first_column_width) + "\tDeltas\tCommit\tDescription"
    print(Format.BOLD + header + Format.RESET)
    print("=" * (len(header) + 10))

    for tree_prefix, branch_name in print_outs:
        branch = branches[branch_name]

        # Branch name column
        first_column = tree_prefix + branch_name
        if branch.active_on_other_worktree:
            first_column += " (" + branch.other_worktree_basedir + ")"

        # Deltas column
        if branch.ahead > 0:
            ahead = ColorFG.GREEN + "+" + str(branch.ahead) + ColorFG.DEFAULT
        else:
            ahead = "+" + str(branch.ahead)
        if branch.behind > 0:
            behind = ColorFG.RED + "-" + str(branch.behind) + ColorFG.DEFAULT
        else:
            behind = "-" + str(branch.behind)
        deltas = ahead + ":" + behind

        row_text = (
            first_column.ljust(first_column_width)
            + deltas
            + "\t"
            + branch.commit
            + "\t"
            + branch.commit_description
        )

        # Print row
        if branch.active_branch:
            print(Format.BOLD + row_text + Format.RESET)
        elif branch.active_on_other_worktree:
            print(Format.ITALIC + row_text + Format.RESET)
        else:
            print(row_text)


def main():
    branches, tree = parse_branches()
    print_outs = []
    collect_depth_first_print_order(tree, "root", "", print_outs)
    print_table(print_outs, branches)


if __name__ == "__main__":
    main()
