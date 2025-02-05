#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import subprocess
import json

from sys import exit


class ColorFG:
    RED = "\x1b[31m"
    GREEN = "\x1b[32m"
    YELLOW = "\x1b[33m"
    BLUE = "\x1b[34m"
    DEFAULT = "\x1b[39m"


def git_local_branch_query():
    git_branch_list = subprocess.check_output(
        ["git", "branch", "--format", "%(refname:short)"]
    )
    return git_branch_list.decode("ASCII").strip().split("\n")


def github_pr_state_query():
    FIELDS = ["headRefName", "state"]
    try:
        gh_pr_list = subprocess.check_output(
            ["gh", "pr", "list", "--state", "all", "--json", ",".join(FIELDS)]
        )
        gh_pr_list = json.loads(gh_pr_list.decode("ASCII").strip())
    except Exception as inst:
        print("Unable to fetch github PR data", inst)
        return {}
    return {pr["headRefName"]: pr["state"] for pr in gh_pr_list}


def filter_branches_by_pr_state(branches, pr_state, filter_state):
    return [
        branch
        for branch in branches
        if branch in pr_state and pr_state[branch] == filter_state
    ]


def git_delete_after_user_confirmation(branches, filter_state):
    space_separated_branches = " ".join(branches)
    newline_separated_branches = "\n  ".join(branches)
    print(f"The following branches are {ColorFG.GREEN}{filter_state}{ColorFG.DEFAULT}:")
    print(f"  {newline_separated_branches}")
    print(f"Delete all? (y/n)")
    if input() == "y":
        try:
            subprocess.check_output(["git", "branch", "-D", *branches])
        except:
            print("Unable to delete branches")
            exit(1)
        print(f"git branch -D {space_separated_branches}")


def main():
    try:
        subprocess.check_output(["git", "rev-parse", "--is-inside-work-tree"])
    except:
        exit(1)

    parser = argparse.ArgumentParser(
        description="Delete git branches according to PR status."
    )
    parser.add_argument(
        "-s",
        "--state",
        choices=["open", "closed", "merged"],
        help="PR state to delete (default: merged)",
        default="merged",
    )
    args = parser.parse_args()

    filter_state = args.state.upper()
    branches = git_local_branch_query()
    pr_state = github_pr_state_query()
    branches = filter_branches_by_pr_state(branches, pr_state, filter_state)
    if len(branches) == 0:
        print(
            f"No branches with PR status {ColorFG.GREEN}{filter_state}{ColorFG.DEFAULT} to delete"
        )
        exit(0)
    git_delete_after_user_confirmation(branches, filter_state)


if __name__ == "__main__":
    main()
