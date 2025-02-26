import pytest
from src.utils.unit_converter import UnitConverter


def test_rpm_to_rpm():
    assert UnitConverter.rpm_to_rpm(1000) == 1000


def test_kw_to_shp():
    assert pytest.approx(UnitConverter.kw_to_shp(100), 0.0001) == 134.102


def test_shp_to_kw():
    assert pytest.approx(UnitConverter.shp_to_kw(100), 0.0001) == 74.57


def test_knm_to_tm():
    assert pytest.approx(UnitConverter.knm_to_tm(100), 0.0001) == 10.1971621


def test_tm_to_knm():
    assert pytest.approx(UnitConverter.tm_to_knm(100), 0.0001) == 980.665


def test_kn_to_t():
    assert pytest.approx(UnitConverter.kn_to_t(100), 0.0001) == 10.1971621


def test_t_to_kn():
    assert pytest.approx(UnitConverter.t_to_kn(100), 0.0001) == 980.665


def test_kwh_to_shph():
    assert pytest.approx(UnitConverter.kwh_to_shph(100),
                         0.0001) == 134.04825737


def test_shph_to_kwh():
    assert pytest.approx(UnitConverter.shph_to_kwh(100), 0.0001) == 74.57
