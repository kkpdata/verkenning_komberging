import marimo

__generated_with = "0.23.6"
app = marimo.App(width="medium")


@app.cell
def _():
    import marimo as mo
    return (mo,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # Kombergend volume door overlopen

    versie met probabilistic library van deltares, zie [deze link](https://github.com/Deltares/ProbabilisticLibrary)
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Omgevingswet:
    Artikel 2.0c Besluit kwaliteit leefomgeving
    https://wetten.overheid.nl/jci1.3:c:BWBR0041313&hoofdstuk=2&afdeling=2.1&paragraaf=2.1.1&artikel=2.0c&z=2024-12-21&g=2024-12-21

    Voor dijktrajecten als bedoeld in bijlage II, onder A, geldt de ten hoogste toelaatbare kans per jaar op verlies van waterkerend vermogen waardoor het door het dijktraject beschermde gebied overstroomt op een zodanige wijze en in zodanige mate dat dit leidt tot dodelijke slachtoffers of substantiële economische schade, bedoeld in bijlage II, onder B, kolom 1.

    In de Grondslagen Waterkeringen wordt een praktisch criterium beschreven voor het begrip substantiële economische schade:
    "als de gemiddelde Waterdiepte in minimaal één gebied of buurt met gelijke viercijferige postcode (op basis van de wijk- en buurtkaart van het CBS) groter is dan 0,2 meter, is er sprake van een overstroming. Dit criterium is gebaseerd op de ervaring dat slachtoffers en grootschalige schade pas optreden als de lokale water­dieptes groter zijn dan circa 0,2 meter. Van dit algemene principe kan in specifieke situaties onderbouwd worden afgeweken."
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Grenstoestandfuncties

    Uitgaande van de hierboven genoemde definitie voor substantiële schade, treedt falen op als het volume water dat tijdens een hoogwaterevent over de dijk stroomt ($V_{overlopen}$) groter is dan het volume water voordat substantiële schade optreedt ($V_{komberging}$). In deze situatie is het waarschijnlijk dat er sprake is van overlopen, dat wil zeggen dat de lokale waterstand groter is dan de kruinhoogte. De grenstoestandfunctie wordt als volgt gedefinieerd:

    $$Z = V_{komberging} - V_{overlopen}$$

    We beschouwen het volume per strekkende meter waterkering [m³/m]. Met deze aanpak sluiten we aan op de grenstoestandfunctie van het eroderen van de toplaag. Gebruikelijk is het om de lengte van de dijkvakken aan te laten sluiten bij de onderlinge afstand van de uitvoerlocaties.
    De formule voor het overstromend debiet per strekkende meter waterkering is:

    $$q = 0.6 \sqrt{g \Delta h^3}$$

    met:

    * $q$: overlopend debiet per strekkende meter waterkering [m²/s]
    * $g$: zwaartekrachtversnelling [m/s²]
    * $\Delta h$: hoogteverschil tussen de lokale waterstand en de kruin (positief) [m]

    Het volume water dat over de kering stroomt is afhankelijk van het hoogteverschil als functie van tijd $\Delta h(t)$ en de duur dat het water over de kering stroomt. Het waterstandsverloop is trapeziumvormig aangenomen met een gelijke stijg- en daalsnelheid $s$ en duur van de top $t_{top}$. De duur $t_{overlopen}$ dat het water over de kering stroomt is daarmee een functie van $\Delta h$. Door substitutie en integratie over de tijdsduur van overlopend water wordt het volume berekend.

    $$V_{overlopen} = \int_{t = 0}^{t_{overlopen}} q(t)\,dt$$

    ## Stochasten

    De volgende stochasten zijn relevant

    * $V_{komberging}$: het volume per strekkende meter waterkering dat net geborgen kan worden voordat sprake is van substantiële economische schade [m³/m]
    * $h$: buitenwaterstand [m+NAP]
    * $\Delta h_{kruin}$: de onzekerheid in de kruinhoogte over ca. 100 m
    * $s$: stijgsnelheid van het water [m/uur]
    * $t_{top}$: duur van de top van de waterstand [uur]

    Daarnaast is de variabele $h_{kruin}$ van belang. Dit is veelal de minimale maximale kruinhoogte van het vak. Deze waarde wordt ook gebruikt in de beoordeling om de zwakste plek in het vak te schematiseren.

    In het geval van overlopen over een waterkering neemt het overstroomde debiet sterk toe bij een stijgende buitenwaterstand. Hierdoor kan het lastig zijn om convergentie te bereiken in een probabilistische berekening. Een alternatieve methode is om de conditionele kans uit te rekenen gegeven een waterstandsverschil over de kruinhoogte. Deze methode wordt uitgewerkt in deze notebook.
    """)
    return


@app.cell
def _():
    from probabilistic_library import (
        DistributionType,
        FragilityCurve,
        FragilityValue,
        ReliabilityMethod,
        ReliabilityProject,
        Stochast,
    )
    import math
    import numpy as np
    import matplotlib.pyplot as plt
    import pandas as pd
    return (
        DistributionType,
        FragilityCurve,
        FragilityValue,
        ReliabilityMethod,
        ReliabilityProject,
        Stochast,
        math,
        np,
        pd,
        plt,
    )


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Functies

    We definiëren de functies voor het overloop debiet, het waterstandsverloop en het instromend volume.

    ### Overlopend debiet
    """)
    return


@app.cell
def _(math):
    def overstromend_debiet(g: float, dh: float) -> float:
        """
        Bereken het overstromend debiet per strekkende meter dijk in m3/s/m.

        Parameters:
        g (float): Gravitatieversnelling in m/s^2.
        dh (float): Hoogteverschil tussen de waterstand en kruinhoogte.

        Returns:
        float: Overstromend debiet per strekkende meter in m3/s/m.
        """
        if dh <= 0:
            return 0.0
        return 0.6 * math.sqrt(g * math.pow(dh, 3))

    return (overstromend_debiet,)


@app.cell
def _(np, overstromend_debiet, plt):
    _dh_plot = np.arange(0.00, 0.5, 0.01)
    _debiet_plot = [overstromend_debiet(9.81, dh) for dh in _dh_plot]
    _fig, _ax = plt.subplots(figsize=(10, 6))
    _ax.plot(_dh_plot, _debiet_plot, label="Overloop debiet (m³/s/m)")
    _ax.set_title("Overloop debiet per strekkende meter")
    _ax.set_xlabel("Hoogteverschil ten opzichte van de kruin (m)")
    _ax.set_ylabel("Overloop debiet (m³/s/m)")
    _ax.grid()
    _ax.legend()
    _fig
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Waterstandsverloop

    Het waterstandsverloop wordt geschematiseerd als een trapezium op basis van de variabelen stijgsnelheid $s$,
    maximale waterstand boven de kruin $\Delta h_{max}$ en tijdsduur van de top.
    """)
    return


@app.cell
def _(np):
    def trapezium_dh(
        dh_max: float, stijgsnelheid: float, tijdsduur_top: float, dt: float = 1.0
    ):
        """
        Genereer een trapeziumvormige tijdreeks voor dh.

        Parameters:
        dh_max (float): Maximale waarde van dh (m).
        stijgsnelheid (float): Stijgsnelheid van de op- en aflopende flank (m/s).
        tijdsduur_top (float): Duur van het plateau (seconden).
        dt (float): Tijdstap (seconden).

        Returns:
        tuple: (times, dh) arrays
        """
        t_flank = dh_max / stijgsnelheid
        t_total = 2 * t_flank + tijdsduur_top
        times = np.arange(0, t_total + dt, dt)
        dh = np.zeros_like(times)
        for i, t in enumerate(times):
            if t < t_flank:
                dh[i] = stijgsnelheid * t
            elif t < t_flank + tijdsduur_top:
                dh[i] = dh_max
            elif t <= t_total:
                dh[i] = dh_max - stijgsnelheid * (t - t_flank - tijdsduur_top)
            else:
                dh[i] = 0.0
        dh = np.clip(dh, 0, dh_max)
        return times, dh

    return (trapezium_dh,)


@app.cell
def _(np, overstromend_debiet):
    def totaal_volume(times, dh, g: float = 9.81) -> float:
        """
        Bereken het totale volume water dat over de dijk stroomt, gegeven een waterstandverloop.

        Parameters:
        times (array): Tijdreeks (seconden).
        dh (array): Hoogteverschillen (m).
        g (float): Gravitatieversnelling (m/s^2).

        Returns:
        float: Totaal volume (m3 per strekkende meter dijk).
        """
        q = np.array([overstromend_debiet(g, h) for h in dh])
        return float(np.trapezoid(q, times))

    return (totaal_volume,)


@app.cell
def _(np, overstromend_debiet, trapezium_dh):
    def volume_trapezium_overloop(
        dh_max: float,
        stijgsnelheid: float,
        breedte_top: float,
        dt: float = 1.0,
        g: float = 9.81,
    ) -> float:
        """
        Combineer het genereren van een trapeziumvormige dh-tijdreeks en het berekenen van het totale volume.

        Parameters:
        dh_max (float): Maximale waarde van dh (m).
        stijgsnelheid (float): Stijgsnelheid van de op- en aflopende flank (m/s).
        breedte_top (float): Duur van het plateau (seconden).
        dt (float): Tijdstap (seconden).
        g (float): Gravitatieversnelling (m/s^2).

        Returns:
        float: Totaal volume (m3 per strekkende meter dijk).
        """
        times, dh = trapezium_dh(dh_max, stijgsnelheid, breedte_top, dt)
        q = np.array([overstromend_debiet(g, h) for h in dh])
        return float(np.trapezoid(q, times))

    return (volume_trapezium_overloop,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Model grenstoestandfunctie komberging

    De volgende grenstoestandfunctie wordt gedefinieerd:
    """)
    return


