from odoo import api,models, fields

class Device(models.Model):
      _name = 'od.device'
      _description = 'Device Record'

      device_name = fields.Char(string='Name')
      device_model =fields.Selection([('zk', 'ZK'), ('suprema', 'SUPREMA')],string='Device Model')
      device_port = fields.Integer(string='Port')
      device_key = fields.Char(string='Key')
      device_enables = fields.Boolean(string='Is Enabled')
      device_dwmode=fields.Selection([('read', 'Read'),('delete', 'Delete')],string='Mode',default='read')
      last_seq =fields.Integer('last sequence')
      treat_seq=fields.Integer('handle from')
      att_seq=fields.Integer('attendance from')
      download_date=fields.Datetime(string='Date/time')
