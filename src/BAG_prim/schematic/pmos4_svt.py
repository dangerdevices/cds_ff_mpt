# -*- coding: utf-8 -*-

from typing import Dict, Any

import os
import pkg_resources

from bag.design.module import MosModuleBase
from bag.design.database import ModuleDB


# noinspection PyPep8Naming
class BAG_prim__pmos4_svt(MosModuleBase):
    """design module for BAG_prim__pmos4_svt.
    """

    def __init__(self, database, params, **kwargs):
        # type: (ModuleDB, Dict[str, Any], **Any) -> None
        MosModuleBase.__init__(self, '', database, params, **kwargs)

