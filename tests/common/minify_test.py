

def test_minified_no_log():
    with open('minified/createstubs.py') as f:
        content = f.readlines()
    for line in content:
        assert line.find('._log') == -1, "all references to ._log have been removed"
