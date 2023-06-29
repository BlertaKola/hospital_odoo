from odoo import fields, models, api
import json

class HospitalCartel(models.Model):
    _name = 'hospital.cartel'
    _description = 'Hospital Cartel'

    name = fields.Char()
    patient = fields.Char(string='Patient', readonly=True)
    test_data = fields.Many2many('hospital.service.assign')
    service = fields.Many2one(related='test_data.service_id')
    diagnosis_data = fields.Many2many('hospital.diagnosis')
    allergies = fields.Char()


    def create(self, vals_list):
        cartel = super(HospitalCartel, self).create(vals_list)
        patient = self.env['hospital.patient'].browse(vals_list.get('patient_id'))
        patient.cartel_id = cartel.id
        return cartel


    def name_get(self):
        result = []
        for rec in self:
            name = f"{rec.patient}'s Cartel"
            result.append((rec.id, name))
        return result

