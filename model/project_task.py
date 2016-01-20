from openerp import models, fields, api, _
import logging
_logger = logging.getLogger(__name__)

class task_from_issue(models.Model):
    _inherit = ['project.task']

    origin_issue = fields.Many2one('project.issue', string="Origin Issue")
    origin_issue_state = fields.Char(string="Origin Issue State", compute="_compute_origin_issue_state")

    @api.onchange('origin_issue')
    def _compute_origin_issue_state(self):
        if self.origin_issue.id != False and self.origin_issue.name != '':
            self.origin_issue_state = self.origin_issue.stage_id.name

    @api.multi
    def open_origin_issue(self):
        if self.origin_issue != None:
            print("open")