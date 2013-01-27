import webapp2
import os

from google.appengine.api import users
from google.appengine.ext import db
from google.appengine.ext.webapp import template
from google.appengine.ext.webapp.util import run_wsgi_app

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

# START: Frame
app = webapp2.WSGIApplication([
    ('/', LandingPage),
    ('/about', About),
    ('/updates', Updates)])

# END: Frame

def main():
    run_wsgi_app(app)

if __name__ == "__main__":
    main()