from google.appengine.ext import db

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