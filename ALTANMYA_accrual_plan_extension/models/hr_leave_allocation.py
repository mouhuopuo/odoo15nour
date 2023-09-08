from collections import defaultdict

from odoo.addons.resource.models.resource import HOURS_PER_DAY
from odoo import api, fields, models, _

from datetime import datetime, time, timedelta
from dateutil.relativedelta import relativedelta
from odoo.tools import get_timedelta


class HolidaysAllocation(models.Model):
    """ Allocation Requests Access specifications: similar to leave requests """
    _inherit = "hr.leave.allocation"
    _description = "Time Off Allocation"

    is_grace_period_passed = fields.Boolean('Is grace period passed', default=True)
    last_year_postponed_days = fields.Float('Last year postponed days')

    @api.model_create_multi
    def create(self, vals_list):
        holidays = super().create(vals_list)
        holidays.write({'is_grace_period_passed': True})
        return holidays

    @api.model
    def _update_accrual(self):
        """
            Method called by the cron task in order to increment the number_of_days when
            necessary.
        """
        # Get the current date to determine the start and end of the accrual period
        today = datetime.combine(fields.Date.today(), time(0, 0, 0))
        this_year_first_day = (today + relativedelta(day=1, month=1)).date()
        # this_year_first_day = '2024-01-01'
        end_of_year_allocations = self.search(
            [('allocation_type', '=', 'accrual'), ('state', '=', 'validate'), ('accrual_plan_id', '!=', False),
             ('employee_id', '!=', False),
             '|', ('date_to', '=', False), ('date_to', '>', fields.Datetime.now()),
             ('lastcall', '<', this_year_first_day)])
        print('end of year ', self.lastcall, end_of_year_allocations, this_year_first_day)

        for eoy_allocation in end_of_year_allocations:
            current_level = eoy_allocation._get_current_accrual_plan_level_id(this_year_first_day)[0]
            if current_level.action_with_unused_accruals != 'contract_postponed':
                eoy_allocation._end_of_year_accrual()
                eoy_allocation.flush()

        # the new implementation
        employees = self.env['hr.employee'].search([])
        for emp in employees:
            contracts = emp._get_first_contracts().sorted('date_start', reverse=True)
            prev_contract = self.env['hr.contract']
            current_contract = self.env['hr.contract']
            print('emp ', emp.name)
            if len(contracts) >= 1:
                current_contract = contracts[0]
            if len(contracts) > 1:
                prev_contract = contracts[1]
            print('curr bro ', current_contract, current_contract.date_start, current_contract.date_end)

            end_of_contract_year_allocations = self.search(
                [('allocation_type', '=', 'accrual'), ('state', '=', 'validate'), ('accrual_plan_id', '!=', False),
                 ('employee_id', '=', emp.id),
                 '|', ('date_to', '=', False), ('date_to', '>', fields.Datetime.now()),
                 ('lastcall', '<=', current_contract.date_start), ]
            )

            for alloc in end_of_contract_year_allocations:
                print('alloc ', alloc)
                curr_lvl = alloc._get_current_accrual_plan_level_id(current_contract.date_start + timedelta(days=1))[0]
                print('employee is : ', emp.name)
                print('current contract ', current_contract)
                print('previous contract ', prev_contract)

                if curr_lvl:
                    if curr_lvl.action_with_unused_accruals != 'contract_postponed':
                        print('hello Im in first if in curr_level altanmya ',curr_lvl.action_with_unused_accruals )
                        if alloc.lastcall < this_year_first_day:
                            alloc._end_of_year_accrual()
                            alloc.flush()
                    elif curr_lvl.action_with_unused_accruals == 'contract_postponed':
                        print('hello Im in elif in curr_level altanmya ', curr_lvl.action_with_unused_accruals)
                        if not current_contract.date_end:
                            print('hello Im in elif-> not current_contract.date_end  ')
                            alloc._end_of_year_accrual()
                            alloc.flush()
                        elif current_contract and current_contract.state == 'open':
                            print('hello Im in elif--------> current_contract and current_contract.state == open')
                            alloc._end_of_contract_year_accrual(prev_contract.date_end, current_contract.date_start)
                            alloc.flush()
                        else:
                            print('hello Im in elif--------> else')
                            alloc._end_of_year_accrual()
                            alloc.flush()


        allocations = self.search(
            [('allocation_type', '=', 'accrual'), ('state', '=', 'validate'), ('accrual_plan_id', '!=', False),
             ('employee_id', '!=', False),
             '|', ('date_to', '=', False), ('date_to', '>', fields.Datetime.now()),
             '|', ('nextcall', '=', False), ('nextcall', '<=', today)])
        # !!! check point
        allocations._process_accrual_plans(date_to=False, force_period=False)
        print('all allocation : ', allocations)

    def _end_of_contract_year_accrual(self, end_of_active_contract, start_of_new_contract):
        today = fields.Date.today()
        last_day_last_year = today + relativedelta(years=-1, month=12, day=31)
        first_day_this_year = today + relativedelta(month=1, day=1)
        print('enterd id ', self.id)
        # first_day_this_year = datetime.strptime('2024-01-01', '%Y-%m-%d').date()

        for allocation in self:
            current_level = allocation._get_current_accrual_plan_level_id(start_of_new_contract)[0]
            if not current_level:
                continue
            print('curr lvl ', current_level)
            lastcall = current_level._get_previous_date(start_of_new_contract)
            nextcall = current_level._get_next_date(start_of_new_contract)

            print('last call ', lastcall)
            print('next call', nextcall)
            if current_level.action_with_unused_accruals == 'contract_postponed' and current_level.postpone_max_days:
                # Make sure the period was ran until the last day of last year
                if allocation.nextcall:
                    allocation.nextcall = end_of_active_contract
                allocation._process_accrual_plans(end_of_active_contract, True)
                number_of_days = min(allocation.number_of_days - allocation.leaves_taken,
                                     current_level.postpone_max_days) + allocation.leaves_taken
                print('number of days : ', number_of_days)
                allocation.write({'number_of_days': number_of_days, 'lastcall': lastcall, 'nextcall': nextcall})
                allocation.write({'is_grace_period_passed': False, 'last_year_postponed_days': number_of_days})
                print('allocation : ', allocation)
    # this handles postponed max_days
    def _end_of_year_accrual(self):
        # to override in payroll
        today = fields.Date.today()
        last_day_last_year = today + relativedelta(years=-1, month=12, day=31)
        first_day_this_year = today + relativedelta(month=1, day=1)

        # first_day_this_year = datetime.strptime('2024-01-01', '%Y-%m-%d').date()
        # last_day_last_year = datetime.strptime('2024-12-31', '%Y-%m-%d').date()

        for allocation in self:
            current_level = allocation._get_current_accrual_plan_level_id(first_day_this_year)[0]
            if not current_level:
                continue
            print('curr lvl ', current_level)
            lastcall = current_level._get_previous_date(first_day_this_year)
            nextcall = current_level._get_next_date(first_day_this_year)
            if current_level.action_with_unused_accruals == 'lost':
                print('lastcall lost ', lastcall)
                if lastcall == first_day_this_year:
                    lastcall = current_level._get_previous_date(first_day_this_year - relativedelta(days=1))
                    nextcall = first_day_this_year
                    print('last and next: ', lastcall, nextcall)
                print('num of days ', allocation.leaves_taken)
                # Allocations are lost but number_of_days should not be lower than leaves_taken
                allocation.write(
                    {'number_of_days': allocation.leaves_taken, 'lastcall': lastcall, 'nextcall': nextcall})
            elif current_level.action_with_unused_accruals in ['postponed', 'contract_postponed'] and current_level.postpone_max_days:
                # Make sure the period was ran until the last day of last year
                if allocation.nextcall:
                    allocation.nextcall = last_day_last_year
                allocation._process_accrual_plans(last_day_last_year, True)
                number_of_days = min(allocation.number_of_days - allocation.leaves_taken,
                                     current_level.postpone_max_days) + allocation.leaves_taken
                print('data : ',
                      min(allocation.number_of_days - allocation.leaves_taken, current_level.postpone_max_days), ' ,, ',
                      allocation.leaves_taken)
                print('number of days : ', number_of_days)
                allocation.write({'number_of_days': number_of_days, 'lastcall': lastcall, 'nextcall': nextcall})
                allocation.write({'is_grace_period_passed': False, 'last_year_postponed_days': number_of_days})
                print('allocation : ', allocation)

    def check_grace_period(self, contract_start_date=False):
        # Get the current date to determine the start and end of the accrual period
        today = datetime.combine(fields.Date.today(), time(0, 0, 0))
        # this_year_first_day = (today + relativedelta(day=1, month=1)).date()
        # this_year_first_day = '2024-01-01'
        allocations = self.search(
            [('allocation_type', '=', 'accrual'), ('state', '=', 'validate'), ('accrual_plan_id', '!=', False),
             ('employee_id', '!=', False),
             '|', ('date_to', '=', False), ('date_to', '>', fields.Datetime.now()),
             ('is_grace_period_passed', '=', False)])
        print('allocations in check grace period ', allocations)
        for allocation in allocations:
            if allocation.accrual_plan_id:
                current_level = self.env['hr.leave.accrual.level']
                if allocation.nextcall:
                    current_level = allocation._get_current_accrual_plan_level_id(allocation.nextcall)[0]
                    print('current level is : ', current_level)
                if current_level and not allocation.is_grace_period_passed:
                    if current_level.action_with_unused_accruals in ('postponed', 'contract_postponed') and current_level.grace_period:
                        print('grace period : ', current_level.grace_period)
                        grace_type_multipliers = {
                            'day': 1,
                            'month': 30,
                        }
                        grace_period_in_days = current_level.grace_period * grace_type_multipliers[
                            current_level.grace_type]
                        print('grace period in days', grace_period_in_days)
                        # needs to check for the next year start date
                        first_day_this_year = today + relativedelta(month=1, day=1)
                        number_of_days_since_the_start_of_year = today - first_day_this_year
                        if current_level.action_with_unused_accruals == 'contract_postponed':
                            contracts = allocation.employee_id._get_first_contracts().sorted('date_start', reverse=True)
                            if len(contracts) >= 1:
                                if not contracts[0].date_end:
                                    number_of_days_since_the_start_of_year = today - first_day_this_year
                                else:
                                    number_of_days_since_the_start_of_year = today.date() - contracts[0].date_start
                        print('dddddddd : ', number_of_days_since_the_start_of_year.days)
                        if grace_period_in_days < number_of_days_since_the_start_of_year.days:
                            employee_days_per_allocation = allocation.holiday_status_id._get_employees_days_per_allocation_in_this_year(
                                allocation.employee_id.ids)
                            print('employee_days_per_allocation: ', employee_days_per_allocation)

                            allocation.max_leaves = allocation.number_of_hours_display if allocation.type_request_unit == 'hour' else allocation.number_of_days
                            allocation.leaves_taken = \
                                employee_days_per_allocation[allocation.employee_id.id][
                                    allocation.holiday_status_id][
                                    allocation]['remaining_leaves']
                            taken_leaves = employee_days_per_allocation[allocation.employee_id.id][
                                allocation.holiday_status_id][
                                allocation]['virtual_leaves_taken']
                            print('days per allocations : ',
                                  employee_days_per_allocation[allocation.employee_id.id][
                                      allocation.holiday_status_id][
                                      allocation]['virtual_leaves_taken'])
                            print('max leaves ', allocation.max_leaves)
                            print('diff is : ',
                                  allocation.max_leaves - employee_days_per_allocation[allocation.employee_id.id][
                                      allocation.holiday_status_id][
                                      allocation]['virtual_leaves_taken'])
                            # last_year_postponed_days = 20
                            if taken_leaves < allocation.last_year_postponed_days:
                                allocation.number_of_days -= (allocation.last_year_postponed_days - taken_leaves)
                                allocation.is_grace_period_passed = True
                            else:
                                allocation.is_grace_period_passed = True


    def _process_accrual_plans(self, date_to=False, force_period=False):
        print("Altanmya _____hello i'm in _process_accrual_plans")
        """
        This method is part of the cron's process.
        The goal of this method is to retroactively apply accrual plan levels and progress from nextcall to date_to or today.
        If force_period is set, the accrual will run until date_to in a prorated way (used for end of year accrual actions).
        """
        date_to = date_to or fields.Date.today()
        first_allocation = _("""This allocation have already ran once, any modification won't be effective to the days allocated to the employee. If you need to change the configuration of the allocation, cancel and create a new one.""")
        for allocation in self:
            level_ids = allocation.accrual_plan_id.level_ids.sorted('sequence')
            if not level_ids:
                continue
            if not allocation.nextcall:
                first_level = level_ids[0]
                first_level_start_date = allocation.date_from + get_timedelta(first_level.start_count, first_level.start_type)
                if date_to < first_level_start_date:
                    # Accrual plan is not configured properly or has not started
                    continue
                allocation.lastcall = max(allocation.lastcall, first_level_start_date)
                allocation.nextcall = first_level._get_next_date(allocation.lastcall)
                if len(level_ids) > 1:
                    second_level_start_date = allocation.date_from + get_timedelta(level_ids[1].start_count, level_ids[1].start_type)
                    allocation.nextcall = min(second_level_start_date, allocation.nextcall)
                allocation._message_log(body=first_allocation)
            days_added_per_level = defaultdict(lambda: 0)
            while allocation.nextcall <= date_to:
                (current_level, current_level_idx) = allocation._get_current_accrual_plan_level_id(allocation.nextcall)
                nextcall = current_level._get_next_date(allocation.nextcall)
                # Since _get_previous_date returns the given date if it corresponds to a call date
                # this will always return lastcall except possibly on the first call
                # this is used to prorate the first number of days given to the employee
                period_start = current_level._get_previous_date(allocation.lastcall)
                period_end = current_level._get_next_date(allocation.lastcall)
                # Also prorate this accrual in the event that we are passing from one level to another
                if current_level_idx < (len(level_ids) - 1) and allocation.accrual_plan_id.transition_mode == 'immediately':
                    next_level = level_ids[current_level_idx + 1]
                    current_level_last_date = allocation.date_from + get_timedelta(next_level.start_count, next_level.start_type)
                    if allocation.nextcall != current_level_last_date:
                        nextcall = min(nextcall, current_level_last_date)
                # We have to check for end of year actions if it is within our period
                #  since we can create retroactive allocations.
                if allocation.lastcall.year < allocation.nextcall.year and\
                    current_level.action_with_unused_accruals == 'postponed' and\
                    current_level.postpone_max_days > 0:
                    # Compute number of days kept
                    allocation_days = allocation.number_of_days - allocation.leaves_taken
                    allowed_to_keep = max(0, current_level.postpone_max_days - allocation_days)
                    number_of_days = min(allocation_days, current_level.postpone_max_days)
                    allocation.number_of_days = number_of_days + allocation.leaves_taken
                    total_gained_days = sum(days_added_per_level.values())
                    days_added_per_level.clear()
                    days_added_per_level[current_level] = min(total_gained_days, allowed_to_keep)
                gained_days = allocation._process_accrual_plan_level(
                    current_level, period_start, allocation.lastcall, period_end, allocation.nextcall)
                days_added_per_level[current_level] += gained_days
                if current_level.maximum_leave > 0 and sum(days_added_per_level.values()) > current_level.maximum_leave:
                    days_added_per_level[current_level] -= sum(days_added_per_level.values()) - current_level.maximum_leave

                allocation.lastcall = allocation.nextcall
                allocation.nextcall = nextcall
                if force_period and allocation.nextcall > date_to:
                    allocation.nextcall = date_to
                    force_period = False

            if days_added_per_level:
                number_of_days_to_add = allocation.number_of_days + sum(days_added_per_level.values())
                # Let's assume the limit of the last level is the correct one
                allocation.number_of_days = min(number_of_days_to_add, current_level.maximum_leave + allocation.leaves_taken) if current_level.maximum_leave > 0 else number_of_days_to_add
                print('allocation.number_of_days', allocation.number_of_days)
        print("odoo _____hello i'm in the end of _process_accrual_plans")
