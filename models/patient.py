from odoo import api, fields, models
from odoo.exceptions import ValidationError
import random
from datetime import datetime

class HospitalPatient(models.Model):
    _name = 'hospital.patient'
    _description = 'Patient Records'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string='Name', required=True, tracking=True)

    notes = fields.Text(string='Notes', tracking=True)

    gender = fields.Selection([('male', 'Male'), ('female', 'Female'), ('other', 'Other')],
                              string='Gender', tracking=True)


    ref = fields.Char(string='Reference', default=lambda self: 'New Patient')

    room_id = fields.Many2one('hospital.room', string='Room')

    doctor_ids = fields.Many2many('hospital.doctor', string='Doctor')

    color = fields.Char(string='Color', compute='_compute_random_color')


    status = fields.Selection([
        ('admitted', 'Admitted'),
        ('other', 'Other')
    ], string='State', compute='_compute_patient_status')

    service_assign_ids = fields.One2many('hospital.service.assign', 'patient_id', string='Services Assigned')
    diagnosis_ids = fields.One2many('hospital.diagnosis', 'patient_id', string='Diagnoses')
    prescription_count = fields.Integer(string='Prescription Count', compute='_compute_prescription_count')
    services_count = fields.Integer(string='Services count', compute='_compute_services_count')
    diagnosis_count = fields.Integer(string='Diagnosis count', compute='_compute_diagnosis_count')
    appointments_count = fields.Integer(string='Appointment count', compute='_compute_appointments_count')
    image = fields.Image(string='Image')
    cartel_id = fields.Many2one('hospital.cartel', string='Cartel', readonly=True)
    allergy_ids = fields.One2many('hospital.allergy', 'patient_id', string='Allergies')
    birthday = fields.Date(string='Birthday')
    age = fields.Integer(string='Age', compute='_compute_age')

    @api.constrains('doctor_ids')
    def _check_doctor_limit(self):
        max_patients_per_doctor = 10

        for patient in self:
            if len(patient.doctor_ids) > 1:
                raise ValidationError("A patient can only have one doctor.")

            doctor = patient.doctor_ids and patient.doctor_ids[0]
            if doctor and len(doctor.patient_ids) > max_patients_per_doctor:
                raise ValidationError(
                    f"The doctor '{doctor.name}' already has {max_patients_per_doctor} patients. Cannot assign more patients to this doctor.")


    @api.depends('birthday')
    def _compute_age(self):
        today = datetime.now().date()
        for record in self:
            if record.birthday:
                birthday = fields.Date.from_string(record.birthday)
                age = today.year - birthday.year
                if (today.month, today.day) < (birthday.month, birthday.day):
                    age -= 1
                record.age = age
            else:
                record.age = 0

    def generate_cartel(self):
        cartel = self.env['hospital.cartel'].create({
            'name': f"{self.name}'s Cartel",
            'patient': self.name
        })
        self.cartel_id = cartel.id


    def _compute_appointments_count(self):
        for rec in self:
            appointments_count = self.env['hospital.meeting'].search_count([('patient_id', '=', rec.id)])
            rec.appointments_count = appointments_count


    def _compute_prescription_count(self):
        for rec in self:
            prescription_count = self.env['hospital.prescription'].search_count([('patient_id', '=', rec.id)])
            rec.prescription_count = prescription_count

    def _compute_diagnosis_count(self):
        for rec in self:
            diagnosis_count = self.env['hospital.diagnosis'].search_count([('patient_id', '=', rec.id)])
            rec.diagnosis_count = diagnosis_count



    def _compute_services_count(self):
        for rec in self:
            services_count = self.env['hospital.service.assign'].search_count([('patient_id', '=', rec.id)])
            rec.services_count = services_count

    def action_open_services_assign(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Assign Services',
            'res_model': 'hospital.service.assign',
            'domain': [('patient_id', '=', False)],
            'view_mode': 'form',
            'target': 'new',
            'context': {'default_patient_id': self.id},
        }



    def action_open_allergies(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Create Allergies',
            'res_model': 'hospital.allergy',
            'domain': [('patient_id', '=', False)],
            'view_mode': 'form',
            'target': 'new',
            'context': {'default_patient_id': self.id},
        }


    def action_open_diagnosis(self):
        print("BLERT")
        return {
            'type': 'ir.actions.act_window',
            'name': 'Create New Diagnosis',
            'res_model': 'hospital.diagnosis',
            'domain': [('patient_id', '=', self.id)],
            'view_mode': 'tree,form',
            'target': 'current',
            'context': {'default_patient_id': self.id},
        }
    def action_open_prescriptions(self):
        print("HELP")
        return {
            'type': 'ir.actions.act_window',
            'name': 'Create New Prescription',
            'res_model': 'hospital.prescription',
            'domain': [('patient_id', '=', False)],
            'view_mode': 'form',
            'target': 'new',
            'context': {'default_patient_id': self.id},
        }

    def action_open_appointments_assign(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Book Appointment',
            'res_model': 'hospital.meeting',
            'domain': [('patient_id', '=', False)],
            'view_mode': 'form',
            'target': 'new',
            'context': {'default_patient_id': self.id}
        }



    @api.depends('room_id.occupancy', 'room_id.occupancy')
    def _compute_patient_status(self):
        for patient in self:
            if patient.room_id:
                patient.status = 'admitted'
            else:
                patient.status = 'other'

    @api.depends('name')
    def _compute_random_color(self):
        for patient in self:
            random_number = random.randint(0, 16777215)  # Generate a random number between 0 and 16777215
            patient.color = '#{:06x}'.format(random_number)  # Convert the random number to a hexadecimal color value

    @api.depends('color')
    def _compute_color_integer(self):
        for patient in self:
            patient.color_integer = int(patient.color[1:], 16)


    #dealing with rooms
    show_button_assign = fields.Boolean(default=True)

    def button_assign(self):
        self.show_button_assign = False

    def button_release(self):
        self.show_button_assign = True

    def assign_room(self):
        room = self.env['hospital.room'].browse(self.room_id.id)
        if room.status in ['available', 'occupied'] and room.occupancy < room.capacity:
            room.occupancy += 1
            self.room_id = room
            self.button_assign()
        else:
            raise ValidationError("The selected room is at full capacity.")

    def release_room(self):
        if not self.room_id:
            raise ValidationError('Patient does not have a room assigned.')
        else:
            self.room_id.occupancy -= 1
            self.room_id = False
            self.button_release()





    @api.model_create_multi
    def create(self, data_list):
        for data in data_list:
            data['ref'] = self.env['ir.sequence'].next_by_code('hospital.patient')
        return super(HospitalPatient, self).create(data_list)

