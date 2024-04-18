# -*- encoding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError
import logging

class PosOrder(models.Model):
    _inherit = 'pos.order'

    tipo_venta = fields.Selection([ ('mesas', 'Mesas'),('mostrador', 'Mostrador'),('domicilio', 'A domicilio'),('especial', 'Pedidos especiales')],'Tipo de venta')
    pedido_especial = fields.Boolean('Pedido especial')
    fecha_especial = fields.Date(string="Fecha entrega")
    hora_especial = fields.Char(string="Hora entrega");
    observaciones_especial = fields.Char("Observaciones")
    sucursal_entrega = fields.Char("Sucursal de entrega")
    autorizo_especial = fields.Char("Autorizó")

    @api.model
    def _order_fields(self, ui_order):
        res = super(PosOrder, self)._order_fields(ui_order)
        session = self.env['pos.session'].search([('id', '=', res['session_id'])], limit=1)

        if 'fecha' in ui_order:
            mal_formato = ui_order['fecha']
    
            res['hora_especial'] = ui_order['hora']
            res['fecha_especial'] = ui_order['fecha']
            res['observaciones_especial']= ui_order['observaciones']
            res['sucursal_entrega'] = ui_order['sucursal_entrega']
            res['autorizo_especial']=ui_order['autorizo']

        return res