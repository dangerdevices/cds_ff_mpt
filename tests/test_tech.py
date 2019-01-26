# -*- coding: utf-8 -*-

import pytest

from pybag.enum import Direction

from bag.layout.tech import TechInfo

via_em_data_str = ('layer_dir, layer, purpose, adj_layer, adj_purpose, cut_w, cut_h, '
                   'm_w, m_l, adj_m_w, adj_m_l, array, dc_temp, rms_dt, idc_e, irms_e, ipeak_e')
via_em_data = [
    (Direction.LOWER, 'M1', '', 'M2', '', 32, 32, -1, -1, -1, -1, False, -1000, -1000,
     100e-6, float('inf'), float('inf')),
]


@pytest.mark.parametrize(via_em_data_str, via_em_data)
def test_via_em_specs(tech_info: TechInfo, layer_dir: Direction, layer: str, purpose: str,
                      adj_layer: str, adj_purpose: str, cut_w: int, cut_h: int,
                      m_w: int, m_l: int, adj_m_w: int, adj_m_l: int, array: bool,
                      dc_temp: int, rms_dt: int, idc_e: float, irms_e: float,
                      ipeak_e: float) -> None:
    idc, irms, ipeak = tech_info.get_via_em_specs(layer_dir, layer, purpose, adj_layer, adj_purpose,
                                                  cut_w, cut_h, m_w, m_l, adj_m_w, adj_m_l, array,
                                                  dc_temp, rms_dt)
    assert idc == idc_e
    assert irms == irms_e
    assert ipeak == ipeak_e
