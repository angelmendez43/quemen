# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import json
import datetime
import math
import re
import warnings

from collections import defaultdict
from dateutil.relativedelta import relativedelta

from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError
from odoo.tools import float_compare, float_round, float_is_zero, format_datetime
from odoo.tools.misc import OrderedSet, format_date, groupby as tools_groupby

from odoo.addons.stock.models.stock_move import PROCUREMENT_PRIORITIES
import logging
SIZE_BACK_ORDER_NUMERING = 3

class MrpProduction(models.Model):
    """ Manufacturing Orders """
    _inherit = 'mrp.production'

    @api.onchange('bom_id', 'product_id', 'product_qty', 'product_uom_id', 'move_raw_ids')
    def _onchange_move_raw(self):
        res = super(MrpProduction, self)._onchange_move_raw()
        logging.warning('CAMBIANDO UBICACION')
        for line in self.move_raw_ids:
            if len(line.product_id.bom_ids) > 0:
                if line.product_id.bom_ids[0].picking_type_id:
                    line.location_id = line.product_id.bom_ids[0].picking_type_id.default_location_dest_id.id