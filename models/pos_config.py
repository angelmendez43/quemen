# -*- encoding: utf-8 -*-

from odoo import models, fields, api, _

class PosConfig(models.Model):
    _inherit = 'pos.config'

    efectivo_maximo = fields.Float(string="Efectivo máxmio")
    # cupones = fields.Boolean('Cupones')
    cliente_id = fields.Many2one('res.partner','Cliente por defecto')
    tipo_venta = fields.Boolean('Tipo de venta')
    envio_salida_vencimiento_id = fields.Many2one('stock.picking.type','Envio de salida por vencimiento')
    # promociones_ids = fields.Many2many('quemen.promociones','quemen_promociones_rel',string="Promociones")
    producto_porciones = fields.Many2one('stock.picking.type', string="tipo de operacion entrada porciones")
    ubicacion_id = fields.Many2one('stock.location', 'Ubicaciíon',store=True, related='picking_type_id.default_location_src_id' )
    terminos_condiciones = fields.Text(string="Terminos y condiciones para pedido espcial: ")

    # cupones no se migra
    # envio salida vencimiento pendiente
    # promociones ids se elimina


    # productos porciones se migra
    # efectivo maximo si se migra
    # Cliente por defecto se queda
    # Tipo de venta se queda
