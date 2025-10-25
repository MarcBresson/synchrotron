from urllib.parse import urlencode, urljoin

GITHUB_REPO_LINK = "https://github.com/MarcBresson/synchrotron/"


def prefilled_issue_link(
    title: str | None = None,
    body: str | None = None,
    github_repo_link: str | None = None,
) -> str:
    params = {}
    if title is not None:
        params["title"] = title
    if body is not None:
        params["body"] = body

    if github_repo_link is None:
        github_repo_link = GITHUB_REPO_LINK

    return urljoin(github_repo_link, "issue?" + urlencode(params))
