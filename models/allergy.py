from odoo import fields, models, api
from datetime import date
from odoo.exceptions import ValidationError

class HospitalAllergy(models.Model):
    _name = 'hospital.allergy'
    _description = 'Allergies'

    name = fields.Char(string='Allergen')
    patient_id = fields.Many2one('hospital.patient', string='Patient')
    allergy_type = fields.Selection([
        ('drug', 'Drug Allergy'),
        ('food', 'Food Allergy'),
        ('environmental', 'Environmental Allergy')
    ], string='Allergy Type')
    severity = fields.Selection([
        ('mild', 'Mild'),
        ('moderate', 'Moderate'),
        ('severe', 'Severe')
    ], string='Severity')
    reactions = fields.Selection([
        ('skin_reactions', 'Skin Reactions'),
        ('respiratory_reactions', 'Respiratory Reactions'),
        ('eye_reactions', 'Eye Reactions'),
        ('gastrointestinal_reactions', 'Gastrointestinal Reactions'),
        ('cardiovascular_reactions', 'Cardiovascular Reactions')
    ], string='Reactions')
    notes = fields.Text(string='Notes')
    medication_ids = fields.Many2many('hospital.medication', string='Allergic to:')
    date = fields.Date(string='Date')



    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            vals['date'] = date.today()
        allergen = super(HospitalAllergy, self).create(vals_list)

        patient = allergen.patient_id
        cartel = patient.cartel_id

        created_allergens = self.env['hospital.allergy'].search([('patient_id', '=', patient.id)])
        res = []
        for rec in created_allergens:
            res.append(rec.id)

        if cartel:
            cartel.write({
                'allergies': res
            })
        else:
            raise ValidationError("You cannot take a service without generating a cartel.")

        return allergen

