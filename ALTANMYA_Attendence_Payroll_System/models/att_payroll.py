from odoo import api,models, fields
from datetime import date,datetime, timedelta
from pytz import timezone, utc
# from odoo.exceptions import UserError,Warning
# import pytz

class AttPayRoll(models.Model):
      _name = 'od.attpayroll'
      _inherit = ['mail.thread', 'mail.activity.mixin']
      _description = 'prepare for payroll'

      employee_id = fields.Many2one('hr.employee',string='Employee name', readonly=True)
      inout=fields.Integer('Reference Id')
      date_in = fields.Datetime(string='time in')
      diff_entry = fields.Char(string='Enter', readonly=True)

      date_out = fields.Datetime(string='time out')
      diff_Exit =fields.Char(string='Exit', readonly=True)

      status =fields.Selection([('draft', 'Draft'), ('validate', 'Validate'), ('reject', 'Reject'),('done', 'Done')],default='draft')
      status_u2 =fields.Selection([('draft', 'Draft'), ('validate', 'Validate'), ('reject', 'Reject'),('done', 'Done')],default='draft')

      status2 =fields.Selection([('draft', 'Draft'),('validate', 'Validate') , ('reject', 'Reject'),('done', 'Done')],default='draft')
      status2_u2 =fields.Selection([('draft', 'Draft'),('validate', 'Validate') , ('reject', 'Reject'),('done', 'Done')],default='draft')

      shift_id = fields.Many2one('resource.calendar.attendance',string='shift')
      att_date=fields.Date(string='Attendance date')
      att_leave=fields.Integer(string="leaving type")
      os_in = fields.Datetime(string='standard time in')
      os_out = fields.Datetime(string='standard time out')
      show_in=fields.Boolean(compute="fnc_show_in",store=False)
      show_out=fields.Boolean(compute="fnc_show_out",store=False)
      approval_level=fields.Integer(compute="check_level",store=False)
      is_hr=fields.Boolean(compute="_is_hr",store=False)

      def _is_hr(self):
          for rec in self:
              ret=False
              if self.env.user.has_group('ALTANMYA_Attendence_Payroll_System.altanmya_fgp_hr') or self.env.user.has_group('ALTANMYA_Attendence_Payroll_System.altanmya_fgp_admin'):
                  ret=True
              rec.is_hr=ret


      @api.depends('status')
      def fnc_show_in(self):
          for rec in self:
              if ((rec.status == 'draft' or rec.status_u2=='draft') and self.env.user.has_group('ALTANMYA_Attendence_Payroll_System.altanmya_fgp_admin'))\
                    or  (rec.status == 'draft'  and self.env.user.has_group('ALTANMYA_Attendence_Payroll_System.altanmya_fgp_manager'))\
                    or ( rec.status_u2=='draft' and self.env.user.has_group('ALTANMYA_Attendence_Payroll_System.altanmya_fgp_hr')  ):
                  rec.show_in= True
              else:
                  rec.show_in= False

      @api.depends('status2')
      def fnc_show_out(self):
          for rec in self:
              if ((rec.status2 == 'draft' or rec.status2_u2 == 'draft') and self.env.user.has_group(
                      'ALTANMYA_Attendence_Payroll_System.altanmya_fgp_admin')) \
                      or (rec.status2 == 'draft' and self.env.user.has_group('ALTANMYA_Attendence_Payroll_System.altanmya_fgp_manager')) \
                      or (rec.status2_u2 == 'draft' and self.env.user.has_group('ALTANMYA_Attendence_Payroll_System.altanmya_fgp_hr')):
                  rec.show_out=  True
              else:
                  rec.show_out=  False

      def btn_ok(self):

            for rec1 in self.ids:

              rec = self.browse(rec1)
              lev = rec.approval_level
              print('ok'+str(lev))
              if ((rec.status == 'draft' or rec.status_u2=='draft') and self.env.user.has_group('ALTANMYA_Attendence_Payroll_System.altanmya_fgp_admin')):
                 rec.status = 'validate'
                 rec.status_u2 = 'validate'
              elif (rec.status_u2 == 'draft'  and self.env.user.has_group('ALTANMYA_Attendence_Payroll_System.altanmya_fgp_hr')):
                  rec.status_u2 = 'validate'
                  if lev==1:
                      rec.status = 'validate'
              elif (rec.status == 'draft'  and self.env.user.has_group('ALTANMYA_Attendence_Payroll_System.altanmya_fgp_manager') and lev==2):
                  rec.status = 'validate'

              self.check_payroll(rec)
            # raise  UserError('ok' + str(self.id))
      # def btn_ok_u2(self):
      #       for rec1 in self.ids:
      #         rec = self.browse(rec1)
      #         if rec.status_u2 == 'draft':
      #            rec.status_u2 = 'validate'
      #            self.check_payroll(rec)
            # raise  UserError('ok' + str(self.id))

      def btn_no(self):

            for rec1 in self.ids:
              rec = self.browse(rec1)
              lev = rec.approval_level
              print('no' + str(lev))
              if ((rec.status == 'draft' or rec.status_u2=='draft') and self.env.user.has_group('ALTANMYA_Attendence_Payroll_System.altanmya_fgp_admin')):
                 rec.status = 'reject'
                 rec.status_u2 = 'reject'
              elif (rec.status_u2 == 'draft'  and self.env.user.has_group('ALTANMYA_Attendence_Payroll_System.altanmya_fgp_hr')):
                  rec.status_u2 = 'reject'
                  if lev==1:
                      rec.status = 'reject'
              elif (rec.status == 'draft'  and self.env.user.has_group('ALTANMYA_Attendence_Payroll_System.altanmya_fgp_manager') and lev==2):
                  rec.status = 'reject'

              self.check_payroll(rec)

            #raise UserError(_('no' + str(self.id)))
      # def btn_no_u2(self):
      #       for rec1 in self.ids:
      #         rec = self.browse(rec1)
      #         if rec.status_u2 == 'draft':
      #            rec.status_u2 = 'reject'
      #            self.check_payroll(rec)
            #raise UserError(_('no' + str(self.id)))

      def btn_ok2(self):

            for rec1 in self.ids:
              rec = self.browse(rec1)
              lev = rec.approval_level
              print('ok2' + str(lev))
              if ((rec.status2 == 'draft' or rec.status2_u2=='draft') and self.env.user.has_group('ALTANMYA_Attendence_Payroll_System.altanmya_fgp_admin')):
                 rec.status2 = 'validate'
                 rec.status2_u2 = 'validate'
              elif (rec.status2_u2 == 'draft'  and self.env.user.has_group('ALTANMYA_Attendence_Payroll_System.altanmya_fgp_hr')):
                  rec.status2_u2 = 'validate'
                  if lev==1:
                      rec.status2 = 'validate'
              elif (rec.status2 == 'draft'  and self.env.user.has_group('ALTANMYA_Attendence_Payroll_System.altanmya_fgp_manager') and lev==2):
                  rec.status2 = 'validate'

              self.check_payroll(rec)
      # def btn_ok2_u2(self):
      #       for rec1 in self.ids:
      #         rec=self.browse(rec1)
      #         if rec.status2_u2 == 'draft':
      #           rec.status2_u2 = 'validate'
      #           self.check_payroll(rec)


      def btn_no2(self):

            for rec1 in self.ids:
              rec = self.browse(rec1)
              lev = rec.approval_level
              print('ho2' + str(lev))
              if ((rec.status2 == 'draft' or rec.status2_u2=='draft') and self.env.user.has_group('ALTANMYA_Attendence_Payroll_System.altanmya_fgp_admin')):
                 rec.status2 = 'reject'
                 rec.status2_u2 = 'reject'
              elif (rec.status2_u2 == 'draft'  and self.env.user.has_group('ALTANMYA_Attendence_Payroll_System.altanmya_fgp_hr')):
                  rec.status2_u2 = 'reject'
                  if lev==1:
                      rec.status2 = 'reject'
              elif (rec.status2 == 'draft'  and self.env.user.has_group('ALTANMYA_Attendence_Payroll_System.altanmya_fgp_manager') and lev==2):
                  rec.status2 = 'reject'

              self.check_payroll(rec)

            # raise UserError(_('no' + str(self.id)))
      # def btn_no2_u2(self):
      #       for rec1 in self.ids:
      #         rec = self.browse(rec1)
      #         if rec.status2_u2 == 'draft':
      #            rec.status2_u2 = 'reject'
      #            self.check_payroll(rec)

            # raise UserError(_('no' + str(self.id)))

      def interval_to_int(self,st):
            sign=1
            res=0
            if st:
                if len(st)==9:
                      sign=-1
                      res = int(st[1: 3]) * 60 + int(st[4: 6])
                else:
                      res = int(st[0: 2]) * 60 + int(st[3: 5])
            return sign*res



      def check_payroll(self,rec):
            diff_hour = -3
            odoobot = self.env['res.users'].browse(1)
            tt = datetime.now(timezone(odoobot.tz)).strftime('%z')
            diff_hour = int(tt[1:3]) + int(tt[3:]) / 60
            if tt[0:1] == '+':
              diff_hour = -1 * diff_hour
            rec_settings = self.env['od.fp.settings'].sudo().search([('setting_name', '=', 'tz')], limit=1)
            if rec_settings:
                diff_hour =-1* rec_settings.setting_value

            if (rec.status in ('reject','validate')) and (rec.status2 in ('reject','validate') and rec.status_u2 in ('reject','validate')) and (rec.status2_u2 in ('reject','validate')):

                  cod_ATTEND=self.env['hr.work.entry.type'].sudo().search([('code', '=', 'ATTEND')], limit=1).id
                  cod_LATE1=self.env['hr.work.entry.type'].sudo().search([('code', '=', 'LATE')], limit=1).id
                  cod_LATE2=self.env['hr.work.entry.type'].sudo().search([('code', '=', 'LATE2')], limit=1).id
                  cod_ERLYOUT=self.env['hr.work.entry.type'].sudo().search([('code', '=', 'ERLYOUT')], limit=1).id
                  cod_BONUSENTRY=self.env['hr.work.entry.type'].sudo().search([('code', '=', 'ERLYIN')], limit=1).id
                  cod_BONUSENTRY2=self.env['hr.work.entry.type'].sudo().search([('code', '=', 'ERLYIN2')], limit=1).id
                  cod_OVT1=self.env['hr.work.entry.type'].sudo().search([('code', '=', 'OVT1')], limit=1).id
                  cod_OVT2=self.env['hr.work.entry.type'].sudo().search([('code', '=', 'OVT2')], limit=1).id
                  cod_OVT3=self.env['hr.work.entry.type'].sudo().search([('code', '=', 'OVT3')], limit=1).id
                  cod_OVT4=self.env['hr.work.entry.type'].sudo().search([('code', '=', 'OVT4')], limit=1).id
                  cod_holiday=self.env['hr.work.entry.type'].sudo().search([('code', '=', 'HOLATT')], limit=1).id
                  cod_weekend=self.env['hr.work.entry.type'].sudo().search([('code', '=', 'WEEKATT')], limit=1).id
                  # leave_delay =rec.shift_id.leave_delay
                  min_in=self.interval_to_int(rec.diff_entry)
                  min_out= self.interval_to_int(rec.diff_Exit)
                  res_entry=None
                  res_exit=None
                  late_entry1=None
                  late_entry2 = None
                  early_exit = None
                  bonus_entry = None
                  bonus_entry2 = None
                  bonus_exit1 = None
                  bonus_exit2 = None
                  late_entry1_2=None
                  isHoliday=False
                  isWeekEnd=False
                  unusaldays = rec.employee_id._get_unusual_days(rec.att_date, rec.att_date)
                  res_entry = rec.date_in
                  res_exit = rec.date_out
                  isFull =False

                  att_entry=datetime.combine(rec.att_date, datetime.min.time())+timedelta(hours=rec.shift_id.hour_from+diff_hour)
                  att_exit=datetime.combine(rec.att_date, datetime.min.time())+ timedelta(hours=rec.shift_id.hour_to+diff_hour)

                  if not rec.shift_id.duration or rec.shift_id.duration ==0:

                      att_exit = datetime.combine(rec.att_date, datetime.min.time())+timedelta(hours=rec.shift_id.hour_to+diff_hour)
                  else:
                      att_exit =datetime.combine(rec.att_date, datetime.min.time()) +timedelta(hours=rec.shift_id.duration+diff_hour)

                  if rec.att_leave != 0:
                      att_entry =rec.os_in
                      att_exit =rec.os_out

                  if  unusaldays and len([elem for elem in unusaldays.values() if elem ])>0 :
                      isHoliday=True
                      if not rec.check_holiday(rec.att_date,rec.att_date):
                          isWeekEnd=True
                  else:
                    if rec.status == 'validate' and rec.status_u2 =='validate'  : # and rec.status2 == 'validate'
                            if min_in<0:
                                 lat_enter1 =  rec.employee_id.resource_calendar_id.late_enter
                                 lat_enter2 =  rec.employee_id.resource_calendar_id.late_enter2
                                 if lat_enter2<=lat_enter1:
                                     lat_enter2=None
                                 if -1*min_in>lat_enter1 :
                                       res_entry = rec.date_in
                                       late_entry1=rec.date_in+ timedelta(minutes=min_in)
                                       late_entry1_2=res_entry
                                       if lat_enter2:
                                        if -1*min_in>lat_enter2:
                                           late_entry1_2=rec.date_in + timedelta(minutes=min_in)+ timedelta(minutes=lat_enter2)
                                           late_entry2 = rec.date_in + timedelta(minutes=min_in)+ timedelta(minutes=lat_enter2)


                                 else:
                                       res_entry = rec.date_in + timedelta(minutes=min_in)
                            else:
                                  eovt1=rec.employee_id.resource_calendar_id.early_overtime
                                  eovt2=rec.employee_id.resource_calendar_id.early_overtime2
                                  if rec.shift_id.early_overtime2:
                                      eovt2=rec.shift_id.early_overtime2
                                  if eovt2<=eovt1:
                                      eovt2=None

                                  res_entry = rec.date_in + timedelta(minutes=min_in)
                                  if min_in>eovt1 and rec.att_leave not in (1,4):
                                       bonus_entry =rec.date_in
                                       if eovt2:
                                        if eovt2>eovt1 and min_in>eovt2:
                                           bonus_entry2 = rec.date_in
                                           bonus_entry = rec.date_in+timedelta(minutes=min_in-eovt2)



                    if rec.status2=='validate' and rec.status2_u2=='validate':
                            if min_out<0:
                                 if -1*min_out>rec.employee_id.resource_calendar_id.early_exit:
                                       res_exit = rec.date_out
                                       early_exit=rec.date_out + timedelta(minutes=-1*min_out)
                                 else:
                                       res_exit=rec.date_out+timedelta(minutes=-1*min_out)
                            else:
                                  ovt1=rec.employee_id.resource_calendar_id.overtime1
                                  ovt2=rec.employee_id.resource_calendar_id.overtime2
                                  if rec.shift_id.overtime2:
                                      ovt2=rec.shift_id.overtime2
                                  if ovt2<=ovt1:
                                      ovt2=None
                                  res_exit = rec.date_out - timedelta(minutes=min_out)
                                  if min_out>ovt1 and  rec.att_leave not in (2,3) :
                                       bonus_exit1 =rec.date_out
                                       if ovt2:
                                        if ovt2>ovt1 and min_out>ovt2:
                                           # bonus_exit2 = rec.date_out
                                           bonus_exit2 = rec.date_out - timedelta(minutes=0)
                                           bonus_exit1 = rec.date_out- timedelta(minutes=min_out)+timedelta(minutes=ovt2)
                                           # aux= datetime.combine(att_exit, datetime.min.time())
                                           aux=att_exit+timedelta(minutes=rec.employee_id.resource_calendar_id.full_duration)
                                           print('------bonus_exit2:--------' + str(bonus_exit2))
                                           print('------aux:--------'+str(aux))
                                           if ovt2:
                                              if rec.employee_id.resource_calendar_id.enable_full_salary and bonus_exit2 >= aux :
                                                  isFull=True

                  if isHoliday and (rec.status == 'reject' or rec.status2 == 'reject' or rec.status_u2 == 'reject' or rec.status2_u2 == 'reject' ):
                      pass
                  elif isHoliday and rec.status=='validate' and rec.status2=='validate' and rec.status_u2=='validate' and rec.status2_u2 =='validate':
                      if isWeekEnd:
                          # Todo: add setting for the next statement to switch between holiday or weekend
                          cod_holiday=cod_weekend
                      qry = f"""select * from hr_work_entry where active=true and (work_entry_type_id is null or work_entry_type_id<>{cod_holiday}) and employee_id={rec.employee_id.id} and
                                        ((date_start>='{res_entry}' and date_start<= '{res_exit}') or
                                        (date_stop>='{res_entry}' and date_stop<= '{res_exit}')  or
                                        (date_start<='{res_entry}' and date_stop>='{res_exit}') )

                      """

                      new_cr=self._cr
                      new_cr.execute(qry)
                      vals = new_cr.dictfetchall()
                      if vals:
                          for row in vals:
                              if row.get('date_start') >=res_entry and row.get('date_stop')<= res_exit:
                                  # qry=f"update hr_work_entry set date_start='{res_entry}',date_stop='{res_exit}',work_entry_type_id={cod_holiday} where id="+str(row.get('id'))
                                  qry=f"delete from hr_work_entry where id="+str(row.get('id'))
                                  new_cr.execute(qry)
                              elif row.get('date_start') >=res_entry and row.get('date_start')<= res_exit:
                                  qry=f"update hr_work_entry set date_start='{res_exit}' where id="+str(row.get('id'))
                                  new_cr.execute(qry)
                              elif row.get('date_stop') >=res_entry and row.get('date_stop')<= res_exit:
                                  qry = f"update hr_work_entry set date_stop='{res_entry}' where id=" + str(row.get('id'))
                                  new_cr.execute(qry)
                              elif row.get('date_start') <=res_entry and row.get('date_stop')>= res_exit:

                                  qry = f"""insert into hr_work_entry
                                  (name,employee_id,work_entry_type_id,date_start,date_stop,company_id,contract_id,state,active,duration)
                                  select name,employee_id,work_entry_type_id,'{res_exit}',date_stop,company_id,contract_id,state,active,EXTRACT(EPOCH FROM (date_stop-timestamp '{res_exit}'))/3600 
                                  from hr_work_entry where id=""" + str(row.get('id'))
                                  new_cr.execute(qry)

                                  qry = f"update hr_work_entry set date_stop='{res_entry}',duration=EXTRACT(EPOCH FROM (timestamp '{res_entry}'- date_start))/3600  where id=" + str(row.get('id'))
                                  new_cr.execute(qry)

                              elif row.get('date_start') >=res_entry and row.get('date_stop')<= res_exit:
                                  qry = f"delete from hr_work_entry where id=" + str(row.get('id'))
                                  new_cr.execute(qry)

                      qry = f"""
                                                  insert into hr_work_entry
                                                  (name,employee_id,work_entry_type_id,date_start,date_stop,company_id,contract_id,state,active,duration)
                                                  select 'holiday attendance {rec.id}' ,employee_id,{cod_holiday},'{res_entry}'
                                                  ,'{res_exit}',hr_employee.company_id,hr_employee.contract_id,'draft',true,
                                                  EXTRACT(EPOCH FROM (timestamp '{res_exit}'-timestamp '{res_entry}'))/3600
                                                  from od_attpayroll inner join hr_employee on 
                                                  hr_employee.id=od_attpayroll.employee_id
                                                  where od_attpayroll.id={rec.id}
                                                  """
                      self._cr.execute(qry)
                      flag_mcgi=self.get_setting('mcgi')
                      if flag_mcgi and isHoliday and not isWeekEnd and ((res_entry+timedelta(hours=-1*diff_hour)).day) != ((res_exit+timedelta(hours=-1*diff_hour)).day):
                          # print('1--------')
                          # print(res_entry+timedelta(hours=-1*diff_hour))
                          # print('2--------')
                          # print(res_exit + timedelta(hours=-1*diff_hour))

                          self.mcgi(rec.att_date,cod_holiday,res_entry,res_exit,rec.id,diff_hour,cod_OVT1,cod_OVT2)
                      # print(qry)






                  else:
                      res_att_entry=att_entry
                      res_att_exit=att_exit
                      if (rec.status=='validate' and rec.status_u2=='validate') or not att_entry:
                          res_att_entry=res_entry
                      if (rec.status2=='validate' and rec.status2_u2=='validate') or not att_exit:
                          res_att_exit=res_exit

                      qry = f"""
                                        insert into hr_work_entry
                                        (name,employee_id,work_entry_type_id,date_start,date_stop,company_id,contract_id,state,active,duration,fromwork_hour,towork_hour)
                                        select 'attendance {rec.id}' ,employee_id,{cod_ATTEND},'{res_att_entry}'
                                        ,'{res_att_exit}',hr_employee.company_id,hr_employee.contract_id,'draft',true,
                                        EXTRACT(EPOCH FROM (timestamp '{res_att_exit}'-timestamp '{res_att_entry}'))/3600,
                                        (EXTRACT(hour  FROM (timestamp '{res_att_entry}')))+(-1*{diff_hour}),
                                        (EXTRACT(hour  FROM (timestamp '{res_att_exit}')))+(-1*{diff_hour})
                                        
                                        from od_attpayroll inner join hr_employee on 
                                        hr_employee.id=od_attpayroll.employee_id
                                        where od_attpayroll.id={rec.id}
                                        """
                      self._cr.execute(qry)
                      qry = f"""delete from hr_work_entry where work_entry_type_id<>{cod_ATTEND} and employee_id={rec.employee_id.id} and
                                        ((date_start<timestamp '{res_att_entry}' and date_stop>timestamp '{res_att_entry}') or
                                        (date_start<timestamp '{res_att_exit}' and date_stop>timestamp '{res_att_exit}')  or
                                        (date_start>=timestamp '{res_att_entry}' and date_stop<=timestamp '{res_att_exit}') )

                      """

                      self._cr.execute(qry)
                      if late_entry1:
                            qry = f"""
                                  insert into hr_work_entry
                                  (name,employee_id,work_entry_type_id,date_start,date_stop,company_id,contract_id,state,active,duration)
                                  select 'late enter {rec.id}' ,employee_id,{cod_LATE1},'{late_entry1}'
                                  ,'{late_entry1_2}',hr_employee.company_id,hr_employee.contract_id,'draft',true,
                                  EXTRACT(EPOCH FROM (timestamp '{late_entry1_2}'-timestamp '{late_entry1}'))/3600
                                  from od_attpayroll inner join hr_employee on 
                                  hr_employee.id=od_attpayroll.employee_id
                                  where od_attpayroll.id={rec.id}
                                  """
                            self._cr.execute(qry)
                            qry = f"""delete from hr_work_entry where work_entry_type_id<>{cod_LATE1}  and employee_id={rec.employee_id.id} and
                                  date_start<timestamp '{late_entry1}' and date_stop>timestamp '{late_entry1}'
                            """
                            self._cr.execute(qry)
                      if late_entry2:
                            qry = f"""
                                  insert into hr_work_entry
                                  (name,employee_id,work_entry_type_id,date_start,date_stop,company_id,contract_id,state,active,duration)
                                  select 'late enter {rec.id}' ,employee_id,{cod_LATE2},'{late_entry2}'
                                  ,'{res_entry}',hr_employee.company_id,hr_employee.contract_id,'draft',true,
                                  EXTRACT(EPOCH FROM (timestamp '{res_entry}'-timestamp '{late_entry2}'))/3600
                                  from od_attpayroll inner join hr_employee on 
                                  hr_employee.id=od_attpayroll.employee_id
                                  where od_attpayroll.id={rec.id}
                                  """
                            self._cr.execute(qry)
                            qry = f"""delete from hr_work_entry where work_entry_type_id<>{cod_LATE2}  and employee_id={rec.employee_id.id} and
                                  date_start<timestamp '{late_entry2}' and date_stop>timestamp '{late_entry2}'
                            """
                            self._cr.execute(qry)
                      if early_exit:
                            qry = f"""
                                  insert into hr_work_entry
                                  (name,employee_id,work_entry_type_id,date_start,date_stop,company_id,contract_id,state,active,duration)
                                  select 'early exit {rec.id}' ,employee_id,{cod_ERLYOUT},'{res_exit}'
                                  ,'{early_exit}',hr_employee.company_id,hr_employee.contract_id,'draft',true,
                                  EXTRACT(EPOCH FROM (timestamp '{early_exit}'-timestamp '{res_exit}'))/3600
                                  from od_attpayroll inner join hr_employee on 
                                  hr_employee.id=od_attpayroll.employee_id
                                  where od_attpayroll.id={rec.id}
                                  """
                            self._cr.execute(qry)
                            qry = f"""delete from hr_work_entry where work_entry_type_id<>{cod_ERLYOUT} and employee_id={rec.employee_id.id} and
                                  date_start<timestamp '{early_exit}' and date_stop>timestamp '{early_exit}'
                                  """
                            self._cr.execute(qry)
                      if bonus_entry:
                            qry = f"""
                                  insert into hr_work_entry
                                  (name,employee_id,work_entry_type_id,date_start,date_stop,company_id,contract_id,state,active,duration)
                                  select 'bonus early {rec.id}' ,employee_id,{cod_BONUSENTRY},'{bonus_entry}'
                                  ,'{res_entry}',hr_employee.company_id,hr_employee.contract_id,'draft',true,
                                  EXTRACT(EPOCH FROM (timestamp '{res_entry}'-timestamp '{bonus_entry}'))/3600
                                  from od_attpayroll inner join hr_employee on 
                                  hr_employee.id=od_attpayroll.employee_id
                                  where od_attpayroll.id={rec.id}
                                  """
                            self._cr.execute(qry)
                            qry = f"""delete from hr_work_entry where work_entry_type_id<>{cod_BONUSENTRY} and employee_id={rec.employee_id.id} and
                                  date_start<timestamp '{bonus_entry}' and date_stop>timestamp '{bonus_entry}'
                                  """
                            self._cr.execute(qry)
                      if bonus_entry2:
                            qry = f"""
                                  insert into hr_work_entry
                                  (name,employee_id,work_entry_type_id,date_start,date_stop,company_id,contract_id,state,active,duration)
                                  select 'bonus early {rec.id}' ,employee_id,{cod_BONUSENTRY2},'{bonus_entry2}'
                                  ,'{bonus_entry}',hr_employee.company_id,hr_employee.contract_id,'draft',true,
                                  EXTRACT(EPOCH FROM (timestamp '{bonus_entry}'-timestamp '{bonus_entry2}'))/3600
                                  from od_attpayroll inner join hr_employee on 
                                  hr_employee.id=od_attpayroll.employee_id
                                  where od_attpayroll.id={rec.id}
                                  """
                            self._cr.execute(qry)
                            qry = f"""delete from hr_work_entry where work_entry_type_id<>{cod_BONUSENTRY2} and employee_id={rec.employee_id.id} and
                                  date_start<timestamp '{bonus_entry2}' and date_stop>timestamp '{bonus_entry2}'
                                  """
                            self._cr.execute(qry)
                      if bonus_exit1:
                            qry = f"""
                                  insert into hr_work_entry
                                  (name,employee_id,work_entry_type_id,date_start,date_stop,company_id,contract_id,state,active,duration)
                                  select '{'overtime3' if isFull else 'overtime1'} {rec.id}' ,employee_id,{cod_OVT3 if isFull else cod_OVT1},'{res_exit}'
                                  ,'{bonus_exit1}',hr_employee.company_id,hr_employee.contract_id,'draft',true,
                                  EXTRACT(EPOCH FROM (timestamp '{bonus_exit1}'-timestamp '{res_exit}'))/3600
                                  from od_attpayroll inner join hr_employee on 
                                  hr_employee.id=od_attpayroll.employee_id
                                  where od_attpayroll.id={rec.id}
                                  """
                            self._cr.execute(qry)
                            qry = f"""delete from hr_work_entry where (work_entry_type_id<>{cod_OVT1} or work_entry_type_id<>{cod_OVT3}) and employee_id={rec.employee_id.id} and
                                  date_start<timestamp '{bonus_exit1}' and date_stop>timestamp '{bonus_exit1}'
                                  """
                            self._cr.execute(qry)
                      if bonus_exit2:
                            qry = f"""
                                  insert into hr_work_entry
                                  (name,employee_id,work_entry_type_id,date_start,date_stop,company_id,contract_id,state,active,duration)
                                  select '{'overtime4' if isFull else 'overtime2'} {rec.id}' ,employee_id,{cod_OVT4 if isFull else cod_OVT2},'{bonus_exit1}'
                                  ,'{bonus_exit2}',hr_employee.company_id,hr_employee.contract_id,'draft',true,
                                  EXTRACT(EPOCH FROM (timestamp '{bonus_exit2}'-timestamp '{bonus_exit1}'))/3600
                                  from od_attpayroll inner join hr_employee on 
                                  hr_employee.id=od_attpayroll.employee_id
                                  where od_attpayroll.id={rec.id}
                                  """
                            self._cr.execute(qry)
                            qry = f"""delete from hr_work_entry where (work_entry_type_id<>{cod_OVT2} or work_entry_type_id<>{cod_OVT4} ) and employee_id={rec.employee_id.id} and
                                  date_start<timestamp '{bonus_exit2}' and date_stop>timestamp '{bonus_exit2}'
                                  """
                            self._cr.execute(qry)

                  rec.status='done'
                  rec.status2='done'


      def mcgi(self,att_date,cod_holiday,res_entry,res_exit,id,diff_hour,cod_OVT1,cod_OVT2):
           if (res_entry.day !=res_exit.day):
               print('res entry')
               print(res_entry)
               print('res exit')
               print(res_exit)
               new_exit=datetime.combine(att_date+timedelta(days=1), datetime.min.time())+timedelta(hours=diff_hour)
               print('new exit')
               print(new_exit)
               qry = f"""
                     update hr_work_entry 
                     set date_stop='{new_exit}',
                     duration=EXTRACT(EPOCH FROM (timestamp '{new_exit}'-timestamp '{res_entry}'))/3600
                     where work_entry_type_id={cod_holiday} and name='holiday attendance {id}'
                     """
               self._cr.execute(qry)
               new_exit2=new_exit+timedelta(hours=7)
               if new_exit2>=res_exit:
                   qry = f"""
                          insert into hr_work_entry
                          (name,employee_id,work_entry_type_id,date_start,date_stop,company_id,contract_id,state,active,duration)
                          select 'overtime2 {id}' ,employee_id,{cod_OVT2},'{new_exit}'
                          ,'{res_exit}',hr_employee.company_id,hr_employee.contract_id,'draft',true,
                          EXTRACT(EPOCH FROM (timestamp '{res_exit}'-timestamp '{new_exit}'))/3600
                          from od_attpayroll inner join hr_employee on 
                          hr_employee.id=od_attpayroll.employee_id
                          where od_attpayroll.id={id}
                          """
                   self._cr.execute(qry)
               else:
                   qry = f"""
                          insert into hr_work_entry
                          (name,employee_id,work_entry_type_id,date_start,date_stop,company_id,contract_id,state,active,duration)
                          select 'overtime2 {id}' ,employee_id,{cod_OVT2},'{new_exit}'
                          ,'{new_exit2}',hr_employee.company_id,hr_employee.contract_id,'draft',true,
                          EXTRACT(EPOCH FROM (timestamp '{new_exit2}'-timestamp '{new_exit}'))/3600
                          from od_attpayroll inner join hr_employee on 
                          hr_employee.id=od_attpayroll.employee_id
                          where od_attpayroll.id={id}
                          """
                   self._cr.execute(qry)
                   qry = f"""
                          insert into hr_work_entry
                          (name,employee_id,work_entry_type_id,date_start,date_stop,company_id,contract_id,state,active,duration)
                          select 'overtime1 {id}' ,employee_id,{cod_OVT1},'{new_exit2}'
                          ,'{res_exit}',hr_employee.company_id,hr_employee.contract_id,'draft',true,
                          EXTRACT(EPOCH FROM (timestamp '{res_exit}'-timestamp '{new_exit2}'))/3600
                          from od_attpayroll inner join hr_employee on 
                          hr_employee.id=od_attpayroll.employee_id
                          where od_attpayroll.id={id}
                          """
                   self._cr.execute(qry)




      def check_level(self):
          lev = 1
          rec_settings = self.env['od.fp.settings'].sudo().search([('setting_name', '=', 'Approval levels')], limit=1)
          if rec_settings:
              lev = rec_settings.setting_value
          # print(lev)
          self.approval_level=lev


      def action_transfer(self):
            if self.tranfer_payroll():
                  notification = {
                        'type': 'ir.actions.client',
                        'tag': 'display_notification',
                        'params': {
                              'title': ('Finger prints'),
                              'message': 'Transfer to payroll is completed successfully',
                              'type': 'success',  # types: success,warning,danger,info
                              'sticky': False,  # True/False will display for few seconds if false
                        },
                  }
                  return notification

      def get_setting(self, settingname):
          last_date_rec = None
          rec_settings = self.env['od.fp.settings'].sudo().search([('setting_name', '=', settingname)], limit=1)
          if rec_settings:
              return rec_settings.setting_value
          else:
              return None

      def check_holiday(self, start_dt, end_dt, resources=None, domain=None, tz=None):
          """ Return the leave intervals in the given datetime range.
              The returned intervals are expressed in specified tz or in the calendar's timezone.
          """
          resources = self.env['resource.resource'] if not resources else resources
          # assert start_dt.tzinfo and end_dt.tzinfo
          self.ensure_one()

          # for the computation, express all datetimes in UTC
          resources_list = list(resources) + [self.env['resource.resource']]
          resource_ids = [r.id for r in resources_list]
          if domain is None:
              domain = [('time_type', '=', 'leave')]
          domain = domain + [
              ('calendar_id', 'in', [False, self.id]),
              ('resource_id', 'in', resource_ids),
              ('date_from', '<=', end_dt),
              ('date_to', '>=', start_dt),
          ]

          # retrieve leave intervals in (start_dt, end_dt)
          result = self.env['resource.calendar.leaves'].search(domain)
          if result and len(result)>0:
             return True
          return False

      def datetime_to_string(dt):
          """ Convert the given datetime (converted in UTC) to a string value. """
          return fields.Datetime.to_string(dt.astimezone(utc))

      def tranfer_payroll(self):
          if self.env.user.has_group('ALTANMYA_Attendence_Payroll_System.altanmya_fgp_admin') or self.env.user.has_group('ALTANMYA_Attendence_Payroll_System.altanmya_fgp_hr')  :
            n_cr=self._cr
            diff_hour = -3
            odoobot = self.env['res.users'].browse(1)
            tt = datetime.now(timezone(odoobot.tz)).strftime('%z')
            diff_hour = int(tt[1:3]) + int(tt[3:]) / 60
            if tt[0:1] == '+':
                  diff_hour = -1 * diff_hour
            rec_settings = self.env['od.fp.settings'].sudo().search([('setting_name', '=', 'tz')],
                                                                    limit=1)
            if rec_settings:
                diff_hour = -1 * rec_settings.setting_value
            qry=f"""
            insert into od_attpayroll (employee_id,"inout",date_in,diff_entry,date_out,"diff_Exit",status,status_u2,shift_id
            ,att_date,status2,status2_u2,att_leave,os_in,os_out)
select EE.id,AA.id,AA.date_in,
case when AA.att_leave<>0 then AA.os_in-AA.date_in else (AA.att_date-AA.date_in)+interval '1 hours'*(rca.hour_from+{diff_hour}) end as diffin,AA.date_out,
case when AA.att_leave<>0 then AA.date_out-AA.os_out else AA.date_out-(AA.att_date+interval '1 hours'*
			(rca.hour_from+{diff_hour}+
(case when COALESCE(rca.duration,0)=0 then rca.hour_to-rca.hour_from else rca.duration end))) end as diffout
,'draft','draft',AA.shift_id,AA.att_date,'draft','draft',AA.att_leave,AA.os_in,AA.os_out
            from od_inout AS AA left join od_attpayroll AS B on AA.id=B.inout
            inner join hr_employee AS EE on EE.studio_employee_number=AA.emp_deviceno
            left join resource_calendar_attendance
			 as  rca on rca.id= AA.shift_id
            where B.id is null and  EE.att_mode in ('shift')
            """
            # Notification section Todo

            n_cr.execute(qry)
            # rec_id = self.env['ir.model'].sudo().search([('model', '=', 'od.attpayroll')], limit=1)
            # if n_cr.rowcount:
            #     qry = f"""
            #                 select  u.id as id
            #                from res_groups_users_rel G inner join res_users U on G.uid=U.id
            #     inner join res_groups s on s.id=G.gid
            #     where s.name='Fgp Hr officer'
            #                 """
            #     n_cr.execute("select max(id) as maxp from od_attpayroll ")
            #
            #     rows=n_cr.dictfetchall()
            #     max_id=rows[0].get('maxp')
            #     n_cr.execute(qry)
            #     rows = n_cr.dictfetchall()
            #     if rows:
            #         for row in rows:
            #             self.env['mail.activity'].sudo().create({
            #                 'activity_type_id': 4,
            #                 'date_deadline': date.today(),
            #                 'summary': 'Request to approve',
            #                 'user_id':row.get('id'),
            #                 'res_model_id': rec_id.id,
            #                  'res_id': max_id
            #             })
            #     # n_cr.execute(qry)
            #     # n_cr.execute(qry)
            #     if self.approval_level == 2:
            #         qry = f"""
            #                     insert into mail_activity (res_model_id, res_id, activity_type_id, summary, date_deadline, user_id)
            #                     select  {rec_id.id},od.id,4,'Request to approve',{date.today()},ee2.user_id from od_attpayroll as od
            #                     inner join hr_employee ee on od.employee_id=ee.id
            #                     inner join hr_employee ee2 on ee2.id=ee.parent_id
            #                     where od.id>{max_id}
            #                     """
                    # n_cr.execute(qry)
            return True
