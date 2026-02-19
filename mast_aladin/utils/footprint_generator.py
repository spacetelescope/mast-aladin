from abc import ABC, abstractmethod

from astropy.table import Table
from pysiaf.utils.rotations import attitude_matrix
from mast_aladin.utils.selectSIAF import (
    defineApertures,
    getVertices,
    computeStcsFootprint,
)


def s_region(apertures, att_matrix):
    """
    Generate a combined STCS region string from multiple apertures.

    This function processes a list of apertures, applies an attitude matrix
    transformation, retrieves their vertices in sky coordinates, and combines
    their individual STCS footprints into a single region string.

    Args:
        apertures (list): A list of aperture objects to process. Each aperture should support
                         set_attitude_matrix(), idl_to_sky(), and have vertex information.
        att_matrix (array-like): The 3x3 attitude matrix to apply to each aperture for
                               coordinate transformation.

    Returns:
        str: A combined STCS region string representing the footprints
             of all valid apertures. Empty string if no apertures have valid
             vertices.

    Notes:
        - Apertures without vertices (e.g., HST/FGS PICK) are skipped.
        - Each aperture's footprint is appended to the combined result.
    """
    combined_s_region = ''

    for ap in apertures:
        ap.set_attitude_matrix(att_matrix)
        xVertices, yVertices = getVertices(ap)

        # Skip PICK (pickle) which do not have vertices
        if (xVertices is not None and yVertices is not None):
            skyRa, skyDec = ap.idl_to_sky(xVertices, yVertices)
            ap_s_region = computeStcsFootprint(ap, skyRa, skyDec)
            combined_s_region += ap_s_region
    return combined_s_region


def exp_list_to_table(exp_list):
    """
    Convert a list of exposure data into an Astropy Table.

    Parameters
    ----------
    exp_list : list of tuples/lists/dicts
        A list containing exposure data where each element corresponds to the
        columns described in the return value (in order unless dicts).

    Returns
    -------
    astropy.table.Table
        An Astropy Table with the following columns:
        - telescope: Telescope name
        - instrument: Instrument name
        - aperture: Aperture specification
        - targ_ra: Target right ascension
        - targ_dec: Target declination
        - aper_ra: RA of the aperture reference point
        - aper_dec: Dec of the aperture reference point
        - program_num: Program number
        - obs_num: Observation number
        - position_angle: Position angle
        - exp_num: Exposure number
        - x_off: X offset from pattern
        - y_off: Y offset from pattern
        - pattern_point: Pattern point identifier
        - s_region: STCS Sky region
    """
    names = [
        'telescope',
        'instrument',
        'aperture',
        'targ_ra',
        'targ_dec',
        'aper_ra',
        'aper_dec',
        'program_num',
        'obs_num',
        'position_angle',
        'exp_num',
        'x_off',
        'y_off',
        'pattern_point',
        's_region',
    ]
    table = Table(names=names, data=exp_list)
    return table


class ExpResultGenerator(ABC):
    """
    """
    @abstractmethod
    def get_exp_list(
        self,
        pa=0,
        program_num=0,
        obs_num=0,
        exp_num=0,
        pattern_point=0,
        pointing=None,
    ) -> list:
        pass


class Pointing:
    """
    A pointing defines a target on the sky and a V2/V3 coordinate that should
    be placed on that target. It is independent of position angle which is the
    angle from North to East measured at a particular V2/V3.
    """

    @property
    def v2(self):
        return self._v2

    @property
    def v3(self):
        return self._v3

    @property
    def ra(self):
        return self._ra

    @property
    def dec(self):
        return self._dec

    @property
    def x_off(self):
        return self._x_off

    @property
    def y_off(self):
        return self._y_off

    def __init__(self, v2, v3, ra, dec, x_off=0, y_off=0):
        """
        Initialize a Pointing object.

        Parameters
        ----------
        v2 : float
            V2 coordinate value.
        v3 : float
            V3 coordinate value.
        ra : float
            Right ascension in degrees.
        dec : float
            Declination in degrees.
        x_off : float, optional
            X-axis offset used to compute the input v2. Not used for
            computation, just for metadata (default: 0).
        y_off : float, optional
            Y-axis offset used to compute the input v3. Not used for
            computation, just for metadata (default: 0).
        """
        self._v2 = v2
        self._v3 = v3
        self._ra = ra
        self._dec = dec
        self._x_off = x_off
        self._y_off = y_off

    def attitude_matrix(self, pa=0):
        att_matrix = attitude_matrix(self.v2, self.v3, self.ra, self.dec, pa)
        return att_matrix


