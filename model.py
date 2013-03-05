import datetime

from google.appengine.ext import db
from google.appengine.ext import blobstore
from google.appengine.api import users

# START: User
class User(db.Model):
    email = db.EmailProperty(required=True)
    nickname = db.StringProperty(default="Your Nickname")

# END: User

# START: Project
class Project(db.Model):
    creator = db.ReferenceProperty(User, collection_name="ProjectStarter", required=True)
    created = db.DateTimeProperty(auto_now_add=True)
    title = db.StringProperty(required=True)
    description = db.TextProperty()

# END: Project

# START: ProjectUser
class ProjectUser(db.Model):
    project = db.ReferenceProperty(Project, collection_name="User")
    user = db.ReferenceProperty(User, collection_name="ProjectUser")

# END: ProjectUser

# START: Task
class Task(db.Model):
    project = db.ReferenceProperty(Project, collection_name="Tasks", required=True)
    creator = db.ReferenceProperty(User, collection_name="TaskCreated", required=True)
    created = db.DateTimeProperty(auto_now_add=True)
    title = db.StringProperty(required=True)
    description = db.TextProperty()
    due = db.DateProperty()
    milestone = db.BooleanProperty(default=False)
    owner = db.ReferenceProperty(User, collection_name="TaskOwned", required=True)
    request = db.BooleanProperty()
    requestStatus = db.BooleanProperty()
    updated = db.DateTimeProperty(auto_now=True)
    complete = db.BooleanProperty(default=False)

    @staticmethod
    def populateTask(project, user, qty):
        i = 0
        day = 1
        while i < qty:
            title = "Task " + str(i)
            date = datetime.datetime.strptime(str(day) + "-04-2013", "%d-%m-%Y").date()
            Task(project=project, creator=user, title=title, description="A simple description.", due=date).put()
            i += 1
            day += 1

# END: Task

# START: Blob
class Blob(db.Model):
    project = db.ReferenceProperty(Project, collection_name="Blobs", required=True)
    uploader = db.ReferenceProperty(User, collection_name="BlobUploaded", required=True)
    blobInfo = blobstore.BlobReferenceProperty()

# END: Blob