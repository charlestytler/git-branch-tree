#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import os
import subprocess
import json

from collections import defaultdict
from sys import exit

from common import get_upstream
from formats import Formats


def assume_main_is_upstream(upstream_branch):
    # Note: also returns true for the main branch itself
    return upstream_branch is None or "origin/" in upstream_branch


class GitBranch:
    def __init__(self, branch_printout, main_branch_name, github_pr_info):
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
        self.upstream_branch = get_upstream(self.name)

        if self.active_on_other_worktree:
            other_worktree_basedir, branch_details = branch_details.lstrip(" (").split(
                ")", maxsplit=1
            )
            self.other_worktree_basedir = os.path.basename(other_worktree_basedir)

        self.has_remote = False
        self.in_sync_with_remote = False
        self._parse_remote_info()

        self.ahead = 0
        self.behind = 0
        if self.name == main_branch_name:
            if self.in_sync_with_remote:
                # Omit display of ahead/behind (default is 0 deltas)
                self.ahead = None
                self.behind = None
            else:
                self._query_ahead_behind("origin/" + main_branch_name)
        elif not assume_main_is_upstream(self.upstream_branch):
            upstream_info, branch_details = branch_details.lstrip(" [").split(
                "]", maxsplit=1
            )
            self._parse_upstream_info(upstream_info)
        else:
            self._query_ahead_behind(main_branch_name)

        self.commit_description = branch_details.lstrip()

        self.has_remote = False
        self.ahead_of_remote = False
        self._parse_remote_info()
        self.pr_url = ""
        self.pr_hyperlink = ""
        self.pr_state = ""
        if self.name in github_pr_info:
            self._parse_pr_info(github_pr_info[self.name])

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

    def _query_ahead_behind(self, upstream_branch_name):
        try:
            behind_ahead = (
                # fmt: off
                subprocess.check_output(
                    [ "git", "rev-list", "--left-right", "--count", upstream_branch_name + "..." + self.name, ])
                # fmt: on
                .decode("ASCII").strip("\n")
            )
            self.behind, self.ahead = [int(x) for x in behind_ahead.split()]
        except subprocess.CalledProcessError:
            print("Unable to determine ahead/behind for branch", self.name)
            return

    def _parse_remote_info(self):
        maybe_remote_branch = (
            # fmt: off
            subprocess.check_output(
                [ "git", "branch", "-r", "-l", "origin/" + self.name, "--format", "%(refname:short)", ]
            ).decode("ASCII").strip("\n")
            # fmt: on
        )
        self.has_remote = len(maybe_remote_branch) != 0
        if not self.has_remote:
            return
        try:
            # fmt: off
            compare_local_remote = [
                "git", "diff", maybe_remote_branch, self.name, "--shortstat" ]
            # fmt: on
            res = subprocess.check_output(compare_local_remote).decode()
            if len(res) == 0:
                # No differences between upstream and current branch.
                self.in_sync_with_remote = True
                return
            self.in_sync_with_remote = False
        except Exception as inst:
            print("An error occurred with running or parsing git show", inst)

    def _parse_pr_info(self, github_branch_pr_info):
        self.pr_url = github_branch_pr_info["url"]
        self.pr_hyperlink = Formats.BLUE.add(Formats.UNDERLINE)(
            hyperlink("#" + str(github_branch_pr_info["number"]), self.pr_url)
        )
        self.pr_state = colorize_github_pr_status(
            github_branch_pr_info["state"], github_branch_pr_info["reviewDecision"]
        )


def github_pr_query():
    FIELDS = ["headRefName", "number", "url", "state", "reviewDecision"]
    try:
        gh_pr_list = subprocess.check_output(
            ["gh", "pr", "list", "--state", "all", "--json", ",".join(FIELDS)]
        )
        gh_pr_list = json.loads(gh_pr_list.decode("ASCII").strip())
    except Exception as inst:
        print("Unable to fetch github PR data", inst)
        return {}
    pr_info = {}
    for pr in gh_pr_list:
        pr_info[pr[FIELDS[0]]] = {field: pr[field] for field in FIELDS[1:]}
    return pr_info


def colorize_github_pr_status(pr_state, pr_review_decision):
    if pr_state == "OPEN":
        status = Formats.YELLOW(pr_state)
        if pr_review_decision == "APPROVED":
            status += Formats.GREEN(" ")
        elif pr_review_decision == "CHANGES_REQUESTED":
            status += Formats.RED(" ")
        else:
            status += "  "  # for column alignment
        return status
    elif pr_state == "CLOSED":
        return Formats.RED(pr_state)
    elif pr_state == "MERGED":
        return Formats.GREEN(pr_state)


