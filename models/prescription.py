from odoo import fields, models, api
from datetime import date

class HospitalPrescription(models.Model):
    _name = 'hospital.prescription'
    _description = 'Description'

    date = fields.Date(string='Date', store=True)
    patient_id = fields.Many2one('hospital.patient', string='Patient')
    patient_age = fields.Integer(related='patient_id.age', string='Age')
    # some contact info that we will add at the patients class
    medication_ids = fields.Many2many('hospital.medication', 'prescription_id', string='Medications', compute='_compute_medications')
    ref = fields.Char(string='Prescription No.', default=lambda self: ('New'))
    doctor_id = fields.Many2one('hospital.doctor', string='Doctor')
    doctor_specialization = fields.Selection(related='doctor_id.specialization')
    done = fields.Boolean(string='Done?', default=False)



    #dont show the medications that a patient is allergic to to the prescription form
    @api.depends('patient_id')
    def _compute_medications(self):
        for prescription in self:
            allergy_records = self.env['hospital.allergy'].search([
                ('patient_id', '=', prescription.patient_id.id),
                ('medication_ids', '!=', False)
            ])
            allergic_medications = allergy_records.mapped('medication_ids')
            prescription.medication_ids = self.env['hospital.medication'].search([
                ('id', 'not in', allergic_medications.ids)
            ])

    @api.model_create_multi
    def create(self, data_list):
        for data in data_list:
            data['date'] = date.today()
            data['ref'] = self.env['ir.sequence'].next_by_code('hospital.prescription')
        return super(HospitalPrescription, self).create(data_list)



