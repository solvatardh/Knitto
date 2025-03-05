from odoo import models, fields
from odoo.exceptions import UserError


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    is_booking_order = fields.Boolean(string='Is Booking Order')
    team_id = fields.Many2one('service.team', string='Team')
    team_leader_id = fields.Many2one('res.users', string='Team Leader')
    team_members_ids = fields.Many2many('res.users', string='Team Members')
    booking_start = fields.Datetime(string='Booking Start')
    booking_end = fields.Datetime(string='Booking End')

    def action_confirm(self):
        self.check_team_availability()
        super(SaleOrder, self).action_confirm()

        work_order_vals = {
            'sale_order_id': self.id,
            'team_id': self.team_id.id,
            'team_leader_id': self.team_leader_id.id,
            'team_members_ids': [(6, 0, self.team_members_ids.ids)],
            'planned_start': self.booking_start,
            'planned_end': self.booking_end,
            'state': 'pending',
            'name': self.env['ir.sequence'].next_by_code('work.order') or 'New',
        }
        self.env['work.order'].create(work_order_vals)

    def check_team_availability(self):
        for order in self:
            overlapping_wo = self.env['work.order'].search([
                ('team_id', '=', order.team_id.id),
                ('state', '!=', 'cancelled'),
                ('planned_start', '<=', order.booking_end),
                ('planned_end', '>=', order.booking_start),
            ])
            if overlapping_wo:
                raise UserError(
                    "Team already has a work order during that period on %s" % overlapping_wo.sale_order_id.name)
        return True
