from openerp import models, fields, api
from openerp import _
import logging
_logger = logging.getLogger(__name__)

class project_issue_improvements(models.Model):
    _inherit = ['project.issue']

    due_date = fields.Date('Due date')
    customer_feedback = fields.Text('Customer Feedback')
    converted_task_state = fields.Char(string="Converted Task State", compute="_compute_converted_task_state")

    @api.one
    @api.onchange('task_id')
    def _compute_converted_task_state(self):
        if self.task_id != None:
            self.converted_task_state = self.task_id.stage_id.name

    @api.multi
    def convert_to_task(self):
        for issue in self:
            if issue.task_id.id != False and issue.task_id.name != '':
                _logger.debug("Already converted to task: %s-%s", issue.task_id, issue.task_id.name)
                return

            # create the taks & set the infos
            new_task_id = self.pool.get('project.task').create(self.env.cr, self.env.uid, {
                    'name': 'Issue #' + str(issue.id) + ": " + issue.name,
                    'project_id': issue.project_id.id,
                    'priority': issue.priority,
                    'description': issue.description,
                    'user_id': issue.user_id.id,
                    'date_deadline': issue.due_date,
                    'origin_issue': issue.id,
            })

            project_task_type_obj = self.pool.get('project.task.type')
            project_task_type_converted = project_task_type_obj.search(self.env.cr, self.env.uid, [('name','=','Converted to Task')])
            project_task_type_converted_id = (project_task_type_obj.browse(self.env.cr, self.env.uid, project_task_type_converted[0])).id
            issue.stage_id = project_task_type_converted_id
            issue.task_id = new_task_id
    
            # open the task
            return {
                'name':_("New Converted Task"),
                'view_mode': 'form',
                'view_id': False,
                'view_type': 'form',
                'res_model': 'project.task',
                'res_id': new_task_id,
                'type': 'ir.actions.act_window',
                'nodestroy': True,
                'domain': '[]',
                'context': self.env.context,
            }

    @api.onchange('user_id','project_id','email_from')
    def change_assignation_state(self):
        if self.project_id.id:
            #get 'Unassigned' Stage ID
            cr = self.env.cr
            uid = self.env.user.id
            project_task_type_obj = self.pool.get('project.task.type')
            project_task_type_unassigned = project_task_type_obj.search(cr, uid, [('name','=','Unassigned')])
            if project_task_type_unassigned:
                project_task_type_unassigned_id = (project_task_type_obj.browse(cr, uid, project_task_type_unassigned[0])).id
                
                #1 case: Assigned to 'Nobody' -> Stage 'Unassigned'
                #3 case: Remove Assigned to 'Someone' -> Stage 'Unassigned'
                #check if a user is assigned
                if not self.user_id.id:
                    self.stage_id = project_task_type_unassigned_id
                    
                #2 case: Assigned to 'Someone' and Stage 'Unassigned' -> Stage 'Open'
                if self.user_id.id and (self.stage_id.id == project_task_type_unassigned_id):
                    #get 'Open' Stage ID
                    project_task_type_open = project_task_type_obj.search(cr, uid, [('name','=','Open')])
                    project_task_type_open_id = (project_task_type_obj.browse(cr, uid, project_task_type_open[0])).id
                    self.stage_id = project_task_type_open_id