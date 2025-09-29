from astropy import units as u
from astropy.table import Table
from astroquery.mast import MastMissions
from pyvo.dal import TAPService

#
# Missions MAST multi-environment helper, plus a couple save query results.
#

def missions_mast(mission, env):
    missions = MastMissions(mission=mission)

    if env in ['dev', 'test', 'int']:
        base_url = f'https://mast{env}.stsci.edu'
        missions._service_api_connection.SERVICE_URL = base_url
        missions._service_api_connection.REQUEST_URL = f'{base_url}/search/{mission}/api/v0.1/'
        missions._service_api_connection.MISSIONS_DOWNLOAD_URL = f'{base_url}/search/'

    return missions


def saved_roman_test_results():
    """
    Return saved results from:

    mast = missions_mast('roman', 'test')
    target = SkyCoord(ra=270, dec=66, unit='deg')
    radius = 0.3 * u.deg
    roman_observations = mast.query_region(target, radius=radius) #, select_cols=['s_region'])
    """
    roman_observations = Table.read("roman_obs.csv")
    return roman_observations


def saved_gaia_reults():
    """
    Return saved results from:

    gaia_sources = Catalogs.query_region(target, radius=0.2, catalog="Gaia", version=2)
    """
    gaia_sources = Table.read("gaia_sources.csv")
    return gaia_sources


#############################################

#
# TAP Region Search Helpers
#

def create_adql_region(region):
    """
    Returns the ADQL description of the given polygon or cirle region

    region - Iterable of RA/Dec pairs as lists/sequences OR
             stc-s POLYGON or CIRCLE string OR
             astropy region (TBD) OR
             other (TBD)
    """
    adql_region = None
    if isinstance(region, str):
        region = region.lower()
        parts = region.split()
        if parts[0] == 'polygon':
            # Assume we've got an STC-s polygon
            try:
                float(parts[1])
                point_parts = parts[1:] # There's no coord frame present if we got this far.
            except ValueError:
                point_parts = parts[2:]
            point_string = ','.join(point_parts)
            adql_region = f"POLYGON('ICRS',{point_string})"
        elif parts[0] == 'circle':
            # Assume we've got an STC-s circle
            try:
                float(parts[1])
                radius = parts[1]
                point_parts = parts[2:]
            except ValueError:
                radius = parts[2]
                point_parts = parts[3:]
            point_string = ','.join(point_parts)
            adql_region = f"CIRCLE('ICRS',{point_string},{radius})"
    else:
        # Assume we've got a list/sequence of points (lists/sequences)
        point_string = ','.join([str(num) for point in region for num in point])
        adql_region = f"POLYGON('ICRS',{point_string})"

    return adql_region


def create_mast_region_adql(region, other_clauses='', limit=50000):
    """
    Creates the ADQL to query the MAST CAOM TAP service for observations over the
    specified region.

    region - Iterable of RA/Dec pairs as lists/sequences OR
             stc-s POLYGON or CIRCLE string OR
             astropy region (TBD) OR
             other (TBD)
    other_clauses - ADQL to tack on to the end of the CAOM TAP obspointing query
    limit - max number of rows to return (default 50000)

    Returns a string containing the necessary ADQL.
    """
    adql = None
    adql_region = create_adql_region(region)
    if adql_region:
        adql = f"""
SELECT TOP {limit} *
FROM dbo.obspointing o
WHERE
CONTAINS(POINT('ICRS',s_ra,s_dec),
   {adql_region}
)=1
"""
        adql += other_clauses
        return adql


def mast_reqion_query(region, other_clauses='', limit=50000, show_query=True):
    """
    Query MAST observations over the specified region using the MAST CAOM TAP service.

    region - Iterable of RA/Dec pairs as lists/sequences OR
             stc-s POLYGON or CIRCLE string OR
             astropy region (TBD) OR
             other (TBD)
    other_clauses - ADQL to tack on to the end of the CAOM TAP obspointing query
    limit - max number of rows to return (default 50000)

    Returns an astropy table of MAST observations much like astroquery.mast Observations queries.
    """
    adql = create_mast_region_adql(region, other_clauses, limit)
    if not adql:
        raise ValueError('region must be iterable of RA/Dec pairs as lists/sequences '
                         'OR valid stc-s POLYGON or CIRCLE string')

    mast_caom_tap_service = TAPService("https://mast.stsci.edu/vo-tap/api/v0.1/caom")

    if show_query:
        print(f'Querying MAST CAOM TAP with:\n{adql}')

    #results = mast_caom_tap_service.run_async(adql)
    results = mast_caom_tap_service.search(adql)
    table_results = results.to_table()
    if show_query:
        print(f'Number of results: {len(table_results)}')

    return table_results


def mast_region_query_aladin_fov(aladin, other_clauses='', limit=50000, show_query=True):
    """
    Query MAST observations over the FoV of the specified Aladin instance.  We won't do the
    search if Aladin's FoV is greater than 1 degree or its WCS doesn't exist for some reason.

    aladin - A MastAladin instance.
    other_clauses - ADQL to tack on to the end of the CAOM TAP obspointing query
    limit - max number of rows to return (default 50000)

    Returns an astropy table of MAST observations much like astroquery.mast Observations queries.
    """
    results = None

    # Don't do it if FoV is bigger than 1 degree.
    if aladin.fov > 1 * u.degree:
        print(f'FoV of {aladin.fov} is greater than the 1 degree limit.')
    elif aladin.wcs:
        footprint = aladin.wcs.calc_footprint()
        results = mast_reqion_query(footprint, other_clauses=other_clauses, limit=limit, show_query=show_query)
    else:
        print('Aladin WCS information not found')

    return results
