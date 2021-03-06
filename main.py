import webapp2
import os
import jinja2
import datetime
import urllib
from model import *

from google.appengine.api import users
from google.appengine.ext import blobstore
from google.appengine.ext.webapp import blobstore_handlers

def dateformat(value, format='%d-%b-%Y'):
    return value.strftime(format)

def timeformat(value, format='%I:%M %p'):
    return value.strftime(format)

jinja_env = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.join(os.path.dirname(__file__), 'static', 'templates')))

jinja_env.filters['dateformat'] = dateformat
jinja_env.filters['timeformat'] = timeformat

# START: Render All Pages
class BaseHandler(webapp2.RequestHandler):
    def user(self):
        user = users.get_current_user()
        return user

    def Me(self):
        Me = User.all().filter("email =", self.user().email()).get()
        return Me

    def activeProject(self):
        projectId = int(self.request.cookies.get('projectId'))
        ActiveProject = Project.get_by_id(projectId)
        return ActiveProject

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
class Login(BaseHandler):
    def get(self):
        #Check is user exists in User(db.Model). If user does not exists, add user to User(db.Model).
        if not self.Me():
            addUser = User(email=self.user().email(), nickname=self.user().nickname())
            addUser.put()
        
        self.redirect('/projects')

# END: Login

# START: Settings
class UserSettings(BaseHandler):
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
class Projects(BaseHandler):
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
class NewProject(BaseHandler):
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
class EditProject(BaseHandler):
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
class ActiveProject(BaseHandler):
    def get(self, projectId):
        self.response.set_cookie('projectId', projectId, path='/')

        self.redirect('/dashboard')

# END: Active Project

# START: Render Dashboard
class Dashboard(BaseHandler):
    def get(self):
        upload_url = blobstore.create_upload_url('/upload')
        page = 'dashboard.html'
        alert = self.request.get('alertMsg')

        #targetEmail = "kevin.loysy@gmail.com"
        #targetUser = User.getTargetUser(targetEmail)
        #targetTasks = targetUser.tasks
        #targetTasksExists = targetTasks.get()

        template_values = {
            'title': "Cuppage | Dashboard",
            'allUsers': User.all().order('nickname'),

            'activeProjectTitle': self.activeProject().title,
            'activeProjectDescription': self.activeProject().description,

            'activeProjectDiscussionsExists': self.activeProject().Discussions.get(), 
            'activeProjectDiscussions': self.activeProject().Discussions.order('-created'),

            'activeProjectTasksExists': self.activeProject().Tasks.get(),
            'activeProjectTasks': self.activeProject().Tasks.order('due'),

            'myPendingTasksExists': self.activeProject().Tasks.filter("owner =", self.Me()).filter("complete =", False).get(),
            'myPendingTasks': self.activeProject().Tasks.filter("owner =", self.Me()).filter("complete =", False),
            'myCompletedTasksExists': self.activeProject().Tasks.filter("owner =", self.Me()).filter("complete =", True).get(),
            'myCompletedTasks': self.activeProject().Tasks.filter("owner =", self.Me()).filter("complete =", True),

            'newRequestExists': self.activeProject().Tasks.filter("owner =", self.Me()).filter("request =", True).get(),
            'newRequest': self.activeProject().Tasks.filter("owner =", self.Me()).filter("request =", True),

            'upload_url': upload_url,
            'blobsExists': self.activeProject().Blobs.get(),
            'blobs': self.activeProject().Blobs,

            'alert': alert,
        }
        self.render(page, template_values)

# END: Render Dashboard

# START: Active Discussion
class ActiveDiscussion(BaseHandler):
    def get(self, threadId):
        self.response.set_cookie('threadId', threadId, path='/')

        self.redirect('/discussion')

# END: Active Discussion

# START: Show Discussion
class ShowDiscussion(BaseHandler):
    def get(self):
        threadId = int(self.request.cookies.get('threadId'))
        discussion = Discussion.get_by_id(int(threadId))
        alert = self.request.get('alertMsg')
        page = 'discussions.html'

        template_values = {
            'title': "Cuppage | Dashboard",
            'allUsers': User.all().order('nickname'),

            'activeProjectTitle': self.activeProject().title,

            'discussion': discussion,
            'posts': discussion.Posts.order('created'),

            'alert': alert,

        }
        self.render(page, template_values)

    # Create Posts on Discussion    
    def post(self, threadId):
        targetDiscussion = Discussion.get_by_id(int(threadId))
        newPost = Post(discussion=targetDiscussion, author=self.Me(), content=self.request.get('inputPost'))
        newPost.put()

        self.redirect('/discussion?thread={}'.format(threadId))

# END: Show Discussion

# START: Delete Post
class DeletePost(BaseHandler):
    def get(self, postId):
        targetPost = Post.get_by_id(int(postId))

        targetPost.delete()

        self.redirect('/discussion')

# END: Delete Post

