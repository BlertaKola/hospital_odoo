import random
from odoo import fields, models, api
from datetime import date
import time
from odoo.exceptions import ValidationError
class HospitalService(models.Model):
    _name = 'hospital.service'
    _description = 'Hospital Services'
    _inherit = 'mail.thread'

    name = fields.Char(string='Service')
    price = fields.Float(string='Price')
    category_id = fields.Many2one('hospital.service.category', string='Category')
    patient_id = fields.Many2one('hospital.patient')
    doctor_id = fields.Many2one('hospital.doctor', string='Doctor')
    ref = fields.Char(string='Reference', default=lambda self: ('New Service'))
    service_assign_ids = fields.One2many('hospital.service.assign', 'service_id', string='Service Assignments')

    @api.model_create_multi
    def create(self, vals):
        for data in vals:
            data['ref'] = self.env['ir.sequence'].next_by_code('hospital.service')
        return super(HospitalService, self).create(vals)


class HospitalServiceAssign(models.Model):
    _name = 'hospital.service.assign'
    _description = 'Hospital Service Assign'

    patient_id = fields.Many2one('hospital.patient', string='Patient')
    service_id = fields.Many2one('hospital.service', string='Services',
                                 domain="[('category_id', '=', service_category_id)]")
    date = fields.Date(string='Date', compute='_compute_date', store=True)
    service_category_id = fields.Many2one('hospital.service.category', string='Service Category')
    doctor = fields.Many2one(related='service_id.doctor_id', string='Doctor')
    result = fields.Selection([
        ('satisfactory', 'Satisfactory'),
        ('unsatisfactory', 'Unsatisfactory'),
        ('positive', 'Positive'),
        ('negative', 'Negative'),
        ('excellent', 'Excellent'),
        ('poor', 'Poor')
    ], string='Results', store=True)



    @api.onchange('service_category_id')
    def _onchange_service_category_id(self):
        self.service_id = False


    def assign_services(self):
        print("BLERTAAAAAAAAAAAAAAAAAaaaa")

    @api.model_create_multi
    def create(self, vals):
        for rec in vals:
            options = [
                'satisfactory',
                'unsatisfactory',
                'positive',
                'negative',
                'excellent',
                'poor'
            ]
            print("DELAY")
            rec['result'] = random.choice(options)
            rec['date'] = date.today()
        service = super(HospitalServiceAssign, self).create(vals)

        patient = service.patient_id
        print(patient.id)
        cartel = patient.cartel_id
        assigned_services = self.env['hospital.service.assign'].search([('patient_id', '=', patient.id)])
        res = []
        for rec in assigned_services:
            res.append(rec.id)
        print(assigned_services)
        print(res)

        if cartel:
            cartel.write({
                'test_data': res
            })
        else:
            raise ValidationError("You cannot take a service without generating a cartel.")

        return service