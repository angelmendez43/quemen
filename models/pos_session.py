# -*- encoding: utf-8 -*-

from odoo import models, fields, api, _
import logging
from odoo.exceptions import UserError, ValidationError

class PosSession(models.Model):
    _inherit = 'pos.session'

    factura_global_id = fields.Many2one("account.move", string="Factura global")
    # retiros_ids = fields.One2many('quemen.retiros','session_id','Retiros')





    # def action_pos_session_validate(self, balancing_account=False, amount_to_balance=0, bank_payment_method_diffs=None):
    #     logging.warn('test')
    #     pedidos_facturar =[]
    #     pagos = {}
    #     ids_pedidos = []
    #     logging.warn(self.order_ids)
    #     if self.order_ids:
    #         for pedido in self.order_ids:
    #             logging.warn(pedido.state)
    #             if pedido.state in ['done', 'paid']:
    #                 pedidos_facturar.append(pedido)
    #                 logging.warn("pedidos_facturar")
    #                 logging.warn(pedidos_facturar)
    #                 ids_pedidos.append(pedido.id)
    #                 for linea in pedido.payment_ids:
    #                     if linea.payment_method_id.id not in pagos:
    #
    #                         pagos[linea.payment_method_id.id] = {'diario': linea.payment_method_id.journal_id, 'cantidad': 0}
    #                     pagos[linea.payment_method_id.id]['cantidad'] += linea.amount
    #
    #     logging.warn(pedidos_facturar)
    #     lineas_facturar = []
    #     logging.warn(pagos)
    #     logging.warning("Que onda?")
    #     logging.warning(self.config_id.invoice_journal_id.name)
    #     logging.warning(self.config_id.invoice_journal_id.id)
    #     if pedidos_facturar:
    #         for pedido in pedidos_facturar:
    #             for linea in pedido.lines:
    #                 lineas_facturar.append(linea)
    #         factura = {
    #             'partner_id': self.config_id.cliente_id.id or 1,
    #             'ref': self.name,
    #             'invoice_date': fields.Date.today(),
    #             'invoice_origin': self.name,
    #             'journal_id': self.config_id.invoice_journal_id.id,
    #             'move_type': 'out_invoice',
    #             'pos_order_ids': [(6, 0, ids_pedidos)],
    #             'invoice_line_ids': [(0, None, self.env['pos.order']._prepare_invoice_line(line)) for line in lineas_facturar],
    #         }
    #         factura_id = self.env['account.move'].create(factura)
    #         logging.warning("Si llega?")
    #         logging.warning(factura_id)
    #         logging.warning(factura)
    #         if factura_id:
    #             factura_id.action_post()
    #             self.factura_global_id = factura_id.id
    #             for pago in pagos:
    #                 logging.warning("PAgos")
    #                 logging.warning(pagos[pago])
    #
    #                 # 'communication':factura_id.name, linea 68
    #
    #                 pago_dic = {'payment_type': 'inbound','date': fields.Date.today(),
    #                 'partner_type': 'customer','partner_id':factura_id.partner_id.id,'payment_method_id':1,
    #                 'journal_id':pagos[pago]['diario'].id,'amount': pagos[pago]['cantidad'],'reconciled_invoice_ids':  [(6, 0, [factura_id.id])],}
    #                 pago_id = self.env['account.payment'].create(pago_dic)
    #                 pago_id.action_post()
    #
    #                 for linea_gasto in pago_id.move_id.line_ids.filtered(lambda r: r.account_id.user_type_id.type == 'receivable' and not r.reconciled):
    #                         for linea_factura in factura_id.line_ids.filtered(lambda r: r.account_id.user_type_id.type == 'receivable' and not r.reconciled):
    #                             if (linea_gasto.debit == linea_factura.credit or linea_gasto.credit - linea_factura.debit ):
    #                                 (linea_gasto | linea_factura).reconcile()
    #                                 break
    #
    #         # if factura_id:
    #         #     for pedido in pedidos_facturar:
    #         #         for linea in pedido.lines:
    #         #             linea = {'move_id':factura_id.id,'product_id': linea.product_id.id,'account_id': linea.product_id.categ_id.property_account_income_categ_id.id,'quantity': linea.qty, 'tax_ids': linea.tax_ids_after_fiscal_position, 'price_unit': linea.price_unit}
    #         #             linea_id = self.env['account.move.line'].create(linea)
    #         #     # factura_id.action_post()
    #         #     logging.warn(factura_id)
    #         # else:
    #             # raise ValidationError(_("Another session is already opened for this point of sale."))
    #
    #     res = super(PosSession, self).action_pos_session_validate(balancing_account, amount_to_balance, bank_payment_method_diffs)
    #     return res
