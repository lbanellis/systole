# Author: Nicolas Legrand <nicolas.legrand@cfin.au.dk>

import itertools
from typing import Dict, List, Optional, Tuple, Union

import numpy as np
import pandas as pd
import seaborn as sns
from matplotlib.axes import Axes

from systole.plots.utils import get_plotting_function


def plot_events(
    triggers: Optional[Union[List, np.ndarray]] = None,
    triggers_idx: Optional[Union[List, np.ndarray]] = None,
    events_labels: Dict[str, str] = {"1": "Event - 1"},
    tmin: float = -1.0,
    tmax: float = 10.0,
    sfreq: int = 1000,
    behavior: Optional[Union[List, pd.DataFrame]] = None,
    figsize: Optional[Union[int, List[int], Tuple[int, int]]] = None,
    ax: Optional[Axes] = None,
    backend: str = "matplotlib",
) -> Axes:
    """Plot events occurence across recording.

    Parameters
    ----------
    triggers : list or np.ndarray
        The events triggers. `0` indicates no events, `1` indicates the triger
        for one event. Different conditions should be provided separately as list
        of arrays.
    triggers_idx : list or np.ndarray
        Trigger indexes. Each value encode the sample where an event occured (see
        also `sfreq`). Different conditions should be provided separately as list of
        arrays (can have different lenght).
    events_labels : dict
        The events label. The key of the dictionary is the condition number (from 1 to
        n, as `str`), the value is the label (`str`). Default set to
        `{"1": "Event - 1"}`.
    tmin, tmax : float
        Start and end time of the epochs in seconds, relative to the time-locked event.
        Defaults to -1.0 and 10.0, respectively.
    sfreq : int
        Signal sampling frequency. Default is set to 1000 Hz.
    behavior : list or pd.DataFrame
        Additional information about trials that should appear when hovering on the
        trial (`bokeh` version only). A py:class:`pd.DataFrame` instance with length =
        n trials, or a list of py:class:`pd.DataFrame` (for multiple conditions) should
        be provided.
    figsize : tuple
        Figure size. Default is `(13, 5)`.
    ax : :class:`matplotlib.axes.Axes` or None
        Where to draw the plot. Default is *None* (create a new figure).
    backend: str
        Select plotting backend {"matplotlib", "bokeh"}. Defaults to
        "matplotlib".

    Returns
    -------
    plot : :class:`matplotlib.axes.Axes` or :class:`bokeh.plotting.figure.Figure`
        The matplotlib axes, or the boken figure containing the plot.

    See also
    --------
    plot_rr, plot_subspaces, plot_events, plot_psd, plot_oximeter, plot_raw

    Examples
    --------

    """

    palette = itertools.cycle(sns.color_palette("deep", as_cmap=True))

    if figsize is None:
        if backend == "matplotlib":
            figsize = (13, 5)
        elif backend == "bokeh":
            figsize = 300

    if triggers_idx is None:
        if triggers is None:
            raise ValueError("No triggers provided")
        else:
            if isinstance(triggers, np.ndarray):
                triggers = [triggers]
            triggers_idx = []
            for this_triggers in triggers:
                triggers_idx.append(np.where(this_triggers)[0])

    # Creating the events info df
    # DataFrame : (tmin, trigger, tmax, label, color, df)
    df = pd.DataFrame([])

    # Loop across conditions
    for i, this_trigger_idx in enumerate(triggers_idx):

        # Event color
        col = next(palette)

        # Loop across triggers
        for event in this_trigger_idx:
            this_tmin = (event / sfreq) + tmin
            this_trigger = event / sfreq
            this_tmax = (event / sfreq) + tmax
            df = df.append(
                pd.DataFrame(
                    {
                        "tmin": this_tmin,
                        "trigger": this_trigger,
                        "tmax": this_tmax,
                        "label": events_labels[str(i + 1)],
                        "color": [col],
                    }
                ),
                ignore_index=True,
            )

            # Add behaviors results when provided

    df["tmin"] = pd.to_datetime(df["tmin"], unit="s", origin="unix")
    df["trigger"] = pd.to_datetime(df["trigger"], unit="s", origin="unix")
    df["tmax"] = pd.to_datetime(df["tmax"], unit="s", origin="unix")

    plot_raw_args = {
        "df": df,
        "figsize": figsize,
        "ax": ax,
    }

    plotting_function = get_plotting_function("plot_events", "plot_events", backend)
    plot = plotting_function(**plot_raw_args)

    return plot
