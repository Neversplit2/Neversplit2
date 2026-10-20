"""Fetch live GitHub data for the profile card and write it to data.json."""

import collections
import datetime
import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request


HERE = os.path.dirname(os.path.abspath(__file__))
with open(os.path.join(HERE, "config.json"), encoding="utf-8") as config_file:
    CONFIG = json.load(config_file)
LOGIN = CONFIG["login"]
TOKEN = os.environ.get("GITHUB_TOKEN")
API_ROOT = "https://api.github.com"
COLORS = {
    "Python": "#3572A5",
    "JavaScript": "#f1e05a",
    "HTML": "#e34c26",
    "CSS": "#563d7c",
    "TypeScript": "#3178c6",
    "Jupyter Notebook": "#DA5B0B",
    "C++": "#f34b7d",
    "Java": "#b07219",
    "MATLAB": "#e16737",
    "R": "#198CE7",
    "Shell": "#89e051",
}

HEADERS = {
    "Accept": "application/vnd.github.v3+json",
    "Content-Type": "application/json",
    "User-Agent": "Neversplit2-profile-card",
}
if TOKEN:
    HEADERS["Authorization"] = f"Bearer {TOKEN}"

GRAPHQL_QUERY = """
query($login: String!) {
  user(login: $login) {
    contributionsCollection {
      totalCommitContributions
      contributionCalendar {
        totalContributions
        weeks {
          contributionDays {
            contributionCount
            color
            date
          }
        }
      }
    }
  }
}
"""


class GitHubAPIError(Exception):
    """An HTTP or GraphQL error returned by GitHub."""

    def __init__(self, message, status=None):
        super().__init__(message)
        self.status = status


def api_call(url, body=None):
    request = urllib.request.Request(url, data=body, headers=HEADERS)
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            return json.load(response)
    except urllib.error.HTTPError as error:
        raise GitHubAPIError(
            f"GitHub API returned HTTP {error.code} for {url}", error.code
        ) from error
    except (
        urllib.error.URLError,
        TimeoutError,
        json.JSONDecodeError,
        UnicodeDecodeError,
    ) as error:
        raise GitHubAPIError(f"GitHub API request failed for {url}: {error}") from error


def report_api_error(section, error):
    print(f"{section} unavailable: {error}", file=sys.stderr)


def get_contributions():
    result = api_call(
        f"{API_ROOT}/graphql",
        json.dumps(
            {"query": GRAPHQL_QUERY, "variables": {"login": LOGIN}}
        ).encode("utf-8"),
    )
    if not isinstance(result, dict):
        raise GitHubAPIError("GitHub returned an invalid GraphQL response")
    if result.get("errors"):
        messages = "; ".join(error.get("message", "GraphQL error") for error in result["errors"])
        raise GitHubAPIError(messages)

    user = (result.get("data") or {}).get("user")
    if not user:
        raise GitHubAPIError(f"GitHub user {LOGIN} was not returned by GraphQL")

    collection = user["contributionsCollection"]
    calendar = collection["contributionCalendar"]
    weeks = calendar.get("weeks", [])[-52:]
    if not weeks:
        raise GitHubAPIError("GitHub returned an empty contribution calendar")

    calendar_weeks = [
        [
            {
                "count": day["contributionCount"],
                "color": day.get("color"),
                "date": day["date"],
            }
            for day in week.get("contributionDays", [])
        ]
        for week in weeks
    ]
    if not any(calendar_weeks):
        raise GitHubAPIError("GitHub returned no contribution days")

    return {
        "commits": collection["totalCommitContributions"],
        "total": calendar["totalContributions"],
        "weeks": calendar_weeks,
    }


def get_repositories():
    repositories = []
    page = 1
    while True:
        page_repos = api_call(
            f"{API_ROOT}/users/{LOGIN}/repos?type=owner&per_page=100&page={page}"
        )
        if not isinstance(page_repos, list) or any(
            not isinstance(repo, dict) for repo in page_repos
        ):
            raise GitHubAPIError("GitHub returned an invalid repository list")
        repositories.extend(page_repos)
        if len(page_repos) < 100:
            return repositories
        page += 1


