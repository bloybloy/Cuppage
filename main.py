import datetime
import os
import webapp2

from google.appengine.api import users
from google.appengine.ext import db
from google.appengine.ext.webapp import template
from google.appengine.ext.webapp.util import run_wsgi_app

# START: User
class User(db.Model):
    email = db.EmailProperty(required=True)
    nickname = db.StringProperty(default="Your Nickname")

    @staticmethod
    def getTargetUser(email):
        targetUser = User.all().filter("email =", email).get()
        if targetUser:
            return targetUser
        else:
            return None

# END: User

# START: Task
class Task(db.Model):
    creator = db.ReferenceProperty(User, collection_name="tasks", required=True)
    title = db.StringProperty(required=True)
    description = db.TextProperty()
    due = db.DateProperty()
    created = db.DateTimeProperty(auto_now_add=True)
    #updated = db.DateTimeProperty(auto_now=True)

    #@staticmethod
    #def getUserTasks(user):
    #    if not user: return []
    #    userTasks = 

# END: Task

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
        path = os.path.join(os.path.dirname(__file__), page)
        self.response.out.write(template.render(path, values))

# END : Render All Pages

# START:  LandingPage
class LandingPage(Handler):
    def get(self):
        page = 'landingpage.html'
        template_values = {
            'title': "Cuppage",
        }
        self.render(page, template_values)

# END: LandingPage

# START: Updates Page
class Updates(Handler):
    def get(self):
        page = 'updates.html'
        template_values = {
            'title': "Cuppage | Updates",
        }
        self.render(page, template_values)

# END: Updates Page

# START: About Page
class About(Handler):
    def get(self):
        page = 'about.html'
        template_values = {
            'title': "Cuppage | About",
        }
        self.render(page, template_values)

# END: About Page

#START: Settings
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

#END: Settings Page

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
        }
        self.render(page, template_values)

# END: Render Dashboard

# START: AddTask
class AddTask(Handler):
    def post(self):
        #creator = self.user().nickname()
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
    ('/', LandingPage),
    ('/about', About),
    ('/updates', Updates),
    ('/settings', UserSettings),
    ('/dashboard', Dashboard),
    ('/addTask', AddTask)])

# END: Frame

def main():
    run_wsgi_app(app)

if __name__ == "__main__":
    main()
    