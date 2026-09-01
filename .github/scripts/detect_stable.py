#!/usr/bin/env python3
"""Detect new upstream stable kernels not yet tracked in sync.yml.

Compares kernel.org/releases.json against sync.yml. If the latest
stable is not being synced, adds it to sync.yml.
"""

import argparse
import json
import re
import sys
import urllib.request

RELEASES_URL = "https://www.kernel.org/releases.json"
STABLE_REMOTE = "https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git"


def fetch_releases(source):
    if source.startswith("http"):
        with urllib.request.urlopen(source) as resp:
            return json.loads(resp.read())
    with open(source) as f:
        return json.load(f)


def parse_sync_yml_stable_branches(sync_yml_path):
    """Extract stable_X.Y.y branch names from sync.yml matrix entries."""
    branches = set()
    with open(sync_yml_path) as f:
        for line in f:
            m = re.search(r"branch:\s*(stable_\d+\.\d+\.y)", line)
            if m:
                branches.add(m.group(1))
    return branches


def version_to_stable_branch(version):
    """Convert a version like '7.2.2' to 'stable_7.2.y'."""
    parts = version.split(".")
    return f"stable_{parts[0]}.{parts[1]}.y"


def stable_branch_to_remote_branch(branch):
    """Convert 'stable_7.2.y' to 'linux-7.2.y'."""
    return branch.replace("stable_", "linux-")


def add_stable_to_sync_yml(sync_yml_path, branch):
    """Add a new stable matrix entry to sync.yml after the last existing stable entry."""
    remote_branch = stable_branch_to_remote_branch(branch)
    new_entry = (
        f"           - branch: {branch}\n"
        f"             remote: {STABLE_REMOTE}\n"
        f"             remote_branch: {remote_branch}\n"
    )

    with open(sync_yml_path) as f:
        lines = f.readlines()

    last_stable_idx = None
    for i, line in enumerate(lines):
        if re.search(r"branch:\s*stable_\d+\.\d+\.y", line):
            last_stable_idx = i

    if last_stable_idx is None:
        print("ERROR: no existing stable entries found in sync.yml")
        return False

    # Find the end of the last stable entry (next entry starts with '           -' or is non-matrix content)
    insert_idx = last_stable_idx + 1
    while insert_idx < len(lines):
        line = lines[insert_idx]
        if re.match(r"\s+- branch:", line) or not line.startswith(" "):
            break
        insert_idx += 1

    lines.insert(insert_idx, new_entry)

    with open(sync_yml_path, "w") as f:
        f.writelines(lines)

    return True


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--releases-json",
        default=RELEASES_URL,
        help="URL or path to releases.json (default: kernel.org)",
    )
    parser.add_argument(
        "--sync-yml",
        required=True,
        help="Path to sync.yml",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print what would be done without modifying sync.yml",
    )
    args = parser.parse_args()

    data = fetch_releases(args.releases_json)
    sync_branches = parse_sync_yml_stable_branches(args.sync_yml)

    latest_stable = data["latest_stable"]["version"]
    latest_stable_branch = version_to_stable_branch(latest_stable)

    print(f"Latest stable: {latest_stable} ({latest_stable_branch})")
    print(f"Sync branches: {sorted(sync_branches)}")

    if latest_stable_branch in sync_branches:
        print("\nNo action needed — latest stable is already tracked.")
        return 0

    if args.dry_run:
        print(f"\nDry run: would add {latest_stable_branch} to sync.yml")
        return 1

    print(f"\nAdding {latest_stable_branch} to sync.yml...")
    if add_stable_to_sync_yml(args.sync_yml, latest_stable_branch):
        print("Done.")
        return 0
    else:
        return 1


if __name__ == "__main__":
    sys.exit(main())
