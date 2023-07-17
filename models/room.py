from odoo import api, fields, models


class HospitalRoom(models.Model):
    _name = 'hospital.room'
    _description = 'Hospital Rooms'
    _inherit = 'mail.thread'

    name = fields.Char(string='Room Number', compute='_compute_room_name', store=True)
    capacity = fields.Integer(string='Capacity', help='Maximum number of occupants')
    occupancy = fields.Integer(string='Occupancy', default='0')
    room_type = fields.Selection([
            ('doctor_room', 'Doctor Room'),
            ('patient_room', 'Patient Room')], string='Room type')
    status = fields.Selection(
        [
            ('available', 'Available'),
            ('occupied', 'Occupied'),
            ('full', 'Full')
        ],
        string='Status',
        compute='_compute_room_status',
    )
    facilities = fields.Text(string='Facilities')
    floor_location = fields.Char(string='Floor/Location')
    price = fields.Float(string='Price')
    doctor_id = fields.Many2one('hospital.doctor')


    @api.depends('capacity', 'occupancy')
    def _compute_room_status(self):
        for room in self:
            if room.occupancy == 0:
                room.status = 'available'
            elif room.occupancy < room.capacity:
                room.status = 'occupied'
            elif room.occupancy >= room.capacity:
                room.status = 'full'

    @api.depends('room_type')
    def _compute_room_name(self):
        for room in self:
            prefix = ''
            if room.room_type == 'patient_room':
                prefix = 'PA'
            elif room.room_type == 'doctor_room':
                prefix = 'DR'
            room.name = f"{prefix}{room.id}"