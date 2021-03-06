import numbers
import numpy as np

from sklearn.utils.testing import assert_array_almost_equal
from sklearn.utils.testing import assert_array_equal
from sklearn.utils.testing import assert_equal
from sklearn.utils.testing import assert_not_equal
from sklearn.utils.testing import assert_less_equal
from sklearn.utils.testing import assert_greater_equal
from sklearn.utils.testing import assert_true
from sklearn.utils.testing import assert_raises_regex

from skopt.space import Space
from skopt.space import Real
from skopt.space import Integer
from skopt.space import Categorical
from skopt.space import check_dimension as space_check_dimension


def check_dimension(Dimension, vals, random_val):
    x = Dimension(*vals)
    assert_equal(x, Dimension(*vals))
    assert_not_equal(x, Dimension(vals[0], vals[1] + 1))
    assert_not_equal(x, Dimension(vals[0] + 1, vals[1]))
    assert_equal(x.rvs(random_state=1), random_val)


def check_categorical(vals, random_val):
    x = Categorical(vals)
    assert_equal(x, Categorical(vals))
    assert_not_equal(x, Categorical(vals[:-1] + ("zzz",)))
    assert_equal(x.rvs(random_state=1), random_val)


def test_dimensions():
    yield (check_dimension, Real, (1., 4.), 2.251066014107722)
    yield (check_dimension, Real, (1, 4), 2.251066014107722)
    yield (check_dimension, Integer, (1, 4), 2)
    yield (check_dimension, Integer, (1., 4.), 2)
    yield (check_categorical, ("a", "b", "c", "d"), "b")
    yield (check_categorical, (1., 2., 3., 4.), 2.)


def check_limits(value, lower_bound, upper_bound):
    assert_less_equal(lower_bound, value)
    assert_greater_equal(upper_bound, value)


def test_real():
    a = Real(1, 25)
    for i in range(50):
        yield (check_limits, a.rvs(random_state=i), 1, 25)
    random_values = a.rvs(random_state=0, n_samples=10)
    assert_array_equal(random_values.shape, (10))
    assert_array_equal(a.transform(random_values), random_values)
    assert_array_equal(a.inverse_transform(random_values), random_values)

    log_uniform = Real(10**-5, 10**5, prior="log-uniform")
    assert_not_equal(log_uniform, Real(10**-5, 10**5))
    for i in range(50):
        random_val = log_uniform.rvs(random_state=i)
        yield (check_limits, random_val, 10**-5, 10**5)
    random_values = log_uniform.rvs(random_state=0, n_samples=10)
    assert_array_equal(random_values.shape, (10))
    transformed_vals = log_uniform.transform(random_values)
    assert_array_equal(transformed_vals, np.log10(random_values))
    assert_array_equal(
        log_uniform.inverse_transform(transformed_vals), random_values)


def test_integer():
    a = Integer(1, 10)
    for i in range(50):
        yield (check_limits, a.rvs(random_state=i), 1, 11)
    random_values = a.rvs(random_state=0, n_samples=10)
    assert_array_equal(random_values.shape, (10))
    assert_array_equal(a.transform(random_values), random_values)
    assert_array_equal(a.inverse_transform(random_values), random_values)


def test_categorical_transform():
    categories = ["apple", "orange", "banana", None, True, False, 3]
    cat = Categorical(categories)

    apple = [1., 0., 0., 0., 0., 0., 0.]
    orange = [0., 1.0, 0.0, 0.0, 0., 0., 0.]
    banana = [0., 0., 1., 0., 0., 0., 0.]
    none = [0., 0., 0., 1., 0., 0., 0.]
    true = [0., 0., 0., 0., 1., 0., 0.]
    false = [0., 0., 0., 0., 0., 1., 0.]
    three = [0., 0., 0., 0., 0., 0., 1.]

    assert_equal(cat.transformed_size, 7)
    assert_equal(cat.transformed_size, cat.transform(["apple"]).size)
    assert_array_equal(
        cat.transform(categories),
        [apple, orange, banana, none, true, false, three]
        )
    assert_array_equal(cat.transform(["apple", "orange"]), [apple, orange])
    assert_array_equal(cat.transform(["apple", "banana"]), [apple, banana])
    assert_array_equal(cat.inverse_transform([apple, orange]),
                       ["apple", "orange"])
    assert_array_equal(cat.inverse_transform([apple, banana]),
                       ["apple", "banana"])
    ent_inverse = cat.inverse_transform(
        [apple, orange, banana, none, true, false, three])
    assert_array_equal(ent_inverse, categories)


