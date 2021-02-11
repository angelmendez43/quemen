# -*- coding: utf-8 -*-
from odoo import api, fields, models, SUPERUSER_ID, _
from odoo.exceptions import UserError
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

class QuemenRetiros(models.Model):
    _name = "quemen.retiros"
    _description = "Retiros de POS"

    name = fields.Char('Nombre', required=True, copy=False, readonly=True, index=True, default=lambda self: _('New'))
    session_id = fields.Many2one('pos.session','Sesión')
    cash_box_id = fields.Many2one('account.bank.statement.cashbox','Caja de efectivo')
    usuario_id = fields.Many2one('res.users','usuario',default=lambda self: self.env.user)
    fecha_hora = fields.Datetime('Hora',default=fields.Datetime.now)
    motivo = fields.Char('Motivo')
    total = fields.Float('Total')

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
