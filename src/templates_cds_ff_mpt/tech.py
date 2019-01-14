# -*- coding: utf-8 -*-

from typing import Tuple

from bag.layout.tech import TechInfo
from bag.layout.template import TemplateBase

from pybag.core import BBox
from pybag.enum import Direction

from . import config as _config
from . import config_fname as _config_fname
from .mos.base import MOSTechCDSFFMPT


class TechInfoCDSFFMPT(TechInfo):
    def __init__(self, process_params):
        TechInfo.__init__(self, process_params, _config, _config_fname)

        process_params['layout']['mos_tech_class'] = MOSTechCDSFFMPT(_config, self)
        process_params['layout']['laygo_tech_class'] = None
        process_params['layout']['res_tech_class'] = None

    # noinspection PyUnusedLocal,PyMethodMayBeStatic
    def _get_metal_idc_factor(self, layer: str, purpose: str, w: int, length: int):
        return 1

    def _get_metal_idc(self, layer: str, purpose: str, w: int, length: int,
                       vertical: bool, dc_temp: int) -> float:
        if vertical:
            raise NotImplementedError('Vertical DC current not supported yet')

        inorm, woff = 1.0, 0.0
        idc = inorm * self._get_metal_idc_factor(layer, purpose, w, length) * (w - woff)
        return self.get_idc_scale_factor(layer, purpose, self.get_dc_temp(dc_temp)) * idc * 1e-3

    # noinspection PyUnusedLocal
    def _get_metal_irms(self, layer: str, purpose: str, w: int, rms_dt: int):
        b = 0.0443
        k, wo, a = 6.0, 0.0, 0.2

        irms_ma = (k * self.get_rms_dt(rms_dt) * (w - wo)**2 * (w - wo + a) / (w - wo + b))**0.5
        return irms_ma * 1e-3

    # noinspection PyUnusedLocal
    def _get_via_idc(self, bot_lp: Tuple[str, str], top_lp: Tuple[str, str], cut_w: int,
                     cut_h: int, bot_dim: Tuple[int, int], top_dim: Tuple[int, int],
                     array: bool, dc_temp: int) -> float:
        if bot_dim[0] > 0:
            bf = self._get_metal_idc_factor(bot_lp[0], bot_lp[1], bot_dim[0], bot_dim[1])
        else:
            bf = 1.0

        if top_dim[0] > 0:
            tf = self._get_metal_idc_factor(top_lp[0], top_lp[1], top_dim[0], top_dim[1])
        else:
            tf = 1.0

        factor = min(bf, tf)
        via_id = self.config['via_id'][(bot_lp, top_lp)]

        if via_id in ('M1_LiPo', 'M1_LiAct', 'M2_M1', 'M3_M2', 'M4_M3'):
            if cut_w == cut_h == 32:
                idc = 0.1
            elif cut_w != cut_h:
                idc = 0.2
            else:
                # we do not support 2X square via, as it has large
                # spacing rule to square/rectangle vias.
                raise ValueError('Unsupported via w/h: ({},{})'.format(cut_w, cut_h))
        else:
            idc = 0.4

        temp = self.get_dc_temp(dc_temp)
        return factor * self.get_idc_scale_factor(bot_lp[0], bot_lp[1], temp) * idc * 1e-3

    def add_cell_boundary(self, template: TemplateBase, box: BBox) -> None:
        pass

    def draw_device_blockage(self, template: TemplateBase) -> None:
        pass

    def get_metal_em_specs(self, layer: str, purpose: str, w: int, length: int = -1,
                           vertical: bool = False, dc_temp: int = -1000, rms_dt: int = -1000
                           ) -> Tuple[float, float, float]:
        idc = self._get_metal_idc(layer, purpose, w, length, vertical, dc_temp)
        irms = self._get_metal_irms(layer, purpose, w, rms_dt)
        ipeak = float('inf')
        return idc, irms, ipeak

    def get_via_em_specs(self, layer_dir: Direction, layer: str, purpose: str, adj_layer: str,
                         adj_purpose: str, cut_w: int, cut_h: int, m_w: int = -1, m_l: int = -1,
                         adj_m_w: int = -1, adj_m_l: int = -1, array: bool = False,
                         dc_temp: int = -1000, rms_dt: int = -1000) -> Tuple[float, float, float]:
        lay_vec = [None, None]
        dim_vec = [None, None]

        didx = layer_dir.value
        lay_vec[didx] = (layer, purpose)
        lay_vec[1 - didx] = (adj_layer, adj_purpose)
        dim_vec[didx] = (m_w, m_l)
        dim_vec[1 - didx] = (adj_m_w, adj_m_l)

        idc = self._get_via_idc(lay_vec[0], lay_vec[1], cut_w, cut_h, dim_vec[0], dim_vec[1],
                                array, dc_temp)
        # via do not have AC current specs
        irms = float('inf')
        ipeak = float('inf')
        return idc, irms, ipeak

    def get_res_em_specs(self, res_type: str, w: int, *, length: int = -1,
                         dc_temp: int = -1000, rms_dt: int = -1000) -> Tuple[float, float, float]:
        dc_temp = self.get_dc_temp(dc_temp)
        rms_dt = self.get_rms_dt(rms_dt)

        idc_scale = self.get_idc_scale_factor('', '', dc_temp, is_res=True)
        idc = 1.0e-3 * w * idc_scale

        irms = 1e-3 * (0.02 * rms_dt * w * (w + 0.5)) ** 0.5

        ipeak = 5e-3 * 2 * w
        return idc, irms, ipeak
