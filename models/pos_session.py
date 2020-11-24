# -*- encoding: utf-8 -*-

from odoo import models, fields, api, _

class PosSession(models.Model):
    _inherit = 'pos.session'

    retiros_ids = fields.One2many('quemen.retiros','session_id','Retiros')
