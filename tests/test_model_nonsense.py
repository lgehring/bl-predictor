# This contains some examples for what functionality might be tested, TODO…:
from teamproject.models.nonsense import Model


def test_fit():
    m1 = Model.fit([1])
    m2 = Model.fit([1, 2])
    assert m1.params == 1
    assert m2.params == 5


def test_predict():
    m1 = Model(1)
    m2 = Model(5)
    assert m1.predict(0) == 0
    assert m1.predict(6) == 6
    assert m2.predict(0) == 0
    assert m2.predict(6) == 30
