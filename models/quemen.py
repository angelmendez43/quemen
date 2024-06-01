# -*- coding: utf-8 -*-
from odoo import api, fields, models, SUPERUSER_ID, _
from datetime import date
from datetime import datetime, timedelta
from odoo.exceptions import UserError, ValidationError
import logging
import pytz

class QuemenPromociones(models.Model):
    _name = "quemen.promociones"

    name = fields.Char("Nombre")
    fecha_inicio = fields.Datetime("Fecha inicio")
    fecha_fin = fields.Datetime("Fecha fin")
    combos_ids = fields.One2many('quemen.promociones_combos','promocion_id',string="Combos")
    dosporuno_ids = fields.One2many('quemen.promociones_dosporuno','promocion_id',string="2X1")

class QuemenPromocionesCombos(models.Model):
    _name = "quemen.promociones_combos"

    promocion_id = fields.Many2one('quemen.promociones','Promocion')
    producto_id = fields.Many2one('product.product','Producto')
    cantidad = fields.Integer('Cantidad compra')
    porcentaje_descuento = fields.Float('% Descuento')
    productos_promocion_ids = fields.Many2many('product.product','quemen_productosp_rel',string="Productos promocion")

class QuemenPromocionesDosporUno(models.Model):
    _name = "quemen.promociones_dosporuno"

    promocion_id = fields.Many2one('quemen.promociones','Promocion')
    producto_id = fields.Many2one('product.product','Producto')
    productos_promocion_ids = fields.Many2many('product.product','quemen_dosporuno_rel',string="Productos promocion")


class QuemenRelojChecador(models.Model):
    _name = "quemen.reloj_checador"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = "Reloj checador"

    ac = fields.Char('AC.No')
    empleado_id = fields.Many2one('hr.employee','Empleado')
    departamento_id = fields.Many2one('hr.department','Departamento')
    area_id = fields.Many2one('hr.area','Area')
    puesto_id = fields.Many2one('hr.job','Puesto')
    dia = fields.Selection([
        ('lunes', 'Lunes'),
        ('martes', 'Martes'),
        ('miercoles', 'Miercoles'),
        ('jueves', 'Jueves'),
        ('viernes', 'Viernes'),
        ('sabado', 'Sabado'),
        ('domingo', 'Domingo')],'Día')
    fecha = fields.Date('Fecha')
    hora_entrada = fields.Float('Hora de entrada')
    hora_salida = fields.Float('Hora de salida')
    horas_laboradas = fields.Float('Horas laboradas')
    jornada_laborada = fields.Float('Jornada laborada')
    horas_extras_laboradas = fields.Float('Horas extras laboradas')

