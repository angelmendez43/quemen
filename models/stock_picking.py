# -*- coding: utf-8 -*-
from odoo import api, fields, models, SUPERUSER_ID, _
from odoo.exceptions import UserError
import logging
import pytz

class Picking(models.Model):
    _inherit = "stock.picking"

    def button_validate(self):
        logging.warn('123456789')
        if self.picking_type_id.code == 'internal':
            if self.location_dest_id.id == self.env.user.pos_id.picking_type_id.default_location_src_id.id or self.env.user.id == 1:
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
        fecha_hoy = datetime.datetime.now().astimezone(timezone).strftime('%Y-%m-%d')
        logging.warn(fecha_hoy)
        inventario = {}
        if stock_quant:
            for linea in stock_quant:
                if linea.location_id.id not in inventario:
                    inventario[linea.location_id.id] = {'productos':[],'bodega':linea.location_id}

                if linea.lot_id and linea.lot_id.life_date and linea.lot_id.life_date.strftime('%Y-%m-%d') == fecha_hoy:
                    logging.warn(linea.lot_id.life_date)
                    inventario[linea.location_id.id]['productos'].append(linea)

        logging.warn(inventario)
        logging.warn('termina')
        return inventario

class StockPickingType(models.Model):
    _inherit = "stock.picking.type"

    devolucion_productos_vencidos = fields.Boolean('¿Desea utilizar este tipo de albaran para devolucion productos vencidos automatico?')
