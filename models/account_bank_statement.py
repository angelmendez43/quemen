# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.osv import expression
from odoo.tools import float_is_zero
from odoo.tools import float_compare, float_round, float_repr
from odoo.tools.misc import formatLang, format_date
from odoo.exceptions import UserError, ValidationError

import time
import math
import base64

class AccountCashboxLine(models.Model):
    _inherit = 'account.cashbox.line'

    denominacion = fields.Selection([ ('billete', 'Billete'),('moneda', 'Moneda')],'Denominación', default='billete')
