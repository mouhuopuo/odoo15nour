from odoo import api,models, fields

class fp_device_log(models.Model):
      _name = 'fp.logerror'
      _description = 'Device Erros'

      log_date = fields.Datetime(string='Date/time')
      log_device = fields.Many2one('od.device', 'device')
      device_error =fields.Char(string='Error desc')