def test_categorical_transform_binary():
    categories = ["apple", "orange"]
    cat = Categorical(categories)

    apple = [0.]
    orange = [1.]

    assert_equal(cat.transformed_size, 1)
    assert_equal(cat.transformed_size, cat.transform(["apple"]).size)
    assert_array_equal(cat.transform(categories), [apple, orange])
    assert_array_equal(cat.transform(["apple", "orange"]), [apple, orange])
    assert_array_equal(cat.inverse_transform([apple, orange]),
                       ["apple", "orange"])
    ent_inverse = cat.inverse_transform([apple, orange])
    assert_array_equal(ent_inverse, categories)


def test_space_consistency():
    # Reals (uniform)

    s1 = Space([Real(0.0, 1.0)])
    s2 = Space([Real(0.0, 1.0)])
    s3 = Space([Real(0, 1)])
    s4 = Space([(0.0, 1.0)])
    s5 = Space([(0.0, 1.0, "uniform")])
    a1 = s1.rvs(n_samples=10, random_state=0)
    a2 = s2.rvs(n_samples=10, random_state=0)
    a3 = s3.rvs(n_samples=10, random_state=0)
    a4 = s4.rvs(n_samples=10, random_state=0)
    a5 = s5.rvs(n_samples=10, random_state=0)
    assert_equal(s1, s2)
    assert_equal(s1, s3)
    assert_equal(s1, s4)
    assert_equal(s1, s5)
    assert_array_equal(a1, a2)
    assert_array_equal(a1, a3)
    assert_array_equal(a1, a4)
    assert_array_equal(a1, a5)

    # Reals (log-uniform)
    s1 = Space([Real(10**-3.0, 10**3.0, prior="log-uniform")])
    s2 = Space([Real(10**-3.0, 10**3.0, prior="log-uniform")])
    s3 = Space([Real(10**-3, 10**3, prior="log-uniform")])
    s4 = Space([(10**-3.0, 10**3.0, "log-uniform")])
    a1 = s1.rvs(n_samples=10, random_state=0)
    a2 = s2.rvs(n_samples=10, random_state=0)
    a3 = s3.rvs(n_samples=10, random_state=0)
    a4 = s4.rvs(n_samples=10, random_state=0)
    assert_equal(s1, s2)
    assert_equal(s1, s3)
    assert_equal(s1, s4)
    assert_array_equal(a1, a2)
    assert_array_equal(a1, a3)
    assert_array_equal(a1, a4)

    # Integers
    s1 = Space([Integer(1, 5)])
    s2 = Space([Integer(1.0, 5.0)])
    s3 = Space([(1, 5)])
    a1 = s1.rvs(n_samples=10, random_state=0)
    a2 = s2.rvs(n_samples=10, random_state=0)
    a3 = s3.rvs(n_samples=10, random_state=0)
    assert_equal(s1, s2)
    assert_equal(s1, s3)
    assert_array_equal(a1, a2)
    assert_array_equal(a1, a3)

    # Categoricals
    s1 = Space([Categorical(["a", "b", "c"])])
    s2 = Space([Categorical(["a", "b", "c"])])
    a1 = s1.rvs(n_samples=10, random_state=0)
    a2 = s2.rvs(n_samples=10, random_state=0)
    assert_equal(s1, s2)
    assert_array_equal(a1, a2)