@app.cell
def _(volume_trapezium_overloop):
    def z_komberging(
        v_kom: float,
        stijgsnelheid: float,
        breedte_top: float,
        dh_max: float,
    ) -> float:
        volume_in = volume_trapezium_overloop(dh_max, stijgsnelheid, breedte_top, dt=10.0)
        return v_kom - volume_in

    return (z_komberging,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Case benedenrivierengebied: waterstandsverloop Krimpen aan de Lek

    Het waterstandsverloop ter hoogte van Krimpen aan de Lek is als volgt:

    /nog toevoegen
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Interactief waterstandsverloop

    Verken het effect van de parameters op het waterstandsverloop en het instromende volume.
    """)
    return


@app.cell
def _(mo):
    slider_dh_max = mo.ui.slider(
        0.01, 0.50, value=0.10, step=0.01,
        label="Maximale waterstand boven de kruin — dh_max (m)",
    )
    slider_stijg = mo.ui.slider(
        0.01, 0.30, value=0.04, step=0.01,
        label="Stijgsnelheid — s (m/uur)",
    )
    slider_top = mo.ui.slider(
        0.5, 6.0, value=2.0, step=0.5,
        label="Duur van de top — t_top (uur)",
    )
    mo.vstack([slider_dh_max, slider_stijg, slider_top])
    return slider_dh_max, slider_stijg, slider_top


@app.cell
def _(mo, np, plt, slider_dh_max, slider_stijg, slider_top, totaal_volume, trapezium_dh):
    _dh_max_val = slider_dh_max.value
    _stijg_val = slider_stijg.value / 3600  # m/uur -> m/s
    _top_val = slider_top.value * 3600      # uren  -> seconden
    _times, _dh = trapezium_dh(_dh_max_val, _stijg_val, _top_val, dt=10.0)
    _vol = totaal_volume(_times, _dh)

    _fig, _ax = plt.subplots(figsize=(10, 5))
    _ax.plot(_times / 3600, _dh, color="steelblue", label="dh")
    _ax.set_xlabel("Tijd (uren)")
    _ax.set_ylabel("Hoogteverschil (m)")
    _ax.set_title("Trapeziumvormig waterstandsverloop")
    _ax.grid()
    _ax.legend()

    mo.vstack([
        _fig,
        mo.callout(mo.md(f"**Totaal instromend volume: {_vol:.2f} m³/m**"), kind="info"),
    ])
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Model en invoer (probabilistisch)

    Stel hieronder de stochastische parameters in. De verdelingen worden direct bijgewerkt.
    """)
    return


