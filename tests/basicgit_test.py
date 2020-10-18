# import sys; sys.path[1:1]=['src']
import sys
import os
import pytest

#make sure that the source can be found
sys.path.insert(1, './src')

# pylint: disable=wrong-import-position,import-error
# Module Under Test
import basicgit as git

def common_tst(tag):
    print(tag)
    assert isinstance(tag, str), "tag must be a string"
    assert tag.startswith('v'), "tags start with a v"
    assert len(tag) >= 2, "tags are longer than 2 chars"

def test_get_tag_current():
    if not os.path.exists('.git'):
        pytest.skip("no git repo in current folder")
    else:
        # get tag of current repro
        common_tst(git.get_tag())

        for testcase in ['.', '.git', './.git', '.\\.git']:
            common_tst(git.get_tag(testcase))


def test_get_failure_throws():
    with pytest.raises(Exception):
        git.get_tag('.not')

def test_pull_master(gitrepo_micropython):
    "test and force update to most recent"
    repo_path = gitrepo_micropython
    x = git.pull(repo_path, 'master')
    #Should succeed.
    assert x
  
def test_get_tag_sibling():
    # get version of sibling repro
    for testcase in ['../micropython', '..\\micropython']:
        common_tst(git.get_tag(testcase))

def test_checkout_sibling(gitrepo_micropython):
    repo_path = gitrepo_micropython
    x = git.get_tag(repo_path)
    # todo detect any pending local changes
    for ver in ['v1.11', 'v1.9.4', 'v1.12']:
        git.checkout_tag(ver, repo=repo_path)
        assert git.get_tag(repo_path) == ver

    git.checkout_tag(x, repo=repo_path)
    assert git.get_tag(repo_path) == x, "can restore to prior version"

