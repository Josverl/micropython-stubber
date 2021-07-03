import subprocess

code = """
print("hello {}".format("Jos"))
"""

code = bytes(code, "utf-8")
output = subprocess.check_output(
    ["black", "-"],
    # env={},   # <-- if empty : OSError: [WinError 87] The parameter is incorrect
    input=code,
)
print(output)


work_with_bytes = False
output = subprocess.check_output(
    formatter_args,
    env={},
    input=code,
    universal_newlines=not work_with_bytes,
    encoding=None if work_with_bytes else "utf-8",
)

print(output)
