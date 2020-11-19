# -*- coding: utf-8 -*-
from odoo import api, fields, models, SUPERUSER_ID, _
from odoo.exceptions import UserError
import logging
import pytz

class QuemenRelojChecador(models.Model):
    _name = "quemen.reloj_checador"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = "Reloj checador"

    empleado_id = fields.Many2one('hr.employee','Empleado')
    fecha = fields.Date('Fecha')
    hora_entrada = fields.Float('Hora de entrada')
    hora_salida = fields.Float('Hora de salida')
