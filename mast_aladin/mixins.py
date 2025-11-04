from functools import wraps


def delay_until_rendered(function, attr='_wcs'):
    """
    Delay a call on `function` until `attr` updates.
    """

    @wraps(function)
    def wrapper(self, *args, **kwargs):
        """Check if the widget is ready to execute a function.

        Parameters
        ----------
        self : any
            The widget object.
        *args : any
            The arguments of the function.
        **kwargs : any
            The keyword arguments of the function.

        Returns
        -------
        any
            The result of the function if the widget is ready.

        """

        # when the app is first constructed but not shown,
        # the default attr `_wcs`` will be an empty dict,
        # so `rendered` will be False. If `len(attr) > 0`,
        # rendered will be True.
        rendered = bool(min(len(getattr(self, attr)), 1))

        def inner_func(change, rendered=rendered):
            # if the app is not rendered:

            if not rendered:
                # we reach this block on first render. now that
                # the widget is available, unobserve the traitlet, and
                # call the delayed function
                rendered = True

                self.unobserve(inner_func, attr)
                return function(self, *args, **kwargs)

        if not rendered:
            # on construction and before render, observe the traitlet
            self.observe(inner_func, attr)
        else:
            # if already rendered, run the function:
            return function(self, *args, **kwargs)

    return wrapper


class DelayUntilRendered:

    @delay_until_rendered
    def delayed_add_fits(self, *args, **kwargs):
        self.add_fits(*args, **kwargs)

    @delay_until_rendered
    def delayed_add_table(self, *args, **kwargs):
        self.add_table(*args, **kwargs)

    @delay_until_rendered
    def delayed_add_graphic_overlay_from_stcs(self, *args, **kwargs):
        self.add_graphic_overlay_from_stcs(*args, **kwargs)

    @delay_until_rendered
    def delayed_add_graphic_overlay_from_region(self, *args, **kwargs):
        self.add_graphic_overlay_from_region(*args, **kwargs)

    @delay_until_rendered
    def delayed_add_markers(self, *args, **kwargs):
        self.add_markers(*args, **kwargs)

    @delay_until_rendered
    def delayed_add_catalog_from_URL(self, *args, **kwargs):
        self.add_catalog_from_URL(*args, **kwargs)

    @delay_until_rendered
    def delayed_delayed_add_moc(self, *args, **kwargs):
        self.add_moc(*args, **kwargs)
