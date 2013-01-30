import webapp2
import os
import jinja2
import datetime
from model import Task, User

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
            'loginUrl': users.create_login_url('/dashboard'),
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

        self.redirect('/dashboard')

# END: Settings Page

# START: Render Dashboard
class Dashboard(Handler):
    def get(self):
        page = 'dashboard.html'
        alert = self.request.get('alertMsg')

        #Check is user exists in User(db.Model). If user does not exists, add user to User(db.Model).
        if not self.Me():
            addUser = User(email=users.get_current_user().email())
            addUser.put()

        #targetEmail = "kevin.loysy@gmail.com"
        #targetUser = User.getTargetUser(targetEmail)
        #targetTasks = targetUser.tasks
        #targetTasksExists = targetTasks.get()

        template_values = {
            'title': "Cuppage | Dashboard",
            'user': self.user(),
            'userId': self.Me().key().id(),
            'userEmail': self.Me().email,
            'userNick': self.Me().nickname,

            'myTasksExists': self.Me().tasks.get(),
            'myTasks': self.Me().tasks.order('due'),
            'allTasksExists': Task.all().get(),
            'allTasks': Task.all().order('due'),

            'alert': alert,
        }
        self.render(page, template_values)

# END: Render Dashboard

# START: AddTask
class CreateTask(Handler):
    def post(self):
        title = self.request.get('inputTitle')

        if title == "TEST":
            qty = int(self.request.get('inputDescription'))
            Task.populateTask(self.Me(), qty)

            self.redirect('/dashboard')

        else: 
            if title:
                createTask = Task(creator=self.Me(), title=self.request.get('inputTitle'))
                if self.request.get('inputDescription') == "":
                    description = "No description."
                    createTask.description = description
                
                createTask.description = self.request.get('inputDescription')
                createTask.due = datetime.datetime.strptime(self.request.get('inputDateDue'), "%d-%m-%Y").date()
            
                createTask.put()
                self.redirect('/dashboard')
            
            else:
                alertMsg = "You did not provide a title for your task."
                self.redirect('/dashboard?alertMsg={}'.format(alertMsg))

# END: AddTask

# START: UpdateTask
class EditTask(Handler):
    def post(self):
        taskId = self.request.get('taskId') #TO DO: Retrieve Task by key
        targetTask = Task(taskId)

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

# END: EditTask

# START: DeleteTask
class DeleteTask(Handler):
    def post(self, taskId):
        targetTask = Task.get_by_id(int(taskId))

        targetTask.delete()

        self.redirect('/dashboard')

# END: DeleteTask

# START: ListUserTasks

# END: ListUserTasks

# START: Frame
app = webapp2.WSGIApplication([
    ('/settings', UserSettings),
    ('/dashboard', Dashboard),
    ('/create', CreateTask),
    ('/edit', EditTask),
    webapp2.Route(r'/delete/<taskId:\d+>', DeleteTask),
], debug=True)

# END: Frame
    