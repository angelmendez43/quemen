# -*- coding: utf-8 -*-

from odoo import api, models
import datetime
import logging

class CaodigoBarrasLote(models.AbstractModel):
    _name = 'report.quemen.reporte_codigo_barras_lote'

    nombre_reporte = ''

    def fecha_hoy(self,o):
        fecha = o.date
        dia = datetime.strptime(str(fecha), '%Y-%m-%d').strftime('%d')
        mes = datetime.strptime(str(fecha), '%Y-%m-%d').strftime('%m')
        mes_letras = odoo.addons.l10n_gt_extra.a_letras.mes_a_letras(int(mes)-1)
        anio = datetime.strptime(str(fecha), '%Y-%m-%d').strftime('%Y')
        fecha = str(dia)+' de '+mes_letras+' de '+str(anio)
        return fecha

    def mes_abreviado(self,mes):
        resultado = False
        if mes == 1:
            resultado = 'ENE'
        elif mes == 2:
            resultado = 'FEB'
        elif mes == 3:
            resultado = 'MAR'
        elif mes == 4:
            resultado = 'ABR'
        elif mes == 5:
            resultado = 'MAY'
        elif mes == 6:
            resultado = 'JUN'
        elif mes == 7:
            resultado = 'JUL'
        elif mes == 8:
            resultado = 'AGO'
        elif mes == 9:
            resultado = 'SEP'
        elif mes == 10:
            resultado = 'OCT'
        elif mes == 11:
            resultado = 'NOV'
        elif mes == 12:
            resultado = 'DIC'
        return resultado

    def fecha_barras(self,o):
        elab = False
        cad = False

        # conversion a fecha formato especial fecha eleboracion
        dia_elab = datetime.datetime.strptime(str(o.create_date),'%Y-%m-%d %H:%M:%S.%f').strftime("%d")
        mes_elab = datetime.datetime.strptime(str(o.create_date),'%Y-%m-%d %H:%M:%S.%f').strftime("%m")
        anio_elab = datetime.datetime.strptime(str(o.create_date),'%Y-%m-%d %H:%M:%S.%f').strftime("%Y")

        elab = str(dia_elab) +'-'+self.mes_abreviado(int(mes_elab))+'-'+str(anio_elab)

        # conversion a fecha formato especial fecha caducidad

        dia_cad = datetime.datetime.strptime(str(o.expiration_date),'%Y-%m-%d %H:%M:%S').strftime("%d")
        mes_cad = datetime.datetime.strptime(str(o.expiration_date),'%Y-%m-%d %H:%M:%S').strftime("%m")
        anio_cad = datetime.datetime.strptime(str(o.expiration_date),'%Y-%m-%d %H:%M:%S').strftime("%Y")

        cad = str(dia_cad) +'-'+self.mes_abreviado(int(mes_cad))+'-'+str(anio_cad)


        return {'elab': elab,'cad':cad}

    def crate_lot(self, product_ids):
        logging.warning('EL O')
        logging.warning(product_ids)
        op_lote_line_ids = self.env['quemen.op_lote_line'].search([('id','in',product_ids )])
        for line in op_lote_line_ids:
            logging.warning(line)
            if line.elaboration_date:
                logging.warning(line.elaboration_date)
                elaboration_date = datetime.datetime.fromisoformat(line.elaboration_date.isoformat() + ' 06:00:00')
                expiration_date = elaboration_date + datetime.timedelta(days=line.product_id.expiration_time)

                lot_id = self.env['stock.production.lot'].create({'product_id': line.product_id.id, 'elaboration_date': elaboration_date , 'expiration_date': expiration_date,'company_id': 1})
                logging.warning('lote')
                logging.warning(lot_id)
                if lot_id:
                    line.write({'lot_id': lot_id})
    @api.model
    def _get_report_values(self, docids, data=None):
        # self.model = 'stock.production.lot'
        # product_ids = data['product_ids']
        logging.warning('_get_report_values')
        # docs = self.env['quemen.op_lote'].browse(product_ids)

        logging.warning('**********')
        logging.warning(docids)
        logging.warning(data)
        logging.warning(data['form']['product_ids'])
        product_ids = data['form']['product_ids']
        self.crate_lot(product_ids)


        return {
            'doc_ids': docids,
            'doc_model': 'quemen.reporte_codigo_barras_lote',
            # 'docs': docs,
            'fecha_barras': self.fecha_barras,
        }
