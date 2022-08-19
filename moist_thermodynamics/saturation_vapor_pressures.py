# -*- coding: utf-8 -*-
"""
Provides a collection of fits for saturation and sublimation vapor pressure

Author: Bjorn Stevens (bjorn.stevens@mpimet.mpg.de)
copygright, bjorn stevens Max Planck Institute for Meteorology, Hamburg

License: BSD-3C
"""
#
from . import constants
import numpy as np


def liq_wagner_pruss(T):
    """Returns saturation vapor pressure (Pa) over planer liquid water

    Encodes the empirical fits of Wagner and Pruss (2002), Eq 2.5a (page 399). Their formulation
    is compared to other fits in the example scripts used in this package, and deemed to be the
    best reference.

    The fit has been verified for TvT <= T < = TvC.  For super cooled water (T<TvT) it deviates
    from the results of Murphy and Koop where were developed for super-cooled water.  It is about
    10% larger at 200 K, 25 % larter at 150 K, and then decreases again so it is 12% smaller at
    the limit (123K) of the Murphy and Koop fit.  For accurate fits for super-cooled water the
    function of Murphy and Koop should be used.

    Args:
        T: temperature in kelvin

    Reference:
        W. Wagner and A. Pruß , "The IAPWS Formulation 1995 for the Thermodynamic Properties
    of Ordinary Water Substance for General and Scientific Use", Journal of Physical and Chemical
    Reference Data 31, 387-535 (2002) https://doi.org/10.1063/1.1461829

    >>> liq_wagner_pruss(np.asarray([273.16,305.]))
    array([ 611.65706974, 4719.32683147])
    """
    TvC = constants.temperature_water_vapor_critical_point
    PvC = constants.pressure_water_vapor_critical_point

    vt = 1.0 - T / TvC
    es = PvC * np.exp(
        TvC
        / T
        * (
            -7.85951783 * vt
            + 1.84408259 * vt**1.5
            - 11.7866497 * vt**3
            + 22.6807411 * vt**3.5
            - 15.9618719 * vt**4
            + 1.80122502 * vt**7.5
        )
    )
    return es


def ice_wagner_etal(T):
    """Returns sublimation vapor pressure (Pa) over simple (Ih) ice

    Encodes the emperical fits of Wagner et al., (2011) which also define the IAPWS standard for
    sublimation vapor pressure over ice-Ih

    Args:
        T: temperature in kelvin

    Reference:
        Wagner, W., Riethmann, T., Feistel, R. & Harvey, A. H. New Equations for the Sublimation
        Pressure and Melting Pressure of H 2 O Ice Ih. Journal of Physical and Chemical Reference
        Data 40, 043103 (2011).


    >>> ice_wagner_etal(np.asarray([273.16,260.]))
    array([611.655     , 195.80103377])
    """
    TvT = constants.temperature_water_vapor_triple_point
    PvT = constants.pressure_water_vapor_triple_point

    a1 = -0.212144006e2
    a2 = 0.273203819e2
    a3 = -0.610598130e1
    b1 = 0.333333333e-2
    b2 = 0.120666667e1
    b3 = 0.170333333e1
    theta = T / TvT
    es = PvT * np.exp((a1 * theta**b1 + a2 * theta**b2 + a3 * theta**b3) / theta)
    return es


def liq_murphy_koop(T):
    """Returns saturation vapor pressure (Pa) over liquid water

    Encodes the empirical fit (Eq. 10) of Murphy and Koop (2011) which improves on the Wagner and
    Pruß fits for supercooled conditions.

    The fit has been verified for 123K <= T < = 332 K

    Args:
        T: temperature in kelvin

    Reference:
        Murphy, D. M. & Koop, T. Review of the vapour pressures of ice and supercooled water for
        atmospheric applications. Q. J. R. Meteorol. Soc. 131, 1539–1565 (2005).

    >>> liq_murphy_koop(np.asarray([273.16,140.]))
    array([6.11657044e+02, 9.39696372e-07])
    """

    X = np.tanh(0.0415 * (T - 218.8)) * (
        53.878 - 1331.22 / T - 9.44523 * np.log(T) + 0.014025 * T
    )
    return np.exp(54.842763 - 6763.22 / T - 4.210 * np.log(T) + 0.000367 * T + X)


def liq_hardy(T):
    """Returns satruation vapor pressure (Pa) over liquid water

    Encodes the empirical fit (Eq. 10) of Hardy (1998) which is often used in the postprocessing
    of radiosondes

    Args:
        T: temperature in kelvin

    Reference:
        Hardy, B., 1998, ITS-90 Formulations for Vapor Pressure, Frostpoint Temperature, Dewpoint
        Temperature, and Enhancement Factors in the Range –100 to +100 °C, The Proceedings of the
        Third International Symposium on Humidity & Moisture, London, England

    >>> liq_hardy(np.asarray([273.16,260.]))
    array([611.65715494, 222.65143353])
    """
    X = (
        -2.8365744e3 / (T * T)
        - 6.028076559e3 / T
        + 19.54263612
        - 2.737830188e-2 * T
        + 1.6261698e-5 * T**2
        + 7.0229056e-10 * T**3
        - 1.8680009e-13 * T**4
        + 2.7150305 * np.log(T)
    )
    return np.exp(X)


