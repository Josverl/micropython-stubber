from micropython import const

case1 = const(11)

# Micropython >= 1.19.0
case2 = const(1.0)
case3 = const(True)
case4 = const("foo")
case5 = const(b"foo")
case6 = const((1, 2, 3))
case7 = const(1 + 2)
case8 = const(1.0 + 2.0)

# Should show error
# todo: how to test for this error?
# case = const({"foo": "bar"})
# case = const(["foo", "bar"])