class Exposure(ExpResultGenerator):

    @property
    def telescope(self):
        return self._telescope

    @property
    def instrument(self):
        return self._instrument

    @property
    def aperture(self):
        return self._aperture

    @property
    def ref_aperture_siaf(self):
        return self._ref_aperture_siaf

    @property
    def target_ra(self):
        return self._target_ra

    @property
    def target_dec(self):
        return self._target_dec

    @property
    def x_off(self):
        return self._x_off

    @property
    def y_off(self):
        return self._y_off

    @property
    def aperture_list(self):
        return self._aperture_list

    @property
    def V2Ref(self):
        return self._V2Ref

    @property
    def V3Ref(self):
        return self._V3Ref

    @property
    def pointing(self):
        return Pointing(
            self.V2Ref,
            self.V3Ref,
            self.target_ra,
            self.target_dec,
            x_off=self.x_off,
            y_off=self.y_off,
        )

    def __init__(self, target_ra, target_dec, x_off=0, y_off=0,
                 telescope='roman', instrument='WFI', aperture='ALL'):
        """
        Initialize an Exposure which represents a telescope aperture pointed at a sky position.

        For convenience, the defaults use the Roman telescope WFI instrument (all detectors).

        Parameters
        ----------
        target_ra : float
            Right ascension of the target in degrees.
        target_dec : float
            Declination of the target in degrees.
        x_off : float, optional
            x offset from the target in detector ideal coordinates (default: 0).
        y_off : float, optional
            y offset from the target in detector ideal coordinates (default: 0).
        telescope : str, optional
            Name of the telescope. Default is 'roman'.  Valid values are:
            - 'roman' allows these values for instrument and aperture:
              - instrument: ALL, WFI, CGI
              - aperture: ALL or individual apertures listed in instrument documentation
            - 'hst' allows these values for instrument and aperture:
              - instrument: ALL, ACS, COS, FGS, NICMOS, STIS, WFC3
              - aperture: ALL or individual apertures listed in instrument documentation
            - 'jwst' allows these values for instrument and aperture:
              - instrument: ALL, FGS, MIRI, NIRCAM, NIRSPEC, NIRISS
              - aperture: ALL or individual apertures listed in instrument documentation
        instrument : str, optional
            Name of the instrument. Default is 'WFI'.  See telescope for allowed values.
        aperture : str, optional
            Aperture specification. Default is 'ALL'.  See telescope for allowed values.
        """

        self._target_ra = target_ra
        self._target_dec = target_dec
        self._x_off = x_off
        self._y_off = y_off
        self._telescope = telescope
        self._instrument = instrument
        self._aperture = aperture

        (
            self._aperture_list,
            aper_v2_ref,
            aper_v3_ref,
            self._ref_aperture_siaf,
        ) = defineApertures(telescope, instrument, aperture)

        self._ref_aper_v2_ref = aper_v2_ref
        self._ref_aper_v3_ref = aper_v3_ref

        if self._ref_aperture_siaf is None:
            # If the reference aperture doesn't exist (e.g., when
            # pseudoaperture jwst fgs all was selected), use the first
            # aperture object in the list to try the offset calculation.
            self._ref_aperture_siaf = self.aperture_list[0]

        # Apply the offset to get the reference V2/V3 for this exposure.
        self._V2Ref, self._V3Ref = self.ref_aperture_siaf.idl_to_tel(
            -x_off,
            -y_off,
            V2Ref_arcsec=aper_v2_ref,
            V3Ref_arcsec=aper_v3_ref
            )

    def get_exp_list(
        self,
        pa=0,
        program_num=0,
        obs_num=0,
        exp_num=0,
        pattern_point=0,
        pointing=None,
    ) -> list:
        """
        Generate a list of exposure dictionaries for the given observation
        parameters.

        For Roman WFI observations with aperture set to 'all', creates separate
        exposure entries for each of the 18 detectors. For other instruments
        or aperture configurations, creates a single exposure entry covering
        all specified apertures.

        Position angle (pa) is the only arg that can affect more than metadata
        in the output exposure list. All these will be set appropriately when
        called by a containing Pattern or Observation.

        Args:
            pa (int, optional): Position angle in degrees. Defaults to 0.
            program_num (int, optional): Program number. Defaults to 0.
            obs_num (int, optional): Observation number. Defaults to 0.
            exp_num (int, optional): Exposure number. Defaults to 0.
            pattern_point (int, optional): Pattern point index. Defaults to 0.
            pointing (Pointing, optional): Pointing information including offsets and attitude.
                If None, uses the instance's pointing attribute. Defaults to None.

        Returns:
            list: A list of exposure dictionaries, each containing exposure metadata
                (aperture, s_region, aper_ra, aper_dec, etc.) and observation parameters.
        """
        exp_list = []
        if pointing is None:
            pointing = self.pointing
        att_matrix = pointing.attitude_matrix(pa)

        if (
            self.telescope.lower() == 'roman'
            and self.instrument.lower() == 'wfi'
            and self.aperture.lower() == 'all'
        ):
            # Separate the 18 detectors into separate "exposures".
            for ap in self.aperture_list:
                exp = self._base_exp_obj(
                    pa,
                    program_num,
                    obs_num,
                    exp_num,
                    pattern_point,
                    pointing.x_off,
                    pointing.y_off,
                )
                exp['aperture'] = ap.AperName
                exp['s_region'] = s_region([ap], att_matrix)
                aper_ra, aper_dec = ap.tel_to_sky(ap.V2Ref, ap.V3Ref)
                exp['aper_ra'] = aper_ra
                exp['aper_dec'] = aper_dec
                exp_list.append(exp)

        else:
            exp = self._base_exp_obj(
                pa,
                program_num,
                obs_num,
                exp_num,
                pattern_point,
                pointing.x_off,
                pointing.y_off,
            )
            exp['s_region'] = s_region(self.aperture_list, att_matrix)
            aper_ra, aper_dec = self.aperture_list[0].tel_to_sky(self._ref_aper_v2_ref,
                                                                 self._ref_aper_v3_ref)
            exp['aper_ra'] = aper_ra
            exp['aper_dec'] = aper_dec
            exp_list.append(exp)

        return exp_list

    def _base_exp_obj(
        self,
        pa=0,
        program_num=0,
        obs_num=0,
        exp_num=0,
        pattern_point=0,
        x_off=0,
        y_off=0,
    ) -> list:

        base_exp_obj = {
            'telescope': self.telescope,
            'instrument': self.instrument,
            'aperture': self.aperture,
            'targ_ra': self.target_ra.degree,
            'targ_dec': self.target_dec.degree,
            'aper_ra': self.target_ra.degree,
            'aper_dec': self.target_dec.degree,
            'program_num': program_num,
            'obs_num': obs_num,
            'position_angle': pa,
            'exp_num': exp_num,
            'x_off': x_off,
            'y_off': y_off,
            'pattern_point': pattern_point,
            's_region': '',
        }

        return base_exp_obj


