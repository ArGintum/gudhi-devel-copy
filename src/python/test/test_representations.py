import os
import sys
import matplotlib.pyplot as plt
import numpy as np
import pytest

from sklearn.cluster import KMeans


def test_representations_examples():
    # Disable graphics for testing purposes
    plt.show = lambda: None
    here = os.path.dirname(os.path.realpath(__file__))
    sys.path.append(here + "/../example")
    import diagram_vectorizations_distances_kernels

    return None


from gudhi.representations.vector_methods import Atol
from gudhi.representations.metrics import *
from gudhi.representations.kernel_methods import *


def _n_diags(n):
    l = []
    for _ in range(n):
        a = np.random.rand(50, 2)
        a[:, 1] += a[:, 0]  # So that y >= x
        l.append(a)
    return l


def test_multiple():
    l1 = _n_diags(9)
    l2 = _n_diags(11)
    l1b = l1.copy()
    d1 = pairwise_persistence_diagram_distances(l1, e=0.00001, n_jobs=4)
    d2 = BottleneckDistance(epsilon=0.00001).fit_transform(l1)
    d3 = pairwise_persistence_diagram_distances(l1, l1b, e=0.00001, n_jobs=4)
    assert d1 == pytest.approx(d2)
    assert d3 == pytest.approx(d2, abs=1e-5)  # Because of 0 entries (on the diagonal)
    d1 = pairwise_persistence_diagram_distances(l1, l2, metric="wasserstein", order=2, internal_p=2)
    d2 = WassersteinDistance(order=2, internal_p=2, n_jobs=4).fit(l2).transform(l1)
    print(d1.shape, d2.shape)
    assert d1 == pytest.approx(d2, rel=0.02)


# Test sorted values as points order can be inverted, and sorted test is not documentation-friendly
def test_atol_doc():
    a = np.array([[1, 2, 4], [1, 4, 0], [1, 0, 4]])
    b = np.array([[4, 2, 0], [4, 4, 0], [4, 0, 2]])
    c = np.array([[3, 2, -1], [1, 2, -1]])

    atol_vectoriser = Atol(quantiser=KMeans(n_clusters=2, random_state=202006))
    assert np.sort(atol_vectoriser.fit(X=[a, b, c]).centers, axis=0) == \
        pytest.approx(np.array([[2. , 0.66666667, -0.4], \
                                [2.6, 2.8       , 3.33333333]]))
    assert np.sort(atol_vectoriser(a)) == pytest.approx(np.array([0.42375966, 1.18168665]))
    assert np.sort(atol_vectoriser(c)) == pytest.approx(np.array([0.02062512, 1.25157463]))
    assert np.sort(atol_vectoriser.transform(X=[a, b, c]), axis=0) == \
        pytest.approx(np.array([[0.02062512, 0.42375966], \
                                [0.29861028, 1.06330156], \
                                [1.18168665, 1.25157463]]))


def test_dummy_atol():
    a = np.array([[1, 2, 4], [1, 4, 0], [1, 0, 4]])
    b = np.array([[4, 2, 0], [4, 4, 0], [4, 0, 2]])
    c = np.array([[3, 2, -1], [1, 2, -1]])

    for weighting_method in ["cloud", "iidproba"]:
        for contrast in ["gaussian", "laplacian", "indicator"]:
            atol_vectoriser = Atol(
                quantiser=KMeans(n_clusters=1, random_state=202006),
                weighting_method=weighting_method,
                contrast=contrast,
            )
            atol_vectoriser.fit([a, b, c])
            atol_vectoriser(a)
            atol_vectoriser.transform(X=[a, b, c])


from gudhi.representations.vector_methods import BettiCurve


def test_infinity():
    a = np.array([[1.0, 8.0], [2.0, np.inf], [3.0, 4.0]])
    c = BettiCurve(20, [0.0, 10.0])(a)
    assert c[1] == 0
    assert c[7] == 3
    assert c[9] == 2
