import re
from urllib.parse import urlparse

import numpy as np
from astropy.coordinates import SkyCoord
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


def find_coord_col(col,
                   table_colnames,
                   radec_field=None):
    """
    Determines the likely RA/Dec column name from a table. First checks
    for the presence of a SkyCoord (if col is 'ra' or 'dec'), and then checks
    against common source catalog RA/Dec column names. If no good
    candidate column is found, this returns '---' (no selection).

    Parameters
    ----------
    col : str
        The coordinate column to guess ('ra' or 'dec').
    table_colnames : list or tuple
        The column names of the table to search.
    radec_field : str, optional
        If provided, this is the name of the RA/Dec column to use instead of guessing.
    """

    # regular expressions to guess which columns correspond to ra, dec
    COORD_PATTERNS = {
        "ra": re.compile(r'^ra$|^ra|ra$|^rightascension$|^rightascension|rightascension$|'
                         r'^right$|^ascension$|^ALPHA$|^ALPHA|ALPHA$', re.IGNORECASE),
        "dec": re.compile(r'^dec$|^dec|dec$|^declination$|^declination|declination$'
                          r'|^DELTA$|^DELTA|DELTA$', re.IGNORECASE)
    }

    if not isinstance(table_colnames, (list, tuple)):
        return '---'

    if table_colnames is None:
        return '---'

    idx = None
    # if column is given as an astropy SkyCoord, find the first column that is a SkyCoord
    if col in ["ra", "dec"] and radec_field is None:
        col_is_sc = [isinstance(table_colnames[i], SkyCoord) for i in range(len(table_colnames))]
        if np.any(col_is_sc):
            idx = np.where(col_is_sc)[0][0]

    if idx is None:
        all_column_names = [str(x).lower().strip() for x in table_colnames]

        get_idx = lambda x, s, d: s.index(x) if x in s else d  # noqa: E731

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
        return table_colnames[idx]


def check_col_tokens(col, token_pattern, tokens):
    if col in ("ra", "dec"):
        return (not any(token in COORD_WORDS_TO_EXCLUDE for token in tokens)
                and any(token_pattern.search(t) for t in tokens)
                )
    else:
        raise NotImplementedError(f"Not a valid coordinate column: {col}.")
