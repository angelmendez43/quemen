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

    def buscar_inventario(self, lotes, ubicacion_id):
        lote_no_existente = []
        logging.warning('buscar_inventario')
        logging.warning(lotes)
        logging.warning(ubicacion_id)
        for i in lotes:
            logging.warning(i)
            stock_quant = self.env['stock.quant'].search([('lot_id.name','=',i['lote']), ('location_id','=',ubicacion_id) ,('product_id','=', i['producto'])])
            if len(stock_quant) == 0:
                lote_no_existente.append(i['lote'])
        logging.warning('lote no existe')
        logging.warning(lote_no_existente)
        return lote_no_existente

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

    def _prepare_invoice_line(self, order_line):
        res = super(PosOrder, self)._prepare_invoice_line(order_line)
        if res:
            res['pedido_referencia'] = order_line.order_id.name
            res['sesion_id'] = order_line.order_id.session_id.id
            res['pedido_id'] = order_line.order_id.id
        return res
