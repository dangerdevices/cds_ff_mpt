# -*- coding: utf-8 -*-

from abs_templates_ec.analog_mos.finfet import MOSTechFinfetBase

from typing import TYPE_CHECKING, Dict, Any, List, Optional

from bag.math import lcm
from bag.layout.util import BBox
from bag.layout.template import TemplateBase

if TYPE_CHECKING:
    from bag.layout.tech import TechInfoConfig


class MOSTechCDSFFMPT(MOSTechFinfetBase):
    tech_constants = dict(
        # space between MD and OD
        md_od_spy=40,
        # space between VIA0
        v0_sp=32,
        # space between VIA1X
        vx_sp=42,
        # minimum PP/NP width.
        imp_wmin=52,
        # minimum M1X area
        mx_area_min=6176,
        # maximum space between metal 1.
        m1_sp_max=1600,
        # space between metal 1 and boundary.
        m1_sp_bnd=800,
        # metal 1 fill minimum length
        m1_fill_lmin=200,
        # metal 1 fill maximum length
        m1_fill_lmax=400,
        # minimum M1X line-end spacing
        mx_spy_min=64,
        # M1 dummy horizontal connection height
        m1_dum_h=40,
        # drain/source M2 vertical spacing
        m2_spy_ds=48,
    )

    def __init__(self, config, tech_info):
        # type: (Dict[str, Any], TechInfoConfig) -> None
        MOSTechFinfetBase.__init__(self, config, tech_info)

    def get_mos_yloc_info(self, lch_unit, w, mos_type, threshold, fg, **kwargs):
        # type: (int, int, str, str, int, **kwargs) -> Dict[str, Any]

        mos_constants = self.get_mos_tech_constants(lch_unit)
        fin_h = mos_constants['fin_h']
        fin_p = mos_constants['mos_pitch']
        od_spy = mos_constants['od_spy']
        mp_cpo_sp = mos_constants['mp_cpo_sp']
        mp_h = mos_constants['mp_h']
        cpo_od_sp = mos_constants['cpo_od_sp']
        cpo_h = mos_constants['cpo_h']
        md_h_min = mos_constants['md_h_min']
        md_od_exty = mos_constants['md_od_exty']
        md_spy = mos_constants['md_spy']
        ds_m2_sp = mos_constants['ds_m2_sp']

        # compute gate/drain connection parameters
        g_conn_info = self.get_conn_drc_info(lch_unit, 'g')
        g_m1_h = g_conn_info[1]['min_len']
        g_m1_top_exty = g_conn_info[1]['top_ext']
        g_m1_bot_exty = g_conn_info[1]['bot_ext']
        g_m1_sple = g_conn_info[1]['sp_le']
        g_m2_h = g_conn_info[2]['w']
        g_m3_h = g_conn_info[3]['min_len']
        g_m3_exty = g_conn_info[3]['top_ext']

        d_conn_info = self.get_conn_drc_info(lch_unit, 'd')
        d_m1_h = d_conn_info[1]['min_len']
        d_m1_bot_exty = d_conn_info[1]['bot_ext']
        d_m2_h = d_conn_info[2]['w']
        d_m3_h = d_conn_info[3]['min_len']
        d_m3_sple = d_conn_info[3]['sp_le']

        od_h = (w - 1) * fin_p + fin_h
        md_h = max(od_h + 2 * md_od_exty, md_h_min)

        # place bottom CPO, compute gate/OD locations
        blk_yb = 0
        cpo_bot_yb = blk_yb - cpo_h // 2
        cpo_bot_yt = cpo_bot_yb + cpo_h
        # get gate via/M1 location
        mp_yb = cpo_bot_yt + mp_cpo_sp
        mp_yt = mp_yb + mp_h
        mp_yc = (mp_yt + mp_yb) // 2
        g_m1_yt = mp_yc + g_m1_top_exty
        # get OD location, round to fin grid.
        od_yc = g_m1_yt + g_m1_sple + md_h // 2
        if w % 2 == 0:
            od_yc = -(-od_yc // fin_p) * fin_p
        else:
            od_yc = -(-(od_yc - fin_p // 2) // fin_p) * fin_p + fin_p // 2
        # compute OD/MD/CMD location
        od_yb = od_yc - od_h // 2
        od_yt = od_yb + od_h
        md_yb = od_yc - md_h // 2
        md_yt = md_yb + md_h
        d_m1_yb = md_yb
        d_m1_yt = d_m1_yb + d_m1_h
        # update gate location
        g_m1_yt = d_m1_yb - g_m1_sple
        g_m1_yb = g_m1_yt - g_m1_h
        g_m2_yc = g_m1_yt - g_m1_bot_exty

        # compute top CPO location.
        blk_yt = od_yt + cpo_od_sp + cpo_h // 2
        blk_yt = -(-blk_yt // fin_p) * fin_p

        # compute gate M2/M3 locations
        g_m2_yt = g_m2_yc + g_m2_h // 2
        g_m2_yb = g_m2_yt - g_m2_h
        g_m3_yt = g_m2_yc + g_m3_exty
        g_m3_yb = g_m3_yt - g_m3_h

        # compute source wire location
        s_m2_yc = d_m1_yb + d_m1_bot_exty
        s_m2_yb = s_m2_yc - d_m2_h // 2
        s_m2_yt = s_m2_yb + d_m2_h
        s_m3_yb = s_m2_yc - d_m3_h // 2
        s_m3_yt = s_m3_yb + d_m3_h
        # compute drain wire location
        d_m2_yb = s_m2_yt + ds_m2_sp
        d_m2_yt = d_m2_yb + d_m2_h
        d_m2_yc = (d_m2_yb + d_m2_yt) // 2
        d_m3_yb = d_m2_yc - d_m3_h // 2
        d_m3_yt = d_m3_yb + d_m3_h

        return dict(
            blk=(blk_yb, blk_yt),
            od=(od_yb, od_yt),
            md=(md_yb, md_yt),
            top_margins=dict(
                od=(blk_yt - od_yt, od_spy),
                md=(blk_yt - md_yt, md_spy),
                m1=(blk_yt - d_m1_yt, g_m1_sple),
                m3=(blk_yt - d_m3_yt, d_m3_sple)
            ),
            bot_margins=dict(
                od=(od_yb - blk_yb, od_spy),
                md=(md_yb - blk_yb, md_spy),
                m1=(g_m1_yb - blk_yb, g_m1_sple),
                m3=(g_m3_yb - blk_yb, d_m3_sple),
            ),
            fill_info={},
            g_y_list=[(mp_yb, mp_yt), (g_m1_yb, g_m1_yt),
                      (g_m2_yb, g_m2_yt), (g_m3_yb, g_m3_yt)],
            d_y_list=[(md_yb, md_yt), (d_m1_yb, d_m1_yt),
                      (d_m2_yb, d_m2_yt), (d_m3_yb, d_m3_yt)],
            s_y_list=[(md_yb, md_yt), (d_m1_yb, d_m1_yt),
                      (s_m2_yb, s_m2_yt), (s_m3_yb, s_m3_yt)],
        )

    def get_sub_yloc_info(self, lch_unit, w, sub_type, threshold, fg, **kwargs):
        # type: (int, int, str, str, int, **kwargs) -> Dict[str, Any]
        """Get substrate layout information.

        Layout is quite simple.  We use M0PO to short adjacent S/D together, so dummies can be
        connected using only M2 or below.

        Strategy:

        1. Find bottom M0_PO and bottom OD coordinates from spacing rules.
        #. Find template top coordinate by enforcing symmetry around OD center.
        #. Round up template height to blk_pitch, then recenter OD.
        #. make sure MD/M1 are centered on OD.
        """

        mos_constants = self.get_mos_tech_constants(lch_unit)
        fin_h = mos_constants['fin_h']
        fin_p = mos_constants['mos_pitch']
        od_spy = mos_constants['od_spy']
        mp_cpo_sp = mos_constants['mp_cpo_sp']
        mp_h = mos_constants['mp_h']
        cpo_od_sp = mos_constants['cpo_od_sp']
        cpo_h = mos_constants['cpo_h']
        md_h_min = mos_constants['md_h_min']
        md_od_exty = mos_constants['md_od_exty']
        md_spy = mos_constants['md_spy']
        mos_conn_w = mos_constants['mos_conn_w']
        vg_info = mos_constants['via_g']
        vd_info = mos_constants['via_d']
        w_conn_g = mos_constants['w_conn_g']
        w_conn_d = mos_constants['w_conn_d']

        fin_p2 = fin_p // 2
        fin_h2 = fin_h // 2

        mos_constants = cls.get_mos_tech_constants(lch_unit)
        sd_pitch = mos_constants['sd_pitch']

        # figure out od/md height
        od_h = (w - 1) * fin_p + fin_h
        md_h = max(md_h_min, od_h + 2 * md_od_exty)
        md_od_exty = (md_h - od_h) // 2

        # step 1: figure out Y coordinate of bottom CPO
        cpo_bot_yt = cpo_h // 2

        # step 2: find bottom M0_PO coordinate
        mp_yb = max(mp_spy // 2, cpo_bot_yt + mp_cpo_sp)
        mp_yt = mp_yb + mp_h

        # step 3: find OD coordinate
        od_bfin_yc = mp_yt + mp_md_sp + md_od_exty
        od_bfin_yc = -(-(od_bfin_yc - fin_p2) // fin_p) * fin_p + fin_p2
        od_yb = od_bfin_yc - fin_h2
        od_yt = od_yb + od_h
        cpo_top_yc = od_yt + od_yb
        # fix substrate height quantization, then recenter OD location
        blk_pitch = lcm([blk_pitch, fin_p])
        blk_h = -(-cpo_top_yc // blk_pitch) * blk_pitch
        cpo_top_yc = blk_h
        od_yb = blk_h // 2 - od_h // 2
        od_yb = (od_yb - fin_p2 + fin_h2) // fin_p * fin_p + fin_p2 - fin_h2
        od_yt = od_yb + od_h
        od_yc = (od_yb + od_yt) // 2

        # step 3: find MD Y coordinates
        md_yb = (od_yb + od_yt - md_h) // 2
        md_yt = md_yb + md_h

        # step 3.5: update MP Y coordinates, compute M1 upper and lower bound
        # bottom MP
        via_info = cls.get_ds_via_info(lch_unit, w)
        gv0_h = via_info['h'][0]
        top_ency = via_info['top_ency'][0]
        gm1_delta = gv0_h // 2 + top_ency
        mp_yt = md_yb - mp_md_sp
        mp_yb = mp_yt - mp_h
        mp_yc = (mp_yt + mp_yb) // 2
        g_m1_yb = mp_yc - gm1_delta
        # top MP
        mp_yb = md_yt + mp_md_sp
        mp_yt = mp_yb + mp_h
        mp_yc = (mp_yb + mp_yt) // 2
        g_m1_yt = mp_yc + gm1_delta

        # step 4: compute PO locations
        po_yb, po_yt = 0, cpo_top_yc

        # step 5: compute layout information
        lay_info_list = [(lay, 0, po_yb, po_yt) for lay in cls.get_mos_layers(sub_type, threshold)]
        lr_edge_info = EdgeInfo(od_type='sub')

        ds_conn_y = (g_m1_yb, g_m1_yt)
        fill_info = FillInfo(layer=('M1', 'drawing'), exc_layer=None,
                             x_intv_list=[], y_intv_list=[ds_conn_y])

        layout_info = dict(
            # information needed for draw_mos
            lch_unit=lch_unit,
            md_w=md_w,
            fg=fg,
            sd_pitch=sd_pitch,
            array_box_xl=0,
            array_box_y=(po_yb, po_yt),
            draw_od=True,
            row_info_list=[RowInfo(od_x_list=[(0, fg)],
                                   od_y=(od_yb, od_yt),
                                   od_type=('sub', sub_type),
                                   po_y=(po_yb, po_yt),
                                   md_y=(md_yb, md_yt)), ],
            lay_info_list=lay_info_list,
            adj_info_list=[],
            left_blk_info=None,
            right_blk_info=None,
            fill_info_list=[fill_info],

            # information needed for computing edge block layout
            blk_type='sub',
            imp_params=None,
        )

        mtype = (sub_type, sub_type)
        po_types = (1,) * fg
        ext_top_info = ExtInfo(
            mx_margin=po_yt - g_m1_yt,
            od_margin=po_yt - od_yt,
            md_margin=po_yt - md_yt,
            m1_margin=po_yt - g_m1_yt,
            imp_min_w=0,
            mtype=mtype,
            thres=threshold,
            po_types=po_types,
            edgel_info=lr_edge_info,
            edger_info=lr_edge_info,
        )
        ext_bot_info = ExtInfo(
            mx_margin=g_m1_yb - po_yb,
            od_margin=od_yb - po_yb,
            md_margin=md_yb - po_yb,
            m1_margin=g_m1_yb - po_yb,
            imp_min_w=0,
            mtype=mtype,
            thres=threshold,
            po_types=po_types,
            edgel_info=lr_edge_info,
            edger_info=lr_edge_info,
        )

        return dict(
            layout_info=layout_info,
            sd_yc=od_yc,
            ext_top_info=ext_top_info,
            ext_bot_info=ext_bot_info,
            left_edge_info=(lr_edge_info, []),
            right_edge_info=(lr_edge_info, []),
            blk_height=po_yt,
            gb_conn_y=ds_conn_y,
            ds_conn_y=ds_conn_y,
        )

    @classmethod
    def get_analog_end_info(cls, lch_unit, sub_type, threshold, fg, is_end, blk_pitch, **kwargs):
        # type: (int, str, str, int, bool, int, **kwargs) -> Dict[str, Any]
        """Get substrate end layout information

        Layout is quite simple.  We draw the right CPO width, and extend PO so PO-CPO overlap
        rule is satisfied.

        Strategy:
        If is not end (array abutment), just draw CPO.  If is end:
        1. find margin between bottom coordinate and array box bottom, round up to block pitch.
        #. Compute CPO location, and PO coordinates if we need to draw PO.
        #. Compute implant location.
        """
        fin_h = cls.tech_constants['fin_h']
        fin_p = cls.tech_constants['fin_pitch']
        cpo_po_ency = cls.tech_constants['cpo_po_ency']
        md_w = cls.tech_constants['md_w']
        cpo_h = cls.tech_constants['cpo_h']

        fin_p2 = fin_p // 2
        fin_h2 = fin_h // 2

        mos_constants = cls.get_mos_tech_constants(lch_unit)
        sd_pitch = mos_constants['sd_pitch']

        lr_edge_info = EdgeInfo(od_type='sub')
        if is_end:
            # step 1: figure out Y coordinates of CPO
            blk_pitch = lcm([blk_pitch, fin_p])
            # first assume top Y coordinate is 0
            arr_yt = 0
            cpo_bot_yt = arr_yt + cpo_h // 2
            cpo_bot_yb = cpo_bot_yt - cpo_h
            finbound_yb = arr_yt - fin_p2 - fin_h2
            min_yb = min(finbound_yb, cpo_bot_yb)
            # make sure all layers are in first quadrant
            if min_yb < 0:
                yshift = -(min_yb // blk_pitch) * blk_pitch
                arr_yt += yshift
                cpo_bot_yt += yshift
                cpo_bot_yb += yshift
                finbound_yb += yshift

            finbound_yt = arr_yt + fin_p2 + fin_h2
            cpo_bot_yc = (cpo_bot_yb + cpo_bot_yt) // 2
            po_yt = arr_yt
            po_yb = cpo_bot_yt - cpo_po_ency
            if po_yt > po_yb:
                adj_info_list = [AdjRowInfo(po_y=(po_yb, po_yt), po_types=(1,) * fg)]
                adj_edge_infos = [lr_edge_info]
            else:
                adj_info_list = []
                adj_edge_infos = []

            lay_info_list = [(('CutPoly', 'drawing'), 0, cpo_bot_yb, cpo_bot_yt)]
            for lay in cls.get_mos_layers(sub_type, threshold):
                if lay[0] == 'FinArea':
                    yb, yt = finbound_yb, finbound_yt
                else:
                    yb, yt = min(po_yb, cpo_bot_yc), arr_yt
                if yt > yb:
                    lay_info_list.append((lay, 0, yb, yt))
        else:
            # we just draw CPO
            arr_yt = 0
            cpo_h = mos_constants['cpo_h']
            lay_info_list = [(('CutPoly', 'drawing'), 0, -cpo_h // 2, cpo_h // 2)]
            adj_info_list = []
            adj_edge_infos = []

        layout_info = dict(
            # information needed for draw_mos
            lch_unit=lch_unit,
            md_w=md_w,
            fg=fg,
            sd_pitch=sd_pitch,
            array_box_xl=0,
            array_box_y=(0, arr_yt),
            draw_od=True,
            row_info_list=[],
            lay_info_list=lay_info_list,
            adj_info_list=adj_info_list,
            left_blk_info=None,
            right_blk_info=None,
            fill_info_list=[],

            # information needed for computing edge block layout
            blk_type='end',
            imp_params=None,
            left_edge_info=(lr_edge_info, adj_edge_infos),
            right_edge_info=(lr_edge_info, adj_edge_infos),
        )

        return dict(
            layout_info=layout_info,
            left_edge_info=(lr_edge_info, adj_edge_infos),
            right_edge_info=(lr_edge_info, adj_edge_infos),
        )

    @classmethod
    def get_sub_ring_end_info(cls, sub_type, threshold, fg, end_ext_info, **kwargs):
        # type: (str, str, int, ExtInfo, **kwargs) -> Dict[str, Any]
        # TODO: add actual implementation
        raise NotImplementedError('not implemented yet.')

    @classmethod
    def get_outer_edge_info(cls, guard_ring_nf, layout_info, is_end, adj_blk_info):
        # type: (int, Dict[str, Any], bool, Optional[Any]) -> Dict[str, Any]
        lch_unit = layout_info['lch_unit']
        edge_info = cls.get_edge_info(lch_unit, guard_ring_nf, is_end)
        outer_fg = edge_info['outer_fg']
        cpo_xl = edge_info['cpo_xl']
        # compute new row_info_list
        # noinspection PyProtectedMember
        row_info_list = [rinfo._replace(od_x_list=[]) for rinfo in layout_info['row_info_list']]

        # compute new lay_info_list
        lay_info_list = layout_info['lay_info_list']
        imp_params = layout_info['imp_params']
        if guard_ring_nf == 0 or imp_params is None:
            # we keep all implant layers, just update left coordinate.
            new_lay_list = [(lay, cpo_xl if lay[0] == 'CutPoly' else 0, yb, yt)
                            for lay, _, yb, yt in lay_info_list]
        else:
            # we need to convert implant layers to substrate implants
            # first, get all CPO layers
            new_lay_list = [(lay, cpo_xl, yb, yt) for lay, _, yb, yt in lay_info_list if lay[0] == 'CutPoly']
            # compute substrate implant layers
            for mtype, thres, imp_yb, imp_yt, thres_yb, thres_yt in imp_params:
                sub_type = 'ptap' if mtype == 'nch' or mtype == 'ptap' else 'ntap'
                for lay in cls.get_mos_layers(sub_type, thres):
                    cur_yb, cur_yt = imp_yb, imp_yt
                    new_lay_list.append((lay, 0, cur_yb, cur_yt))

        # compute new adj_info_list
        adj_info_list = layout_info['adj_info_list']
        if adj_blk_info is None:
            adj_blk_info = (None, [None] * len(adj_info_list))

        new_adj_list = []
        if outer_fg > 0:
            for adj_edge_info, adj_info in zip(adj_blk_info[1], adj_info_list):
                if adj_edge_info is not None and (adj_edge_info.od_type == 'mos' or adj_edge_info.od_type == 'sub'):
                    po_types = (0,) * (outer_fg - 1) + (1,)
                else:
                    po_types = (0,) * outer_fg
                # noinspection PyProtectedMember
                new_adj_list.append(adj_info._replace(po_types=po_types))

        # compute new fill information
        sd_pitch = layout_info['sd_pitch']
        if outer_fg > 0:
            mos_constants = cls.get_mos_tech_constants(lch_unit)
            m1_w = mos_constants['mos_conn_w']
            x_intv_list = [(sd_pitch - m1_w // 2, sd_pitch + m1_w // 2)]
        else:
            x_intv_list = []
        # noinspection PyProtectedMember
        fill_info_list = [f._replace(x_intv_list=x_intv_list) for f in layout_info['fill_info_list']]

        return dict(
            lch_unit=lch_unit,
            md_w=layout_info['md_w'],
            fg=outer_fg,
            sd_pitch=sd_pitch,
            array_box_xl=0,
            array_box_y=layout_info['array_box_y'],
            draw_od=True,
            row_info_list=row_info_list,
            lay_info_list=new_lay_list,
            adj_info_list=new_adj_list,
            left_blk_info=EdgeInfo(od_type=None),
            right_blk_info=adj_blk_info[0],
            fill_info_list=fill_info_list,

            blk_type='edge' if guard_ring_nf == 0 else 'gr_edge',
        )

    @classmethod
    def get_gr_sub_info(cls, guard_ring_nf, layout_info):
        # type: (int, Dict[str, Any]) -> Dict[str, Any]

        lch_unit = layout_info['lch_unit']
        edge_constants = cls.get_edge_tech_constants(lch_unit)
        gr_nf_min = edge_constants['gr_nf_min']
        gr_sub_fg_margin = edge_constants['gr_sub_fg_margin']

        if guard_ring_nf < gr_nf_min:
            raise ValueError('guard_ring_nf = %d < %d' % (guard_ring_nf, gr_nf_min))

        fg = gr_nf_min + 2 + 2 * gr_sub_fg_margin

        # compute new row_info_list
        od_x_list = [(gr_sub_fg_margin + 1, gr_sub_fg_margin + 1 + gr_nf_min)]
        # noinspection PyProtectedMember
        row_info_list = [rinfo._replace(od_x_list=od_x_list, od_type=('sub', rinfo.od_type[1]))
                         for rinfo in layout_info['row_info_list']]

        # compute new lay_info_list
        lay_info_list = layout_info['lay_info_list']
        imp_params = layout_info['imp_params']
        if imp_params is None:
            # don't have to recompute implant layers
            new_lay_list = lay_info_list
        else:
            # we need to convert implant layers to substrate implants
            # first, get all CPO layers
            new_lay_list = [lay_info for lay_info in lay_info_list if lay_info[0][0] == 'CutPoly']
            # compute substrate implant layers
            for mtype, thres, imp_yb, imp_yt, thres_yb, thres_yt in imp_params:
                sub_type = 'ptap' if mtype == 'nch' or mtype == 'ptap' else 'ntap'
                for lay in cls.get_mos_layers(sub_type, thres):
                    cur_yb, cur_yt = imp_yb, imp_yt
                    new_lay_list.append((lay, 0, cur_yb, cur_yt))

        # compute new adj_info_list
        po_types = (0,) * gr_sub_fg_margin + (1,) * (gr_nf_min + 2) + (0,) * gr_sub_fg_margin
        # noinspection PyProtectedMember
        adj_info_list = [ar_info._replace(po_types=po_types) for ar_info in layout_info['adj_info_list']]

        # compute new fill information
        # noinspection PyProtectedMember
        fill_info_list = [f._replace(x_intv_list=[]) for f in layout_info['fill_info_list']]

        return dict(
            lch_unit=lch_unit,
            md_w=layout_info['md_w'],
            fg=fg,
            sd_pitch=layout_info['sd_pitch'],
            array_box_xl=0,
            array_box_y=layout_info['array_box_y'],
            draw_od=True,
            row_info_list=row_info_list,
            lay_info_list=new_lay_list,
            adj_info_list=adj_info_list,
            left_blk_info=None,
            right_blk_info=None,
            fill_info_list=fill_info_list,

            blk_type='gr_sub',
        )

    @classmethod
    def get_gr_sep_info(cls, layout_info, adj_blk_info):
        # type: (Dict[str, Any], Any) -> Dict[str, Any]

        lch_unit = layout_info['lch_unit']
        edge_constants = cls.get_edge_tech_constants(lch_unit)
        fg = edge_constants['gr_sep_fg']

        # compute new row_info_list
        # noinspection PyProtectedMember
        row_info_list = [rinfo._replace(od_x_list=[]) for rinfo in layout_info['row_info_list']]

        # compute new adj_info_list
        adj_info_list = layout_info['adj_info_list']
        new_adj_list = []
        for adj_edge_info, adj_info in zip(adj_blk_info[1], adj_info_list):
            if adj_edge_info.od_type == 'mos' or adj_edge_info.od_type == 'sub':
                po_types = (0,) * (fg - 1) + (1,)
            else:
                po_types = (0,) * fg
            # noinspection PyProtectedMember
            new_adj_list.append(adj_info._replace(po_types=po_types))

        # compute new fill information
        mos_constants = cls.get_mos_tech_constants(lch_unit)
        m1_w = mos_constants['mos_conn_w']
        x_intv_list = [(-m1_w // 2, m1_w // 2)]
        # noinspection PyProtectedMember
        fill_info_list = [f._replace(x_intv_list=x_intv_list) for f in layout_info['fill_info_list']]

        return dict(
            lch_unit=lch_unit,
            md_w=layout_info['md_w'],
            fg=fg,
            sd_pitch=layout_info['sd_pitch'],
            array_box_xl=0,
            array_box_y=layout_info['array_box_y'],
            draw_od=True,
            row_info_list=row_info_list,
            lay_info_list=layout_info['lay_info_list'],
            adj_info_list=new_adj_list,
            left_blk_info=None,
            right_blk_info=adj_blk_info[0],
            fill_info_list=fill_info_list,

            blk_type='gr_sep',
        )

    @classmethod
    def draw_mos(cls, template, layout_info):
        # type: (TemplateBase, Dict[str, Any]) -> None
        """Draw transistor related layout.

        the layout information dictionary should contain the following entries:


        blk_type
            a string describing the type of this block.
        lch_unit
            channel length in resolution units
        md_w
            M0OD width in resolution units
        fg
            the width of this template in number of fingers
        sd_pitch
            the source/drain pitch of this template.
        array_box_xl
            array box left coordinate.  All PO X coordinates are calculated
            relative to this point.
        array_box_y
            array box Y coordinates as two-element integer tuple.
        od_type
            the OD type in this template.  Either 'mos', 'sub', or 'dum'.
        draw_od
            If False, we will not draw OD in this template.  This is used for
            supporting the ds_dummy option.
        row_info_list
            a list of named tuples for each transistor row we need to draw in
            this template.

            a transistor row is defines as a row of OD/PO/MD that either acts
            as an active device or used for dummy fill purposes.  Each named tuple
            should have the following entries:

            od_x_list
                A list of transistor X intervals in finger index.
            od_y
                OD Y coordinates as two-element integer tuple.
            po_y
                PO Y coordinates as two-element integer tuple.
            md_y
                MD Y coordinates as two-element integer tuple.
        lay_info_list
            a list of layers to draw.  Each layer information is a tuple
            of (imp_layer, xl, yb, yt).
        adj_info_list
            a list of named tuples for geometries belonging to adjacent
            rows.  Each named tuple should contain:

            po_y
                PO Y coordinates as two-element integer tuple.
            po_types
                list of po types.  1 for drawing, 0 for dummy.
        left_blk_info
            a tuple of (EdgeInfo, List[EdgeInfo]) that represents edge information
            of the left adjacent block.  These influences the geometry abutting the
            left block.  If None, assume default behavior.
        right_blk_info
            same as left_blk_info, but for the right edge.
        fill_info_list:
            a list of fill information named tuple.  Each tuple contains:

            layer
                the fill layer
            exc_layer
                the fill exclusion layer
            x_intv_list
                a list of X intervals of the fill
            y_intv_list
                a list of Y intervals of the fill

        Parameters
        ----------
        template : TemplateBase
            the template to draw the layout in.
        layout_info : Dict[str, Any]
            the layout information dictionary.
        """
        res = template.grid.resolution

        fin_pitch = cls.tech_constants['fin_pitch']
        fin_h = cls.tech_constants['fin_h']

        fin_pitch2 = fin_pitch // 2
        fin_h2 = fin_h // 2

        blk_type = layout_info['blk_type']
        lch_unit = layout_info['lch_unit']
        md_w = layout_info['md_w']
        fg = layout_info['fg']
        sd_pitch = layout_info['sd_pitch']
        arr_xl = layout_info['array_box_xl']
        arr_yb, arr_yt = layout_info['array_box_y']
        draw_od = layout_info['draw_od']
        row_info_list = layout_info['row_info_list']
        lay_info_list = layout_info['lay_info_list']
        adj_info_list = layout_info['adj_info_list']
        left_blk_info = layout_info['left_blk_info']
        right_blk_info = layout_info['right_blk_info']
        fill_info_list = layout_info['fill_info_list']

        default_edge_info = EdgeInfo(od_type=None)
        if left_blk_info is None:
            if fg == 1 and right_blk_info is not None:
                # make sure if we only have one finger, PO purpose is still chosen correctly.
                left_blk_info = right_blk_info
            else:
                left_blk_info = default_edge_info
        if right_blk_info is None:
            if fg == 1:
                # make sure if we only have one finger, PO purpose is still chosen correctly.
                right_blk_info = left_blk_info
            else:
                right_blk_info = default_edge_info

        blk_w = fg * sd_pitch + arr_xl

        # figure out transistor layout settings
        od_dum_lay = ('Active', 'dummy')
        po_dum_lay = ('Poly', 'dummy')
        md_lay = ('LiAct', 'drawing')

        po_xc = arr_xl + sd_pitch // 2
        # draw transistor rows
        for row_info in row_info_list:
            od_type = row_info.od_type[0]
            if od_type == 'dum' or od_type is None:
                od_lay = od_dum_lay
            else:
                od_lay = ('Active', 'drawing')
            od_x_list = row_info.od_x_list
            od_yb, od_yt = row_info.od_y
            po_yb, po_yt = row_info.po_y
            md_yb, md_yt = row_info.md_y

            po_on_od = [False] * fg
            md_on_od = [False] * (fg + 1)
            if od_yt > od_yb:
                # draw OD and figure out PO/MD info
                for od_start, od_stop in od_x_list:
                    # mark PO/MD indices that are on OD
                    if od_start - 1 >= 0:
                        po_on_od[od_start - 1] = True
                    for idx in range(od_start, od_stop + 1):
                        md_on_od[idx] = True
                        if idx < fg:
                            po_on_od[idx] = True

                    if draw_od:
                        od_xl = po_xc - lch_unit // 2 + (od_start - 1) * sd_pitch
                        od_xr = po_xc + lch_unit // 2 + od_stop * sd_pitch
                        template.add_rect(od_lay, BBox(od_xl, od_yb, od_xr, od_yt, res, unit_mode=True))

            # draw PO
            if po_yt > po_yb:
                for idx in range(fg):
                    po_xl = po_xc + idx * sd_pitch - lch_unit // 2
                    po_xr = po_xl + lch_unit
                    if po_on_od[idx]:
                        cur_od_type = od_type
                        is_edge = False
                    else:
                        if idx == 0:
                            cur_od_type = left_blk_info.od_type
                            is_edge = True
                        elif idx == fg - 1:
                            cur_od_type = right_blk_info.od_type
                            is_edge = True
                        else:
                            cur_od_type = None
                            is_edge = False

                    if is_edge and cur_od_type is not None:
                        lay = ('Poly', 'edge')
                    elif cur_od_type == 'mos' or cur_od_type == 'sub':
                        lay = ('Poly', 'drawing')
                    else:
                        lay = ('Poly', 'dummy')
                    template.add_rect(lay, BBox(po_xl, po_yb, po_xr, po_yt, res, unit_mode=True))

            # draw MD if it's physical
            if md_yt > md_yb and fg > 0:
                md_range = range(1, fg) if blk_type == 'gr_sub' else range(fg + 1)
                for idx in md_range:
                    md_xl = arr_xl + idx * sd_pitch - md_w // 2
                    md_xr = md_xl + md_w
                    if md_on_od[idx]:
                        template.add_rect(md_lay, BBox(md_xl, md_yb, md_xr, md_yt, res, unit_mode=True))

        # draw other layers
        for imp_lay, xl, yb, yt in lay_info_list:
            if imp_lay[0] == 'FinArea':
                # round to fin grid
                yb = (yb - fin_pitch2 + fin_h2) // fin_pitch * fin_pitch + fin_pitch2 - fin_h2
                yt = -(-(yt - fin_pitch2 - fin_h2) // fin_pitch) * fin_pitch + fin_pitch2 + fin_h2
            box = BBox(xl, yb, blk_w, yt, res, unit_mode=True)
            if box.is_physical():
                template.add_rect(imp_lay, box)

        # draw adjacent row geometries
        for adj_info in adj_info_list:
            po_yb, po_yt = adj_info.po_y
            for idx, po_type in enumerate(adj_info.po_types):
                lay = po_dum_lay if po_type == 0 else ('Poly', 'drawing')
                po_xl = po_xc + idx * sd_pitch - lch_unit // 2
                po_xr = po_xl + lch_unit
                template.add_rect(lay, BBox(po_xl, po_yb, po_xr, po_yt, res, unit_mode=True))

        # set size and add PR boundary
        arr_box = BBox(arr_xl, arr_yb, blk_w, arr_yt, res, unit_mode=True)
        bound_box = arr_box.extend(x=0, y=0, unit_mode=True)
        template.array_box = arr_box
        template.prim_bound_box = bound_box
        if bound_box.is_physical():
            template.add_cell_boundary(bound_box)

            # draw metal fill.  This only needs to be done if the template has nonzero area.
            for fill_info in fill_info_list:
                exc_lay = fill_info.exc_layer
                lay = fill_info.layer
                x_intv_list = fill_info.x_intv_list
                y_intv_list = fill_info.y_intv_list
                if exc_lay is not None:
                    template.add_rect(exc_lay, bound_box)
                for xl, xr in x_intv_list:
                    for yb, yt in y_intv_list:
                        template.add_rect(lay, BBox(xl, yb, xr, yt, res, unit_mode=True))

    @classmethod
    def draw_substrate_connection(cls, template, layout_info, port_tracks, dum_tracks, dummy_only,
                                  is_laygo, is_guardring):
        # type: (TemplateBase, Dict[str, Any], List[int], List[int], bool, bool, bool) -> bool

        fin_h = cls.tech_constants['fin_h']
        fin_p = cls.tech_constants['fin_pitch']
        mp_md_sp = cls.tech_constants['mp_md_sp']
        mp_h = cls.tech_constants['mp_h']
        mp_po_ovl = cls.tech_constants['mp_po_ovl']

        lch_unit = layout_info['lch_unit']
        sd_pitch = layout_info['sd_pitch']
        row_info_list = layout_info['row_info_list']

        sd_pitch2 = sd_pitch // 2

        has_od = False
        for row_info in row_info_list:
            od_yb, od_yt = row_info.od_y
            if od_yt > od_yb:
                has_od = True
                # find current port name
                od_start, od_stop = row_info.od_x_list[0]
                fg = od_stop - od_start
                xshift = od_start * sd_pitch
                sub_type = row_info.od_type[1]
                port_name = 'VDD' if sub_type == 'ntap' else 'VSS'

                # draw substrate connection only if OD exists.
                od_yc = (od_yb + od_yt) // 2
                w = (od_yt - od_yb - fin_h) // fin_p + 1

                via_info = cls.get_ds_via_info(lch_unit, w, compact=is_guardring)

                # find X locations of M1/M3.
                # we can export all dummy tracks.
                m1_x_list = [idx * sd_pitch for idx in range(fg + 1)]
                if dummy_only:
                    # find X locations to draw vias
                    m3_x_list = []
                else:
                    # first, figure out port/dummy tracks.
                    # Try to add as many unused tracks to port tracks as possible, while making sure we don't end
                    # up with adjacent port tracks.  This improves substrate connection resistance to supply.

                    # use half track indices so we won't have rounding errors.
                    phtr_set = set((int(2 * v + 1) for v in port_tracks))
                    # add as many unused tracks as possible to port tracks
                    for htr in range(0, 2 * fg + 1, 2):
                        if htr + 2 not in phtr_set and htr - 2 not in phtr_set:
                            phtr_set.add(htr)
                    # find X coordinates
                    m3_x_list = [sd_pitch2 * v for v in sorted(phtr_set)]

                m1_warrs, m3_warrs = cls._draw_ds_via(template, sd_pitch, od_yc, fg, via_info, 1, 1,
                                                      m1_x_list, m3_x_list, xshift=xshift)
                template.add_pin(port_name, m1_warrs, show=False)
                template.add_pin(port_name, m3_warrs, show=False)

                if not is_guardring:
                    md_yb, md_yt = row_info.md_y
                    # draw M0PO connections
                    res = template.grid.resolution
                    gv0_h = via_info['h'][0]
                    gv0_w = via_info['w'][0]
                    top_encx = via_info['top_encx'][0]
                    top_ency = via_info['top_ency'][0]
                    gm1_delta = gv0_h // 2 + top_ency
                    m1_w = gv0_w + 2 * top_encx
                    bot_encx = (m1_w - gv0_w) // 2
                    bot_ency = (mp_h - gv0_h) // 2
                    # bottom MP
                    mp_yt = md_yb - mp_md_sp
                    mp_yb = mp_yt - mp_h
                    mp_yc = (mp_yt + mp_yb) // 2
                    m1_yb = mp_yc - gm1_delta
                    mp_y_list = [(mp_yb, mp_yt)]
                    # top MP
                    mp_yb = md_yt + mp_md_sp
                    mp_yt = mp_yb + mp_h
                    mp_yc = (mp_yb + mp_yt) // 2
                    m1_yt = mp_yc + gm1_delta
                    mp_y_list.append((mp_yb, mp_yt))

                    # draw MP, M1, and VIA0
                    via_type = 'M1_LiPo'
                    mp_dx = sd_pitch // 2 - lch_unit // 2 + mp_po_ovl
                    enc1 = [bot_encx, bot_encx, bot_ency, bot_ency]
                    enc2 = [top_encx, top_encx, top_ency, top_ency]
                    for idx in range(0, fg + 1, 2):
                        mp_xl = xshift + idx * sd_pitch - mp_dx
                        mp_xr = xshift + idx * sd_pitch + mp_dx
                        for mp_yb, mp_yt in mp_y_list:
                            template.add_rect('LiPo', BBox(mp_xl, mp_yb, mp_xr, mp_yt, res, unit_mode=True))
                        m1_xc = xshift + idx * sd_pitch
                        template.add_rect('M1', BBox(m1_xc - m1_w // 2, m1_yb, m1_xc + m1_w // 2, m1_yt, res,
                                                     unit_mode=True))
                        for mp_yb, mp_yt in mp_y_list:
                            mp_yc = (mp_yb + mp_yt) // 2
                            template.add_via_primitive(via_type, [m1_xc, mp_yc], enc1=enc1, enc2=enc2, unit_mode=True)

        return has_od

    @classmethod
    def draw_mos_connection(cls, template, mos_info, sdir, ddir, gate_pref_loc, gate_ext_mode,
                            min_ds_cap, is_diff, diode_conn, options):
        # type: (TemplateBase, Dict[str, Any], int, int, str, int, bool, bool, bool, Dict[str, Any]) -> None

        # NOTE: ignore min_ds_cap.
        if is_diff:
            raise ValueError('differential connection not supported yet.')

        fin_h = cls.tech_constants['fin_h']
        fin_pitch = cls.tech_constants['fin_pitch']

        gate_yc = mos_info['gate_yc']
        layout_info = mos_info['layout_info']
        lch_unit = layout_info['lch_unit']
        fg = layout_info['fg']
        sd_pitch = layout_info['sd_pitch']
        od_yb, od_yt = layout_info['row_info_list'][0].od_y

        w = (od_yt - od_yb - fin_h) // fin_pitch + 1
        ds_via_info = cls.get_ds_via_info(lch_unit, w)

        g_via_info = cls.get_gate_via_info(lch_unit)

        stack = options.get('stack', 1)
        wire_pitch = stack * sd_pitch
        if fg % stack != 0:
            raise ValueError('AnalogMosConn: stack = %d must evenly divides fg = %d' % (stack, fg))
        num_seg = fg // stack

        s_x_list = list(range(0, num_seg * wire_pitch + 1, 2 * wire_pitch))
        d_x_list = list(range(wire_pitch, num_seg * wire_pitch + 1, 2 * wire_pitch))
        sd_yc = (od_yb + od_yt) // 2
        if diode_conn:
            if fg == 1:
                raise ValueError('1 finger transistor connection not supported.')

            sloc = 0 if sdir <= 1 else 2
            dloc = 2 - sloc

            # draw source
            _, sarr = cls._draw_ds_via(template, wire_pitch, 0, num_seg, ds_via_info, sloc, sdir,
                                       s_x_list, s_x_list)
            # draw drain
            m1d, darr = cls._draw_ds_via(template, wire_pitch, 0, num_seg, ds_via_info, dloc, ddir,
                                         d_x_list, d_x_list)
            # draw gate
            m1g, _ = cls._draw_g_via(template, lch_unit, fg, sd_pitch, gate_yc - sd_yc, g_via_info, [],
                                     gate_ext_mode=gate_ext_mode)
            m1_yt = m1d[0].upper
            m1_yb = m1g[0].lower
            template.add_wires(1, m1d[0].track_id.base_index, m1_yb, m1_yt, num=len(m1d), pitch=2 * stack)
            template.add_pin('g', _to_warr(darr), show=False)
            template.add_pin('d', _to_warr(darr), show=False)
            template.add_pin('s', _to_warr(sarr), show=False)
        else:
            # determine gate location
            if sdir == 0:
                gloc = 'd'
            elif ddir == 0:
                gloc = 's'
            else:
                gloc = gate_pref_loc

            if (gloc == 's' and num_seg == 2) or gloc == 'd':
                sloc, dloc = 0, 2
            else:
                sloc, dloc = 2, 0

            if gloc == 'd':
                g_x_list = list(range(wire_pitch, num_seg * wire_pitch, 2 * wire_pitch))
            else:
                if num_seg != 2:
                    g_x_list = list(range(2 * wire_pitch, num_seg * wire_pitch, 2 * wire_pitch))
                else:
                    g_x_list = [0, 2 * wire_pitch]

            # draw gate
            _, garr = cls._draw_g_via(template, lch_unit, fg, sd_pitch, gate_yc - sd_yc, g_via_info,
                                      g_x_list, gate_ext_mode=gate_ext_mode)
            # draw source
            _, sarr = cls._draw_ds_via(template, wire_pitch, 0, num_seg, ds_via_info, sloc, sdir,
                                       s_x_list, s_x_list)
            # draw drain
            _, darr = cls._draw_ds_via(template, wire_pitch, 0, num_seg, ds_via_info, dloc, ddir,
                                       d_x_list, d_x_list)

            template.add_pin('s', _to_warr(sarr), show=False)
            template.add_pin('d', _to_warr(darr), show=False)
            template.add_pin('g', _to_warr(garr), show=False)

    @classmethod
    def draw_dum_connection(cls, template, mos_info, edge_mode, gate_tracks, options):
        # type: (TemplateBase, Dict[str, Any], int, List[int], Dict[str, Any]) -> None

        fin_h = cls.tech_constants['fin_h']
        fin_pitch = cls.tech_constants['fin_pitch']
        m1_dum_h = cls.tech_constants['m1_dum_h']

        gate_yc = mos_info['gate_yc']
        layout_info = mos_info['layout_info']
        lch_unit = layout_info['lch_unit']
        fg = layout_info['fg']
        sd_pitch = layout_info['sd_pitch']
        od_yb, od_yt = layout_info['row_info_list'][0].od_y

        sd_yc = (od_yb + od_yt) // 2
        w = (od_yt - od_yb - fin_h) // fin_pitch + 1
        ds_via_info = cls.get_ds_via_info(lch_unit, w)

        g_via_info = cls.get_gate_via_info(lch_unit)

        left_edge = edge_mode % 2 == 1
        right_edge = edge_mode // 2 == 1
        if left_edge:
            ds_x_start = 0
        else:
            ds_x_start = sd_pitch
        if right_edge:
            ds_x_stop = fg * sd_pitch
        else:
            ds_x_stop = (fg - 1) * sd_pitch

        ds_x_list = list(range(ds_x_start, ds_x_stop + 1, sd_pitch))

        # draw gate
        m1g, _ = cls._draw_g_via(template, lch_unit, fg, sd_pitch, gate_yc - sd_yc, g_via_info, [])
        # draw drain/source
        m1d, _ = cls._draw_ds_via(template, sd_pitch, 0, fg, ds_via_info, 1, 1, ds_x_list, [], draw_m2=False)

        # connect gate and drain/source together
        res = template.grid.resolution
        m1_yb = int(round(m1g[0].lower / res))
        m1_yt = m1_yb + m1_dum_h
        template.connect_wires(m1g + m1d, lower=m1_yb, unit_mode=True)
        if ds_x_stop > ds_x_start:
            template.add_rect('M1', BBox(ds_x_start, m1_yb, ds_x_stop, m1_yt, res, unit_mode=True))

        template.add_pin('dummy', m1g, show=False)

    @classmethod
    def draw_decap_connection(cls, template, mos_info, sdir, ddir, gate_ext_mode, export_gate, options):
        # type: (TemplateBase, Dict[str, Any], int, int, int, bool, Dict[str, Any]) -> None
        raise NotImplementedError('Not implemented')

    @classmethod
    def _draw_g_via(cls, template, lch_unit, fg, sd_pitch, gate_yc, via_info, m3_x_list,
                    gate_ext_mode=0, dx=0):

        res = cls.tech_constants['resolution']
        mp_po_ovl = cls.tech_constants['mp_po_ovl']
        mp_h = cls.tech_constants['mp_h']
        mx_area_min = cls.tech_constants['mx_area_min']

        w_list = via_info['w']
        h_list = via_info['h']
        bot_encx = via_info['bot_encx']
        top_encx = via_info['top_encx']
        bot_ency = via_info['bot_ency']
        top_ency = via_info['top_ency']
        m1_h = via_info['m1_h']
        m2_h = via_info['m2_h']
        m3_h = via_info['m3_h']

        m1_top_ency = top_ency[0]
        v0_h = h_list[0]
        m2_top_encx = top_encx[1]
        v1_w = w_list[1]

        m1_yt = gate_yc + v0_h // 2 + m1_top_ency
        m1_yb = m1_yt - m1_h

        # compute minimum M2 width from area rule, make sure it's even.
        m2_w_min = -(-mx_area_min // (2 * m2_h)) * 2
        m2_yb = gate_yc - m2_h // 2
        m2_yt = m2_yb + m2_h

        if fg % 2 == 0:
            gate_fg_list = [2] * (fg // 2)
        else:
            if fg == 1:
                raise ValueError('cannot connect 1 finger transistor')
            if fg <= 5:
                gate_fg_list = [fg]
            else:
                num_mp_half = (fg - 3) // 2
                gate_fg_list = [2] * num_mp_half
                gate_fg_list.append(3)
                gate_fg_list.extend((2 for _ in range(num_mp_half)))

        m2_xl = m2_xr = dx + fg * sd_pitch // 2
        # extend gate in left/right direction with M2 if necessary.
        if gate_ext_mode % 2 == 1:
            m2_xl = dx
        if gate_ext_mode // 2 == 1:
            m2_xr = dx + fg * sd_pitch

        # connect gate to M2.
        v0_enc1 = [bot_encx[0], bot_encx[0], bot_ency[0], bot_ency[0]]
        v0_enc2 = [top_encx[0], top_encx[0], top_ency[0], top_ency[0]]
        v1_enc1 = [bot_encx[1], bot_encx[1], bot_ency[1], bot_ency[1]]
        v1_enc2 = [top_encx[1], top_encx[1], top_ency[1], top_ency[1]]
        tot_fg = 0
        m1_warrs = []
        for num_fg in gate_fg_list:
            via_xoff = dx + (tot_fg + 1) * sd_pitch
            cur_xc = dx + tot_fg * sd_pitch + num_fg * sd_pitch // 2
            # draw MP
            mp_w = (num_fg - 1) * sd_pitch - lch_unit + 2 * mp_po_ovl
            mp_xl = cur_xc - mp_w // 2
            mp_xr = mp_xl + mp_w
            mp_yb = gate_yc - mp_h // 2
            mp_yt = mp_yb + mp_h
            template.add_rect(('LiPo', 'drawing'), BBox(mp_xl, mp_yb, mp_xr, mp_yt, res, unit_mode=True))
            # draw V0, M1, and V1
            for idx in range(num_fg - 1):
                via_xc = via_xoff + idx * sd_pitch
                vloc = [via_xc, gate_yc]
                cur_tidx = template.grid.coord_to_track(1, via_xc, unit_mode=True)
                template.add_via_primitive('M1_LiPo', vloc, enc1=v0_enc1, enc2=v0_enc2, unit_mode=True)
                m1_warrs.append(template.add_wires(1, cur_tidx, m1_yb, m1_yt, unit_mode=True))
                if m3_x_list:
                    template.add_via_primitive('M2_M1', vloc, enc1=v1_enc1, enc2=v1_enc2, unit_mode=True)

            m2_xl = min(via_xoff - v1_w // 2 - m2_top_encx, m2_xl)
            m2_xr = max(via_xoff + (num_fg - 2) * sd_pitch + v1_w // 2 + m2_top_encx, m2_xr)
            tot_fg += num_fg

        # fix M2 area rule
        m2_xc = (m2_xl + m2_xr) // 2
        m2_xl = min(m2_xl, m2_xc - m2_w_min // 2)
        m2_xl = max(dx, m2_xl)
        m2_xr = max(m2_xr, m2_xl + m2_w_min)
        if m3_x_list:
            template.add_rect('M2', BBox(m2_xl, m2_yb, m2_xr, m2_yt, res, unit_mode=True))

        # connect gate to M3
        m3_warrs = []
        v2_h = h_list[2]
        v2_enc1 = [bot_encx[2], bot_encx[2], bot_ency[2], bot_ency[2]]
        v2_enc2 = [top_encx[2], top_encx[2], top_ency[2], top_ency[2]]
        m3_yt = gate_yc + v2_h // 2 + v2_enc2[2]
        m3_yb = m3_yt - m3_h
        for xc in m3_x_list:
            template.add_via_primitive('M3_M2', [xc, gate_yc], enc1=v2_enc1, enc2=v2_enc2,
                                       cut_height=v2_h, unit_mode=True)
            tr_idx = template.grid.coord_to_track(3, xc, unit_mode=True)
            m3_warrs.append(template.add_wires(3, tr_idx, m3_yb, m3_yt, unit_mode=True))

        return m1_warrs, m3_warrs

    @classmethod
    def _draw_ds_via(cls, template, wire_pitch, od_yc, num_seg, via_info, m2_loc, m3_dir,
                     m1_x_list, m3_x_list, xshift=0, draw_m2=True):
        res = cls.tech_constants['resolution']
        v0_sp = cls.tech_constants['v0_sp']
        mx_area_min = cls.tech_constants['mx_area_min']

        nv0 = via_info['num_v0']
        m1_h = via_info['m1_h']
        m2_h = via_info['m2_h']
        m3_h = via_info['m3_h']
        md_encx, m1_bot_encx, m2_bot_encx = via_info['bot_encx']
        m1_encx, m2_encx, m3_encx = via_info['top_encx']
        md_ency, m1_bot_ency, m2_bot_ency = via_info['bot_ency']
        m1_ency, m2_ency, m3_ency = via_info['top_ency']
        v0_h, v1_h, v2_h = via_info['h']

        # draw via to M1
        via_type = 'M1_LiAct'
        enc1 = [md_encx, md_encx, md_ency, md_ency]
        enc2 = [m1_encx, m1_encx, m1_ency, m1_ency]
        template.add_via_primitive(via_type, [xshift, od_yc], num_rows=nv0, sp_rows=v0_sp,
                                   enc1=enc1, enc2=enc2, nx=num_seg + 1, spx=wire_pitch, unit_mode=True)

        # find M2 location
        m1_yb = od_yc - m1_h // 2
        m1_yt = m1_yb + m1_h
        if m2_loc == 0:
            via_yc = m1_yb + m1_bot_ency + v1_h // 2
        elif m2_loc == 1:
            via_yc = od_yc
        else:
            via_yc = m1_yt - m1_bot_ency - v1_h // 2

        # add M1 and M2
        m2_xl, m2_xr = None, None
        m1_warrs = []
        v1_enc1 = [m1_bot_encx, m1_bot_encx, m1_bot_ency, m1_bot_ency]
        v1_enc2 = [m2_encx, m2_encx, m2_ency, m2_ency]
        for xloc in m1_x_list:
            tidx = template.grid.coord_to_track(1, xloc, unit_mode=True)
            cur_warr = template.add_wires(1, tidx, m1_yb, m1_yt, unit_mode=True)
            m1_warrs.append(cur_warr)
            if draw_m2:
                template.add_via_primitive('M2_M1', [xloc, via_yc], cut_height=v1_h, enc1=v1_enc1,
                                           enc2=v1_enc2, unit_mode=True)
                m2_xl = xloc if m2_xl is None else min(xloc, m2_xl)
                m2_xr = xloc if m2_xr is None else max(xloc, m2_xr)

        # draw via to M3 and add metal/ports
        v2_enc1 = [m2_bot_encx, m2_bot_encx, m2_bot_ency, m2_bot_ency]
        v2_enc2 = [m3_encx, m3_encx, m3_ency, m3_ency]
        m3_warrs = []
        for xloc in m3_x_list:
            if m3_dir == 0:
                m_yt = via_yc + v2_h // 2 + v2_enc2[2]
                m_yb = m_yt - m3_h
            elif m3_dir == 2:
                m_yb = via_yc - v2_h // 2 - v2_enc2[3]
                m_yt = m_yb + m3_h
            else:
                m_yb = via_yc - m3_h // 2
                m_yt = m_yb + m3_h

            cur_xc = xshift + xloc
            loc = [cur_xc, via_yc]
            template.add_via_primitive('M3_M2', loc, cut_height=v2_h, enc1=v2_enc1, enc2=v2_enc2, unit_mode=True)
            tr_idx = template.grid.coord_to_track(3, cur_xc, unit_mode=True)
            m3_warrs.append(template.add_wires(3, tr_idx, m_yb, m_yt, unit_mode=True))

        if m2_xl is not None and m2_xr is not None:
            # fix M2 area rule
            m2_w_min = -(-mx_area_min // (2 * m2_h)) * 2
            m2_xc = (m2_xl + m2_xr) // 2
            m2_xl = min(m2_xl, m2_xc - m2_w_min // 2)
            m2_xr = max(m2_xr, m2_xl + m2_w_min)

            m2_yb = via_yc - m2_h // 2
            m2_yt = m2_yb + m2_h
            template.add_rect('M2', BBox(m2_xl, m2_yb, m2_xr, m2_yt, res, unit_mode=True))

        return m1_warrs, m3_warrs
