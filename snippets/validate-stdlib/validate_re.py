import re

# As re doesn't support escapes itself, use of r"" strings is not
# recommended.
regex = re.compile("[\r\n]")

regex.split("line1\rline2\nline3\r\n")

# Result:
# ['line1', 'line2', 'line3', '', '']


# ========================

# import re module
import re

Substring = ".*string.*"


String2 = "We are learning regex regex is very useful for string matching."

# Use of re.match() Method
print(re.match(Substring, String2))


import re

Substring = ".*Python"
String1 = "MicroPython"

m = re.match(Substring, String1)
print(type(m))
print(dir(m))
