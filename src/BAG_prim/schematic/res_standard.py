# -*- coding: utf-8 -*-

from typing import Dict, Any

import os
import pkg_resources

from bag.design.module import ResPhysicalModuleBase
from bag.design.database import ModuleDB


# noinspection PyPep8Naming
class BAG_prim__res_standard(ResPhysicalModuleBase):
    """design module for BAG_prim__res_standard.
    """

    yaml_file = pkg_resources.resource_filename(__name__,
                                                os.path.join('netlist_info',
                                                             'res_standard.yaml'))

    def __init__(self, database, params, **kwargs):
        # type: (ModuleDB, Dict[str, Any], **Any) -> None
        ResPhysicalModuleBase.__init__(self, self.yaml_file, database, params, **kwargs)
