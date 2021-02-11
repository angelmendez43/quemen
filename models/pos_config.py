# -*- encoding: utf-8 -*-

from odoo import models, fields, api, _

class PosConfig(models.Model):
    _inherit = 'pos.config'

    efectivo_maximo = fields.Float(string="Efectivo máxmio")
    cupones = fields.Boolean('Cupones')
    cliente_id = fields.Many2one('res.partner','Cliente por defecto')
    tipo_venta = fields.Boolean('Tipo de venta')
    envio_salida_vencimiento_id = fields.Many2one('stock.picking.type','Envio de salida por vencimiento')
    promociones_ids = fields.Many2many('quemen.promociones','quemen_promociones_rel',string="Promociones")
