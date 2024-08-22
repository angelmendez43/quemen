# -*- coding: utf-8 -*-
import base64
from odoo import api, fields, models, SUPERUSER_ID, _
from odoo.exceptions import UserError
import logging

import pytz
from datetime import datetime
_logger = logging.getLogger(__name__)

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
    

    def process_edi_invoices(self):
        # Ejecutar con permisos elevados si es necesario
        self = self.sudo()

        # Buscar todas las facturas con los estados especificados y que estén publicadas
        invoices = self.search([
            ('l10n_mx_edi_sat_status', '=', 'undefined'),
            ('edi_state', '=', 'to_send'),
            ('state', '=', 'posted'),  # Asegurarse de que estén publicadas
            ('move_type', 'in', ['out_invoice', 'in_invoice'])  # Solo facturas de ventas o compras
        ])

        # Procesar cada factura
        for invoice in invoices:
            try:
                # Log para verificar si es una factura
                is_invoice = invoice.is_invoice()
                _logger.info(f"Factura {invoice.name} - is_invoice(): {is_invoice}")

                # Log para verificar el tipo de movimiento
                _logger.info(f"Factura {invoice.name} - move_type: {invoice.move_type}")

                _logger.info(f"Procesando factura {invoice.name} con estado {invoice.state} y edi_state {invoice.edi_state}")
                
                # Procesar el EDI de la factura
                invoice.button_process_edi_web_services()

                # Esperar un poco y refrescar el registro para obtener los valores actualizados
                invoice.refresh()

                _logger.info(f"Después de procesar EDI: Factura {invoice.name} con edi_state {invoice.edi_state}")

                # Verificar si el campo edi_state está en estado "sent"
                if invoice.edi_state == 'sent':
                    _logger.info(f"Factura {invoice.name} con ID {invoice.id} está en estado 'sent'.")

                    # Verificar si invoice.id es válido
                    if invoice.id:
                        _logger.info(f"ID de la factura {invoice.name} es {invoice.id}. Se procederá a enviar.")
                        
                        # Configurar el contexto como lo hace `action_invoice_sent`
                        ctx = dict(
                            default_model='account.move',
                            default_res_id=invoice.id,
                            default_res_model='account.move',
                            default_use_template=True,
                            default_template_id=self.env.ref('account.email_template_edi_invoice').id,
                            default_composition_mode='comment',
                            mark_invoice_as_sent=True,
                            custom_layout="mail.mail_notification_paynow",
                            model_description=invoice.type_name,
                            force_email=True,
                            active_ids=[invoice.id],
                        )

                        # Crear una instancia de account.invoice.send con el contexto adecuado
                        send_wizard = self.env['account.invoice.send'].with_context(ctx).create({
                            'invoice_ids': [(6, 0, [invoice.id])],
                        })

                        # Asegúrate de que el wizard se ha creado correctamente
                        if send_wizard:
                            _logger.info(f"Wizard creado con éxito para la factura {invoice.name}. Se procederá a enviar e imprimir.")
                            try:
                                result = send_wizard.send_and_print_action()
                                _logger.info(f"send_and_print_action() result: {result}")
                            except Exception as e:
                                _logger.error(f"Error en send_and_print_action() para la factura {invoice.name}: {str(e)}")
                        else:
                            _logger.error(f"El wizard no se creó correctamente para la factura {invoice.name}.")
                    else:
                        _logger.warning(f"ID de la factura {invoice.name} no es válido: {invoice.id}.")
                else:
                    _logger.warning(f"La factura {invoice.name} no está en el estado 'sent' después de procesar EDI.")
            except Exception as e:
                _logger.error(f"Error al enviar la factura {invoice.name}: {str(e)}")
                
class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    pedido_referencia = fields.Char('Pedido referencia')
    sesion_id = fields.Many2one('pos.session')
    pedido_id = fields.Many2one('pos.order')
