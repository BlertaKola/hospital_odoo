from odoo import fields, models, api


class ModelName(models.Model):
    _name = 'hospital.allergy'
    _description = 'Allergies'

    name = fields.Char()

