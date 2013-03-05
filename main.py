import webapp2
import os
import jinja2
import datetime
import urllib
from model import *

from google.appengine.api import users
from google.appengine.ext import blobstore
from google.appengine.ext.webapp import blobstore_handlers

def datetimeformat(value, format='%d-%b-%Y'):
    return value.strftime(format)

jinja_env = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.join(os.path.dirname(__file__), 'static', 'templates')))

jinja_env.filters['datetimeformat'] = datetimeformat

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
            'user': self.Me(),
            'userNick': self.Me().nickname,
            'loginUrl': users.create_login_url('/login'),
            'logoutUrl': users.create_logout_url('/'),
        }
        values.update(template_values)
        template = jinja_env.get_template(page)
        self.response.out.write(template.render(values))
# END : Render All Pages

# START: Login
class Login(Handler):
    def get(self):
        #Check is user exists in User(db.Model). If user does not exists, add user to User(db.Model).
        if not self.Me():
            addUser = User(email=self.user().email(), nickname=self.user().nickname())
            addUser.put()

            self.redirect('/settings')

        else:
            self.redirect('/projects')

# END: Login

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
        newNickname = self.request.get('inputNickname')

        if newNickname:
            update.nickname = newNickname

        update.put()

        self.redirect('/projects')

# END: Settings 

# START: Projects
class Projects(Handler):
    def get(self):
        page = 'projects.html'
        alert = self.request.get('alertMsg')

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

# END: Create Project

# START: Edit Project
class EditProject(Handler):
    def post(self, projectId):
        targetProject = Project.get_by_id(int(projectId))

        newTitle = self.request.get('inputProjectTitle')
        newDescription = self.request.get('inputProjectDesc')

        if newTitle:
            targetProject.title = newTitle
        if newDescription:
            targetProject.description = newDescription

        targetProject.put()

        self.redirect('/projects')

# END: Edit Task

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
            'allUsers': User.all().order('nickname'),

            'activeProjectTitle': activeProject.title,

            'activeProjectTasksExists': activeProject.Tasks.get(),
            'activeProjectTasks': activeProject.Tasks.order('due'),

            'myPendingTasksExists': activeProject.Tasks.filter("owner =", self.Me()).filter("complete =", False).get(),
            'myPendingTasks': activeProject.Tasks.filter("owner =", self.Me()).filter("complete =", False),
            'myCompletedTasksExists': activeProject.Tasks.filter("owner =", self.Me()).filter("complete =", True).get(),
            'myCompletedTasks': activeProject.Tasks.filter("owner =", self.Me()).filter("complete =", True),

            'newRequestExists': activeProject.Tasks.filter("owner =", self.Me()).filter("request =", True).get(),
            'newRequest': activeProject.Tasks.filter("owner =", self.Me()).filter("request =", True),

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
                newTask = Task(project=activeProject, creator=self.Me(), title=self.request.get('inputTitle'), owner=self.Me())                
                newTask.description = self.request.get('inputDescription')
                newTask.due = datetime.datetime.strptime(self.request.get('inputDateDue'), "%d-%m-%Y").date()

                if self.request.get('inputDescription') == "":
                    newTask.description = "No description."

                if self.request.get('inputOwner') != "Me":
                    newTask.owner = User.all().filter("nickname =", self.request.get('inputOwner')).get() 
                    newTask.request = True
                
                newTask.put()
                self.redirect('/dashboard')
            
            else:
                alertMsg = "You did not provide a title for your task."
                self.redirect('/dashboard?alertMsg={}'.format(alertMsg))

# END: New Task

# START: Complete Task
class CompleteTask(Handler):
    def get(self, taskId):
        targetTask = Task.get_by_id(int(taskId))

        targetTask.complete = True
        targetTask.put()

        self.redirect('/dashboard')

# END: Complete Task

