# -*- coding: utf-8 -*-
from odoo import api, fields, models, SUPERUSER_ID, _
from odoo.exceptions import UserError
import logging


class Picking(models.Model):
    _inherit = "stock.picking"

    def button_validate(self):
        res = super(Picking, self).button_validate()
        logging.warn(self.env.user.has_group('quemen.quemen_validar_envio_tienda'))
        if self.env.user.has_group('quemen.quemen_validar_envio_tienda') and self.picking_type_id.code == 'internal':
            return res
        elif self.env.user.has_group('quemen.quemen_validar_envio_tienda') == False and self.picking_type_id.code != 'internal' :
            return res
        else:
            raise UserError(_('No tiene permisos para validar'))
