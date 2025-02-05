# from cmath import isnan
# from hypothesis import assume, given, strategies as st, example, event
# import pytest


# def floats():
#     return st.floats(allow_nan=True, allow_infinity=True)


# @given(st.integers())
# @example(42)
# def test_integers(i):
#     pass


# @pytest.mark.parametrize("m", [3, 5, 6, 7])
# @given(i=st.integers().filter(lambda x: x % 2 == 0))
# def test_even_integers(i, m):
#     event(f"i mod {m} = {i%m}")
#     # event(f"i mod 7 = {i%7}")
#     pass


# @given(x=floats())
# def test_negation_is_self_inverse(x):
#     assume(not isnan(x))
#     assert x == -(-x)


# @given(
#     st.lists(st.integers(1, 2000)),
# )
# def test_sum_is_positive(xs):
#     assume(xs)
#     # assume(len(xs) > 10)
#     assume(all(x > 0 for x in xs))
#     # print(xs)
#     assert sum(xs) > 0
