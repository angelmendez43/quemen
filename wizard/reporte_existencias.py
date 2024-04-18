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

class reporte_existencias_wizard(models.TransientModel):
    _name = 'quemen.reporte_existencias.wizard'

    def _tienda_actual(self):
        tienda = False
        logging.warning('usuario ')
        logging.warning(self.env.user)
        almacen_id = self.env.user.property_warehouse_id.id
        tienda_id = self.env['pos.config'].search([('warehouse_id','=',almacen_id)])
        if len(tienda_id) > 0:
            tienda = tienda_id 
        return tienda
    
    tienda_id = fields.Many2one('pos.config', 'Tienda/Sucursal', default=_tienda_actual, required=True)

    def print_report(self):
        logging.warning('print report existencias')
        data = {
             'ids': [],
             'model': 'quemen.reporte_existencias.wizard',
             'form': self.read()[0]
        }
        return self.env.ref('quemen.action_reporte_existencias').report_action(self, data=data)
