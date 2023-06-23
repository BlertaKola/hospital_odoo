from odoo import fields, models, api
from datetime import date

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

    # def write(self, vals):
    #     result = super(HospitalDiagnosis, self).write(vals)
    #     self.patient_id.update_medical_report()
    #     return result
