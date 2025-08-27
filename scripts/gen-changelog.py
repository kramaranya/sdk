import argparse
import sys

try:
    from github import Github
except ImportError:
    print("Install PyGithub with pip install -e \".[dev]\"")
    sys.exit(1)

REPO_NAME = "kubeflow/sdk"
CHANGELOG_FILE = "CHANGELOG.md"


def categorize_pr(title: str) -> str:
    title = title.lower().strip()
    if title.startswith('feat'):
        return 'feat'
    elif title.startswith('fix'):
        return 'fix'
    elif title.startswith('chore'):
        return 'chore'
    elif title.startswith('revert'):
        return 'revert'
    else:
        return 'misc'


def get_initial_commit(github_repo):
    commits = list(github_repo.get_commits())
    return commits[-1].sha


def main():
    parser = argparse.ArgumentParser(description="Generate changelog for Kubeflow SDK")
    parser.add_argument("--token", required=True, help="GitHub Access Token")
    parser.add_argument("--version", required=True, help="Target version (e.g. v0.1.0)")

    args = parser.parse_args()

    current_release = args.version
    github_repo = Github(args.token).get_repo(REPO_NAME)

    try:
        tags = list(github_repo.get_tags())
        if not tags:
            print("First release - using full history")
            previous_release = get_initial_commit(github_repo)
        else:
            previous_release = tags[0].name
            print(f"Generating changelog: {previous_release} → HEAD (for {current_release})")
    except Exception as e:
        print(f"Error finding previous release: {e}")
        sys.exit(1)

    comparison = github_repo.compare(previous_release, "HEAD")
    commits = list(comparison.commits)

    if not commits:
        print("No commits found in range")
        sys.exit(1)

    categories = {
        'feat': [],
        'fix': [],
        'chore': [],
        'revert': [],
        'misc': []
    }

    pr_set = set()
    for commit in reversed(commits):
        for pr in commit.get_pulls():
            if pr.number in pr_set:
                continue
            pr_set.add(pr.number)

            category = categorize_pr(pr.title)
            pr_entry = (f"- {pr.title} ([#{pr.number}]({pr.html_url})) "
                        f"by [@{pr.user.login}]({pr.user.html_url})")
            categories[category].append(pr_entry)

    if not pr_set:
        print("No PRs found in range")
        sys.exit(1)

    release_date = str(commits[-1].commit.author.date).split(" ")[0]
    release_url = f"https://github.com/{REPO_NAME}/releases/tag/{current_release}"

    changelog_content = [
        f"# [{current_release}]({release_url}) ({release_date})\n\n"
    ]

    if categories['feat']:
        changelog_content.append("## New Features\n\n")
        changelog_content.append("\n".join(categories['feat']) + "\n\n")

    if categories['fix']:
        changelog_content.append("## Bug Fixes\n\n")
        changelog_content.append("\n".join(categories['fix']) + "\n\n")

    if categories['chore']:
        changelog_content.append("## Maintenance\n\n")
        changelog_content.append("\n".join(categories['chore']) + "\n\n")

    if categories['revert']:
        changelog_content.append("## Reverts\n\n")
        changelog_content.append("\n".join(categories['revert']) + "\n\n")

    if categories['misc']:
        changelog_content.append("## Other Changes\n\n")
        changelog_content.append("\n".join(categories['misc']) + "\n\n")

    changelog_content.append(f"**Full Changelog**: {comparison.html_url}\n\n")

    try:
        with open(CHANGELOG_FILE, "r") as f:
            existing_content = f.read()
    except FileNotFoundError:
        existing_content = "# Changelog\n\n"

    lines = existing_content.split('\n')

    insert_index = 0
    for i, line in enumerate(lines):
        if line.strip() == "# Changelog":
            insert_index = i + 1
            while insert_index < len(lines) and not lines[insert_index].strip():
                insert_index += 1
            break

    new_content = ''.join(changelog_content)
    new_lines = (
        lines[:insert_index] + new_content.rstrip().split('\n') + [''] + lines[insert_index:]
    )

    with open(CHANGELOG_FILE, "w") as f:
        f.write('\n'.join(new_lines))

    print("Changelog has been updated")
    print(f"Found {len(pr_set)} PRs for {current_release}")


if __name__ == "__main__":
    main()
