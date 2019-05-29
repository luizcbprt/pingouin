import scipy
import numpy as np
import pandas as pd
from unittest import TestCase
from pingouin.nonparametric import (mad, madmedianrule, mwu, wilcoxon,
                                    kruskal, friedman, cochran)

np.random.seed(1234)
x = np.random.normal(size=100)
y = np.random.normal(size=100)
z = np.random.normal(size=100)


class TestNonParametric(TestCase):
    """Test nonparametric.py."""

    def test_mad(self):
        """Test function mad."""
        a = [1.2, 3, 4.5, 2.4, 5, 6.7, 0.4]
        # Compare to Matlab
        assert mad(a, normalize=False) == 1.8
        assert np.round(mad(a), 3) == np.round(1.8 * 1.4826, 3)

    def test_madmedianrule(self):
        """Test function madmedianrule."""
        a = [1.2, 3, 4.5, 2.4, 5, 12.7, 0.4]
        assert np.alltrue(madmedianrule(a) == [False, False, False,
                                               False, False, True, False])

    def test_mwu(self):
        """Test function mwu"""
        mwu_scp = scipy.stats.mannwhitneyu(x, y, use_continuity=True,
                                           alternative='two-sided')
        mwu_pg = mwu(x, y, tail='two-sided')
        assert mwu_scp[0] == mwu_pg.at['MWU', 'U-val']
        assert mwu_scp[1] == mwu_pg.at['MWU', 'p-val']
        mwu(x, y, tail='one-sided')

    def test_wilcoxon(self):
        """Test function wilcoxon"""
        wc_scp = scipy.stats.wilcoxon(x, y, correction=True)
        wc_pg = wilcoxon(x, y, tail='two-sided')
        wc_pg_1 = wilcoxon(x, y, tail='one-sided')
        assert wc_scp[0] == wc_pg.at['Wilcoxon', 'W-val']
        assert wc_scp[1] == wc_pg.at['Wilcoxon', 'p-val']
        assert (wc_pg.at['Wilcoxon', 'p-val'] / 2) == wc_pg_1.at['Wilcoxon',
                                                                 'p-val']

    def test_friedman(self):
        """Test function friedman"""
        df = pd.DataFrame({'DV': np.r_[x, y, z],
                           'Time': np.repeat(['A', 'B', 'C'], 100),
                           'Subject': np.tile(np.arange(100), 3)})
        friedman(data=df, dv='DV', subject='Subject', within='Time')
        summary = friedman(data=df, dv='DV', within='Time', subject='Subject',
                           export_filename='test_export.csv')
        # Compare with SciPy built-in function
        from scipy import stats
        Q, p = stats.friedmanchisquare(x, y, z)
        assert np.allclose(np.round(Q, 3), summary['Q']['Friedman'])
        assert np.allclose(p, summary['p-unc']['Friedman'])
        # Test with NaN
        df.loc[10, 'DV'] = np.nan
        friedman(data=df, dv='DV', subject='Subject', within='Time')

    def test_kruskal(self):
        """Test function kruskal"""
        x_nan = x.copy()
        x_nan[10] = np.nan
        df = pd.DataFrame({'DV': np.r_[x_nan, y, z],
                           'Group': np.repeat(['A', 'B', 'C'], 100)})
        kruskal(data=df, dv='DV', between='Group')
        summary = kruskal(data=df, dv='DV', between='Group',
                          export_filename='test_export.csv')
        # Compare with SciPy built-in function
        H, p = scipy.stats.kruskal(x_nan, y, z, nan_policy='omit')
        assert np.allclose(np.round(H, 3), summary['H']['Kruskal'])
        assert np.allclose(p, summary['p-unc']['Kruskal'])

    def test_cochran(self):
        """Test function cochran"""
        from pingouin import read_dataset
        df = read_dataset('cochran')
        st = cochran(dv='Energetic', within='Time', subject='Subject', data=df)
        assert st.loc['cochran', 'Q'] == 6.706
        cochran(dv='Energetic', within='Time', subject='Subject', data=df,
                export_filename='test_export.csv')
        # With a NaN value
        df.loc[2, 'Energetic'] = np.nan
        cochran(dv='Energetic', within='Time', subject='Subject', data=df)
