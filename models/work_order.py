from datetime import datetime
from odoo import models, fields, api


class WorkOrder(models.Model):
    _name = 'work.order'
    _description = 'Work Order'

    name = fields.Char(string='WO Number', required=True, readonly=True, default=lambda self: _('New'))
    sale_order_id = fields.Many2one('sale.order', string='Booking Order Reference', readonly=True)
    team_id = fields.Many2one('service.team', string='Team', required=True)
    team_leader_id = fields.Many2one('res.users', string='Team Leader', required=True)
    team_members_ids = fields.Many2many('res.users', string='Team Members')
    planned_start = fields.Datetime(string='Planned Start', required=True)
    planned_end = fields.Datetime(string='Planned End', required=True)
    date_start = fields.Datetime(string='Date Start', readonly=True)
    date_end = fields.Datetime(string='Date End', readonly=True)
    state = fields.Selection([
        ('pending', 'Pending'),
        ('in_progress', 'In Progress'),
        ('done', 'Done'),
        ('cancelled', 'Cancelled')
    ], string='Status', default='pending')
    notes = fields.Text(string='Notes')

    def action_start_work(self):
        self.write({
            'state': 'in_progress',
            'date_start': datetime.now(),
        })

    def action_end_work(self):
        self.write({
            'state': 'done',
            'date_end': datetime.now(),
        })

    def action_reset_work(self):
        self.write({
            'state': 'pending',
            'date_start': False,
        })

    def action_cancel_work(self):
        reason = self.env.context.get('cancel_reason', '')
        self.write({
            'state': 'cancelled',
            'notes': (self.notes or '') + '\n' + reason,
        })
