# -*- coding: utf-8 -*-

from odoo import models, fields, api

class Employee(models.Model):
    _inherit = "hr.employee"

    id_reloj = fields.Char('ID reloj checador')
    hora_entrada = fields.Float('Hora entrada')
    hora_salida = fields.Float('Hora salida')
