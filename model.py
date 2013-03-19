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

# START: Discussion
class Discussion(db.Model):
    project = db.ReferenceProperty(Project, collection_name="Discussions", required=True)
    creator = db.ReferenceProperty(User, collection_name="DiscussionsCreated", required=True)
    created = db.DateTimeProperty(auto_now_add=True)
    title = db.StringProperty(required=True)    

# END: Discussion

# START: Post
class Post(db.Model):
    discussion = db.ReferenceProperty(Discussion, collection_name="Posts", required=True)
    author = db.ReferenceProperty(User, collection_name="Posts", required=True)
    content = db.TextProperty(required=True)
    created = db.DateTimeProperty(auto_now_add=True)

# END: Post

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

# END: Task

# START: Blob
class Blob(db.Model):
    project = db.ReferenceProperty(Project, collection_name="Blobs", required=True)
    uploader = db.ReferenceProperty(User, collection_name="BlobUploaded", required=True)
    blobInfo = blobstore.BlobReferenceProperty()

# END: Blob