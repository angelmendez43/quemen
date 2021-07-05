# -*- coding: utf-8 -*-
from odoo import api, fields, models, SUPERUSER_ID, _
from odoo.exceptions import UserError
import logging
import pytz
from datetime import datetime

class Picking(models.Model):
    _inherit = "stock.picking"

    # def button_validate(self):
    #     logging.warn('123456789')
    #     logging.warn(self.env.user)
    #     if self.picking_type_id.code == 'internal':
    #         if self.env.user.id == 2 or self.location_dest_id.id == self.env.user.pos_id.picking_type_id.default_location_src_id.id:
    #             return super(Picking, self).button_validate()
    #         else:
    #             return UserError(_('No tiene permisos para validar'))
    #     else:
    #         return super(Picking, self).button_validate()
    #         ____________________________________________________
        # if self.env.user.pos_id.picking_type_id
        # if self.env.user.has_group('quemen.quemen_validar_envio_tienda') and self.picking_type_id.code == 'internal':
        #     return res
        # elif self.env.user.has_group('quemen.quemen_validar_envio_tienda') == False and self.picking_type_id.code != 'internal' :
        #     return res
        # else:
        #     raise UserError(_('No tiene permisos para validar'))

    # def button_validate(self):
    #     res = super(Picking, self).button_validate()
    #     # productos = self.enviando_producto()
    #     # logging.warn("PRODUCTOS")
    #     # logging.warn(productos)
    #
    #     return res

    def enviando_producto(self):
        lista_id = {}
        lista_objeto = {}
        lineas = self.move_line_ids_without_package

        for linea in lineas:
            if (linea.product_id.producto_porciones.name != False) and (linea.product_id.porciones > 0):
                tipo_de_operacion = self.env.user.pos_id.producto_porciones.id
                warehouse_id = self.env.user.pos_id.producto_porciones.warehouse_id.id
                sequence_code = self.env.user.pos_id.producto_porciones.sequence_code
                logging.warn("linea.product_id.producto_porciones.name")
                logging.warn(linea.product_id.producto_porciones.name)
                logging.warn(linea.product_id.producto_porciones.id)

                if linea.product_id.id not in lista_id:
                    producto_id = linea.product_id.producto_porciones.id

                    hecho = linea.qty_done
                    product_uom_qty = linea.product_uom_qty
                    product_uom_id = linea.product_uom_id.id
                    location_id = linea.location_id.id
                    location_dest_id = linea.location_dest_id.id

                    lista_id[lineas.product_id.id]={
                    'product_id': producto_id,
                    'qty_done': hecho,
                    'product_uom_qty': product_uom_qty,
                    'product_uom_id': product_uom_id,
                    'location_id': location_id,
                    'location_dest_id': location_dest_id
                    }

                    #lista_objeto = {'picking_type_id': tipo_de_operacion}

        transferencia_id = self.env['stock.picking'].create({ 'picking_type_id': tipo_de_operacion })

        for lneas in lista_id:
            lineas_transferencia_id = self.env['stock.move.line'].create({
            'picking_id': transferencia_id.id,
            'product_id': lista_id[lneas]['product_id'],
            'qty_done': lista_id[lneas]['qty_done'],
            'product_uom_qty': lista_id[lneas]['product_uom_qty'],
            'product_uom_id': lista_id[lneas]['product_uom_id'],
            'location_id': lista_id[lneas]['location_id'],
            'location_dest_id': lista_id[lneas]['location_dest_id']
            })

        return transferencia_id, lineas_transferencia_id



    def verificar_productos_vencidos(self):
        logging.warn('verificar para albaran')
        stock_quant = self.env['stock.quant'].search([('quantity','>',0)])
        timezone = pytz.timezone(self._context.get('tz') or self.env.user.tz or 'UTC')
        fecha_hoy = datetime.now().astimezone(timezone).strftime('%Y-%m-%d')
        logging.warn(fecha_hoy)
        logging.warn('entra')
        inventario = {}
        salida = self.env.user.pos_id.envio_salida_vencimiento_id
        ubicacion_actual = False
        if stock_quant:
            for linea in stock_quant:
                if linea.location_id.id not in inventario:
                    inventario[linea.location_id.id] = {'productos':[],'bodega':linea.location_id}

                if linea.lot_id and linea.lot_id.life_date and linea.lot_id.life_date.strftime('%Y-%m-%d') == fecha_hoy:
                    logging.warn(linea.lot_id.life_date)
                    inventario[linea.location_id.id]['productos'].append(linea)

            tiendas_ids = self.env['pos.config'].search([])

            logging.warn('TIENDA E INVENTARIO')
            logging.warn(tiendas_ids)
            logging.warn(inventario)
            if tiendas_ids:
                for tienda in tiendas_ids:
                    ubicacion_actual = tienda.picking_type_id.default_location_src_id
                    if tienda.envio_salida_vencimiento_id and tienda.picking_type_id.default_location_src_id.id in inventario:
                        destino_id = tienda.envio_salida_vencimiento_id.default_location_dest_id
                        tipo_envio_id = tienda.envio_salida_vencimiento_id
                        logging.warn('1')
                        # logging.warn(inventario[tienda.picking_type_id.default_location_src_id.id]['productos'])
                        if len(inventario[tienda.picking_type_id.default_location_src_id.id]['productos']) > 0:
                            logging.warn('2')
                            stock_quant = []
                            envio = {
                                'picking_type_id': tienda.envio_salida_vencimiento_id.id,
                                'location_id': ubicacion_actual.id,
                                'location_dest_id': destino_id.id,
                            }
                            logging.warn(envio)
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
                                    'location_dest_id': destino_id.id,
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
                                    'location_dest_id': destino_id.id,
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
