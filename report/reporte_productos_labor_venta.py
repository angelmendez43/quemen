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

class ReportProductosLaborVenta(models.AbstractModel):
    _name = 'report.quemen.reporte_productos_labor_venta'

    def productos_vencimiento(self,fecha_vencimiento, tienda_id):
        logging.warn("tienda_id")
        logging.warn(tienda_id)

        tienda_id = self.env['pos.config'].search([('id','=',tienda_id[0])])

        ubicacion_id = tienda_id.picking_type_id.default_location_src_id

        stock_id = self.env['stock.quant'].search([('location_id','=',ubicacion_id.id)])
        inventario = []
        if stock_id:
            for producto in stock_id:
                logging.warn(producto.lot_id.life_date.strftime('%Y-%m-%d') if producto.lot_id.life_date else '')
                if producto.lot_id and producto.lot_id.life_date and producto.lot_id.life_date.strftime('%Y-%m-%d') == fecha_vencimiento:
                    logging.warn(producto.inventory_quantity)
                    inventario.append(producto)
        logging.warn(inventario)
        return inventario

    def fecha_hora_actual(self):
        logging.warn(datetime.datetime.now())

        timezone = pytz.timezone(self._context.get('tz') or self.env.user.tz or 'UTC')
        fecha_hora = datetime.datetime.now().astimezone(timezone).strftime('%d/%m/%Y %H:%M:%S')
        return fecha_hora

    def obtener_tienda(self, tienda_id):
        tienda = self.env['pos.config'].search([('id','=',tienda_id[0])])

        return tienda;

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
        tienda_id = data['form']['tienda_id']
        return {
            'doc_ids': self.ids,
            'doc_model': model,
            'data': data['form'],
            'docs': docs,
            'productos_vencimiento': self.productos_vencimiento,
            'fecha_hora_actual': self.fecha_hora_actual,
            'obtener_tienda': self.obtener_tienda
            # 'mes_letras': self.mes_letras,
            # 'fecha_hoy': self.fecha_hoy,
            # 'a_letras': odoo.addons.hr_gt.a_letras,
            # 'datos_recibo': self.datos_recibo,
            # 'lineas': self.lineas,
            # 'horas_extras': self.horas_extras,
        }
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
