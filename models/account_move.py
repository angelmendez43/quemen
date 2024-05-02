# -*- coding: utf-8 -*-
import base64
from odoo import api, fields, models, SUPERUSER_ID, _
from odoo.exceptions import UserError
import logging
import pytz
from datetime import datetime

class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    pedido_referencia = fields.Char('Pedido referencia')