class Pattern(ExpResultGenerator):

    @property
    def exposure(self):
        return self._exposure

    @property
    def pointings(self):
        return self._pointings

    def __init__(self, exposure):
        """
        Pattern is not meant to be directly instantiated. This should be
        called only by subclasses.
        """
        super().__init__()
        self._exposure = exposure

    def get_exp_list(
        self,
        pa=0,
        program_num=0,
        obs_num=0,
        exp_num=0,
        pattern_point=0,
        pointing=None,
    ) -> list:
        """
        Generate a list of exposure dictionaries for this pattern and the
        given observation parameters. Delegate to Exposure.get_exp_list()
        for the exposure details.

        Position angle (pa) is the only arg that can affect more than
        metadata in the output exposure list. All these will be set
        appropriately when called by a containing Pattern or Observation.

        Args:
            pa (int, optional): Position angle in degrees. Defaults to 0.
            program_num (int, optional): Program number. Defaults to 0.
            obs_num (int, optional): Observation number. Defaults to 0.
            exp_num (int, optional): Exposure number. Defaults to 0.
            pattern_point (int, optional): Pattern point index.
                Defaults to 0.
            pointing (Pointing, optional): Ignored since the pointings
                are defined by the pattern. Defaults to None.

        Returns:
            list: A list of exposure dictionaries, each containing exposure metadata
                (aperture, s_region, aper_ra, aper_dec, etc.) and observation parameters.
        """
        exp_list = []
        for p in self.pointings:
            sub_list = self.exposure.get_exp_list(
                pa, program_num, obs_num, exp_num, pattern_point, p
            )
            exp_list.extend(sub_list)
            pattern_point += 1

        return exp_list


