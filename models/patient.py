from odoo import api, fields, models
from odoo.exceptions import ValidationError
import random


class HospitalPatient(models.Model):
    _name = 'hospital.patient'
    _description = 'Patient Records'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string='Name', required=True, tracking=True)

    age = fields.Integer(string='Age', tracking=True)

    is_child = fields.Boolean(string='Is child?', tracking=True)

    notes = fields.Text(string='Notes', tracking=True)

    gender = fields.Selection([('male', 'Male'), ('female', 'Female'), ('other', 'Other')],
                              string='Gender', tracking=True)

    capitalized_name = fields.Char(string='Capitalized Name', compute="_compute_capitalized_name")

    ref = fields.Char(string='Reference', default=lambda self: ('New Patient'))

    room_id = fields.Many2one('hospital.room', string='Room')

    doctor_ids = fields.Many2many('hospital.doctor', string='Doctor')

    color = fields.Char(string='Color', compute='_compute_random_color')

    prescription_ids = fields.One2many('hospital.patient.lines', 'patient_id', string='Prescription')

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
        print("MARVIIIIIIIIIIIIIIIIIIIIII")
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



    def assign_room(self, room_id):
        room = self.env['hospital.room'].browse(room_id)
        if room.status in ['available', 'occupied'] and room.occupancy < room.capacity:
            room.occupancy += 1
            self.room_id = room
            # self.state = 'admitted'
        else:
            raise ValidationError("The selected room is at full capacity.")

    def release_room(self):
        if not self.room_id:
            raise ValidationError('Patient does not have a room assigned.')
        else:
            self.room_id.occupancy -= 1
            self.room_id = False





    @api.model_create_multi
    def create(self, data_list):
        for data in data_list:
            data['ref'] = self.env['ir.sequence'].next_by_code('hospital.patient')
        return super(HospitalPatient, self).create(data_list)

    @api.depends('name')
    def _compute_capitalized_name(self):
        for rec in self:
            if rec.name:
                rec.capitalized_name = rec.name.upper()
            else:
                rec.capitalized_name = ''

    @api.onchange('age')
    def _onchange_age(self):
        if self.age <= 10:
            self.is_child = True
        else:
            self.is_child = False


    # @api.onchange('service_assign_ids', 'diagnosis_ids', 'prescription_ids')
    # def update_medical_report(self):
    #     print("BLERTAAAAAAAAAAAAA")
    #     medical_report = self.medical_report_id
    #
    #     # Fetch related records
    #     services = self.service_assign_ids
    #     diagnoses = self.diagnosis_ids
    #     prescriptions = self.prescription_ids
    #
    #     # Update fields in the medical report
    #     medical_report.service_count = len(services)
    #     medical_report.diagnosis_count = len(diagnoses)
    #     medical_report.prescription_count = len(prescriptions)
    #
    #     # You can add more logic here to update other fields in the medical report
    #     return True

    # def write(self, vals):
    #     result = super(HospitalPatient, self).write(vals)
    #     self.update_medical_report()
    #     return result





class HospitalPatientLines(models.Model):
    _name = 'hospital.patient.lines'
    _description = 'Hospital Patient Lines'

    patient_id = fields.Many2one('hospital.patient')
    prescription_id = fields.Many2one('hospital.prescription', string='Prescription')
