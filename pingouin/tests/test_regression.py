import numpy as np
from numpy.testing import assert_almost_equal
from pingouin.tests._tests_pingouin import _TestPingouin
from pingouin.regression import linear_regression, mediation_analysis
from pingouin.datasets import read_dataset

from scipy.stats import linregress
from sklearn.linear_model import LinearRegression

df = read_dataset('mediation')


class TestRegression(_TestPingouin):
    """Test regression.py."""

    def test_linear_regression(self):
        """Test function linear_regression."""

        # Simple regression
        lm = linear_regression(df['X'], df['Y'])  # Pingouin
        sc = linregress(df['X'].values, df['Y'].values)  # SciPy
        assert_almost_equal(lm['coef'][1], sc.slope)
        assert_almost_equal(lm['coef'][0], sc.intercept)
        assert_almost_equal(lm['se'][1], sc.stderr)
        assert_almost_equal(lm['pvals'][1], sc.pvalue, decimal=5)
        assert_almost_equal(np.sqrt(lm['rsquared']), sc.rvalue)

        # Multiple regression with intercept
        X = df[['X', 'M']].values
        y = df['Y'].values
        lm = linear_regression(X, y)  # Pingouin
        sk = LinearRegression(fit_intercept=True).fit(X, y)  # SkLearn
        assert_almost_equal(lm['coef'][1:], sk.coef_)
        assert_almost_equal(lm['coef'][0], sk.intercept_)
        assert_almost_equal(sk.score(X, y), lm['rsquared'])

        # No intercept
        lm = linear_regression(X, y, add_intercept=False)
        sk = LinearRegression(fit_intercept=False).fit(X, y)
        assert_almost_equal(lm['coef'], sk.coef_)
        assert_almost_equal(sk.score(X, y), lm['rsquared'])

        # Test other arguments
        linear_regression(df[['X', 'M']], df['Y'], coef_only=True)
        linear_regression(df[['X', 'M']], df['Y'], alpha=0.01)
        linear_regression(df[['X', 'M']], df['Y'], alpha=0.10)

    def test_mediation_analysis(self):
        """Test function mediation_analysis."""
        ma = mediation_analysis(data=df, x='X', m='M', y='Y', n_boot=500)
        assert ma['Beta'][0] == 0.5610
        assert ma['Beta'][2] == 0.3961
        assert ma['Beta'][3] == 0.0396
        assert ma['Beta'][4] == 0.3565

        _, dist = mediation_analysis(data=df, x='X', m='M', y='Y', n_boot=1000,
                                     return_dist=True)
        assert dist.size == 1000
        mediation_analysis(data=df, x='X', m='M', y='Y', alpha=0.01)
