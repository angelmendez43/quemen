# -*- coding: utf-8 -*-
from odoo import api, fields, models, SUPERUSER_ID, _
from odoo.exceptions import UserError
import logging
import pytz
from datetime import datetime

class StockQuant(models.Model):
    _inherit = "stock.quant"

    referencia_interna = fields.Char('Referencia interna',related="product_id.default_code",store=True)