class CustomPattern(Pattern):

    def __init__(self, exposure, offsets):
        """
        Create a dither pattern of the specified exposure using the custom
        list of ideal detector coordinate offsets provided.

        Args:
            exposure: Has the target and aperture that define the initial
                pointing before offsets are applied.
            offsets: List of tuples/lists representing (x, y) arcsecond
                offsets for each point in the pattern.
        """
        super().__init__(exposure)

        self._offsets = offsets
        self._pointings = self._generate_pointings()

    @property
    def offsets(self):
        return self._offsets

    def _generate_pointings(self):
        pointings = []
        V2Ref_arcsec = self.exposure.V2Ref
        V3Ref_arcsec = self.exposure.V3Ref
        ref_aperture_siaf = self.exposure.ref_aperture_siaf

        ra = self.exposure.target_ra
        dec = self.exposure.target_dec

        for offset in self.offsets:
            total_x_off = offset[0]
            total_y_off = offset[1]

            # Negate the offsets since they will define ideal coords on
            # which to place the target, but the user is picturing moving
            # the aperture in the direction of the ideal axes.
            offset_v2, offset_v3 = ref_aperture_siaf.idl_to_tel(
                -total_x_off,
                -total_y_off,
                V2Ref_arcsec=V2Ref_arcsec,
                V3Ref_arcsec=V3Ref_arcsec
                )

            pointing = Pointing(
                offset_v2,
                offset_v3,
                ra,
                dec,
                x_off=total_x_off,
                y_off=total_y_off
                )
            pointings.append(pointing)

        return pointings


class DitherPattern(Pattern):

    def __init__(
        self,
        exposure,
        num_rows=1,
        num_cols=1,
        row_x_offset=0,
        row_y_offset=0,
        col_x_offset=0,
        col_y_offset=0,
    ):
        """
        Create a dither pattern of the specified exposure. The pattern will
        have the specified number of rows and columns. Both the X and Y
        offsets within a row or column can be specified. The X and Y refer
        to Ideal Detector Coordinates.

        Args:
            exposure: Has the target and aperture that define the initial
                pointing before offsets are applied.
            num_rows (int, optional): Number of rows in the grid.
                Defaults to 1.
            num_cols (int, optional): Number of columns in the grid.
                Defaults to 1.
            row_x_offset (int, optional): X-axis offset (arcsecs) within
                a row. Defaults to 0.
            row_y_offset (int, optional): Y-axis offset (arcsecs) within
                a row. Defaults to 0.
            col_x_offset (int, optional): X-axis offset (arcsecs) within
                a column. Defaults to 0.
            col_y_offset (int, optional): Y-axis offset (arcsecs) within
                a column. Defaults to 0.
        """
        super().__init__(exposure)

        self._num_rows = num_rows
        self._num_cols = num_cols

        self._row_x_off = row_x_offset
        self._row_y_off = row_y_offset
        self._col_x_off = col_x_offset
        self._col_y_off = col_y_offset

        self._pointings = self._generate_pointings()

    @property
    def num_rows(self):
        return self._num_rows

    @property
    def num_cols(self):
        return self._num_cols

    @property
    def row_x_off(self):
        return self._row_x_off

    @property
    def row_y_off(self):
        return self._row_y_off

    @property
    def col_x_off(self):
        return self._col_x_off

    @property
    def col_y_off(self):
        return self._col_y_off

    def _generate_pointings(self):
        pointings = []
        V2Ref_arcsec = self.exposure.V2Ref
        V3Ref_arcsec = self.exposure.V3Ref
        ref_aperture_siaf = self.exposure.ref_aperture_siaf
        if ref_aperture_siaf is None:
            # If the reference aperture doesn't exist (e.g., when
            # pseudoaperture jwst fgs all was selected), use the first
            # aperture object in the list to try the offset calculation.
            ref_aperture_siaf = self.exposure.aperture_list[0]
        ra = self.exposure.target_ra
        dec = self.exposure.target_dec

        for col in range(0, self._num_cols):
            col_x_off = col * self._col_x_off
            col_y_off = col * self._col_y_off
            for row in range(0, self._num_rows):
                row_x_off = row * self._row_x_off
                row_y_off = row * self._row_y_off
                total_x_off = col_x_off + row_x_off
                total_y_off = col_y_off + row_y_off

                # Negate the offsets since they will define ideal coords on
                # which to place the target, but the user is picturing moving
                # the aperture in the direction of the ideal axes.
                offset_v2, offset_v3 = ref_aperture_siaf.idl_to_tel(
                    -total_x_off,
                    -total_y_off,
                    V2Ref_arcsec=V2Ref_arcsec,
                    V3Ref_arcsec=V3Ref_arcsec
                    )

                pointing = Pointing(
                    offset_v2,
                    offset_v3,
                    ra,
                    dec,
                    x_off=total_x_off,
                    y_off=total_y_off
                    )

                pointings.append(pointing)

        return pointings


