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
        update.nickname = self.request.get("inputNickname")
        update.put()

        self.redirect('/dashboard')

# END: Settings Page

# START: Render Dashboard
class Dashboard(Handler):
    def get(self):
        page = 'dashboard.html'

        #Check is user exists in User(db.Model). If user does not exists, add user to User(db.Model).
        if not self.Me():
            addUser = User(email=users.get_current_user().email())
            addUser.put()

        #targetEmail = "kevin.loysy@gmail.com"
        #targetUser = User.getTargetUser(targetEmail)
        #targetTasks = targetUser.tasks
        #targetTasksExists = targetTasks.get()


        myTasks = self.Me().tasks.order('due')
        myTasksExists = myTasks.get()
        allTasks = Task.all().order('due')
        allTasksExists = allTasks.get()
        template_values = {
            'title': "Cuppage | Dashboard",
            'user': self.user(),
            'userId': self.user().user_id(),
            'userEmail': self.user().email(),
            'userNick': self.Me().nickname,
            'myTasksExists': myTasksExists,
            'myTasks': myTasks,
            'allTasksExists': allTasksExists,
            'allTasks': allTasks,
            'error': None, #HEY DANIEL! I would like to have AddTask.error = "All fields need to be filled." here. 
                            #Not sure how to pass that from AddTask(Handler) to Dashboard(Handler)
        }
        self.render(page, template_values)

# END: Render Dashboard

# START: AddTask
class AddTask(Handler):
    def post(self):
        creator = User.all().filter("email =", self.user().email()).get()
        title = self.request.get("inputTitle")

        if title:
            addTask = Task(creator=creator, title=title)
            if self.request.get("inputDescription") == "":
                description = "No description."
                addTask.description = description
            else:
                addTask.description = self.request.get("inputDescription")
            addTask.due = datetime.datetime.strptime(self.request.get("inputDateDue"), "%d-%m-%Y").date()
            addTask.put()
            self.redirect('/dashboard')
            
        else:
            error = "All fields need to be filled."
            self.redirect('/dashboard')

# END: AddTask

# START: EditTask

# END: EditTask

# START: AssignTask

# END: AssignTask

# START: ListUserTasks

# END:

# START: Frame
app = webapp2.WSGIApplication([
    ('/settings', UserSettings),
    ('/dashboard', Dashboard),
    ('/addTask', AddTask)
], debug=True)

# END: Frame
    