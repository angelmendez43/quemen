# -*- coding: utf-8 -*-
from odoo import api, fields, models, SUPERUSER_ID, _
from odoo.exceptions import UserError
import logging
import pytz

# class QuemenPromociones(models.Model):
#     _name = "quemen.promociones"
#
#     name = fields.Char("Nombre")
#     fecha_inicio = fields.Datetime("Fecha inicio")
#     fecha_fin = fields.Datetime("Fecha fin")
#     combos_ids = fields.One2many('quemen.promociones_combos','promocion_id',string="Combos")
#     dosporuno_ids = fields.One2many('quemen.promociones_dosporuno','promocion_id',string="2X1")
#
# class QuemenPromocionesCombos(models.Model):
#     _name = "quemen.promociones_combos"
#
#     promocion_id = fields.Many2one('quemen.promociones','Promocion')
#     producto_id = fields.Many2one('product.product','Producto')
#     cantidad = fields.Integer('Cantidad compra')
#     porcentaje_descuento = fields.Float('% Descuento')
#     productos_promocion_ids = fields.Many2many('product.product','quemen_productosp_rel',string="Productos promocion")
#
# class QuemenPromocionesDosporUno(models.Model):
#     _name = "quemen.promociones_dosporuno"
#
#     promocion_id = fields.Many2one('quemen.promociones','Promocion')
#     producto_id = fields.Many2one('product.product','Producto')
#     productos_promocion_ids = fields.Many2many('product.product','quemen_dosporuno_rel',string="Productos promocion")
#
#
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

class QuemenOPLote(models.Model):
    _name = "quemen.op_lote"
    _description = "Ordenes de producción por lote"
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(
        'Name', default=lambda self: _('New'),
        copy=False, readonly=True, tracking=True)
    fecha = fields.Date(
        'Fecha', default=fields.Date.context_today,
        copy=False, required=True, tracking=True)
    producto_ids = fields.One2many('quemen.op_lote_linea','op_lote_id', string='Productos')
    state = fields.Selection([
        ('borrador', 'Borrador'),
        ('confirmado', 'Confirmado')], 'Estado', default='borrador',
        copy=False, readonly=True, tracking=True)

    @api.model
    def create(self, vals):
        if vals.get('name', _('New')) == _('New'):
            vals['name'] = self.env['ir.sequence'].next_by_code('quemen.op_lote')
        return super().create(vals)

    def boton_confirmar(self):
        for op in self:
            if op.producto_ids:
                for linea in op.producto_ids:
                    mrp_order = {
                        'product_id': linea.producto_id.id,
                        'product_uom_id': linea.producto_id.uom_id.id,
                        'qty_producing': linea.cantidad,
                        'product_qty': linea.cantidad,
                        'bom_id': linea.producto_id.bom_ids.id,
                        'origin': op.name,
                    }
                    mrp_order_id = self.env['mrp.production'].create(mrp_order)
                    mrp_order_id._onchange_move_raw()
                    mrp_order_id._onchange_workorder_ids()
                    mrp_order_id._onchange_move_finished()
                    
                op.state = 'confirmado'
        return True

class QuemenOPLoteLinea(models.Model):
    _name = "quemen.op_lote_linea"
    _description = "Lines de ordenes producción por lote"

    op_lote_id = fields.Many2one('quemen.op_lote','OP Lote')
    producto_id = fields.Many2one('product.product','Producto')
    cantidad = fields.Float('Cantidad')

class QuemenRetirosEfectivo(models.Model):
    _name = "quemen.retiros_efectivo"
    _description = "Retiro efectivo"

    cantidad = fields.Float('Cantidad')
    moneda_billete_id = fields.Many2one('pos.bill')
    denominacion = fields.Selection([ ('billete', 'Billete(s)'),('moneda', 'Moneda(s)')],'Denominación', default='billete')
    retiro_id = fields.Many2one('quemen.retiros','Retiros')