@app.cell
def _(mo):
    num_v_kom_mean = mo.ui.number(
        value=1000.0, start=100.0, stop=5000.0, step=50.0,
        label="v_kom gemiddelde (m³/m)",
    )
    slider_v_kom_vk = mo.ui.slider(
        0.05, 0.5, value=0.1, step=0.05,
        label="v_kom variatiecoëfficiënt",
    )
    slider_stijg_mean = mo.ui.slider(
        0.01, 0.30, value=0.12, step=0.01,
        label="Stijgsnelheid gemiddelde (m/uur)",
    )
    slider_stijg_vk = mo.ui.slider(
        0.05, 0.5, value=0.2, step=0.05,
        label="Stijgsnelheid variatiecoëfficiënt",
    )
    slider_top_mean = mo.ui.slider(
        0.5, 4.0, value=1.0, step=0.25,
        label="Duur top gemiddelde (uur)",
    )
    slider_top_vk = mo.ui.slider(
        0.05, 0.5, value=0.2, step=0.05,
        label="Duur top variatiecoëfficiënt",
    )
    mo.vstack([
        mo.hstack([
            mo.vstack([mo.md("**Kombergend volume**"), num_v_kom_mean, slider_v_kom_vk]),
            mo.vstack([mo.md("**Stijgsnelheid**"), slider_stijg_mean, slider_stijg_vk]),
            mo.vstack([mo.md("**Duur van de top**"), slider_top_mean, slider_top_vk]),
        ], justify="start"),
    ])
    return (
        num_v_kom_mean,
        slider_stijg_mean,
        slider_stijg_vk,
        slider_top_mean,
        slider_top_vk,
        slider_v_kom_vk,
    )


