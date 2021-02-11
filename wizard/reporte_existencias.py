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

    fecha_vencimiento = fields.Date('Fecha de vencimiento de productos')

    def print_report(self):
        data = {
             'ids': [],
             'model': 'quemen.reporte_existencias.wizard',
             'form': self.read()[0]
        }
        return self.env.ref('quemen.action_reporte_existencias').report_action(self, data=data)
