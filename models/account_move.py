# -*- coding: utf-8 -*-
import base64
from odoo import api, fields, models, SUPERUSER_ID, _
from odoo.exceptions import UserError
import logging
import pytz
from datetime import datetime

class AccountMove(models.Model):
    _inherit = "account.move"

    factura_global = fields.Boolean('Factura global')
    
    def generar_factura_nueva(self, factura):
        for f in factura:
            factura_dic = {
                'partner_id': f.partner_id.id,
                'ref': f.ref,
                'invoice_date': f.invoice_date,
                'invoice_origin': f.invoice_origin,
                'journal_id': f.journal_id.id,
                'l10n_mx_edi_usage': 'S01',
                'move_type': 'out_invoice',
                'pos_order_ids': [(6, 0, f.pos_order_ids.ids)] if f.pos_order_ids else [],
                'invoice_line_ids': [(0, None, self._prepare_invoice_line(line)) for line in f.invoice_line_ids],
            }
            factura_id = self.env['account.move'].create(factura_dic)

    def _prepare_invoice_line(self, order_line):
        return {
            'product_id': order_line.product_id.id,
            'quantity': order_line.quantity,
            'discount': order_line.discount,
            'price_unit': order_line.price_unit,
            'name': order_line.name,
            'tax_ids': [(6, 0, order_line.product_id.taxes_id.ids)],
            'product_uom_id': order_line.product_uom_id.id,
        }
class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    pedido_referencia = fields.Char('Pedido referencia')
    sesion_id = fields.Many2one('pos.session')
    pedido_id = fields.Many2one('pos.order')
