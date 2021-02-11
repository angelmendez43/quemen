# -*- encoding: utf-8 -*-

from odoo import api, models, fields
from datetime import date
import datetime
import time
import dateutil.parser
from dateutil.relativedelta import relativedelta
from dateutil import relativedelta as rdelta
from odoo.fields import Date, Datetime
import logging
from operator import itemgetter
import pytz
# import odoo.addons.hr_gt.a_letras

class ReportEntregaValores(models.AbstractModel):
    _name = 'report.quemen.reporte_entrega_valores'


    def _get_entrega_valores(self, fecha_inicio,fecha_fin):
        sesiones = self.env['pos.session'].search([('config_id','=',self.env.user.pos_id.id),('start_at','>=',fecha_inicio),('start_at','<=',fecha_fin)],order='start_at asc')
        fondo_caja = {}
        retiro_efectivo = {}
        logging.warn(sesiones)
        if sesiones:
            for sesion in sesiones:
                if sesion.retiros_ids:
                    fecha_sesion = dateutil.parser.parse(str(sesion.start_at)).date()
                    if fecha_sesion not in retiro_efectivo:
                        retiro_efectivo[fecha_sesion] = {'fecha': fecha_sesion, 'retiros': [],'total_retiros': 0}

                    for retiro in sesion.retiros_ids:
                        retiro_efectivo[fecha_sesion]['retiros'].append(retiro)
                        retiro_efectivo[fecha_sesion]['total_retiros'] += retiro.total

        return {'retiro_efectivo': retiro_efectivo.values()}

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
                    inventario[linea.location_id.id] = {'productos':[],'ubicacion':linea.location_id}

                if linea.lot_id and linea.lot_id.life_date and linea.lot_id.life_date.strftime('%Y-%m-%d') == fecha_hoy:
                    logging.warn(linea.lot_id.life_date)
                    inventario[linea.location_id.id]['productos'].append(linea)

        logging.warn(inventario)
        logging.warn('termina')
        inventario = inventario.values()
        for dato in inventario:
            logging.warn(dato)
            if len(dato['productos']) > 0:
                ubicacion = dato['ubicacion']
                tipo_albaran = self.env['stock.picking.type'].search([('default_location_src_id','=', ubicacion.id),('devolucion_productos_vencidos','=',True)])
                if tipo_albaran:
                    logging.warn('tipo albaran')
                    logging.warn(tipo_albaran)
                    moves = {}
                    envio = {'picking_type_id': tipo_albaran.id,'location_id': tipo_albaran.default_location_src_id.id, 'location_dest_id': tipo_albaran.default_location_dest_id.id}
                    picking_id = self.env['stock.picking'].create(envio)
                    for linea in dato['productos']:
                        mv = {'name': linea.product_id.name,'product_id': linea.product_id.id,
                        'product_uom':linea.product_uom_id.id,
                        'product_uom_qty': linea.quantity,'picking_id':picking_id.id,'location_id':tipo_albaran.default_location_src_id.id,'location_dest_id':tipo_albaran.default_location_dest_id.id}
                        move_id = self.env['stock.move'].create(mv)
                        # move_id.write({'move_line_ids':[(0, 0, {'move_id':move_id.id,'location_id': move_id.location_id.id, 'location_dest_id': move_id.location_dest_id.id,'lot_id':linea.lot_id.id,'qty_done': linea.quantity,'product_uom_id': linea.product_uom_id.id,'company_id':tipo_albaran.company_id.id})]})
                        if move_id.id not in moves:
                            moves[move_id.id] = {'move': move_id,'lot_id': linea.lot_id}
                    picking_id.action_assign()

                    # for linea in picking_id.

                    # for m in moves.values():
                    #     ml = {'move_id': m['move'].id,'location_id': m['move'].location_id.id, 'location_dest_id': m['move'].location_dest_id.id,'lot_id':m['lot_id'].id,'qty_done': m['move'].product_uom_qty,'product_uom_id': m['move'].product_uom.id,'company_id':tipo_albaran.company_id.id}
                    #     move_line = self.env['stock.move.line'].create(ml)
                        # if move_id:
                        #     ml = {'move_id':move_id.id,'location_id': move_id.location_id.id, 'location_dest_id': move_id.location_dest_id.id,'lot_id':linea.lot_id.id,'qty_done': linea.quantity,'product_uom_id': linea.product_uom_id.id,'company_id':tipo_albaran.company_id.id}
                        #     move_line = self.env['stock.move.line'].create(ml)

        return inventario

    def productos_existencia(self):
        # logging.warn(fecha_vencimiento)
        self.verificar_productos_vencidos()
        ubicacion_id = self.env.user.pos_id.picking_type_id.default_location_src_id
        stock_id = self.env['stock.quant'].search([('location_id','=',ubicacion_id.id)])
        logging.warn(stock_id)
        inventario = {}
        if stock_id:
            for linea in stock_id:
                if linea.lot_id and linea.lot_id.life_date:
                    if str(linea.product_id.categ_id.parent_id.id)+'/'+str(linea.product_id.categ_id.id) not in inventario:
                        inventario[str(linea.product_id.categ_id.parent_id.id)+'/'+str(linea.product_id.categ_id.id)] = {'productos': [],'categoria_padre': linea.product_id.categ_id.parent_id.name, 'categoria_hija': linea.product_id.categ_id.name }

                    inventario[str(linea.product_id.categ_id.parent_id.id)+'/'+str(linea.product_id.categ_id.id)]['productos'].append(linea)


        logging.warn('product existencias')
        logging.warn(inventario)
        return inventario

    def fecha_hora_actual(self):
        logging.warn(datetime.datetime.now())

        timezone = pytz.timezone(self._context.get('tz') or self.env.user.tz or 'UTC')
        fecha_hora = datetime.datetime.now().astimezone(timezone).strftime('%d/%m/%Y %H:%M:%S')
        return fecha_hora
    # def pagos_deducciones(self,o):
    #     ingresos = 0
    #     descuentos = 0
    #     datos = {'ordinario': 0, 'extra_ordinario':0,'bonificacion':0}
    #     for linea in o.linea_ids:
    #         if linea.salary_rule_id.id in o.company_id.ordinario_ids.ids:
    #             datos['ordinario'] += linea.total
    #         elif linea.salary_rule_id.id in o.company_id.extra_ordinario_ids.ids:
    #             datos['extra_ordinario'] += linea.total
    #         elif linea.salary_rule_id.id in o.company_id.bonificacion_ids.ids:
    #             datos['bonificacion'] += linea.total
    #     return True

    # @api.model
    # def _get_report_values(self, docids, data=None):
    #     return self.get_report_values(docids, data)