@app.cell
def _(
    DistributionType,
    ReliabilityMethod,
    ReliabilityProject,
    num_v_kom_mean,
    slider_stijg_mean,
    slider_stijg_vk,
    slider_top_mean,
    slider_top_vk,
    slider_v_kom_vk,
    z_komberging,
):
    project = ReliabilityProject()
    project.model = z_komberging

    project.variables["v_kom"].distribution = DistributionType.log_normal
    project.variables["v_kom"].mean = num_v_kom_mean.value
    project.variables["v_kom"].deviation = num_v_kom_mean.value * slider_v_kom_vk.value

    project.variables["stijgsnelheid"].distribution = DistributionType.log_normal
    project.variables["stijgsnelheid"].mean = slider_stijg_mean.value / 3600
    project.variables["stijgsnelheid"].deviation = slider_stijg_mean.value / 3600 * slider_stijg_vk.value

    project.variables["breedte_top"].distribution = DistributionType.log_normal
    project.variables["breedte_top"].mean = slider_top_mean.value * 3600
    project.variables["breedte_top"].deviation = slider_top_mean.value * 3600 * slider_top_vk.value

    project.settings.reliability_method = ReliabilityMethod.form
    project.settings.relaxation_factor = 0.15
    project.settings.maximum_iterations = 100
    project.settings.variation_coefficient = 0.01

    return (project,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""### Verdelingen van de stochasten""")
    return


@app.cell
def _(Stochast, mo, np, plt, project):
    _figs = []
    for _var in ["v_kom", "stijgsnelheid", "breedte_top"]:
        _s = Stochast()
        _s.name = _var
        _s.distribution = project.variables[_var].distribution
        _s.mean = project.variables[_var].mean
        _s.deviation = project.variables[_var].deviation
        _val_grid = np.linspace(_s.get_quantile(0.001), _s.get_quantile(0.999), 100)
        _pdf = [_s.get_pdf(v) for v in _val_grid]
        _cdf = [_s.get_cdf(v) for v in _val_grid]

        _fig, _ax1 = plt.subplots()
        _ax1.set_xlabel("waarde")
        _ax1.set_ylabel("pdf", color="tab:blue")
        _ax1.plot(_val_grid, _pdf, color="tab:blue")
        _ax1.tick_params(axis="y", labelcolor="tab:blue")
        _ax2 = _ax1.twinx()
        _ax2.set_ylabel("cdf", color="tab:red")
        _ax2.plot(_val_grid, _cdf, "r--")
        _ax2.tick_params(axis="y", labelcolor="tab:red")
        _ax1.set_title(f"Verdeling van {_var}")
        _figs.append(_fig)

    mo.hstack(_figs)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Fragility curve maken

    De fragility curve geeft de conditionele kans op falen als functie van $\Delta h_{max}$.
    Klik op de knop om de berekening te starten (FORM per stap, kan even duren).
    """)
    return


@app.cell
def _(mo):
    run_fragility = mo.ui.run_button(label="Bereken fragility curve")
    run_fragility
    return (run_fragility,)


@app.cell
def _(
    DistributionType,
    FragilityCurve,
    FragilityValue,
    mo,
    np,
    pd,
    plt,
    project,
    run_fragility,
):
    mo.stop(
        not run_fragility.value,
        mo.callout(
            mo.md("Klik op **Bereken fragility curve** om de berekening te starten."),
            kind="warn",
        ),
    )

    fragility_curve = FragilityCurve()
    fragility_curve.name = "Conditioneel op dh_max"

    _fc_pf = []
    _dh_max_arr = np.arange(0.00, 0.3, 0.01)
    _loop_data = []

    for _dh in _dh_max_arr:
        project.variables["dh_max"].distribution = DistributionType.deterministic
        project.variables["dh_max"].mean = _dh
        project.run()
        _dp = project.design_point

        _value = FragilityValue()
        _value.x = _dh
        _value.reliability_index = _dp.reliability_index
        _value.design_point = _dp
        fragility_curve.fragility_values.append(_value)
        _fc_pf.append(_dp.probability_failure)

        _row = {
            "dh (m)": _dh,
            "converged": _dp.is_converged,
            "reliability_index": _dp.reliability_index,
            "probability_failure": _dp.probability_failure,
        }
        for _alpha in _dp.alphas:
            _row[f"{_alpha.variable.name}_alpha"] = _alpha.alpha
            _row[f"{_alpha.variable.name}_dp"] = _alpha.x
        _loop_data.append(_row)

    df_loop_results = pd.DataFrame(_loop_data)

    _fig, _ax = plt.subplots(figsize=(10, 6))
    _ax.plot(_dh_max_arr, _fc_pf, "o--", color="steelblue")
    _ax.grid()
    _ax.set_xlabel("dh_max: hoogteverschil ten opzichte van de kruin (m)")
    _ax.set_ylabel("P(Z<0 | dh_max)")
    _ax.set_title("Fragility curve — conditioneel op dh_max")

    mo.vstack([
        _fig,
        mo.ui.table(df_loop_results),
    ])
    return df_loop_results, fragility_curve


if __name__ == "__main__":
    app.run()
