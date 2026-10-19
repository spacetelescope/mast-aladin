import re
from urllib.parse import urlparse
from astropy.coordinates import SkyCoord
from astropy.table import QTable, Table

COORD_WORDS_TO_EXCLUDE = ['radius', 'radio', 'radial', 'extragalactic',
                          'infrared', 'fraction', 'gradient', 'ratio',
                          'integrated', 'radian', 'random', 'parallax', 'range',
                          'decade', 'decadal', 'decrement', 'deconvolve',
                          'err', 'bbox', 'min', 'max', 'error', 'xp']
# regular expressions to guess which columns correspond to ra, dec
COORD_PATTERNS = {
    "ra": re.compile(r'^ra$|^ra|ra$|^rightascension$|^rightascension|rightascension$|'
                     r'^right$|^ascension$|^ALPHA$|^ALPHA|ALPHA$', re.IGNORECASE),
    "dec": re.compile(r'^dec$|^dec|dec$|^declination$|^declination|declination$'
                      r'|^DELTA$|^DELTA|DELTA$', re.IGNORECASE)
}


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


def guess_coord_cols(table, ra_field=None, dec_field=None):
    """
    Determine the likely RA and Dec column names in `table` in a single pass.

    If `ra_field` and/or `dec_field` are explicitly provided, they are returned
    as-is for that coordinate. Otherwise, this first checks for the presence of a
    `~astropy.coordinates.SkyCoord` column, then checks if any columns contain
    UCDs in the metadata that indicate they are RA/Dec columns, and then falls back
    to matching column names against conventional source catalog RA/Dec
    naming patterns. If no good candidate column is found for a coordinate,
    '---' is returned for that coordinate (no selection).

    Parameters
    ----------
    table : `~astropy.table.Table` or `~astropy.table.QTable`
        The table to search for RA/Dec columns.
    ra_field, dec_field : str, optional
        If provided, used directly instead of guessing for that coordinate.

    Returns
    -------
    tuple of str
        (ra_column, dec_column). Either entry may be '---' if no good
        candidate column was found (and none was given explicitly).
    """

    if not isinstance(table, (Table, QTable)):
        return ra_field or '---', dec_field or '---'

    if ra_field is not None and dec_field is not None:
        return ra_field, dec_field

    table_colnames = table.colnames

    skycoord_col = next(
        (name for name in table_colnames if isinstance(table[name], SkyCoord)),
        None
    )

    all_column_names = [str(x).lower().strip() for x in table_colnames]

    for col in ("ra", "dec"):
        field = ra_field if col == "ra" else dec_field
        if field is not None:
            continue

        if skycoord_col is not None:
            guess = skycoord_col
        else:
            # check if any columns have a UCD that indicates they are RA/Dec columns
            ucd_prefix = f'pos.eq.{col}'
            column_ucds = {
                name: (table[name].meta.get('ucd') or '').strip().lower()
                for name in table_colnames
            }
            ucd_col = (next(
                (name for name, ucd in column_ucds.items()
                 if ucd == f'{ucd_prefix};meta.main'), None)
                       or next(
                    (name for name, ucd in column_ucds.items()
                     if ucd.startswith(ucd_prefix)), None)
                       )

            if ucd_col is not None:
                guess = ucd_col
            else:
                # finally, check if any column names match the conventional RA/Dec naming patterns
                token_pattern = COORD_PATTERNS[col]
                guess = next(
                    (table_colnames[i] for i, name in enumerate(all_column_names)
                     if check_col_tokens(col, token_pattern,
                                         re.split(r'[\s_\-\.]+', name))),
                    '---'
                )

        if col == "ra":
            ra_field = guess
        elif col == "dec":
            dec_field = guess
        else:
            raise NotImplementedError(f"Not a valid coordinate column: {col}.")

    return ra_field, dec_field


def check_col_tokens(col, token_pattern, tokens):
    if col in ("ra", "dec"):
        return (not any(token in COORD_WORDS_TO_EXCLUDE for token in tokens)
                and any(token_pattern.search(t) for t in tokens)
                )
    else:
        raise NotImplementedError(f"Not a valid coordinate column: {col}.")
