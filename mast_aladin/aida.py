from astropy.coordinates import SkyCoord, Angle
import astropy.units as u
import warnings
from enum import StrEnum

__all__ = ['AIDA']


class AIDA_aspects(StrEnum):
    CENTER = "center"
    FOV = "fov"
    ROTATION = "rotation"
    IMAGE_LABEL = "image_label"
    PROJECTION = "projection"


class AIDA:
    """
    Mixin class based on the Astro Image Display API (AIDA) [1]_.

    References
    ----------
    .. [1] https://github.com/astropy/astro-image-display-api/

    """
    def _set_center(self, center=None):
        if center is None:
            return

        if not isinstance(center, SkyCoord):
            raise TypeError(
                f"`center` must be a SkyCoord object. Received {center=}"
            )

        self.target = center

    def _set_fov(self, fov=None):
        if fov is None:
            return

        if isinstance(fov, (float, int)):
            fov = fov * u.deg

        elif not isinstance(fov, (u.Quantity, Angle)):
            raise ValueError(
                f"`fov` must be an `~astropy.coordinates.Angle` or float. Received {fov=}"
            )

        # Determine the scale factor by which we want to adjust setting the
        # ipyaladin horizontal fov
        scale_factor = fov / min(self.fov_xy)
        self.fov = self.fov * scale_factor

    def _set_rotation(self, rotation=None):
        if rotation is None:
            return

        if not isinstance(rotation, (u.Quantity, Angle, float)):
            raise TypeError(
                f"`rotation` must be an `~astropy.coordinates.Angle` or float. Received {rotation=}"
            )

        if isinstance(rotation, (u.Quantity, Angle)):
            rotation = rotation.to_value(u.deg)

        self.rotation = rotation

    def _set_projection(self, projection=None):
        if projection is None:
            return

        self.projection = projection

    def set_viewport(
        self,
        center=None,
        fov=None,
        rotation=None,
        projection=None,
        image_label=None,
        **kwargs
    ):
        """
        Sets the viewport based on provided parameters.

        Parameters
        ----------
        center : `~astropy.coordinates.SkyCoord`
            Center the viewer on this coordinate.
        fov : `~astropy.coordinates.Angle` or float
            Set the length of the viewport's smaller axis to span `fov`, as an
            `~astropy.coordinates.Angle` or as a float in units of degrees.
        rotation : `~astropy.coordinates.Angle`, float
            Set the angle between "+y" or "up" in the viewport and north in
            degrees east of north (counter-clockwise). It can be set with
            an `~astropy.coordinates.Angle` or floats interpreted
            as angles in units of degrees.
        projection: str, optional
            Set the projection of the viewer.
        image_label : str, optional
            ``image_label`` is a required argument for ``AID`` API compatibility,
            but it is not relevant for HiPS browsers like aladin-lite. If not
            `None`, a warning will be emitted.

        Raises
        ------
        TypeError
            If: center is not provided as SkyCoord; fov is not provided as
            Angle or float; or rotation is not provided as Angle or float.

        Warning
            Image label was passed.
        """

        if image_label is not None:
            warnings.warn(
                "aladin-lite only shows one 'image' per viewer, and does not use "
                "the concept of labels. `image_label` should be set to `None`.",
                UserWarning
            )

        self._set_center(center)
        self._set_fov(fov)
        self._set_rotation(rotation)
        self._set_projection(projection)

    def get_viewport(
        self, sky_or_pixel="sky", image_label=None
    ):
        """
        Gets the viewport center, field of view, and rotation.

        Parameters
        ----------
        sky_or_pixel : str, optional
            If `"sky"` or `None`, the viewport center and field of view will be returned
            in world coordinates. `"pixel"` is not supported for HiPS viewers.
        image_label : str, optional
            `image_label` is a required argument for ``AIDA`` compatibility,
            but it is not relevant for HiPS browsers like aladin-lite. If not
            `None`, an error will be raised.

        Returns
        -------
        dict

            Dictionary containing the following entries:

            * center : `~astropy.coordinates.SkyCoord`
               * Center coordinates of the viewer.
            * fov : `~astropy.coordinates.Angle`
               * Length of the shorter viewport axis.
            * rotation : `~astropy.coordinates.Angle`
               * Angle of the view center to north pole angle in degrees.
            * projection : `str`
               * A string representing the projection of the viewer.
            * image_label : `None`
               * A string representing the label of the image, always `None` for aladin-lite.

        Raises
        ------
        NotImplementedError
            Given `sky_or_pixel` is not "sky" or `None`.
        Warning
            Image label was passed.

        """

        if sky_or_pixel != "sky" and sky_or_pixel is not None:
            raise NotImplementedError(
                "aladin-lite is a HiPS viewer without a concept of pixels."
                "`sky_or_pixel` must be set to 'sky' or `None`"
            )

        if image_label is not None:
            warnings.warn(
                "aladin-lite only shows one 'image' per viewer, and does not use "
                "the concept of labels. `image_label` should be set to `None`.",
                UserWarning
            )

        viewport_state = dict(
            center=self.target,
            fov=min(self.fov_xy),
            rotation=self.rotation,
            projection=self.projection,
            image_label=None
        )

        return viewport_state
