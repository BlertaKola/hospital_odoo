from odoo import fields, models, api
from datetime import date

class HospitalPrescription(models.Model):
    _name = 'hospital.prescription'
    _description = 'Description'

    date = fields.Date(string='Date', compute='_compute_date', store=True)
    patient_id = fields.Many2one('hospital.patient', string='Patient')
    patient_age = fields.Integer(related='patient_id.age', string='Age')
    # some contact info that we will add at the patients class
    medication_ids = fields.Many2many('hospital.medication', 'prescription_id', string='Medications')
    ref = fields.Char(string='Prescription No.', default=lambda self: ('New'))
    doctor_id = fields.Many2one('hospital.doctor', string='Doctor')
    doctor_specialization = fields.Selection(related='doctor_id.specialization')
    done = fields.Boolean(string='Done?', default=False)
    # report_id = fields.Many2one('hospital.report')





    @api.depends('done')
    def _compute_date(self):
        for rec in self:
            if rec.done:
                rec.date = date.today()
            else:
                rec.date = False


    @api.model_create_multi
    def create(self, data_list):
        for data in data_list:
            data['ref'] = self.env['ir.sequence'].next_by_code('hospital.prescription')
        return super(HospitalPrescription, self).create(data_list)



