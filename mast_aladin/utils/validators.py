import re
from urllib.parse import urlparse

import numpy as np
from astropy.coordinates import SkyCoord
from astropy.table import Table, QTable
COORD_WORDS_TO_EXCLUDE = ['radius', 'radio', 'radial', 'extragalactic',
                          'infrared', 'fraction', 'gradient', 'ratio',
                          'integrated', 'radian', 'random', 'parallax', 'range',
                          'decade', 'decadal', 'decrement', 'deconvolve',
                          'err', 'bbox', 'min', 'max', 'error', 'xp']



def is_valid_s3_uri(uri: str) -> bool:
    parsed = urlparse(uri)
    # Check scheme is 's3' and a bucket name exists in netloc
    return parsed.scheme == 's3' and bool(parsed.netloc)


def check_table_for_columns(table, ra_field, dec_field):
    """
    Raise ValueError if `ra_field` and `dec_field` are not column
    names in `table`.

    Parameters
    ----------
    table : `~astropy.table.Table`
        _description_
    ra_field : str
        RA column name
    dec_field : str
        Dec column name

    Raises
    ------
    ValueError
    """
    for col, name in [[ra_field, 'RA'], [dec_field, 'Dec']]:
        if col not in table.colnames:
            raise ValueError(f"{name} column '{col}' not found in table.")


def guess_coord_cols(col, table):
    """
    Rough guess at detecting RA/Dec columns from input table to determine
    the initial selections for the column select dropdown. This starts
    by checking for the presence of a SkyCoord (if col is 'ra' or 'dec'),
    and next checking against some common source catalog column names.
    If no good candidate column is found, return '---' (no selection).
    """

    # regular expressions to guess which columns correspond to ra, dec
    COORD_PATTERNS = {
        "ra": re.compile(r'^ra$|^ra|ra$|^rightascension$|^rightascension|rightascension$|'
                         r'^right$|^ascension$|^ALPHA$|^ALPHA|ALPHA$', re.IGNORECASE), # noqa
        "dec": re.compile(r'^dec$|^dec|dec$|^declination$|^declination|declination$'
                          r'|^DELTA$|^DELTA|DELTA$', re.IGNORECASE), # noqa
    }

    if not isinstance(table, (Table, QTable)):
        return

    colnames = table.colnames

    if colnames is None:
        return

    idx = None
    # if column is given as an astropy SkyCoord, find the first column that is a SkyCoord
    if col in ['ra', 'dec']:
        col_is_sc = [isinstance(table[colnames[i]], SkyCoord) for i in range(len(colnames))]
        if np.any(col_is_sc):
            idx = np.where(col_is_sc)[0][0]

    if idx is None:
        all_column_names = [str(x).lower().strip() for x in colnames]

        get_idx = lambda x, s, d: s.index(x) if x in s else d # noqa

        if col in ("ra", "dec"):
            token_pattern = COORD_PATTERNS[col]
        else:
            raise NotImplementedError(f"Not a valid coordinate column: {col}.")

        idx = next((get_idx(c, all_column_names, None) for c in all_column_names
                    if check_col_tokens(col, token_pattern, re.split(r'[\s_\-\.]+', c))),
                   None)

    # if no good candidate found, default to '---' (no selection)
    if idx is None:
        return '---'
    else:
        return colnames[idx]


def check_col_tokens(self, col, token_pattern, tokens):
    if col in ("ra", "dec"):
        return (not any(token in COORD_WORDS_TO_EXCLUDE for token in tokens)
                and any(token_pattern.search(t) for t in tokens)
                )
    else:
        raise NotImplementedError(f"Not a valid coordinate column: {col}.")