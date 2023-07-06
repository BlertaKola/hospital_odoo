from odoo import fields, models, api
from datetime import date
from odoo.exceptions import ValidationError

class HospitalDiagnosis(models.Model):
    _name = 'hospital.diagnosis'
    _description = 'Medical Diagnosis'

    name = fields.Char(string='Name', readonly=True, copy=False)
    patient_id = fields.Many2one('hospital.patient', string='Patient')
    doctor_id = fields.Many2one('hospital.doctor', string='Doctor')
    date = fields.Date(string='Date', store=True)
    description = fields.Text(string='Diagnosis')
    dietary_restrictions = fields.Selection([
        ('alcohol', 'Alcohol'),
        ('fibre', 'Fibre'),
        ('sugar', 'Sugar'),
        ('lactose_free', 'Lactose-free'),
        ('gluten_free', 'Gluten-free'),
    ], string='Dietary Restrictions', widget='many2many_tags')

    medication_restrictions = fields.Selection([
        ('antibiotics', 'Antibiotics'),
        ('ibubrofen', 'Ibubrofen'),
        ('drugs', 'drugs')
    ], string='Medication Restrictions', widget='many2many_tags')
    done = fields.Boolean(string='Done?', default=False)



    @api.model_create_multi
    def create(self, vals_list):
        for rec in vals_list:
            rec['date'] = date.today()
        diagnosis = super(HospitalDiagnosis, self).create(vals_list)

        patient = diagnosis.patient_id

        if patient:
            diagnosis.name = f"{patient.name}'s Diagnosis"

        cartel = patient.cartel_id
        patient_diagnosis = self.env['hospital.diagnosis'].search([('patient_id', '=', patient.id)])
        res = []
        for rec in patient_diagnosis:
            res.append(rec.id)
        #write in the cartel diagnosis you get from the patient
        if cartel:
            cartel.write({
                'diagnosis_data': res
            })
        else:
            raise ValidationError("You cant write a diagnosis without generating a cartel")

        return diagnosis


    def name_get(self):
        result = []
        for rec in self:
            name = f"{rec.patient_id}'s Diagnosis"
            result.append((rec.id, name))
        return result