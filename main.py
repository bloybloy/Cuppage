import webapp2
import os
import jinja2
import datetime
from model import *

from google.appengine.api import users

jinja_env = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.join(os.path.dirname(__file__), 'static', 'templates')))

# START: Render All Pages
class Handler(webapp2.RequestHandler):
    def user(self):
        user = users.get_current_user()
        return user

    def Me(self):
        Me = User.all().filter("email =", self.user().email()).get()
        return Me

    def render(self, page, template_values={}):
        values = {
            'user': self.user(),
            'userNick': self.Me().nickname,
            'loginUrl': users.create_login_url('/projects'),
            'logoutUrl': users.create_logout_url('/'),
        }
        values.update(template_values)
        template = jinja_env.get_template(page)
        self.response.out.write(template.render(values))
# END : Render All Pages

# START: Settings
class UserSettings(Handler):
    def get(self):
        page = 'settings.html'
        template_values = {
            'title': "Cuppage | Settings",
            'email': self.Me().email,
            'userNick': self.Me().nickname,
        }
        self.render(page, template_values)

    def post(self):
        update = self.Me()
        update.nickname = self.request.get('inputNickname')
        update.put()

        self.redirect('/projects')

# END: Settings 

# START: Projects
class Projects(Handler):
    def get(self):
        page = 'projects.html'
        alert = self.request.get('alertMsg')

        #Check is user exists in User(db.Model). If user does not exists, add user to User(db.Model).
        if not self.Me():
            addUser = User(email=users.get_current_user().email())
            addUser.put()

            self.redirect('/firstlogin')

        template_values = {
            'alert': alert,
            'projectExists': Project.all().get(),
            'projects': Project.all().order('title'),
        }
        self.render(page, template_values)

# END: Projects

# START: Create Project
class NewProject(Handler):
    def post(self):
        title = self.request.get('inputProjectTitle')

        if title:
            newProject = Project(creator=self.Me(), title=title, description=self.request.get('inputProjectDesc'))
            newProject.put()

            self.redirect('/projects')

        else:
            alertMsg = "You did not provide a title for your project."
            self.redirect('/projects?alertMsg={}'.format(alertMsg))

# START: Active Project
class ActiveProject(Handler):
    def get(self, projectId):
        self.response.set_cookie('projectId', projectId, path='/')

        self.redirect('/dashboard')

# END: Active Project


# START: Render Dashboard
class Dashboard(Handler):
    def get(self):
        projectId = int(self.request.cookies.get('projectId'))
        activeProject = Project.get_by_id(projectId)
        page = 'dashboard.html'
        alert = self.request.get('alertMsg')

        #targetEmail = "kevin.loysy@gmail.com"
        #targetUser = User.getTargetUser(targetEmail)
        #targetTasks = targetUser.tasks
        #targetTasksExists = targetTasks.get()

        template_values = {
            'title': "Cuppage | Dashboard",
            'user': self.user(),
            'userId': self.Me().key().id(),
            'userEmail': self.Me().email,
            'allUsers': User.all().order('nickname'),

            'activeProjectTitle': activeProject.title,

            'myCreatedExists': self.Me().TaskCreated.get(),
            'myCreated': self.Me().TaskCreated.order('due'),
            'myOwnedExists': self.Me().TaskOwned.get(),
            'myOwned': self.Me().TaskOwned.order('due'),
            'allTasksExists': Task.all().get(),
            'allTasks': Task.all().order('due'),

            'alert': alert,
        }
        self.render(page, template_values)

# END: Render Dashboard

# START: New Task
class NewTask(Handler):
    def post(self):
        projectId = int(self.request.cookies.get('projectId'))
        activeProject = Project.get_by_id(projectId)
        title = self.request.get('inputTitle')

        if title == "TEST":
            qty = int(self.request.get('inputDescription'))
            Task.populateTask(activeProject, self.Me(), qty)

            self.redirect('/dashboard')

        else: 
            if title:
                newTask = Task(project=activeProject, creator=self.Me(), title=self.request.get('inputTitle'))
                if self.request.get('inputDescription') == "":
                    description = "No description."
                    createTask.description = description
                
                newTask.description = self.request.get('inputDescription')
                newTask.due = datetime.datetime.strptime(self.request.get('inputDateDue'), "%d-%m-%Y").date()
                if self.request.get('inputOwner'):    
                    newTask.owner = User.all().filter("nickname =", self.request.get('inputOwner')).get()
            
                newTask.put()
                self.redirect('/dashboard')
            
            else:
                alertMsg = "You did not provide a title for your task."
                self.redirect('/dashboard?alertMsg={}'.format(alertMsg))

# END: New Task

# START: Edit Task
class EditTask(Handler):
    def post(self, taskId):
        targetTask = Task.get_by_id(int(taskId))

        newTitle = self.request.get('inputTitle')
        newDateDue = datetime.datetime.strptime(self.request.get('inputDateDue'), "%d-%m-%Y").date()
        newDescription = self.request.get('inputDescription')

        if newTitle:
            targetTask.title = newTitle
        if newDateDue:
            targetTask.due = newDateDue
        if newDescription:
            targetTask.description = newDescription

        targetTask.put()

        self.redirect('/dashboard')

# END: Edit Task

# START: Delete Task
class DeleteTask(Handler):
    def get(self, taskId):
        targetTask = Task.get_by_id(int(taskId))

        targetTask.delete()

        self.redirect('/dashboard')

# END: Delete Task

# START: ListUserTasks

# END: ListUserTasks

# START: Frame
app = webapp2.WSGIApplication([
    ('/firstlogin', UserSettings),
    ('/settings', UserSettings),
    ('/projects', Projects),
    ('/newProject', NewProject),
    ('/newTask', NewTask),
    ('/dashboard', Dashboard),
    webapp2.Route(r'/activeProject/<projectId:\d+>', ActiveProject),
    webapp2.Route(r'/edit/<taskId:\d+>', EditTask),
    webapp2.Route(r'/delete/<taskId:\d+>', DeleteTask),
], debug=True)

# END: Frame
    