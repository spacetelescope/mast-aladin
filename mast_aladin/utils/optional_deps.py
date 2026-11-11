import warnings


def import_jdaviz():
    try:
        import jdaviz
    except ImportError:
        warnings.warn(
            "The optional dependency `jdaviz` is not installed in this environment. "
            "To gain access to `jdaviz`-related features in `mast-aladin`, install jdaviz."
        )
        jdaviz = None
    return jdaviz
