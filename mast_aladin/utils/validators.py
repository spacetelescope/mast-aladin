from urllib.parse import urlparse


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
