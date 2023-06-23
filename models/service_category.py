from odoo import fields, models, api


class HospitalServiceCategory(models.Model):
    _name = 'hospital.service.category'
    _description = 'Hospital Service Category'
    _inherit = 'mail.thread'

    name = fields.Char(string='Category')
    service_ids = fields.One2many('hospital.service', 'category_id', string='Services')
    ref = fields.Char(string='Reference', default=lambda self: ('New Category'))



    @api.model_create_multi
    def create(self, data_list):
        for data in data_list:
            data['ref'] = self.env['ir.sequence'].next_by_code('hospital.service.category')
        return super(HospitalServiceCategory, self).create(data_list)

