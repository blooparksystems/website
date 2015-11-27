# -*- coding: utf-8 -*-
##############################################################################
#
# Odoo, an open source suite of business apps
# This module copyright (C) 2015 bloopark systems (<http://bloopark.de>).
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
from openerp.addons.web import http
from openerp.addons.web.http import request
from openerp.addons.website.controllers.main import Website as BaseWebsite
from openerp.addons.website_blog.controllers.main import QueryURL, WebsiteBlog
from openerp.addons.website_seo.models import website
from openerp.addons.website_seo.models.website import slug
from openerp.osv.orm import browse_record

import werkzeug


class QueryURL(QueryURL):

    """Copy of QueryURL class of website_blog module to handle SEO urls."""

    def __call__(self, path=None, path_args=None, **kw):
        """Update the url generation to use the new SEO url structure."""
        path = path or self.path
        for k, v in self.args.items():
            kw.setdefault(k, v)
        path_args = set(path_args or []).union(self.path_args)
        paths, fragments = [], []
        for key, value in kw.items():
            if value and key in path_args:
                if isinstance(value, browse_record):
                    paths.append((key, slug(value)))
                else:
                    paths.append((key, value))
            elif value:
                if isinstance(value, list) or isinstance(value, set):
                    fragments.append(
                        werkzeug.url_encode([(key, item) for item in value]))
                else:
                    fragments.append(werkzeug.url_encode([(key, value)]))
        for key, value in paths:
            if key in ['blog', 'post', 'tag']:
                path += '/%s' % value
            else:
                path += '/' + key + '/%s' % value
        if fragments:
            path += '?' + '&'.join(fragments)
        return path


class WebsiteBlog(WebsiteBlog):

    @http.route()
    def blogs(self, page=1, **post):
        """Update blog url of original blogs function with SEO url."""

        response = super(WebsiteBlog, self).blogs(page=page, **post)
        response.qcontext.update({'blog_url': QueryURL('/blog', ['blog', 'tag'])})

        return request.website.render(response.template, response.qcontext)

    @http.route()
    def blog(self, blog=None, tag=None, page=1, **opt):
        """Update blog url and pager of original blog function with SEO url."""

        env = request.env(context=request.context)
        blog_post_obj = env['blog.post']
        date_end = opt.get('date_end')
        response = super(WebsiteBlog, self).blog(blog=blog, tag=None, page=page,
                                                 **opt)
        values = response.qcontext
        blog_url = QueryURL('/blog', ['blog', 'tag'], blog=blog, tag=tag,
                            date_begin=values['date'], date_end=date_end)

        domain = []
        if blog:
            domain += [('blog_id', '=', blog.id)]
        if tag:
            domain += [('tag_ids', 'in', [tag.id])]
        if values['date'] and date_end:
            domain += [("create_date", ">=", values['date']),
                       ("create_date", "<=", date_end)]
        blog_posts = blog_post_obj.search(domain, order="create_date desc")

        pager = request.website.pager(
            url=blog_url(),
            total=len(blog_posts),
            page=page,
            step=self._blog_post_per_page,
        )

        values.update({
            'blog_posts': blog_posts,
            'blog_url': blog_url,
            'pager': pager,
            'main_object': tag or blog
        })

        return request.website.render(response.template, values)

    @http.route()
    def blog_post(self, blog, blog_post, tag_id=None, page=1,
                  enable_editor=None, **post):
        """Update blog url of original blog_post function with SEO url."""

        date_end = post.get('date_end')
        response = super(WebsiteBlog, self).blog_post(
            blog=blog, blog_post=blog_post, tag_id=tag_id, page=page,
            enable_editor=enable_editor, **post)
        values = response.qcontext
        values.update({'blog_url': QueryURL(
            '/blog', ['blog', 'tag'], blog=blog_post.blog_id, tag=values['tag'],
            date_begin=values['date'], date_end=date_end)})

        return request.website.render(response.template, values)


class Website(BaseWebsite):

    @http.route([
        '/blog/<string:seo_url>',
        '/blog/<string:seo_url>/<string:seo_url_tag>'
    ], type='http', auth="public", website=True)
    def blog_seo_url(self, seo_url, seo_url_tag=None, **opt):
        website = WebsiteBlog()
        env = request.env(context=request.context)
        domain = [('seo_url', '=', seo_url)]

        blog = env['blog.blog'].search(domain)
        if blog:
            tags = env['blog.tag'].search([('seo_url', '=', seo_url_tag)])
            tag = tags and tags[0] or False
            return website.blog(blog=blog[0], tag=tag, **opt)
        post = env['blog.post'].search(domain)
        if post:
            return website.blog_post(post[0].blog_id, post[0], **opt)

        url = self.look_for_redirect_url('/blog/%s' % seo_url, **opt)
        if url:
            return request.redirect(url, code=301)

        # TODO: use defaults urls instead
        return request.redirect('/blog')
