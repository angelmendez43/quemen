# -*- coding: utf-8 -*-
from odoo import api, fields, models, SUPERUSER_ID, _
from odoo.exceptions import UserError
import logging
import pytz
from datetime import datetime

class StockMove(models.Model):
    _inherit = "stock.move"

    def _search_picking_for_assignation(self):
        res = super(StockMove, self)._search_picking_for_assignation()
        res = False
        return res

class StockMoveLine(models.Model):
    _inherit = "stock.move.line"

    barcode = fields.Char('Código de barra')

    @api.onchange('barcode')
    def _onchange_barcode(self):
        for line in self:
            if line.barcode:
                lot_id = self.env['stock.production.lot'].search([('name','=',line.barcode)])
                if len(lot_id) > 0:
                    line.product_id = lot_id.product_id.id
                    line.lot_id = lot_id.id
                    line.qty_done = 1
                else:
                    raise ValidationError(_("Código de barra inválido"))
