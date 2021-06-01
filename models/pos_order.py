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

    def obtener_inventario_producto(self,producto,tipo_ubicacion,lote):
        cantidad_producto = 0
        producto_id = self.env['product.product'].search([('id','=',producto)])
        tipo_ubicacion_id = self.env['stock.picking.type'].search([('id','=',tipo_ubicacion)])
        lote_id = False
        logging.warn(lote_id)
        if producto_id and tipo_ubicacion_id:
            if lote:
                lote_id = self.env['stock.production.lot'].search([('name','=',lote)])
                if lote_id:
                    existencia = self.env['stock.quant']._get_available_quantity(producto_id,tipo_ubicacion_id.default_location_src_id,lote_id)
                    cantidad_producto = existencia
            else:
                quant = self.env['stock.quant'].search([('product_id','=',producto_id.id),('location_id','=',tipo_ubicacion_id.default_location_src_id.id)])
                if quant:
                    cantidad_producto = quant.quantity
        return cantidad_producto