# START: Edit Task
class EditTask(Handler):
    def post(self, taskId):
        targetTask = Task.get_by_id(int(taskId))

        newTitle = self.request.get('inputTitle')
        newDateDue = self.request.get('inputDateDue')
        newDescription = self.request.get('inputDescription')
        newOwner = User.all().filter("nickname =", self.request.get('inputOwner')).get()

        if newTitle:
            targetTask.title = newTitle
        if newDateDue:
            targetTask.due = datetime.datetime.strptime(self.request.get('inputDateDue'), "%d-%m-%Y").date()
        if newDescription:
            targetTask.description = newDescription
        if newOwner:
            targetTask.owner = newOwner
            targetTask.request = True

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

# START: Accept Task
class AcceptTask(Handler):
    def get(self, taskId):
        targetTask = Task.get_by_id(int(taskId))

        targetTask.request = None
        targetTask.requestStatus = True
        targetTask.put()

        self.redirect('/dashboard')

# END: Accept Task

# START: Reject Task
class RejectTask(Handler):
    def get(self, taskId):
        targetTask = Task.get_by_id(int(taskId))

        targetTask.request = None
        targetTask.requestStatus = False
        targetTask.owner = targetTask.creator
        targetTask.put()

        self.redirect('/dashboard')

# END: Reject Task

# START: Render Blobstore
class Blobstore(Handler):
    def get(self):
        projectId = int(self.request.cookies.get('projectId'))
        activeProject = Project.get_by_id(projectId)
        upload_url = blobstore.create_upload_url('/upload')
        page = 'blobstore.html'
        template_values = {
            'title': "Cuppage | Blobstore",

            'activeProjectTitle': activeProject.title,

            'upload_url': upload_url,
            'blobsExists': activeProject.Blobs.get(),
            'blobs': activeProject.Blobs,
        }
        self.render(page, template_values)

# END: Render Blobstore

# START: Upload Blob
class UploadBlob(blobstore_handlers.BlobstoreUploadHandler, Handler):
    def post(self):
        projectId = int(self.request.cookies.get('projectId'))
        activeProject = Project.get_by_id(projectId)
        upload_files = self.get_uploads('file')  # 'file' is file upload field in the form
        for i in upload_files:
            newBlob = Blob(project=activeProject, uploader=self.Me())
            newBlob.blobInfo = i.key()

            newBlob.put()
        #blob_info = upload_files[0]
        #self.redirect('/serve/%s' % blob_info.key())
        self.redirect('/blobstore')

# END: Upload Blob

# START: Serve Blob
class ServeBlob(blobstore_handlers.BlobstoreDownloadHandler):
    def get(self, blobKey):
        resource = str(urllib.unquote(blobKey))
        blob_info = blobstore.BlobInfo.get(resource)
        self.send_blob(blob_info, save_as=True)

# END: Serve Blob

# START: Delete Blob
class DeleteBlob(Handler):
    def get(self, blobKey):
        resource = str(urllib.unquote(blobKey))
        blob_info = blobstore.BlobInfo.get(resource)
        blob = Blob.all().filter("blobInfo =", blob_info.key()).get()

        blob.delete()
        blob_info.delete()

        self.redirect('/blobstore')

# END: Delete Blob

# START: Frame
app = webapp2.WSGIApplication([
    ('/login', Login),
    ('/settings', UserSettings),
    ('/projects', Projects),
    ('/newProject', NewProject),
    ('/newTask', NewTask),
    ('/dashboard', Dashboard),
    webapp2.Route(r'/activeProject/<projectId:\d+>', ActiveProject),
    webapp2.Route(r'/editProject/<projectId:\d+>', EditProject),
    webapp2.Route(r'/done/<taskId:\d+>', CompleteTask),
    webapp2.Route(r'/edit/<taskId:\d+>', EditTask),
    webapp2.Route(r'/delete/<taskId:\d+>', DeleteTask),
    webapp2.Route(r'/accept/<taskId:\d+>', AcceptTask),
    webapp2.Route(r'/reject/<taskId:\d+>', RejectTask),
    ('/blobstore', Blobstore),
    ('/upload', UploadBlob),
    webapp2.Route(r'/serve/<blobKey:([^/]+)?>', ServeBlob),
    webapp2.Route(r'/deleteBlob/<blobKey:([^/]+)?>', DeleteBlob),
], debug=True)

# END: Frame
    