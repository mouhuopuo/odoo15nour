from odoo import api, models,fields
from datetime import datetime, timedelta

class ConfirmDate(models.TransientModel):
  _name='process.attendance.date.wizard'
  to_date = fields.Date('Process to date')


  def process_to_date(self):
    ret =False
    if self.to_date:
      # print('------------------jjj----------')
      # print(self.to_date)
      # dd = datetime.now().strftime('%Y-%m-%d')
      # print(dd)
      ret=self.env['od.attendance'].handle_all_cases(self.to_date)
    else:
      ret= self.env['od.attendance'].handle_all_cases()

    notification = {
        'type': 'ir.actions.client',
        'tag': 'display_notification',
        'params': {
            'title': ('Finger prints'),
            'message': 'Attendance Process is completed successfully',
            'type': 'success',  # types: success,warning,danger,info
            'sticky': False,  # True/False will display for few seconds if false
        },
    }
    if ret:
       return notification


