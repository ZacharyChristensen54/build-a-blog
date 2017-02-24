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
from google.appengine.ext import db

template_dir = os.path.dirname(__file__)
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir),
                                autoescape = True)

class Blog(db.Model):
    title = db.StringProperty(required = True)
    blog_content = db.TextProperty(required = True)
    created = db.DateTimeProperty(auto_now_add = True)

class Handler(webapp2.RequestHandler):
    def write(self, *args, **kwargs):
        self.response.write(*args, **kwargs)

    def render_str(self, template, **params):
        t = jinja_env.get_template(template)
        return t.render(**params)

    def render(self, template, **kw):
        self.write(self.render_str(template, **kw)) 

# def get_posts(limit, offset):
#     posts = db.GqlQuery('SELECT * FROM Blog LIMIT %d OFFSET %d ORDER BY created DESC' % (limit, offset))
#     return posts

class MakePost(Handler):
    def get(self):
        self.render('add_blog.html')

    def post(self):
        title = self.request.get('title')
        blog_content = self.request.get('blog_content')

        title_error = ''
        content_error = ''

        if title and blog_content:
            b = Blog(title = title, blog_content = blog_content)
            b.put()
            self.redirect('/blog/%s' % b.key().id())
        else:
            if not title:
                title_error = 'There must be a title'
            if not blog_content:
                content_error = 'You must have a blog entry'
            self.render('add_blog.html', title_error = title_error, 
                                            content_error = content_error, 
                                            blog_content = blog_content, 
                                            title = title)



class MainHandler(Handler):
    def render_front_page(self):
        blogz = db.GqlQuery('SELECT * FROM Blog ORDER BY created DESC LIMIT 5')
        list_of_blog_ids = []
        for blog in blogz:
            list_of_blog_ids += [blog.key().id()]
        self.render('front_page.html', blogz=blogz, list_of_blog_ids=list_of_blog_ids)

    def get(self):
        self.render_front_page()
    
class ViewPostHandler(webapp2.RequestHandler):
    def get(self, id):
        try:
            post = Blog.get_by_id(int(id))
            self.response.write(post.title + '<br>'*2 + post.blog_content)
        except:
            self.response.write("Blog with ID:%s doesn't exist" % id)
        

app = webapp2.WSGIApplication([
    ('/', MainHandler),
    ('/newpost', MakePost),
    webapp2.Route('/blog/<id:\d+>', ViewPostHandler)
], debug=True)