# START: Start Discussion
class StartDiscussion(BaseHandler):
    def post(self):
        newDiscussion = Discussion(project=self.activeProject(), creator=self.Me(), title=self.request.get('inputTitle'))                
        newDiscussion.put()

        newPost = Post(discussion=newDiscussion, author=self.Me(), content=self.request.get('inputPost'))
        newPost.put()

        self.redirect('/dashboard')

# END: Start Discussion

# START: Delete Discussion
class DeleteDiscussion(BaseHandler):
    def get(self, threadId):
        targetDiscussion = Discussion.get_by_id(int(threadId))

        targetDiscussion.delete()

        self.redirect('/dashboard')

# END: Delete Discussion

# START: New Task
class AddTask(BaseHandler):
    def post(self):
        title = self.request.get('inputTitle')

        if title:
            newTask = Task(project=self.activeProject(), creator=self.Me(), title=title, owner=self.Me())                
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
class CompleteTask(BaseHandler):
    def get(self, taskId):
        targetTask = Task.get_by_id(int(taskId))

        targetTask.complete = True
        targetTask.put()

        self.redirect('/dashboard')

# END: Complete Task

# START: Edit Task
class EditTask(BaseHandler):
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
class DeleteTask(BaseHandler):
    def get(self, taskId):
        targetTask = Task.get_by_id(int(taskId))

        targetTask.delete()

        self.redirect('/dashboard')

# END: Delete Task

# START: Accept Task
class AcceptTask(BaseHandler):
    def get(self, taskId):
        targetTask = Task.get_by_id(int(taskId))

        targetTask.request = None
        targetTask.requestStatus = True
        targetTask.put()

        self.redirect('/dashboard')

# END: Accept Task

# START: Reject Task
class RejectTask(BaseHandler):
    def get(self, taskId):
        targetTask = Task.get_by_id(int(taskId))

        targetTask.request = None
        targetTask.requestStatus = False
        targetTask.owner = targetTask.creator
        targetTask.put()

        self.redirect('/dashboard')

# END: Reject Task

# START: Upload Blob
class UploadBlob(blobstore_handlers.BlobstoreUploadHandler, BaseHandler):
    def post(self):
        upload_files = self.get_uploads('file')  # 'file' is file upload field in the form
        for i in upload_files:
            newBlob = Blob(project=self.activeProject(), uploader=self.Me())
            newBlob.blobInfo = i.key()

            newBlob.put()
        #blob_info = upload_files[0]
        #self.redirect('/serve/%s' % blob_info.key())
        self.redirect('/dashboard')

# END: Upload Blob

# START: Serve Blob
class ServeBlob(blobstore_handlers.BlobstoreDownloadHandler):
    def get(self, blobKey):
        resource = str(urllib.unquote(blobKey))
        blob_info = blobstore.BlobInfo.get(resource)
        self.send_blob(blob_info, save_as=True)

# END: Serve Blob

# START: Delete Blob
class DeleteBlob(BaseHandler):
    def get(self, blobKey):
        resource = str(urllib.unquote(blobKey))
        blob_info = blobstore.BlobInfo.get(resource)
        blob = Blob.all().filter("blobInfo =", blob_info.key()).get()

        blob.delete()
        blob_info.delete()

        self.redirect('/dashboard')

# END: Delete Blob

# START: Frame
app = webapp2.WSGIApplication([
    ('/login', Login),
    ('/settings', UserSettings),
    ('/projects', Projects),
    ('/newProject', NewProject),
    webapp2.Route(r'/editProject/<projectId:\d+>', EditProject),
    webapp2.Route(r'/activeProject/<projectId:\d+>', ActiveProject),

    webapp2.Route(r'/activeDiscussion/<threadId:\d+>', ActiveDiscussion),
    ('/startDiscussion', StartDiscussion),
    webapp2.Route(r'/deleteThread/<threadId:\d+>', DeleteDiscussion),
    ('/discussion', ShowDiscussion),
    webapp2.Route(r'/post/<threadId:\d+>', ShowDiscussion),
    webapp2.Route(r'/deletePost/<postId:\d+>', DeletePost),

    ('/dashboard', Dashboard),

    ('/addTask', AddTask),    
    webapp2.Route(r'/done/<taskId:\d+>', CompleteTask),
    webapp2.Route(r'/edit/<taskId:\d+>', EditTask),
    webapp2.Route(r'/delete/<taskId:\d+>', DeleteTask),
    webapp2.Route(r'/accept/<taskId:\d+>', AcceptTask),
    webapp2.Route(r'/reject/<taskId:\d+>', RejectTask),
    
    ('/upload', UploadBlob),
    webapp2.Route(r'/serve/<blobKey:([^/]+)?>', ServeBlob),
    webapp2.Route(r'/deleteBlob/<blobKey:([^/]+)?>', DeleteBlob),
], debug=True)

# END: Frame
    