# -*- encoding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
import time
import base64
import xlsxwriter
import io
import logging
from datetime import date
import datetime
import dateutil.parser
from dateutil.relativedelta import relativedelta
from dateutil import relativedelta as rdelta
from odoo.fields import Date, Datetime

class reporte_codigo_barras_wizard(models.TransientModel):
    _name = 'quemen.reporte_codigo_barras.wizard'

    product_ids = fields.Many2many('quemen.op_lote_line',string='Productos')

    def print_report(self):
        data = {
             'ids': [],
             'model': 'quemen.reporte_codigo_barras.wizard',
             'form': self.read()[0],
        }
        logging.warning('1')
        # product_ids = self.env['quemen.op_lote_line'].search([('id','=',data['form']['product_ids'] )])
        product_ids = data['form']['product_ids']
        logging.warning(product_ids)
        data['product_ids'] = product_ids
        # logging.warning('2')
        # logging.warning(self.read()[0]['form'])
        report_reference = self.env.ref('quemen.action_report_codigo_barras_lote').report_action(self, data=data)
        report_reference.update({'close_on_report_download': True})
        return report_reference
