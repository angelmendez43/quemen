# -*- encoding: utf-8 -*-

from openerp import models, fields, api, _
from odoo.exceptions import UserError
import logging

class PosOrder(models.Model):
    _inherit = 'pos.order'

    tipo_venta = fields.Selection([ ('mesas', 'Mesas'),('mostrador', 'Mostrador'),('domicilio', 'A domicilio'),('especial', 'Pedidos especiales')],'Tipo de venta')

    def deshabilitar_cupon(self,cupon):
        logging.warn(cupon)
        cupon_id = self.env['sale.coupon'].search([('id','=',cupon)])
        if cupon_id:
            cupon_id.write({'state': 'used'})
        return True

    def habilitar_cupon(self,cupon):
        logging.warn(cupon)
        cupon_id = self.env['sale.coupon'].search([('code','=',str(cupon))])
        if cupon_id:
            cupon_id.write({'state': 'new'})
        return True

    @api.model
    def _order_fields(self, ui_order):
        res = super(PosOrder, self)._order_fields(ui_order)
        sesion = self.env['pos.session'].search([('id', '=', res['session_id'])], limit=1)
        logging.warn(res)
        if sesion.config_id.tipo_venta:
            res['tipo_venta'] = ui_order['tipo_venta'] or ""
        return res
