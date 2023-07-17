from odoo import fields, models, api
from odoo.exceptions import ValidationError
from datetime import timedelta


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
    status = fields.Selection([
        ('due', 'Due'),
        ('upcoming', 'Upcoming'),
        ('completed', 'Completed')
    ], string='Status', compute='_compute_status')

    @api.depends('state', 'starting_time')
    def _compute_status(self):
        now = fields.Datetime.now()
        for rec in self:
            if rec.state == 'draft':
                if rec.starting_time and rec.starting_time <= now:
                    rec.status = 'due'
                else:
                    rec.status = 'upcoming'
            elif rec.state == 'done':
                rec.status = 'completed'
            else:
                rec.status = False

    # timing
    starting_time = fields.Datetime(string='Starting at', required=True)
    ending_time = fields.Datetime(string='Ending Time', compute='_compute_ending_time', store=True)

    @api.depends('starting_time')
    def _compute_ending_time(self):
        for rec in self:
            if rec.starting_time:
                starting_time = fields.Datetime.from_string(rec.starting_time)
                duration = timedelta(hours=1)  # Assuming the meeting duration is 1 hour
                rec.ending_time = starting_time + duration
            else:
                rec.ending_time = False

    # Some other code that I tried, but it did not cover the patient meeting conflict
    # @api.constrains('starting_time')
    # def _check_existing_meetings(self):
    #     for meeting in self:
    #         start_time = meeting.starting_time
    #         end_time = meeting.starting_time + timedelta(hours=1)  # Assuming the meeting duration is 1 hour
    #         domain = [
    #             ('starting_time', '<', end_time),
    #             ('ending_time', '>', start_time),
    #             ('doctor_id', '=', meeting.doctor_id.id),
    #             ('id', '!=', meeting.id)
    #         ]
    #         conflicting_meetings = self.search(domain)
    #
    #         for rec in conflicting_meetings:
    #             if rec.state in ('draft', 'in_progress'):
    #                 if rec.starting_time <= start_time < rec.ending_time:
    #                     raise ValidationError(
    #                         "This hour is already taken by another meeting. Please choose another timeslot.")
    #                 if rec.starting_time < end_time <= rec.ending_time:
    #                     raise ValidationError(
    #                         "This hour is already taken by another meeting. Please choose another timeslot.")

    @api.constrains('starting_time', 'patient_id')
    def _check_existing_meetings(self):
        for meeting in self:
            start_time = meeting.starting_time
            end_time = meeting.starting_time + timedelta(hours=1)  # Assuming the meeting duration is 1 hour
            domain = [
                ('starting_time', '<', end_time),
                ('ending_time', '>', start_time),
                ('id', '!=', meeting.id)
            ]
            conflicting_meetings = self.search(domain)

            for rec in conflicting_meetings:
                if rec.state in ('draft', 'in_progress'):
                    if rec.doctor_id.id == meeting.doctor_id.id:
                        raise ValidationError(
                            "This doctor already has a meeting at the given time. Please choose another timeslot.")
                    if rec.patient_id.id == meeting.patient_id.id:
                        raise ValidationError(
                            "This patient already has a meeting at the given time. Please choose another timeslot.")

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
