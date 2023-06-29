from odoo import fields, models, api
from datetime import date
from odoo.exceptions import ValidationError

class HospitalDiagnosis(models.Model):
    _name = 'hospital.diagnosis'
    _description = 'Medical Diagnosis'

    patient_id = fields.Many2one('hospital.patient', string='Patient')
    doctor_id = fields.Many2one('hospital.doctor', string='Doctor')
    date = fields.Date(string='Date', compute='_compute_date', store=True)
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



    @api.depends('done')
    def _compute_date(self):
        for rec in self:
            if rec.done:
                rec.date = date.today()
            else:
                rec.date = False

    @api.model_create_multi
    def create(self, vals_list):
        diagnosis = super(HospitalDiagnosis, self).create(vals_list)

        patient = diagnosis.patient_id
        cartel = patient.cartel_id
        patient_diagnosis = self.env['hospital.diagnosis'].search([('patient_id', '=', patient.id)])
        res = []
        for rec in patient_diagnosis:
            res.append(rec.id)

        print("RESSSSSS")
        print(res)
        if cartel:
            cartel.write({
                'diagnosis_data': res
            })
        else:
            raise ValidationError("You cant write a diagnosis without generating a cartel")

        return diagnosis
