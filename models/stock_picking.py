# -*- coding: utf-8 -*-
from odoo import api, fields, models, SUPERUSER_ID, _
from odoo.exceptions import UserError
import logging
import pytz
from datetime import datetime

class Picking(models.Model):
    _inherit = "stock.picking"

    def button_validate(self):
        logging.warn('123456789')
        logging.warn(self.env.user)
        if self.picking_type_id.code == 'internal':
            if self.env.user.id == 2 or self.location_dest_id.id == self.env.user.pos_id.picking_type_id.default_location_src_id.id:
                return super(Picking, self).button_validate()
            else:
                return UserError(_('No tiene permisos para validar'))
        else:
            return super(Picking, self).button_validate()
        # if self.env.user.pos_id.picking_type_id
        # if self.env.user.has_group('quemen.quemen_validar_envio_tienda') and self.picking_type_id.code == 'internal':
        #     return res
        # elif self.env.user.has_group('quemen.quemen_validar_envio_tienda') == False and self.picking_type_id.code != 'internal' :
        #     return res
        # else:
        #     raise UserError(_('No tiene permisos para validar'))

    def verificar_productos_vencidos(self):
        logging.warn('verificar para albaran')
        stock_quant = self.env['stock.quant'].search([('quantity','>',0)])
        timezone = pytz.timezone(self._context.get('tz') or self.env.user.tz or 'UTC')
        fecha_hoy = datetime.now().astimezone(timezone).strftime('%Y-%m-%d')
        logging.warn(fecha_hoy)
        logging.warn('entra')
        inventario = {}
        salida = self.env.user.pos_id.envio_salida_vencimiento_id
        ubicacion_actual = self.env.user.pos_id.picking_type_id.default_location_src_id
        if stock_quant:
            for linea in stock_quant:
                if linea.location_id.id not in inventario:
                    inventario[linea.location_id.id] = {'productos':[],'bodega':linea.location_id}

                if linea.lot_id and linea.lot_id.life_date and linea.lot_id.life_date.strftime('%Y-%m-%d') == fecha_hoy:
                    logging.warn(linea.lot_id.life_date)
                    inventario[linea.location_id.id]['productos'].append(linea)

            tiendas_ids = self.env['pos.config'].search([])
            logging.warn(tiendas_ids)
            if tiendas_ids:
                for tienda in tiendas_ids:
                    if tienda.envio_salida_vencimiento_id and tienda.picking_type_id.default_location_src_id.id in inventario:
                        logging.warn('1')
                        logging.warn(inventario[tienda.picking_type_id.default_location_src_id.id]['productos'])
                        if len(inventario[tienda.picking_type_id.default_location_src_id.id]['productos']) > 0:
                            logging.warn('2')
                            stock_quant = []
                            envio = {
                                'picking_type_id': salida.id,
                                'location_id': ubicacion_actual.id,
                                'location_dest_id': salida.default_location_dest_id.id,
                            }
                            envio_id = self.env['stock.picking'].create(envio)
                            logging.warn('ENVIO')
                            for quant in inventario[tienda.picking_type_id.default_location_src_id.id]['productos']:
                                # linea_envio = {
                                #     'product_id': quant.product_id.id,
                                #     'location_id': ubicacion_actual.id,
                                #     'product_uom_id': quant.product_id.uom_id.id,
                                #     'location_dest_id': salida.default_location_dest_id.id,
                                #     'lot_id': quant.lot_id.id,
                                #     'picking_id': envio_id.id
                                # }
                                move = {
                                    'product_id': quant.product_id.id,
                                    'name': quant.product_id.name,
                                    'product_uom': quant.product_id.uom_id.id,

                                    'location_id': ubicacion_actual.id,
                                    'product_uom_qty': 0,
                                    'location_dest_id': salida.default_location_dest_id.id,
                                    # 'lot_id': quant.lot_id.id,
                                    'picking_id': envio_id.id
                                }
                                move_id = self.env['stock.move'].create(move)
                                move['move_id'] = move_id.id
                                move['lot_id'] = quant.lot_id.id
                                move['product_uom_qty'] = quant.quantity
                                stock_quant.append(move)

                            envio_id.action_confirm()
                            for quant in stock_quant:
                                ml = {
                                    'product_id': quant['product_id'],
                                    'location_id': ubicacion_actual.id,
                                    'product_uom_id': quant['product_uom'],
                                    'location_dest_id': salida.default_location_dest_id.id,
                                    'lot_id': quant['lot_id'],
                                    'move_id': quant['move_id'],
                                    'qty_done': quant['product_uom_qty'],
                                    'picking_id':envio_id.id,
                                }
                                self.env['stock.move.line'].create(ml)
                            envio_id.button_validate()
        logging.warn(inventario)
        logging.warn('termina')
        return inventario

class StockPickingType(models.Model):
    _inherit = "stock.picking.type"

    devolucion_productos_vencidos = fields.Boolean('¿Desea utilizar este tipo de albaran para devolucion productos vencidos automatico?')