def get_languages(repositories):
    sizes = collections.Counter()
    colors = {}
    incomplete = False
    for repo in repositories:
        full_name = repo.get("full_name")
        if not full_name:
            continue
        encoded_name = urllib.parse.quote(full_name, safe="/")
        try:
            language_sizes = api_call(f"{API_ROOT}/repos/{encoded_name}/languages")
        except GitHubAPIError as error:
            report_api_error(f"Languages for {full_name}", error)
            incomplete = True
            if error.status in (403, 429):
                break
            continue

        if not isinstance(language_sizes, dict):
            report_api_error(
                f"Languages for {full_name}",
                GitHubAPIError("GitHub returned an invalid language breakdown"),
            )
            incomplete = True
            continue
        for language, byte_count in language_sizes.items():
            if not isinstance(byte_count, int):
                report_api_error(
                    f"Languages for {full_name}",
                    GitHubAPIError(f"Invalid byte count for {language}"),
                )
                incomplete = True
                continue
            sizes[language] += byte_count
            colors[language] = COLORS.get(language, "#8b949e")

    total_bytes = sum(sizes.values())
    if not total_bytes:
        return [], incomplete

    ranked = sizes.most_common()
    displayed = ranked[:5]
    if len(ranked) > 5:
        displayed.append(("Other", sum(size for _, size in ranked[5:])))

    languages = []
    used_percentage = 0.0
    for index, (name, byte_count) in enumerate(displayed):
        if index == len(displayed) - 1:
            percentage = round(100.0 - used_percentage, 1)
        else:
            percentage = round(byte_count * 100.0 / total_bytes, 1)
            used_percentage += percentage
        languages.append(
            {
                "name": name,
                "color": colors.get(name, "#8b949e"),
                "pct": percentage,
            }
        )
    return languages, incomplete


def relative_time(timestamp):
    committed_at = datetime.datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
    seconds = max(
        0,
        int(
            (
                datetime.datetime.now(datetime.timezone.utc)
                - committed_at.astimezone(datetime.timezone.utc)
            ).total_seconds()
        ),
    )
    for unit_seconds, unit in ((86400, "d"), (3600, "h"), (60, "m")):
        if seconds >= unit_seconds:
            return f"{seconds // unit_seconds}{unit} ago"
    return "just now"


def get_recent_commits(repositories):
    events = api_call(f"{API_ROOT}/users/{LOGIN}/events/public?per_page=100")
    if not isinstance(events, list):
        raise GitHubAPIError("GitHub returned an invalid public-events list")
    commits = []
    for event in events:
        if not isinstance(event, dict):
            continue
        if event.get("type") != "PushEvent":
            continue
        repo_data = event.get("repo")
        payload = event.get("payload")
        timestamp = event.get("created_at")
        if not isinstance(repo_data, dict) or not isinstance(payload, dict) or not timestamp:
            continue
        repository = repo_data.get("name", "").rsplit("/", 1)[-1]
        for commit in reversed(payload.get("commits", [])):
            if not isinstance(commit, dict):
                continue
            message = commit.get("message", "").splitlines()
            if not message:
                continue
            commits.append(
                {
                    "msg": message[0],
                    "repo": repository,
                    "when": relative_time(timestamp),
                }
            )
            if len(commits) == 5:
                return commits
    if commits:
        return commits

    repository_names = {
        repo["full_name"]
        for repo in repositories
        if isinstance(repo.get("full_name"), str) and repo["full_name"]
    }
    repository_names.update(
        full_name
        for full_name in CONFIG.get("projects", [])
        if isinstance(full_name, str) and full_name
    )
    dated_commits = []
    for full_name in sorted(repository_names):
        encoded_name = urllib.parse.quote(full_name, safe="/")
        payload = api_call(
            f"{API_ROOT}/repos/{encoded_name}/commits"
            f"?author={urllib.parse.quote(LOGIN)}&per_page=5"
        )
        if not isinstance(payload, list):
            raise GitHubAPIError(
                f"GitHub returned an invalid commit list for {full_name}"
            )
        for item in payload:
            if not isinstance(item, dict):
                continue
            commit = item.get("commit")
            if not isinstance(commit, dict):
                continue
            message = commit.get("message", "").splitlines()
            author = commit.get("author")
            timestamp = author.get("date") if isinstance(author, dict) else None
            if not message or not timestamp:
                continue
            committed_at = datetime.datetime.fromisoformat(
                timestamp.replace("Z", "+00:00")
            ).astimezone(datetime.timezone.utc)
            dated_commits.append(
                (
                    committed_at,
                    {
                        "msg": message[0],
                        "repo": full_name.rsplit("/", 1)[-1],
                        "when": relative_time(timestamp),
                    },
                )
            )

    dated_commits.sort(key=lambda item: item[0], reverse=True)
    return [commit for _, commit in dated_commits[:5]]


