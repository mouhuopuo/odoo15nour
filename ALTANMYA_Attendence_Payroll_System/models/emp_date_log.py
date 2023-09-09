from odoo import api, fields, models, tools

class empdatelog(models.Model):
    _name = "emp.date.log"
    _auto = False
    inout_id = fields.Many2one('od.inout', 'inout_id', index=True)
    log_seq = fields.Integer(string='Sequence', index=True)
    log_date = fields.Datetime(string='Date/time', index=True)
    log_device = fields.Many2one('od.device', 'device', index=True)

    def name_get(self):
        lst = []
        for v in self:
            lst.append((v.id, str(v.id)))
        return lst

    def init(self):
        """ Event Question main report """
        tools.drop_view_if_exists(self._cr, 'emp_date_log')
        self._cr.execute(""" CREATE VIEW emp_date_log AS (
     SELECT row_number() OVER (ORDER BY od_attendance.log_date)  as id, 
        od_inout.id as inout_id, 
        od_attendance.log_seq,
        od_attendance.log_date,
        od_attendance.log_device
       FROM od_inout inner join od_attendance
       on (od_inout.emp_deviceno =od_attendance.log_userid) 
       and (od_attendance.log_date>=  (od_inout.att_date - INTERVAL '1 DAY' ) )
       and (od_attendance.log_date<=  (od_inout.att_date+ INTERVAL '2 DAY') )
       order by od_attendance.log_date
            )""")