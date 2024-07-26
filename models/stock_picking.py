# -*- coding: utf-8 -*-
from odoo import api, fields, models, SUPERUSER_ID, _
from odoo.exceptions import UserError
import logging
import pytz
from datetime import datetime
from lxml import etree
import re

class Picking(models.Model):
    _inherit = "stock.picking"

    l10n_mx_edi_customs_regime_ids = fields.Many2many(
        string="Customs Regimes",
        help="Regimes associated to the good's transfer (import or export).",
        comodel_name='l10n_mx_edi.customs.regime',
        ondelete='restrict',
    )

    @api.model
    def create(self, vals):
        res = super(Picking, self).create(vals)
        if res:
            if res.picking_type_id and res.picking_type_id.picking_partner_id and res.picking_type_id.tipo_transporte:
                res.write({'partner_id': res.picking_type_id.picking_partner_id.id})
                res.write({'l10n_mx_edi_transport_type': res.picking_type_id.tipo_transporte})
        return res

    def button_validate(self):
        res = super(Picking, self).button_validate()

        logging.warning('button_validate')
        logging.warning(self.picking_type_id.tipo_operacion_porcion_id)
        if self.picking_type_id.tipo_operacion_porcion_id:
            transferencia_id = self.producto_porciones()
            logging.warning(transferencia_id)
            if  transferencia_id:
                transferencia_id.action_assign()
                transferencia_id.button_validate()
        return res


    def producto_porciones(self):
        almacen_id = self.env.user.property_warehouse_id.id
        # tipo_operacion_porciones = self.env['stock.picking.type'].search([('warehouse_id','=', almacen_id)])
        # if len(tipo_operacion_porciones) > 0:
        lista_id = {}
        transferencia_id = False
        tipo_de_operacion = self.env.user.pos_id.producto_porciones.id
        lineas = self.move_line_ids_without_package
        tipo_de_operacion = self.picking_type_id.tipo_operacion_porcion_id
        logging.warning('entra funcion')
        ubicacion_id = self.picking_type_id.tipo_operacion_porcion_id.default_location_src_id
        ubicacion_dest_id = self.picking_type_id.tipo_operacion_porcion_id.default_location_dest_id
        for linea in lineas:
            if linea.product_id.producto_porciones:
                logging.warning('linea produco porcioes')

                product_porciones_id= self.env['product.product'].search([('product_tmpl_id','=',linea.product_id.producto_porciones.id)])
                qty_done = 0
                cantidad_entera = 0
                cantidad_porcion = 0
                if linea.product_id.id not in lista_id:
                    producto_id = linea.product_id.producto_porciones.id

                    # logging.warn("linea.product_id.producto_porciones.name")
                    # logging.warn(linea.product_id.producto_porciones.name)
                    hecho = linea.qty_done
                    product_uom_qty = linea.product_uom_qty
                    product_uom_id = linea.product_uom_id.id
                    location_id = linea.location_id.id
                    location_dest_id = linea.location_dest_id.id
                    lot_id = linea.lot_id.name
                    expiration_date = linea.lot_id.expiration_date
                    cantidad_entera = linea.qty_done
                    cantidad_porcion = linea.product_id.porciones
                    qty_done = cantidad_entera * cantidad_porcion
                    # logging.warn("linea.qty_done * linea.product_id.producto_porciones.porciones")
                    # logging.warn(qty_done)
                    lista_id[linea.product_id.id]={
                    'product_id': product_porciones_id.id,
                    'qty_done': hecho,
                    'product_uom_qty': product_uom_qty,
                    'product_uom_id': product_uom_id,
                    'location_id': location_id,
                    'location_dest_id': location_dest_id,
                    'lot_id': lot_id,
                    'expiration_date': expiration_date,
                    'qty_done': qty_done
                    }
        if  len(lista_id)>0:

            transferencia_id = self.env['stock.picking'].create({
            'picking_type_id': tipo_de_operacion.id,
            'location_id': ubicacion_id.id,
            'location_dest_id': ubicacion_dest_id.id, })

            for lneas in lista_id:
                # logging.warn("lista_id[lneas]['product_id']")
                # logging.warn(lista_id[lneas]['product_id'])

                lotes = self.env['stock.production.lot'].search([('name', '=', lista_id[lneas]['lot_id']), ('product_id', '=', lista_id[lneas]['product_id'])])
                lote2_id = False
                if len(lotes)>0:
                    # logging.warn(">0")
                    lote2_id = lotes
                    # logging.warn(lote2_id)
                else:
                    # logging.warn("else")
                    lote2_id = self.env['stock.production.lot'].create({
                    'name': lista_id[lneas]['lot_id'],
                    'company_id': self.env.company.id,
                    'expiration_date': lista_id[lneas]['expiration_date'],
                    'product_id': lista_id[lneas]['product_id']})
                    # logging.warn(lote2_id)

                lineas_transferencia_id = self.env['stock.move.line'].create({
                'picking_id': transferencia_id.id,
                'product_id': lista_id[lneas]['product_id'],
                'qty_done': lista_id[lneas]['qty_done'],
                'product_uom_qty': lista_id[lneas]['product_uom_qty'],
                'product_uom_id': lista_id[lneas]['product_uom_id'],
                'location_id': ubicacion_id.id,
                'location_dest_id': ubicacion_dest_id.id,
                'qty_done': lista_id[lneas]['qty_done'],
                'lot_id': lote2_id.id
                })
        return transferencia_id

    def enviando_producto(self):
        lista_id = {}
        lista_objeto = {}
        lista_almacenes = []
        transferencia_id = False
        lineas = self.move_line_ids_without_package
        tipo_de_operacion = self.env.user.pos_id.producto_porciones.id
        ubicacion_id = self.env.user.pos_id.producto_porciones.default_location_src_id
        ubicacion_dest_id = self.env.user.pos_id.producto_porciones.default_location_dest_id

        tiendas_almacenes= self.env['pos.config'].search([])

        for tienda_almacen in tiendas_almacenes:
            if tienda_almacen.producto_porciones and tienda_almacen.producto_porciones.warehouse_id:
                lista_almacenes.append(tienda_almacen.producto_porciones.warehouse_id.id)


        # logging.warn("lista_almacenes")
        # logging.warn(lista_almacenes)


        if (self.picking_type_id.code == 'internal') and (self.picking_type_id.tipo_operacion_porcion_id) and (int(self.picking_type_id.warehouse_id.id) in lista_almacenes):
            # logging.warn("Estamos entrando C=")
            for linea in lineas:
                if (int(linea.product_id.producto_porciones.id) > 0):

                    warehouse_id = self.env.user.pos_id.producto_porciones.warehouse_id.id
                    sequence_code = self.env.user.pos_id.producto_porciones.sequence_code


                    product_porciones_id= self.env['product.product'].search([('product_tmpl_id','=',linea.product_id.producto_porciones.id)])
                    qty_done = 0
                    cantidad_entera = 0
                    cantidad_porcion = 0
                    if linea.product_id.id not in lista_id:
                        producto_id = linea.product_id.producto_porciones.id

                        # logging.warn("linea.product_id.producto_porciones.name")
                        # logging.warn(linea.product_id.producto_porciones.name)
                        hecho = linea.qty_done
                        product_uom_qty = linea.product_uom_qty
                        product_uom_id = linea.product_uom_id.id
                        location_id = linea.location_id.id
                        location_dest_id = linea.location_dest_id.id
                        lot_id = linea.lot_id.name
                        life_date = linea.lot_id.expiration_date
                        cantidad_entera = linea.qty_done
                        cantidad_porcion = linea.product_id.porciones
                        qty_done = cantidad_entera * cantidad_porcion
                        # logging.warn("linea.qty_done * linea.product_id.producto_porciones.porciones")
                        # logging.warn(qty_done)
                        lista_id[linea.product_id.id]={
                        'product_id': product_porciones_id.id,
                        'qty_done': hecho,
                        'product_uom_qty': product_uom_qty,
                        'product_uom_id': product_uom_id,
                        'location_id': location_id,
                        'location_dest_id': location_dest_id,
                        'lot_id': lot_id,
                        'life_date': life_date,
                        'qty_done': qty_done
                        }

        if  len(lista_id)>0:

            transferencia_id = self.env['stock.picking'].create({
            'picking_type_id': tipo_de_operacion,
            'location_id': ubicacion_id.id,
            'location_dest_id': ubicacion_dest_id.id, })

            for lneas in lista_id:
                # logging.warn("lista_id[lneas]['product_id']")
                # logging.warn(lista_id[lneas]['product_id'])

                lotes = self.env['stock.production.lot'].search([('name', '=', lista_id[lneas]['lot_id']), ('product_id', '=', lista_id[lneas]['product_id'])])
                lote2_id = False
                if len(lotes)>0:
                    # logging.warn(">0")
                    lote2_id = lotes
                    # logging.warn(lote2_id)
                else:
                    # logging.warn("else")
                    lote2_id = self.env['stock.production.lot'].create({
                    'name': lista_id[lneas]['lot_id'],
                    'company_id': self.env.company.id,
                    'life_date': lista_id[lneas]['life_date'],
                    'product_id': lista_id[lneas]['product_id']})
                    # logging.warn(lote2_id)

                lineas_transferencia_id = self.env['stock.move.line'].create({
                'picking_id': transferencia_id.id,
                'product_id': lista_id[lneas]['product_id'],
                'qty_done': lista_id[lneas]['qty_done'],
                'product_uom_qty': lista_id[lneas]['product_uom_qty'],
                'product_uom_id': lista_id[lneas]['product_uom_id'],
                'location_id': ubicacion_id.id,
                'location_dest_id': ubicacion_dest_id.id,
                'qty_done': lista_id[lneas]['qty_done'],
                'lot_id': lote2_id.id
                })

        return transferencia_id

    def verificar_productos_vencidos_hoy(self):
        stock_quant = self.env['stock.quant'].sudo().search([('quantity','>',0),('removal_date','!=',False)])
        timezone = pytz.timezone(self._context.get('tz') or self.env.user.tz or 'UTC')
        fecha_hoy = datetime.now().astimezone(timezone).strftime('%Y-%m-%d')
        # Sumarle un dia a la fecha de HOY

        dia_actual = datetime.now().astimezone(timezone).strftime('%d')
        mes_ao_actual = datetime.now().astimezone(timezone).strftime('%Y-%m')
        dia_mañana = int(dia_actual) + 0
        if dia_mañana<10:
            dia_mañana = '0'+str(dia_mañana)
        fecha_mañana = str(mes_ao_actual)+'-'+str(dia_mañana)
        inventario = {}
        ubicacion_actual = False
        if stock_quant:
            for linea in stock_quant:
                if linea.location_id.id not in inventario:
                    inventario[linea.location_id.id] = {'productos':[],'bodega':linea.location_id}
                if linea.lot_id and linea.lot_id.expiration_date and (linea.lot_id.expiration_date.astimezone(timezone).strftime('%Y-%m-%d') == fecha_mañana or linea.lot_id.expiration_date.astimezone(timezone).strftime('%Y-%m-%d') <= fecha_mañana or linea.lot_id.expiration_date.astimezone(timezone).strftime('%Y-%m-%d') == fecha_hoy):
                    inventario[linea.location_id.id]['productos'].append(linea)

            tiendas_ids = self.env['pos.config'].search([('envio_salida_vencimiento_id','!=', False)])
            # picking_ids = self.env['stock.picking.type'].search([('tipo_operacion_caducidad_id','!=', False)])
            if tiendas_ids:
                for tienda in tiendas_ids:
                    ubicacion_actual = tienda.envio_salida_vencimiento_id.default_location_src_id
                    if tienda.envio_salida_vencimiento_id.default_location_src_id.id in inventario:
                        destino_id = tienda.envio_salida_vencimiento_id.default_location_dest_id
                        tipo_envio_id = tienda.envio_salida_vencimiento_id
                        # logging.warn(inventario[tienda.picking_type_id.default_location_src_id.id]['productos'])
                        if len(inventario[tienda.envio_salida_vencimiento_id.default_location_src_id.id]['productos']) > 0:
                            stock_quant_lista = []
                            logging.warning('salida vencimiento')
                            logging.warning(tienda.envio_salida_vencimiento_id.id)
                            envio = {
                                'picking_type_id': tienda.envio_salida_vencimiento_id.id,
                                'location_id': ubicacion_actual.id,
                                'location_dest_id': destino_id.id,
                                'immediate_transfer': True,
                            }
                            envio_id = self.env['stock.picking'].create(envio)
                            for quant in inventario[tienda.envio_salida_vencimiento_id.default_location_src_id.id]['productos']:
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
                                    'product_uom_qty': quant.quantity,
                                    'location_dest_id': destino_id.id,
                                    # 'lot_id': quant.lot_id.id,
                                    'picking_id': envio_id.id
                                }
                                move_id = self.env['stock.move'].create(move)
                                move['move_id'] = move_id.id
                                move['lot_id'] = quant.lot_id.id
                                move['product_uom_qty'] = quant.quantity
                                stock_quant_lista.append(move)

                            # envio_id.action_confirm()
                            # envio_id.action_assign()
                            for quant in stock_quant_lista:
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
                                move_line_id = self.env['stock.move.line'].create(ml)
                            envio_id.action_assign()
                            # envio_id.button_validate()
                            # envio_id.button_validate()

                            # envio_id.button_validate()

        return inventario

    def verificar_productos_vencidos(self):
        stock_quant = self.env['stock.quant'].sudo().search([('quantity','>',0),('removal_date','!=',False)])
        timezone = pytz.timezone(self._context.get('tz') or self.env.user.tz or 'UTC')
        fecha_hoy = datetime.now().astimezone(timezone).strftime('%Y-%m-%d')
        # Sumarle un dia a la fecha de HOY

        dia_actual = datetime.now().astimezone(timezone).strftime('%d')
        mes_ao_actual = datetime.now().astimezone(timezone).strftime('%Y-%m')
        dia_mañana = int(dia_actual) + 1
        if dia_mañana<10:
            dia_mañana = '0'+str(dia_mañana)
        fecha_mañana = str(mes_ao_actual)+'-'+str(dia_mañana)
        inventario = {}
        ubicacion_actual = False
        if stock_quant:
            for linea in stock_quant:
                if linea.location_id.id not in inventario:
                    inventario[linea.location_id.id] = {'productos':[],'bodega':linea.location_id}
                if linea.lot_id and linea.lot_id.expiration_date and (linea.lot_id.expiration_date.astimezone(timezone).strftime('%Y-%m-%d') == fecha_mañana or linea.lot_id.expiration_date.astimezone(timezone).strftime('%Y-%m-%d') <= fecha_mañana or linea.lot_id.expiration_date.astimezone(timezone).strftime('%Y-%m-%d') == fecha_hoy):
                    inventario[linea.location_id.id]['productos'].append(linea)

            tiendas_ids = self.env['pos.config'].search([('envio_salida_vencimiento_id','!=', False)])
            # picking_ids = self.env['stock.picking.type'].search([('tipo_operacion_caducidad_id','!=', False)])
            if tiendas_ids:
                for tienda in tiendas_ids:
                    ubicacion_actual = tienda.envio_salida_vencimiento_id.default_location_src_id
                    if tienda.envio_salida_vencimiento_id.default_location_src_id.id in inventario:
                        destino_id = tienda.envio_salida_vencimiento_id.default_location_dest_id
                        tipo_envio_id = tienda.envio_salida_vencimiento_id
                        # logging.warn(inventario[tienda.picking_type_id.default_location_src_id.id]['productos'])
                        if len(inventario[tienda.envio_salida_vencimiento_id.default_location_src_id.id]['productos']) > 0:
                            stock_quant_lista = []
                            envio = {
                                'picking_type_id': tienda.envio_salida_vencimiento_id.id,
                                'location_id': ubicacion_actual.id,
                                'location_dest_id': destino_id.id,
                                'immediate_transfer': True,
                            }
                            envio_id = self.env['stock.picking'].create(envio)
                            for quant in inventario[tienda.envio_salida_vencimiento_id.default_location_src_id.id]['productos']:
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
                                    'product_uom_qty': quant.quantity,
                                    'location_dest_id': destino_id.id,
                                    # 'lot_id': quant.lot_id.id,
                                    'picking_id': envio_id.id
                                }
                                move_id = self.env['stock.move'].create(move)
                                move['move_id'] = move_id.id
                                move['lot_id'] = quant.lot_id.id
                                move['product_uom_qty'] = quant.quantity
                                stock_quant_lista.append(move)

                            # envio_id.action_confirm()
                            # envio_id.action_assign()
                            for quant in stock_quant_lista:
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
                                move_line_id = self.env['stock.move.line'].create(ml)
                            envio_id.action_assign()
                            # envio_id.button_validate()
                            # envio_id.button_validate()

                            # envio_id.button_validate()

        return inventario

class StockPickingType(models.Model):
    _inherit = "stock.picking.type"

    tipo_operacion_caducidad_id = fields.Many2one('stock.picking.type', string='Tipo operacion caducidad')
    # porciones = fields.Boolean('Porciones?')
    tipo_operacion_porcion_id = fields.Many2one('stock.picking.type', string='Tipo operacion porcion')
    picking_partner_id = fields.Many2one('res.partner','Contacto')
    tipo_transporte = fields.Selection([('00', 'Sin uso de Carreteras Federales'), ('01', 'Autotransporte Federal')], string='Tipo de transporte')