class QuemenRetirosEfectivo(models.Model):
    _name = "quemen.retiros_efectivo"
    _description = "Retiros de POS"

    def _denominacion_actual(self):
        denominacion_ids = self.env['pos.bill'].search([('id','>', 0)], order='value asc')
        lista_denominaciones = []
        if len(denominacion_ids) > 0:
            for denominacion in denominacion_ids:
                if denominacion.value >= 0.50:
                    valor = {'denominacion_id': denominacion.id, 'cantidad': 0.00}
                    lista_denominaciones.append((0,0,valor))
        return lista_denominaciones


    def _sesion_actual(self):
        sesion = False
        sesion_id = self.env['pos.session'].search([('user_id','=',self.env.user.id),('state','in',['opened','closing_control'])])
        if len(sesion_id) > 0:
            sesion = sesion_id
        # else:
        #     raise ValidationError(_('No puede retirar efectivo'))
        return sesion

    @api.depends('denominacion_ids')
    def _calcular_total(self):
        for retiro in self:
            total = 0
            for linea in retiro.denominacion_ids:
                total += (linea.cantidad * linea.denominacion_id.value)
            retiro.total = total

    name = fields.Char('Nombre', required=True, copy=False, readonly=True, index=True, default=lambda self: _('New'))
    usuario_id = fields.Many2one('res.users','usuario',default=lambda self: self.env.user)
    fecha_hora = fields.Datetime('Hora',default=fields.Datetime.now)
    sesion_id = fields.Many2one('pos.session','Sesión', default=_sesion_actual, required=True, store=True)
    tienda_id = fields.Many2one('pos.config','tienda', related='sesion_id.config_id', store=True)
    motivo = fields.Char('Motivo', required=True, default = "Retiro de efectivo")
    total = fields.Float('Total', compute='_calcular_total')
    denominacion_ids = fields.One2many('quemen.retiro_denominacion','retiro_id',string="Denominaciones",default=_denominacion_actual)
    state = fields.Selection(
    [('borrador', 'Borrador'), ('confirmado', 'Confirmado')],
    'Estado', readonly=True, copy=False, default= "borrador")
    cajero = fields.Char('Cajero', required=True)
    entregado = fields.Boolean('Entregado', readonly=True)

    @api.model_create_multi
    def create(self, vals_list):
        logging.warning('valores')
        logging.warning(vals_list)
        logging.warning(self)
        for vals in vals_list:
            secuencia_id = self.env['pos.session'].search([('id', '=', vals['sesion_id'])]).config_id.secuencia_id
            if vals.get('name', _('New')) == _('New'):
                seq_date = None
                if 'company_id' in vals:
                    vals['name'] = self.env['ir.sequence'].with_context(force_company=vals['company_id']).next_by_code(
                        'quemen.retiros', sequence_date=seq_date) or _('New')
                else:
                    vals['name'] = secuencia_id._next() or _('New')
        result = super(QuemenRetirosEfectivo, self).create(vals_list)
        return result

    def confirmar_retiro(self):
        for retiro in self:
            retiro.sesion_id.cash_register_id.write({'line_ids': [(0, 0,  { 'payment_ref': retiro.motivo, 'amount': retiro.total*-1})] })
            retiro.write({'state': 'confirmado'})


class QuemenRetiros(models.Model):
    _name = "quemen.retiro_denominacion"

    retiro_id = fields.Many2one('quemen.retiros_efectivo','Retiro')
    denominacion_id = fields.Many2one('pos.bill','Denominacion')
    cantidad = fields.Integer('Cantidad')

class QuemenRetiros(models.Model):
    _name = "quemen.retiros"
    _description = "Retiros de POS"

    name = fields.Char('Nombre', required=True, copy=False, readonly=True, index=True, default=lambda self: _('New'))
    session_id = fields.Many2one('pos.session','Sesión')
    # cash_box_id = fields.Many2one('account.bank.statement.cashbox','Caja de efectivo')
    # usuario_id = fields.Many2one('res.users','usuario',default=lambda self: self.env.user)
    # fecha_hora = fields.Datetime('Hora',default=fields.Datetime.now)
    # motivo = fields.Char('Motivo')
    # total = fields.Float('Total')

    # @api.model
    # def create(self, vals):
    #     if vals.get('name', _('New')) == _('New'):
    #         seq_date = None
    #         if 'company_id' in vals:
    #             vals['name'] = self.env['ir.sequence'].with_context(force_company=vals['company_id']).next_by_code(
    #                 'quemen.retiros', sequence_date=seq_date) or _('New')
    #         else:
    #             vals['name'] = self.env['ir.sequence'].next_by_code('quemen.retiros', sequence_date=seq_date) or _('New')

    #     result = super(QuemenRetiros, self).create(vals)
    #     return result

