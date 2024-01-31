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

    name = fields.Char(default="Retiro por límite de efectivo")
    cash_box_id = fields.Many2one('account.bank.statement.cashbox','Caja de efectivo')

    @api.onchange('cash_box_id')
    def _onchange_cash_box_id(self):
        total = 0
        if self.cash_box_id and self.cash_box_id.cashbox_lines_ids:
            total = self.cash_box_id.total
            self.amount = total * -1

    def run(self):
        active_model = self.env.context.get('active_model', False)
        active_ids = self.env.context.get('active_ids', [])
        if active_model == 'pos.session':
            for session in self.env[active_model].browse(active_ids):
                if self.amount < 0:
                    retiro_id = self.env['quemen.retiros'].create({
                        'session_id': session.id,
                        'total': self.amount * -1,
                        'motivo': self.name,
                        'cash_box_id': self.cash_box_id.id

                    })
        return super(PosBox, self).run()
