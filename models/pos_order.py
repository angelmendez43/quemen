# -*- encoding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError
import logging

class PosOrder(models.Model):
    _inherit = 'pos.order'

    tipo_venta = fields.Selection([ ('mesas', 'Mesas'),('mostrador', 'Mostrador'),('domicilio', 'A domicilio'),('especial', 'Pedidos especiales')],'Tipo de venta')
