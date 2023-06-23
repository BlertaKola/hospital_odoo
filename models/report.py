from odoo import fields, models, api
from datetime import date


class HospitalReport(models.Model):
    _name = 'hospital.report'
    _description = 'Medical Report'
    _inherit = 'mail.thread'

    name = fields.Char(string='Report Name')
    patient_id = fields.Many2one('hospital.patient', string='Patient')
    age = fields.Integer(string='age')
    doctor_ids = fields.Many2many(string='doctors')







