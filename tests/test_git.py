import os
from local_mcp_adapters import GitMCPClient

def test_git_init_add_commit(tmp_path):
    git = GitMCPClient(base_dir=str(tmp_path))

    # Init repo
    result = git.init_repo("myrepo")
    assert result["status"] == "ok"
    repo_path = tmp_path / "myrepo"

    # Create file
    test_file = repo_path / "a.txt"
    test_file.write_text("contenido", encoding="utf-8")

    # Add file
    add_res = git.add("myrepo", str(test_file))
    assert add_res["status"] == "ok"

    # Commit
    commit_res = git.commit("myrepo", "primer commit", author="Test User <test@example.com>")
    assert commit_res["status"] == "ok"
    # Must accept either real or simulated commits
    assert "message" in commit_res
