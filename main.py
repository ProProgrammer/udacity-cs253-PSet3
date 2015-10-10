#!/usr/bin/env python
#
# Copyright 2007 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
import webapp2
import os
import jinja2

import re

from google.appengine.ext import db

template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(loader=jinja2.FileSystemLoader(template_dir),
    autoescape=True)

class Handler(webapp2.RequestHandler):
    def write(self, *a, **kw):
        self.response.write(*a, **kw)

    def render_str(self, template, **params):
        t = jinja_env.get_template(template)
        return t.render(params)

    def render(self, template, **kw):
        self.write(self.render_str(template, **kw))


class Post(db.Model):

    subject = db.StringProperty(required = True)
    content = db.TextProperty(required = True)
    created = db.DateTimeProperty(auto_now_add = True)

class NewPostHandler(Handler):
    def render_front(self, subject="", content="", error=""):
        self.render("newPost.html", subject=subject, content=content, error=error)

    def get(self):
        self.render_front()

    def post(self):
        subject = self.request.get('subject')
        content = self.request.get('content')

        a = Post(subject = subject, content = content)
        a.put()
        keyID = str(a.key().id())

        if subject and content:
            self.redirect('/blog/%s' % keyID)
        else:
            error = "Please enter subject as well as content in order to submit the post!"
            self.render_front(subject=subject, content=content, error=error)

class BlogHandler(Handler):
    def get(self):

        blogPosts = db.GqlQuery("SELECT * FROM Post ORDER BY created DESC LIMIT 10")

        self.render("blog.html", blogPosts=blogPosts)

class PostHandler(Handler):
    def get(self, keyID):
        post = Post.get_by_id(int(keyID), parent=None)
        
        if not post:
            self.error(404)
            return
        else:
            self.render("postPage.html", post=post)

app = webapp2.WSGIApplication([
    ('/blog/newpost', NewPostHandler),
    ('/blog', BlogHandler),
    (r'/blog/([0-9]+)', PostHandler)
], debug=True)