class QuemenOpLote(models.Model):
    _name = "quemen.op_lote"
    _inherit = ['mail.thread', 'mail.activity.mixin', 'utm.mixin']

    name = fields.Char('Nombre', required=True, copy=False, readonly=True, index=True, default=lambda self: _('New'), tracking=True)
    date = fields.Date('Fecha', tracking=True)
    date_mrp_production = fields.Date('Fecha producción', tracking=True)
    product_ids = fields.One2many('quemen.op_lote_line', 'lot_id', string="Productos", tracking=True)
    reference = fields.Char('Referencia', tracking=True)
    state = fields.Selection(
        [('borrador', 'Borrador'), ('confirmado', 'Confirmado')],
        'Estado', readonly=True, copy=False, default='borrador', tracking=True)

    @api.model
    def create(self, vals):
        if vals.get('name', _('New')) == _('New'):
            seq_date = None
            if 'company_id' in vals:
                vals['name'] = self.env['ir.sequence'].with_context(force_company=vals['company_id']).next_by_code(
                    'quemen.retiros', sequence_date=seq_date) or _('New')
            else:
                vals['name'] = self.env['ir.sequence'].next_by_code('quemen.op_lote', sequence_date=seq_date) or _('New')

        result = super(QuemenOpLote, self).create(vals)
        return result

    def create_lot(self):
        for lot in self:
            if lot.product_ids and lot.state == "borrador":
                for line in lot.product_ids:
                    if len(line.lot_barcode_id) == 0:
                        elaboration_date = datetime.fromisoformat(line.elaboration_date.isoformat() + ' 06:00:00')
                        expiration_date = elaboration_date + timedelta(days=line.product_id.expiration_time)
                        removal_date = elaboration_date + timedelta(days=line.product_id.removal_time)
                        use_date = elaboration_date + timedelta(days=line.product_id.use_time)
                        alert_date = elaboration_date + timedelta(days=line.product_id.alert_time)
                        lot_id = self.env['stock.production.lot'].create({'product_id': line.product_id.id,
                                                                          'elaboration_date': elaboration_date,
                                                                          'expiration_date': expiration_date,
                                                                          'removal_date': removal_date,
                                                                          'use_date': use_date,
                                                                          'alert_date': alert_date,
                                                                          'company_id': 1})
                        logging.warning('lote')
                        logging.warning(lot_id)
                        if lot_id:
                            line.write({'lot_barcode_id': lot_id})


    def confirm_lot(self):
        for lot in self:
            logging.warning('LOTE')
            logging.warning(lot)
            if lot.product_ids:
                for line in lot.product_ids:
                    if line.lot_barcode_id == False:
                        raise ValidationError(_('No puede validar productos sin Lote.'))
                    logging.warning(line.product_id.name)
                    date_planed_start = datetime.fromisoformat(lot.date_mrp_production.isoformat() + ' 06:00:00')
                    mrp_order = {
                        # 'name': line.lot_id.name,
                        'product_id': line.product_id.id,
                        'product_uom_id': line.product_id.uom_id.id,
                        'qty_producing': line.quantity,
                        'product_qty': line.quantity,
                        'bom_id': line.product_id.bom_ids.id,
                        'origin': line.lot_id.name,
                        'lot_producing_id': line.lot_barcode_id.id,
                        'date_planned_start': date_planed_start,
                        'picking_type_id': line.product_id.bom_ids.picking_type_id.id,
                        'location_src_id': line.product_id.bom_ids.picking_type_id.default_location_src_id.id,
                        'location_dest_id': line.product_id.bom_ids.picking_type_id.default_location_dest_id.id
                        # 'move_line_id': line.id,
                    }
                    mrp_order_id = self.env['mrp.production'].create(mrp_order)

                    mrp_order_id._onchange_move_raw()
                    mrp_order_id._onchange_move_finished()
            lot.write({'state': "confirmado"})
        return True

class QuemenOpLoteLinea(models.Model):
    _name = "quemen.op_lote_line"
    _rec_name = "product_id"

    lot_id = fields.Many2one("quemen.op_lote", "Lote")
    product_id = fields.Many2one('product.product','Producto',tracking=True)
    quantity = fields.Float('Cantidad',tracking=True)
    elaboration_date = fields.Date('Fecha elaboracion',tracking=True)
    qty_label = fields.Float('Cantidad etiquetas', default=1)
    lot_barcode_id = fields.Many2one('stock.production.lot', 'Lote',tracking=True)
    lot_state = fields.Selection(
        [('borrador', 'Borrador'), ('confirmado', 'Confirmado')],
        'Estado', readonly=True, copy=False, related='lot_id.state')
    # wizard_id = fields.Many2one('quemen.reporte_codigo_barras.wizard', 'Wizard')

    @api.onchange('quantity')
    def _onchange_quantity(self):
        if self.product_id:
            self.qty_label = self.quantity
