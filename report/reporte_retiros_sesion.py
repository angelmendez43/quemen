# -*- encoding: utf-8 -*-

from odoo import api, models, fields
from datetime import date
from datetime import datetime
import datetime
import time
import dateutil.parser
from dateutil.relativedelta import relativedelta
from dateutil import relativedelta as rdelta
from odoo.fields import Date, Datetime
import logging
from operator import itemgetter
import pytz

class ReporteRetiros(models.AbstractModel):
    _name = 'report.quemen.reporte_retiros_sesion'

    def _get_entrega_valores(self, retiro_id):
        #punto_venta
        punto_venta = self.env.user.pos_id.name
        retiros_pos = self.env['quemen.retiros'].search([('id', '=', retiro_id[0])])
        hora_fecha = retiros_pos.fecha_hora
        hora_correct = fields.Datetime.to_string(fields.Datetime.context_timestamp(self.with_context(tz=self.env.user.tz), fields.Datetime.from_string(hora_fecha)))

        fecha = dateutil.parser.parse(hora_correct)
        formato_correcto = fecha.strftime('%d/%m/%Y')

        retiros = {}

        retiros={
        'punto_venta': punto_venta,
        'nombre': retiros_pos.name,
        'sesion': retiros_pos.session_id.name,
        'hora_correct': formato_correcto,
        'usuario': retiros_pos.usuario_id.name,
        'motivo': retiros_pos.motivo,
        'total': retiros_pos.total
        }

        return {'retiros': retiros}


    @api.model
    def _get_report_values(self, docids, data=None):
        model = self.env.context.get('active_model')
        retiro_id = data['form']['retiro_id']

        return {
            'doc_ids': docids,
            'doc_model': model,
            'retiro_id': retiro_id,
            '_get_entrega_valores': self._get_entrega_valores,

            }
