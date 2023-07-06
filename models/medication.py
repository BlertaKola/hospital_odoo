import uuid
from odoo import fields, models, api
from datetime import date
from odoo.exceptions import ValidationError


class HospitalMedication(models.Model):
    _name = 'hospital.medication'
    _description = 'Medication'
    _inherit = 'mail.thread'

    name = fields.Char(string='Name', required=True)
    description = fields.Text(string='Description')
    dosage = fields.Float(string='Dosage')
    frequency = fields.Selection(
        [
            ('daily', 'Daily'),
            ('weekly', 'Weekly'),
            ('monthly', 'Monthly')
        ], string='Frequency', default='daily'
    )
    instructions = fields.Text(string='Instructions')
    expiry_date = fields.Date(string='Expiry Date')
    ref = fields.Char(string='Reference', default=lambda self: ('New'))
    prescription_ids = fields.Many2many('hospital.prescription')
    quantity = fields.Integer(string='Medication quantity')
    active = fields.Boolean('Active', default=True)

    @api.depends('quantity')
    def _check_quantity(self):
        for rec in self:
            if rec.quantity <= 0:
                rec.active = False
                raise ValidationError("This medication is not available!")

            else:
                rec.active = True

    def check_expiry_date(self):
        today = date.today()
        for rec in self:
            if rec.expiry_date < today:
                raise ValidationError("This medication has expired!")

    @api.model_create_multi
    def create(self, data_list):
        for data in data_list:
            data['ref'] = self.env['ir.sequence'].next_by_code('hospital.medication')
        return super(HospitalMedication, self).create(data_list)