def empty_data():
    return {
        "updated": None,
        "login": LOGIN,
        "api_status": "unavailable",
        "stats": {"repos": None, "stars": None, "commits": None, "followers": None},
        "total": None,
        "calendar_start": None,
        "weeks": [],
        "languages": [],
        "projects": [],
        "commits": [],
    }


def fetch_data():
    data = empty_data()
    errors = []
    successful_requests = 0

    try:
        profile = api_call(f"{API_ROOT}/users/{LOGIN}")
        if not isinstance(profile, dict):
            raise GitHubAPIError("GitHub returned an invalid user profile")
        data["stats"]["repos"] = profile["public_repos"]
        data["stats"]["followers"] = profile["followers"]
        successful_requests += 1
    except (GitHubAPIError, KeyError, TypeError) as error:
        report_api_error("Profile metrics", error)
        errors.append("profile")

    try:
        repositories = get_repositories()
        successful_requests += 1
        data["stats"]["stars"] = sum(
            repo.get("stargazers_count", 0) for repo in repositories
        )
    except (GitHubAPIError, TypeError) as error:
        report_api_error("Repository metrics", error)
        errors.append("repositories")
        repositories = []

    try:
        contribution_data = get_contributions()
        data["stats"]["commits"] = contribution_data["commits"]
        data["total"] = contribution_data["total"]
        data["weeks"] = contribution_data["weeks"]
        successful_requests += 1
        data["calendar_start"] = next(
            day["date"] for week in data["weeks"] for day in week
        )
    except (GitHubAPIError, KeyError, TypeError, ValueError) as error:
        report_api_error("Contribution activity", error)
        errors.append("contributions")

    if "repositories" not in errors:
        try:
            data["languages"], incomplete = get_languages(repositories)
            successful_requests += 1
            if incomplete:
                errors.append("languages")
        except (GitHubAPIError, TypeError) as error:
            report_api_error("Language breakdown", error)
            errors.append("languages")

    data["projects"] = []
    for full_name in CONFIG.get("projects", []):
        encoded_name = urllib.parse.quote(full_name, safe="/")
        try:
            repo = api_call(f"{API_ROOT}/repos/{encoded_name}")
            if not isinstance(repo, dict):
                raise GitHubAPIError("GitHub returned invalid repository data")
            language = repo.get("language") or ""
            data["projects"].append(
                {
                    "name": repo["name"],
                    "description": repo.get("description") or "",
                    "language": language,
                    "color": COLORS.get(language, "#8b949e"),
                    "stars": repo.get("stargazers_count", 0),
                    "forks": repo.get("forks_count", 0),
                    "url": repo.get("html_url", f"https://github.com/{full_name}"),
                    "tags": (repo.get("topics") or [])[:4],
                }
            )
            successful_requests += 1
        except (GitHubAPIError, KeyError, TypeError) as error:
            report_api_error(f"Project {full_name}", error)
            errors.append("projects")
            data["projects"].append(
                {
                    "name": full_name.rsplit("/", 1)[-1],
                    "description": "Repository data unavailable",
                    "language": "",
                    "color": "#8b949e",
                    "stars": None,
                    "forks": None,
                    "url": f"https://github.com/{full_name}",
                    "tags": [],
                }
            )

    try:
        data["commits"] = get_recent_commits(repositories)
        successful_requests += 1
    except (GitHubAPIError, KeyError, TypeError, ValueError) as error:
        report_api_error("Recent commits", error)
        errors.append("commits")

    data["updated"] = datetime.datetime.now(datetime.timezone.utc).isoformat()
    data["api_status"] = (
        "unavailable"
        if successful_requests == 0
        else "live"
        if not errors
        else "partial"
    )
    return data


if __name__ == "__main__":
    result = fetch_data()
    output_path = os.path.join(HERE, "data.json")
    with open(output_path, "w", encoding="utf-8") as output_file:
        json.dump(result, output_file, indent=1)
    print(f"data.json written ({result['api_status']})")