def test_space_api():
    space = Space([(0.0, 1.0), (-5, 5),
                   ("a", "b", "c"), (1.0, 5.0, "log-uniform"), ("e", "f")])

    assert_equal(len(space.dimensions), 5)
    assert_true(isinstance(space.dimensions[0], Real))
    assert_true(isinstance(space.dimensions[1], Integer))
    assert_true(isinstance(space.dimensions[2], Categorical))
    assert_true(isinstance(space.dimensions[3], Real))
    assert_true(isinstance(space.dimensions[4], Categorical))

    samples = space.rvs(n_samples=10, random_state=0)
    assert_equal(len(samples), 10)
    assert_equal(len(samples[0]), 5)

    assert_true(isinstance(samples, list))
    for n in range(4):
        assert_true(isinstance(samples[n], list))

    assert_true(isinstance(samples[0][0], numbers.Real))
    assert_true(isinstance(samples[0][1], numbers.Integral))
    assert_true(isinstance(samples[0][2], str))
    assert_true(isinstance(samples[0][3], numbers.Real))
    assert_true(isinstance(samples[0][4], str))

    samples_transformed = space.transform(samples)
    assert_equal(samples_transformed.shape[0], len(samples))
    assert_equal(samples_transformed.shape[1], 1 + 1 + 3 + 1 + 1)
    assert_array_equal(samples, space.inverse_transform(samples_transformed))

    samples = space.inverse_transform(samples_transformed)
    assert_true(isinstance(samples[0][0], numbers.Real))
    assert_true(isinstance(samples[0][1], numbers.Integral))
    assert_true(isinstance(samples[0][2], str))
    assert_true(isinstance(samples[0][3], numbers.Real))
    assert_true(isinstance(samples[0][4], str))

    for b1, b2 in zip(space.bounds,
                      [(0.0, 1.0), (-5, 5),
                       np.asarray(["a", "b", "c"]), (1.0, 5.0),
                       np.asarray(["e", "f"])]):
        assert_array_equal(b1, b2)

    for b1, b2 in zip(space.transformed_bounds,
                      [(0.0, 1.0), (-5, 5), (0.0, 1.0), (0.0, 1.0), (0.0, 1.0),
                       (np.log10(1.0), np.log10(5.0)), (0.0, 1.0)]):
        assert_array_equal(b1, b2)


def test_normalize():
    a = Real(2.0, 30.0, transform="normalize")
    for i in range(50):
        yield (check_limits, a.rvs(random_state=i), 2, 30)

    rng = np.random.RandomState(0)
    X = rng.randn(100)
    X = 28 * (X - X.min()) / (X.max() - X.min()) + 2

    # Check transformed values are in [0, 1]
    assert_true(np.all(a.transform(X) <= np.ones_like(X)))
    assert_true(np.all(np.zeros_like(X) <= a.transform(X)))

    # Check inverse transform
    assert_array_almost_equal(a.inverse_transform(a.transform(X)), X)

    # log-uniform prior
    a = Real(10**2.0, 10**4.0, prior="log-uniform", transform="normalize")
    for i in range(50):
        yield (check_limits, a.rvs(random_state=i), 10**2, 10**4)

    rng = np.random.RandomState(0)
    X = np.clip(10**3 * rng.randn(100), 10**2.0, 10**4.0)

    # Check transform
    assert_true(np.all(a.transform(X) <= np.ones_like(X)))
    assert_true(np.all(np.zeros_like(X) <= a.transform(X)))

    # Check inverse transform
    assert_array_almost_equal(a.inverse_transform(a.transform(X)), X)

    a = Integer(2, 30, transform="normalize")
    for i in range(50):
        yield (check_limits, a.rvs(random_state=i), 2, 30)
    assert_array_equal(a.transformed_bounds, (0, 1))

    X = rng.randint(2, 31)
    # Check transformed values are in [0, 1]
    assert_true(np.all(a.transform(X) <= np.ones_like(X)))
    assert_true(np.all(np.zeros_like(X) <= a.transform(X)))

    # Check inverse transform
    X_orig = a.inverse_transform(a.transform(X))
    assert_equal(X_orig.dtype, "int64")
    assert_array_equal(X_orig, X)


def check_valid_transformation(klass):
    assert klass(2, 30, transform="normalize")
    assert klass(2, 30, transform="identity")
    assert_raises_regex(ValueError, "should be 'normalize' or 'identity'",
                        klass, 2, 30, transform='not a valid transform name')


def test_valid_transformation():
    yield (check_valid_transformation, Integer)
    yield (check_valid_transformation, Real)


def test_invalid_dimension():
    assert_raises_regex(ValueError, "has to be a list or tuple",
                        space_check_dimension, "23")
    assert_raises_regex(ValueError, "Invalid dimension",
                        space_check_dimension, (23,))


def test_categorical_identity():
    categories = ["cat", "dog", "rat"]
    cat = Categorical(categories, transform="identity")
    samples = cat.rvs(100)
    assert_true(all([t in categories for t in cat.rvs(100)]))
    transformed = cat.transform(samples)
    assert_array_equal(transformed, samples)
    assert_array_equal(samples, cat.inverse_transform(transformed))