# {'context': {'tz': False, 'uid': 1, 'params':
# {'action': 473}, 'active_model': 'hr_gt.recibo_pago.wizard', 'active_id': 5, 'active_ids': [5], 'search_disable_custom_filters': True}, 'ids': [], 'model': 'hr_gt.recibo_pago.wizard', 'form': {'id': 5, 'nomina_ids': [17], 'formato_recibo_pago_id': [1, 'RECIBO DE PAGO PLANILLA'], 'fecha_inicio': False, 'fecha_fin': False, 'create_uid': [1, 'Administrator'], 'create_date': '2020-06-22 01:42:19', 'write_uid': [1, 'Administrator'], 'write_date': '2020-06-22 01:42:19', 'display_name': 'hr_gt.recibo_pago.wizard,5', '__last_update': '2020-06-22 01:42:19'}}

    @api.model
    def _get_report_values(self, docids, data=None):
        model = self.env.context.get('active_model')
        docs = self.env[model].browse(self.env.context.get('active_ids', []))
        fecha_inicio = data['form']['fecha_inicio']
        fecha_fin = data['form']['fecha_fin']
        tienda_id = data['form']['tienda_id']
        fecha_generacion = data['form']['fecha_generacion']

        logging.warn(data['form'])
        return {
            'doc_ids': self.ids,
            'doc_model': model,
            'data': data['form'],
            'docs': docs,
            'fecha_inicio': fecha_inicio,
            'fecha_fin': fecha_fin,
            'tienda_id': tienda_id,
            'fecha_generacion': fecha_generacion,
            '_get_entrega_valores': self._get_entrega_valores,
            # 'productos_existencia': self.productos_existencia,
            # 'fecha_hora_actual': self.fecha_hora_actual,
            # 'mes_letras': self.mes_letras,
            # 'fecha_hoy': self.fecha_hoy,
            # 'a_letras': odoo.addons.hr_gt.a_letras,
            # 'datos_recibo': self.datos_recibo,
            # 'lineas': self.lineas,
            # 'horas_extras': self.horas_extras,
        }
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
