
from odoo import fields, models, api
from datetime import datetime, timedelta


class HospitalMeeting(models.Model):
    _name = 'hospital.meeting'
    _description = 'Hospital Appointment'

    name = fields.Selection([
        ('general', 'General Check-up'),
        ('consultation', 'Specialist Consultation'),
        ('follow-up', 'Follow-up Visit')
    ], string='Meeting Subject', required=True)
    patient_id = fields.Many2one('hospital.patient', string='Patient', required=True)
    doctor_id = fields.Many2one('hospital.doctor', string='Doctor', required=True)

    #timing
    starting_time = fields.Datetime(string='Starting at')
    ending_time = fields.Datetime(string='Ending at')
    duration = fields.Float(string='Duration')


    doc_room = fields.Many2one(related='doctor_id.room_id', readonly=True)

    state = fields.Selection([
        ('draft', 'Draft'),
        ('in_progres', 'In progres'),
        ('done', 'Done'),
        ('cancel', 'Cancel')
    ], string='State', default='draft', required=True)
    priority = fields.Selection([
        ('1', 'Low'),
        ('2', 'Medium'),
        ('3', 'High'),
        ('4', 'Urgent')
    ], string="Priority", default=2, required=True)


    def action_in_progress(self):
        for rec in self:
            rec.state = 'in_progres'

    def action_done(self):
        for rec in self:
            rec.state = 'done'

    def action_cancel(self):
        for rec in self:
            rec.state = 'cancel'

    def action_draft(self):
        for rec in self:
            rec.state = 'draft'