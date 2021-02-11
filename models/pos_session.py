# -*- encoding: utf-8 -*-

from odoo import models, fields, api, _
import logging
from odoo.exceptions import UserError, ValidationError

class PosSession(models.Model):
    _inherit = 'pos.session'

    retiros_ids = fields.One2many('quemen.retiros','session_id','Retiros')

    def action_pos_session_validate(self):
        res = super(PosSession, self).action_pos_session_validate()
        logging.warn('test')
        pedidos_facturar =[]
        pagos = {}
        ids_pedidos = []
        if self.order_ids:
            for pedido in self.order_ids:
                logging.warn(pedido.state)
                if pedido.state in ['done']:
                    pedidos_facturar.append(pedido)
                    ids_pedidos.append(pedido.id)
                    for linea in pedido.payment_ids:
                        if linea.payment_method_id.id not in pagos:
                            pagos[linea.payment_method_id.id] = {'diario': linea.payment_method_id, 'cantidad': 0}
                        pagos[linea.payment_method_id.id]['cantidad'] += linea.amount

        logging.warn(pedidos_facturar)
        lineas_facturar = []
        logging.warn(pagos)
        if pedidos_facturar:
            for pedido in pedidos_facturar:
                for linea in pedido.lines:
                    lineas_facturar.append(linea)
            factura = {
                'partner_id': self.config_id.cliente_id.id,
                'ref': self.name,
                'invoice_date': fields.Date.today(),
                'invoice_origin': self.name,
                'journal_id': self.config_id.invoice_journal_id.id,
                'type': 'out_invoice',
                'pos_order_ids': [(6, 0, ids_pedidos)],
                'invoice_line_ids': [(0, None, self.env['pos.order']._prepare_invoice_line(line)) for line in lineas_facturar],
            }
            factura_id = self.env['account.move'].create(factura)
            if factura_id:
                factura_id.post()
                for pago in pagos:
                    pago_dic = {'payment_type': 'inbound','payment_date': fields.Date.today(),
                    'partner_type': 'customer','partner_id':factura_id.partner_id.id,'payment_method_id':1,
                    'journal_id':pagos[pago]['diario'].id,'amount': pagos[pago]['cantidad'],'communication':factura_id.name,'invoice_ids':  [(6, 0, [factura_id.id])],}
                    pago_id = self.env['account.payment'].create(pago_dic)
                    pago_id.post()
            # if factura_id:
            #     for pedido in pedidos_facturar:
            #         for linea in pedido.lines:
            #             linea = {'move_id':factura_id.id,'product_id': linea.product_id.id,'account_id': linea.product_id.categ_id.property_account_income_categ_id.id,'quantity': linea.qty, 'tax_ids': linea.tax_ids_after_fiscal_position, 'price_unit': linea.price_unit}
            #             linea_id = self.env['account.move.line'].create(linea)
            #     # factura_id.action_post()
            #     logging.warn(factura_id)
            # else:
                # raise ValidationError(_("Another session is already opened for this point of sale."))
        return res
