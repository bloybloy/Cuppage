import webapp2
import os
import jinja2

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
    ('/updates', Updates)
], debug=True)

# END: Frame