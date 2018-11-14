# -*- coding: utf-8 -*-

from typing import Dict, Any, Set

import os
import pkg_resources

from bag.design.module import ResIdealModuleBase
from bag.design.database import ModuleDB


# noinspection PyPep8Naming
class BAG_prim__res_ideal(ResIdealModuleBase):
    """design module for BAG_prim__res_ideal.
    """

    yaml_file = pkg_resources.resource_filename(__name__,
                                                os.path.join('netlist_info',
                                                             'res_ideal.yaml'))

    def __init__(self, database, lib_name, params, used_names, **kwargs):
        # type: (ModuleDB, str, Dict[str, Any], Set[str], **Any) -> None
        ResIdealModuleBase.__init__(self, self.yaml_file, database, lib_name, params, used_names, **kwargs)