def parse_branches(concise):
    main_branch_name = (
        subprocess.check_output(
            ["git", "symbolic-ref", "--short", "refs/remotes/origin/HEAD"]
        )
        .decode("ASCII")
        .strip("\n")
        .split("/")[1]
    )
    git_br_output = subprocess.check_output(["git", "branch", "-vv"])
    git_br_output_lines = git_br_output.splitlines()
    github_pr_info = github_pr_query() if not concise else {}

    tree = defaultdict(list)
    branches = {}
    for line in git_br_output_lines:
        branch = GitBranch(line, main_branch_name, github_pr_info)
        branches[branch.name] = branch

        # Build tree contents of the form {"parent": "child"}.
        if branch.name == main_branch_name:
            tree["root"].append(branch.name)
        elif assume_main_is_upstream(branch.upstream_branch):
            # Assume the branch is downstream of the main branch.
            tree[main_branch_name].append(branch.name)
        else:
            tree[branch.upstream_branch].append(branch.name)

    return branches, tree


def collect_depth_first_print_order(tree, node, prefix, print_outs):
    """Recursively walk the tree and collect the print outs."""
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


def hyperlink(text, url):
    return f"\033]8;;{url}\033\\{text}\033]8;;\033\\"


def print_table(print_outs, branches, concise=False, highlight_branch=""):
    """
    Take the branch-structure print_outs,
    Derive additional column information according to the branches[],
    Exlude some detailed information when concise is true,
    Add highlighting for the specified highlight_branch,
    Print the table
    """
    # Print header
    first_column_width = calculate_branch_column_width(print_outs, branches)
    header = "Branch".ljust(first_column_width) + "  Deltas  Commit"
    if not concise:
        header += "   Status  PR "
    print(Formats.BOLD(header))
    print("=" * (len(header) + 2))

    for tree_prefix, branch_name in print_outs:
        branch = branches[branch_name]

        # Branch name column
        column_width_count = len(tree_prefix) + len(branch_name)
        if assume_main_is_upstream(branch.upstream_branch):
            tree_prefix = Formats.YELLOW(tree_prefix.replace("─", "-"))
        first_column = tree_prefix + branch_name
        if branch.active_on_other_worktree:
            first_column += " (" + branch.other_worktree_basedir + ")"
            column_width_count += len(branch.other_worktree_basedir) + 3
        first_column += " " * (first_column_width - column_width_count)

        # Deltas column
        if branch.ahead is None or branch.behind is None:
            deltas = ""
            deltas_column_length = 0
        else:
            branch_ahead_str = str(branch.ahead)
            branch_behind_str = str(branch.behind)
            if branch.ahead > 0:
                ahead = Formats.GREEN("+" + branch_ahead_str)
            else:
                ahead = "+" + str(branch.ahead)
            if branch.behind > 0:
                behind = Formats.RED("-" + branch_behind_str)
            else:
                behind = "-" + branch_behind_str
            deltas = ahead + ":" + behind
            deltas_column_length = len(branch_ahead_str) + len(branch_behind_str) + 3

        # Remote column
        remote_text = "\uE0A0" if branch.has_remote else " "
        if branch.has_remote and not branch.in_sync_with_remote:
            remote_text = Formats.YELLOW(remote_text)

        # Note: `ljust()` does not ignore escape characters (including for setting colors).
        # Therefore, `remote_text` cannot be combined into `first_column` or it would mess up
        # the padding.
        row_text = (
            remote_text
            + " "
            + first_column
            + deltas
            # Default width of 8 (+XX:-XX ), but enforce 1 space
            + max(8 - deltas_column_length, 1) * " "
            + branch.commit
        )
        if not concise:
            row_text += (
                "  "
                + branch.pr_state
                + "  "
                + branch.pr_hyperlink
                # TODO: Description is too long to fit, maybe set up a flag to show it.
                # + branch.commit_description
            )

        # Add any appropriate styling modifiers
        modifiers = Formats.EMPTY
        if branch.active_branch:
            modifiers += Formats.BOLD
        if branch.active_on_other_worktree:
            modifiers += Formats.ITALIC
        if branch.name == highlight_branch:
            modifiers += Formats.INVERSE
        print(modifiers(row_text))


def main():
    try:
        subprocess.check_output(["git", "rev-parse", "--is-inside-work-tree"])
    except:
        exit(1)

    parser = argparse.ArgumentParser(
        description="Print git branches showing upstream branch linkages."
    )
    parser.add_argument(
        "--concise",
        action="store_true",
        help="Concise output that does not include PR information",
    )
    parser.add_argument("--highlight", help="Highlight provided branch name")
    args = parser.parse_args()

    branches, tree = parse_branches(args.concise)
    print_outs = []
    collect_depth_first_print_order(tree, "root", "", print_outs)
    print_table(print_outs, branches, args.concise, args.highlight)


if __name__ == "__main__":
    main()
