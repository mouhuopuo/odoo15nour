from odoo import api,models, fields

class module_settings(models.Model):
      _name = 'od.fp.settings'
      _description = 'internal use'

      setting_name = fields.Char(string='Name')
      setting_value = fields.Integer(string='Value')
      setting_value_text = fields.Char(string='Text value')

class hrattendance_ext(models.Model):
      _inherit = 'hr.attendance'
      _description = 'internal use'

      inout_ref = fields.Integer(string='Reference FP',index=True)

# class hratt_emp_ext(models.Model):
#       _inherit = 'hr.employee'
#       _description = 'Attendance processing mode'


class cal_att_ext(models.Model):
      _inherit = 'resource.calendar.attendance'
      _description = 'Extend calendar attendance'

      duration = fields.Integer(string='Duration in Hours')
