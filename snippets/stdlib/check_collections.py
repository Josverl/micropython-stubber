from collections import namedtuple

MyTuple = namedtuple("MyTuple", ("id", "name"))
t1 = MyTuple(1, "foo")
t2 = MyTuple(2, "bar")
print(t1.name)
assert t2.name == t2[1]

print(type(MyTuple))
print(type(t1))
print(type(t2))


from collections import OrderedDict

# To make benefit of ordered keys, OrderedDict should be initialized
# from sequence of (key, value) pairs.
d = OrderedDict([("z", 1), ("a", 2)])
# More items can be added as usual
# PYRIGHT: adding to ordered dict is flagged by pyright
d["w"] = 5  # type: ignore
d["b"] = 3  # type: ignore
for k, v in d.items():
    print(k, v)
