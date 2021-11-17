# -*- encoding: utf-8 -*-

from odoo import models, fields, api, _
import logging
from odoo.exceptions import UserError, ValidationError

class PosSession(models.Model):
    _inherit = 'pos.session'

    factura_global_id = fields.Many2one("account.move", string="Factura global")
    retiros_ids = fields.One2many('quemen.retiros','session_id','Retiros')

    # def action_pos_session_validate(self):
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
    #                         pagos[linea.payment_method_id.id] = {'diario': linea.payment_method_id, 'cantidad': 0}
    #                     pagos[linea.payment_method_id.id]['cantidad'] += linea.amount
    #
    #     logging.warn(pedidos_facturar)
    #     lineas_facturar = []
    #     logging.warn(pagos)
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
    #             'type': 'out_invoice',
    #             'pos_order_ids': [(6, 0, ids_pedidos)],
    #             'invoice_line_ids': [(0, None, self.env['pos.order']._prepare_invoice_line(line)) for line in lineas_facturar],
    #         }
    #         factura_id = self.env['account.move'].create(factura)
    #         logging.warn(factura_id)
    #         logging.warn(factura)
    #         if factura_id:
    #             factura_id.action_post()
    #             self.factura_global_id = factura_id.id
    #             for pago in pagos:
    #                 pago_dic = {'payment_type': 'inbound','payment_date': fields.Date.today(),
    #                 'partner_type': 'customer','partner_id':factura_id.partner_id.id,'payment_method_id':1,
    #                 'journal_id':pagos[pago]['diario'].id,'amount': pagos[pago]['cantidad'],'communication':factura_id.name,'invoice_ids':  [(6, 0, [factura_id.id])],}
    #                 pago_id = self.env['account.payment'].create(pago_dic)
    #                 pago_id.post()
    #         # --------------------------------------------
    #         # if factura_id:
    #         #     for pedido in pedidos_facturar:
    #         #         for linea in pedido.lines:
    #         #             linea = {'move_id':factura_id.id,'product_id': linea.product_id.id,'account_id': linea.product_id.categ_id.property_account_income_categ_id.id,'quantity': linea.qty, 'tax_ids': linea.tax_ids_after_fiscal_position, 'price_unit': linea.price_unit}
    #         #             linea_id = self.env['account.move.line'].create(linea)
    #         #     # factura_id.action_post()
    #         #     logging.warn(factura_id)
    #         # else:
    #             # raise ValidationError(_("Another session is already opened for this point of sale."))
    #         # ---------------------------------------------------
    #     res = super(PosSession, self).action_pos_session_validate()
    #     return res

    def _l10n_mx_edi_create_cfdi_values(self):
        """Generating the base dict with data needed to generate the electronic
        document
        :return: Base data to generate electronic document
        :rtype: dict
        """
        session = self.mapped('session_id')
        invoice_obj = self.env['account.move']
        precision_digits = 6
        company_id = session.config_id.company_id

        invoice = {
            'record': self,
            'invoice': invoice_obj,
            'currency': session.currency_id.name,
            'supplier': company_id.partner_id.commercial_partner_id,
            'folio': session.name,
            'serie': 'NA',
        }
        invoice['subtotal_wo_discount'] = '%.*f' % (precision_digits, sum([
            self._get_subtotal_wo_discount(precision_digits, l) for l in
            self.mapped('lines')]))
        invoice['amount_untaxed'] = abs(float_round(sum(
            [self._get_subtotal_wo_discount(precision_digits, p) for p in
             self.mapped('lines')]), 2))
        invoice['amount_discount'] = '%.*f' % (precision_digits, sum([
            float(self._get_discount(precision_digits, p)) for p in
            self.mapped('lines')]))

        invoice['tax_name'] = lambda t: {
            'ISR': '001', 'IVA': '002', 'IEPS': '003'}.get(t, False)
        invoice['taxes'] = self._l10n_mx_edi_create_taxes_cfdi_values()

        invoice['amount_total'] = abs(float_round(float(
            invoice['amount_untaxed']), 2) - round(float(
                invoice['amount_discount'] or 0), 2) + (round(
                    invoice['taxes']['total_transferred'] or 0, 2)) - (round(
                        invoice['taxes']['total_withhold'] or 0, 2)))
        invoice['document_type'] = 'I' if self.filtered(
            lambda r: r.amount_total > 0) else 'E'
        payment_ids = self.mapped('payment_ids').filtered(
            lambda st: st.amount > 0)
        payments = payment_ids.mapped('payment_method_id')
        journal_ids = payments.read_group([
            ('id', 'in', payments.ids)], ['cash_journal_id'],
            'cash_journal_id')
        max_count = 0
        journal_id = False
        for journal in journal_ids:
            if journal.get('cash_journal_id_count') and journal.get('cash_journal_id_count') > max_count:
                max_count = journal.get('cash_journal_id_count')
                journal_id = journal.get('cash_journal_id')[0]
        invoice['payment_method'] = self.env['account.journal'].browse(
            journal_id).l10n_mx_edi_payment_method_id.code if journal_id else '99'  # noqa
        return invoice