class Observation(ExpResultGenerator):
    @property
    def pa(self):
        return self._pa

    @property
    def contents(self):
        return self._contents

    def __init__(self, pa=0):
        """
        Create an Observation with an optional position angle. Exposures
        and patterns can be added to an observation.

        Args:
            pa (int, optional): Position angle in degrees. Defaults to 0.
        """
        super().__init__()
        self._pa = pa
        self._contents = []

    def add_pattern(self, pattern: Pattern):
        """
        Add a pattern to this Observation.

        Args:
            pattern (Pattern): The pattern object to be added.

        Returns:
            Pattern: The added pattern object.
        """
        self._contents.append(pattern)
        return pattern

    def add_exposure(self, exposure: Exposure):
        """
        Add an exposure to this Observation.

        Args:
            exposure (Exposure): The exposure object to be added.

        Returns:
            Exposure: The exposure object that was added.
        """
        self._contents.append(exposure)
        return exposure

    def get_exp_list(
        self,
        pa=None,
        program_num=0,
        obs_num=0,
        exp_num=0,
        pattern_point=0,
        pointing=None,
    ) -> list:
        """
        Generate a list of exposure dictionaries for this observation.
        Delegate to Pattern.get_exp_list() and Exposure.get_exp_list()
        for the exposure details.

        Position angle (pa) is the only arg that can affect more than
        metadata in the output exposure list. All these will be set
        appropriately when called by a containing Pattern or Observation.

        Args:
            pa (int, optional): Position angle in degrees. If set, will
                override the position angle of this observation.
                Defaults to 0.
            program_num (int, optional): Program number. Defaults to 0.
            obs_num (int, optional): Observation number. Defaults to 0.
            exp_num (int, optional): Exposure number. Defaults to 0.
            pattern_point (int, optional): Pattern point index.
                Defaults to 0.
            pointing (Pointing, optional): Ignored since the pointings
                are defined by the patterns and exposures. Defaults to None.

        Returns:
            list: A list of exposure dictionaries, each containing exposure metadata
                (aperture, s_region, aper_ra, aper_dec, etc.) and observation parameters.
        """
        exp_list = []
        if pa is None:
            pa = self.pa
        for c in self.contents:
            sub_list = c.get_exp_list(pa=pa, program_num=program_num, obs_num=obs_num)
            exp_list.extend(sub_list)
            exp_num += 1

        return exp_list


class Program(ExpResultGenerator):
    @property
    def program_num(self):
        return self._program_num

    @property
    def contents(self):
        return self._contents

    def __init__(self, program_num=0):
        """
        Create an empty observing program with the specified program number.
        Observations can later be added to this Program via
        add_observation().

        Args:
            program_num (int, optional): The program number to associate
                with this object. Defaults to 0.
        """
        super().__init__()
        self._program_num = program_num
        self._contents = []

    def add_observation(self, obs: Observation):
        """
        Add an observation to this Program.

        Args:
            obs (Observation): The observation object to add.

        Returns:
            Observation: The observation object that was added.
        """
        self._contents.append(obs)
        return obs

    def get_exp_list(
        self,
        pa=0,
        program_num=0,
        obs_num=0,
        exp_num=0,
        pattern_point=0,
        pointing=None,
    ) -> list:
        """
        Generate a list of exposure dictionaries for this program. Delegate
        to Pattern.get_exp_list() and Exposure.get_exp_list() in the
        contained observations for the exposure details.

        The arguments are essentially ignored since they are determined by
        the contained observations, although a non-zero obs_num can be
        specified as the starting number for contained observations.

        Returns:
            list: A list of exposure dictionaries, each containing exposure metadata
                (aperture, s_region, aper_ra, aper_dec, etc.) and observation parameters.
        """
        exp_list = []
        for c in self.contents:
            sub_list = c.get_exp_list(program_num=self.program_num, obs_num=obs_num)
            exp_list.extend(sub_list)
            obs_num += 1

        return exp_list
