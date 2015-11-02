from openerp import models, fields, api

class project_issue_improvements(models.Model):
    _inherit = ['project.issue']
    due_date = fields.Date('Due date')
    customer_feedback = fields.Text('Customer Feedback')

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
                
                #1° case: Assigned to 'Nobody' -> Stage 'Unassigned'
                #3° case: Remove Assigned to 'Someone' -> Stage 'Unassigned'
                #check if a user is assigned
                if not self.user_id.id:
                    self.stage_id = project_task_type_unassigned_id
                    
                #2° case: Assigned to 'Someone' and Stage 'Unassigned' -> Stage 'Open'
                if self.user_id.id and (self.stage_id.id == project_task_type_unassigned_id):
                    #get 'Open' Stage ID
                    project_task_type_open = project_task_type_obj.search(cr, uid, [('name','=','Open')])
                    project_task_type_open_id = (project_task_type_obj.browse(cr, uid, project_task_type_open[0])).id
                    self.stage_id = project_task_type_open_id