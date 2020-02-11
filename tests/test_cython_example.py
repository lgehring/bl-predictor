from scaffold.cython_example import gauss_sum


def test_gauss_sum():
    assert gauss_sum(0) == 0
    assert gauss_sum(1) == 1
    assert gauss_sum(2) == 3
    assert gauss_sum(3) == 6
    assert gauss_sum(100) == 5050
