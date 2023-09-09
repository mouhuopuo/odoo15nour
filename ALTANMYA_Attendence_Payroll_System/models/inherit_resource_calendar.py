from odoo import api, models, fields
from odoo.exceptions import ValidationError

class ExtendResourceCal(models.Model):
    _inherit = 'resource.calendar'
    late_enter = fields.Integer(string='Late enter')
    late_enter2 = fields.Integer(string='Late enter 2')

    early_exit = fields.Integer(string='Early exit')
    early_overtime = fields.Integer(string='Early overtime')
    early_overtime2 = fields.Integer(string='Early overtime2')
    overtime1 = fields.Integer(string='Overtime1')
    overtime2 = fields.Integer(string='Overtime2')
    work_shift = fields.Selection([('oneweek', 'One week'), ('twoweek', 'Two weeks'), ('flex', 'Flexible')], string='Work shift mode'
                                  ,default='oneweek')
    enable_full_salary=fields.Boolean("Is employee type?")
    full_duration=fields.Integer(string='Full contract after duration')
    full_time= fields.Float(string='Full contract time')
    tol_in_early = fields.Float(string='Early in delay')
    tol_in_late = fields.Float(string='Late in delay')
    tol_out_early = fields.Float(string='Early out delay')
    tol_out_over = fields.Float(string='Late out delay')

    # leave_delay = fields.Integer(string='leave delay')
    @api.constrains('late_enter2')
    def _check_late_enter2(self):
        for record in self:
            if record.late_enter2:
                if record.late_enter2 <= record.late_enter or not record.late_enter :
                     raise ValidationError("Second stage of late enter should be greater than late enter stage one")

    @api.constrains('overtime2')
    def _check_overtime2(self):
        for record in self:
            if record.overtime2:
                if record.overtime2 <= record.overtime1 or not record.overtime1 :
                     raise ValidationError("Second stage of overtime should be greater than overtime stage one")
    @api.constrains('early_overtime2')
    def _check_overtime2(self):
        for record in self:
            if record.early_overtime2:
                if record.early_overtime2 <= record.early_overtime or not record.early_overtime :
                     raise ValidationError("Second stage of early overtime should be greater than early overtime stage one")



class tanExtendShift(models.Model):
    _inherit = 'resource.calendar.attendance'
    duration=fields.Integer(string="Duration")
    tol_in_early = fields.Float(string='Early in delay')
    tol_in_late = fields.Float(string='Late in delay')
    tol_out_early = fields.Float(string='Early out delay')
    tol_out_over = fields.Float(string='Late out delay')

    early_overtime2 = fields.Integer(string='Early overtime2')
    overtime2 = fields.Integer(string='Overtime2')