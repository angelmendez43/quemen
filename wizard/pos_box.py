# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api,fields,tools, _
from odoo.exceptions import UserError
import pytz
from odoo.addons.account.wizard.pos_box import CashBox
import datetime
import logging

class PosBox(CashBox):
    _inherit = "cash.box.out"

    def run(self):
        active_model = self.env.context.get('active_model', False)
        active_ids = self.env.context.get('active_ids', [])
        if active_model == 'pos.session':
            for session in self.env[active_model].browse(active_ids):
                if self.amount < 0:
                    retiro_id = self.env['quemen.retiros'].create({
                        'session_id': session.id,
                        'total': self.amount,
                        'motivo': self.name,

                    })
        return super(PosBox, self).run()
