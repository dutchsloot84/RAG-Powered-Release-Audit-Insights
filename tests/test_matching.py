from datetime import datetime

from app.core import matching
from app.models import Commit, Issue


def test_matching_basic():
    issues = [
        Issue(key="ABC-1", summary="", description="", components=[], fixversions=[], updated=datetime.utcnow()),
        Issue(key="ABC-2", summary="", description="", components=[], fixversions=[], updated=datetime.utcnow()),
    ]
    commits = [
        Commit(sha="1", author="a", date=datetime.utcnow(), message="fix ABC-1 bug", repo="r", branch="b"),
        Commit(sha="2", author="b", date=datetime.utcnow(), message="misc", repo="r", branch="b"),
    ]
    res = matching.match_commits(issues, commits)
    assert res["missing"] == ["ABC-2"]
    assert commits[1] in res["unlinked"]
    assert res["coverage"] == 50.0
