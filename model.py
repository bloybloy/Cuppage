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
    creator = db.ReferenceProperty(User, collection_name="tasks", required=True)
    title = db.StringProperty(required=True)
    description = db.TextProperty()
    due = db.DateProperty()
    created = db.DateTimeProperty(auto_now_add=True)
    #updated = db.DateTimeProperty(auto_now=True)

    @staticmethod
    def populateTask(user, qty):
        i = 0
        while i < qty:
            title = "Task " + str(i)
            Task(creator=user, title=title).put()
            i += 1


    #@staticmethod
    #def getUserTasks(user):
    #    if not user: return []
    #    userTasks = 

# END: Task