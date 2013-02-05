import datetime

from google.appengine.ext import db
from google.appengine.api import users

# START: User
class User(db.Model):
    email = db.EmailProperty(required=True)
    nickname = db.StringProperty(default="Your Nickname")

    @staticmethod
    def getTargetUser(id):
        targetUser = User.get_by_id(id)
        if targetUser:
            return targetUser
        else:
            return None

# END: User

# START: Task
class Task(db.Model):
    creator = db.ReferenceProperty(User, collection_name="created", required=True)
    title = db.StringProperty(required=True)
    description = db.TextProperty()
    due = db.DateProperty()
    owner = db.ReferenceProperty(User, collection_name="owned")
    created = db.DateTimeProperty(auto_now_add=True)
    #updated = db.DateTimeProperty(auto_now=True)

    @staticmethod
    def populateTask(user, qty):
        i = 0
        day = 1
        while i < qty:
            title = "Task " + str(i)
            date = datetime.datetime.strptime(str(day) + "-04-2013", "%d-%m-%Y").date()
            Task(creator=user, title=title, description="A simple description.", due=date).put()
            i += 1
            day += 1


    #@staticmethod
    #def getUserTasks(user):
    #    if not user: return []
    #    userTasks = 

# END: Task