class QuemenRetiros(models.Model):
    _name = "quemen.retiros"
    _description = "Retiros de POS"

    name = fields.Char('Nombre', required=True, copy=False, readonly=True, index=True, default=lambda self: _('New'))
    session_id = fields.Many2one('pos.session','Sesión',compute='_compute_cash_box_id_cash')
    cash_box_id = fields.Many2one('account.bank.statement','Caja de efectivo' ,compute='_compute_cash_box_id_cash')
    usuario_id = fields.Many2one('res.users','usuario',default=lambda self: self.env.user)
    fecha_hora = fields.Datetime('Hora',default=fields.Datetime.now)
    motivo = fields.Char('Motivo')
    total = fields.Float('Total')
    efectivo_ids = fields.One2many('quemen.retiros_efectivo','retiro_id',string='Efectivo')
    linea_extracto_id = fields.Many2one('account.bank.statement.line', string='Linea extracto')
    state = fields.Selection([
    ('borrador', 'Borrador'),
    ('validado', 'Validado'),
    ], string='Status', readonly=True, index=True, copy=False, default='borrador')


    def validar_retiro(self):
        for retiro in self:
            if retiro.linea_extracto_id != True:
                statement_line_dic = {
                    'date': fields.Date.today(),
                    'payment_ref': retiro.motivo,
                    'amount': retiro.total * -1,
                    'statement_id': retiro.cash_box_id.id,
                    
                }
                linea_id = self.env['account.bank.statement.line'].create(statement_line_dic)
                retiro.linea_extracto_id = linea_id.id
                retiro.write({'state': 'validado'})
            
        return True


    @api.onchange('efectivo_ids')
    def _onchange_efectivo_ids(self):
        for retiro in self:
            total = 0
            if retiro.efectivo_ids:
                for linea in retiro.efectivo_ids:
                    total += linea.cantidad * linea.moneda_billete_id.value
            retiro.total = total

    @api.depends('usuario_id','name')
    def _compute_cash_box_id_cash(self):
        for retiro in self:
            lineas = []
            monedas_billete_ids = self.env['pos.bill'].search([])
            if monedas_billete_ids:
                for moneda_billete in monedas_billete_ids:
                    linea_id = self.env['quemen.retiros_efectivo'].create({'cantidad': 0, 'moneda_billete_id': moneda_billete.id})
                    lineas.append(linea_id.id)
            retiro.cash_box_id = lineas
            if self.env.user.pos_id:
                sesion_id = self.env['pos.session'].search([('config_id','=', self.env.user.pos_id.id),('state','in',['opened','closing_control'])])
                logging.warning('sesion_id')
                logging.warning(sesion_id)
                if sesion_id:
                    retiro.cash_box_id = sesion_id.cash_register_id.id
                    retiro.session_id = sesion_id.id
        

    
    @api.onchange('cash_box_id')
    def _onchange_cash_box_id(self):
        monedas_billete_ids = self.env['pos.bill'].search([])
        for retiro in self:
            if len(retiro.efectivo_ids) > 0:
                retiro.efectivo_ids.unlink()
            if monedas_billete_ids:
                for moneda_billete in monedas_billete_ids:
                    self.env['quemen.retiros_efectivo'].create({'cantidad': 0, 'moneda_billete_id': moneda_billete.id, 'retiro_id': retiro.id})
    
    @api.model
    def create(self, vals):
        if vals.get('name', _('New')) == _('New'):
            seq_date = None
            if 'company_id' in vals:
                vals['name'] = self.env['ir.sequence'].with_context(force_company=vals['company_id']).next_by_code(
                    'quemen.retiros', sequence_date=seq_date) or _('New')
            else:
                vals['name'] = self.env['ir.sequence'].next_by_code('quemen.retiros', sequence_date=seq_date) or _('New')

        result = super(QuemenRetiros, self).create(vals)
        return result