def analytic(T, lx, cx):
    """returns saturation vapor pressure over a given phase

    Uses the rankine (constant specific heat, negligible condensate volume) approximations to
    calculate the saturation vapor pressure over a phase with the specific heat cx, and phase
    change enthalpy (from vapor) lx, at temperature T.

    Args:
        T: temperature in kelvin
        lx: phase change enthalpy between vapor and given phase (liquid, ice)
        cx: specific heat capacity of given phase (liquid, ice)

    Returns:
        value of saturation vapor pressure over liquid water in Pa

    Reference:
        Romps, D. M. Exact Expression for the Lifting Condensation Level. Journal of the Atmospheric
        Sciences 74, 3891–3900 (2017).
        Romps, D. M. Accurate expressions for the dew point and frost point derived from the Rankine-
        Kirchhoff approximations. Journal of the Atmospheric Sciences (2021) doi:10.1175/JAS-D-20-0301.1.

    >>> analytic(305.,constants.lvT,constants.cl)
    4711.131611687174
    """
    TvT = constants.temperature_water_vapor_triple_point
    PvT = constants.pressure_water_vapor_triple_point
    Rv = constants.water_vapor_gas_constant

    c1 = (constants.cpv - cx) / Rv
    c2 = lx / (Rv * TvT) - c1
    es = PvT * np.exp(c2 * (1.0 - TvT / T)) * (T / TvT) ** c1
    return es


def liq_analytic(T, lx=constants.lvT, cx=constants.cl):
    """Analytic approximation for saturation vapor pressure over iquid

    Uses the rankine (constant specific heat, negligible condensate volume) approximations to
    calculate the saturation vapor pressure over liquid.  The procedure is described in Eq(4) of
    Romps (2017) and best approximates the actual value for specific heats that differ slightly
    from the best estimates of these quantities which are provided as default quantities.
    Romps recommends cl = 4119 J/kg/K, and cpv = 1861 J/kg/K.

    Args:
        T: temperature in kelvin
        lx: enthalpy of vaporization, at triple point, default constants.lvT
        cl: specific heat capacity of liquid at triple point

    Returns:
        value of saturation vapor pressure over liquid water in Pa

    Reference:
        Romps, D. M. Exact Expression for the Lifting Condensation Level. Journal of the Atmospheric
        Sciences 74, 3891–3900 (2017).
        Romps, D. M. Accurate expressions for the dew point and frost point derived from the Rankine-
        Kirchhoff approximations. Journal of the Atmospheric Sciences (2021) doi:10.1175/JAS-D-20-0301.1.

    >>> liq_analytic(np.asarray([273.16,305.]))
    array([ 611.655     , 4711.13161169])
    """
    return analytic(T, lx, cx)


def ice_analytic(T, lx=constants.lsT, cx=constants.ci):
    """Analytic approximation for saturation vapor pressure over ice

    Uses the rankine (constant specific heat, negligible condensate volume) approximations to
    calculate the saturation vapor pressure over ice.  The procedure is described in Eq(4) of
    Romps (2017) and best approximates the actual value for specific heats that differ slightly
    from the best estimates of these quantities which are provided as default quantities.
    Romps recommends ci = 1861 J/kg/K, and cpv = 1879 J/kg/K.

    Args:
        T: temperature in kelvin
        lx: enthalpy of sublimation, at triple point, default constants.lsT
        ci: specific heat capacity of ice Ih, at triple point

    Returns:
        value of saturation vapor pressure over ice in Pa

    Reference:
        Romps, D. M. Exact Expression for the Lifting Condensation Level. Journal of the Atmospheric
        Sciences 74, 3891–3900 (2017).
        Romps, D. M. Accurate expressions for the dew point and frost point derived from the Rankine-
        Kirchhoff approximations. Journal of the Atmospheric Sciences (2021) doi:10.1175/JAS-D-20-0301.1.


    >>> ice_analytic(np.asarray([273.16,260.]))
    array([611.655     , 195.99959431])
    """
    return analytic(T, lx, cx)


def tetens(T, a, b):
    """Returns saturation vapor pressure over liquid using the Magnus-Teten's formula

    This equation is written in a general form, with the constants a and b determining the fit.  As
    such it can be specified for either ice or water, or adapted as originally impelemented in ICON,
    in which case PvT and TvT need to be substituted by Pv0 and T0.

    Args:
        T: temperature in kelvin

    >>> tetens(285.,17.269,35.86)
    1389.7114123472836
    """

    es = constants.PvT * np.exp(a * (T - constants.TvT) / (T - b))
    return es


def liq_tetens(T):
    """Returns saturation vapor pressure over liquid using the Magnus-Teten's formula

    This equation is what is used in the ICON code, hence its inclusion in this library.  The original
    ICON implementation followed Murray's choice of constants (T0=273.15, Pv0=610.78, a=17.269, b=35.86).
    This implementation is referenced to the triple point values of temperature and vapor and with
    revised constants (a,b) chosen to better agree with the fits of Wagner and Pruss

    Args:
        T: temperature in kelvin

    Reference:
        Murray, F. W. On the Computation of Saturation Vapor Pressure. Journal of Applied Meteorology
        and Climatology 6, 203–204 (1967).

    >>> liq_tetens(np.asarray([273.16,305.]))
    array([ 611.655     , 4719.73680592])
    """
    a = 17.41463775
    b = 33.6393413

    return tetens(T, a, b)


def ice_tetens(T):
    """Returns saturation vapor pressure over liquid using the Magnus-Teten's formula

    This equation is what is used in the ICON code, hence its inclusion in this library.  The original
    ICON implementation followed Murray's choice of constants (T0=273.15, Pv0=610.78, a=21.875, b=7.66).
    This implementation is referenced to the triple point values of temperature and vapor and with
    revised constants (a,b) chosen to better agree with the fits of Wagner and Pruss

    Args:
        T: temperature in kelvin

    Reference:
        Murray, F. W. On the Computation of Saturation Vapor Pressure. Journal of Applied Meteorology
        and Climatology 6, 203–204 (1967).

    >>> ice_tetens(np.asarray([273.16,260.]))
    array([611.655     , 196.10072658])
    """
    a = 22.0419977
    b = 5.0

    return tetens(T, a, b)