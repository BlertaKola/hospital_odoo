from odoo import fields, models, api
import random

class HospitalDoctor(models.Model):
    _name = 'hospital.doctor'
    _description = 'Doctor'
    _inherit = 'mail.thread'

    name = fields.Char(string='Name', required=True)
    specialization = fields.Selection(
        [
            ('general_medicine', 'General Medicine'),
            ('cardiologist', 'Cardiologist'),
            ('neurologist', 'Neurologist'),
            ('oncologist', 'Oncologist'),
            ('pulmonologist', 'Pulmonologist'),
            ('psychiatrist', 'Psychiatrist'),
            ('ophthalmologist', 'Ophthalmologist'),
            ('pediatrician', 'Pediatrician'),
            ('gynecologist_obstetrician', 'Gynecologist/Obstetrician'),
            ('dermatologist', 'Dermatologist'),
            ('endocrinologist', 'Endocrinologist'),
            ('gastroenterologist', 'Gastroenterologist'),
            ('nephrologist', 'Nephrologist'),
            ('Urologist', 'Urologist'),
            ('rheumatologist', 'Rheumatologist'),
            ('anesthesiologist', 'Anesthesiologist'),
            ('hematologist', 'Hematologist'),
            ('allergist_immunologist', 'Allergist/Immunologist'),
            ('infectious_disease_specialist', 'Infectious Disease Specialist'),
        ], string='Specialization'
    )
    contact_info = fields.Text(string='Contact Information')
    patient_ids = fields.Many2many('hospital.patient', string='Patients')
    ref = fields.Char(string='Reference', default=lambda self: ('New'))
    color = fields.Char(string='Color', compute='_compute_random_color')
    room_id = fields.Many2one('hospital.room', string='Room Number')
    service_id = fields.Many2one('hospital.service', string='Service Provided')
    image = fields.Image(string='Image')

    @api.depends('name')
    def _compute_random_color(self):
        for patient in self:
            random_number = random.randint(0, 16777215)  # Generate a random number between 0 and 16777215
            patient.color = '#{:06x}'.format(random_number)  # Convert the random number to a hexadecimal color value

    @api.depends('color')
    def _compute_color_integer(self):
        for patient in self:
            patient.color_integer = int(patient.color[1:], 16)

    @api.model_create_multi
    def create(self, data_list):
        for data in data_list:
            data['ref'] = self.env['ir.sequence'].next_by_code('hospital.doctor')
        return super(HospitalDoctor, self).create(data_list)



