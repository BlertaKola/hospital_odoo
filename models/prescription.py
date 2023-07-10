from odoo import fields, models, api
from datetime import date
from odoo.exceptions import ValidationError


class HospitalPrescription(models.Model):
    _name = 'hospital.prescription'
    _description = 'Description'

    date = fields.Date(string='Date', store=True)
    patient_id = fields.Many2one('hospital.patient', string='Patient')
    patient_age = fields.Integer(related='patient_id.age', string='Age')
    ref = fields.Char(string='Prescription No.', default=lambda self: 'New')
    doctor_id = fields.Many2one('hospital.doctor', string='Doctor')
    doctor_specialization = fields.Selection(related='doctor_id.specialization')
    medication_ids = fields.Many2many('hospital.medication', string='Medications')


    @api.model_create_multi
    def create(self, data_list):
        for data in data_list:
            data['date'] = date.today()
            data['ref'] = self.env['ir.sequence'].next_by_code('hospital.prescription')
        prescription = super(HospitalPrescription, self).create(data_list)

        patient = prescription.patient_id


        cartel = patient.cartel_id

        patient_diagnosis = self.env['hospital.prescription'].search([('patient_id', '=', patient.id)])
        res = []
        for rec in patient_diagnosis:
            res.append(rec.id)
        # write in the cartel diagnosis you get from the patient
        if cartel:
            cartel.write({
                'prescription_data': res
            })
        else:
            raise ValidationError("You cant write a prescription without generating a cartel")
        print(prescription)
        allergic_medications = patient.allergy_ids.mapped('medication_ids')
        selected_medications = prescription.medication_ids

        overlapping_medications = allergic_medications & selected_medications
        if overlapping_medications:
            medication_names = ', '.join(overlapping_medications.mapped('name'))
            error_msg = f"You're allergic to the following medications: {medication_names}"
            raise ValidationError(error_msg)

        return prescription

    def name_get(self):
        result = []
        for rec in self:
            name = f"{rec.ref}"
            result.append((rec.id, name))
        return result

    def write(self, vals):
        if 'medication_ids' in vals:
            allergic_medications = self.patient_id.allergy_ids.mapped('medication_ids')
            selected_medications = self.medication_ids

            overlapping_medications = allergic_medications & selected_medications
            if overlapping_medications:
                medication_names = ', '.join(overlapping_medications.mapped('name'))
                error_msg = f"You're allergic to the following medications: {medication_names}"
                raise ValidationError(error_msg)

        return super(HospitalPrescription, self).write(vals)