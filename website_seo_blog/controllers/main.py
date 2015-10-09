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
            if key in ['blog', 'post']:
                path += '/%s' % value
            else:
                path += '/' + key + '/%s' % value
        if fragments:
            path += '?' + '&'.join(fragments)
        return path


class Website(BaseWebsite):

    @http.route(['/<path:seo_url>'], type='http', auth="public", website=True)
    def path_page(self, seo_url, **post):

        page = 'website.page_404'
        response = super(Website, self).path_page(seo_url, **post)
        if response.template != page:
            return request.website.render(response.template)

        env = request.env(context=request.context)
        seo_url_parts = [s.encode('utf8') for s in seo_url.split('/')
                         if s != '']
        seo_url_blog = seo_url_parts.pop(0)

        blogs = env['blog.blog'].search([('seo_url', '=', seo_url_blog)])
        if blogs:
            blog_instance = WebsiteBlog()
            if seo_url_parts:
                blog_posts = env['blog.post'].search([
                    ('blog_id', 'in', [x.id for x in blogs]),
                    ('seo_url', '=', seo_url_parts[0])
                ])
                if blog_posts:
                    return blog_instance.blog_post(blog_posts[0].blog_id, blog_posts[0], **post)
            else:
                return blog_instance.blog(blogs[0], **post)

        return request.render(page, {})


class WebsiteBlog(WebsiteBlog):

    @http.route()
    def blogs(self, page=1, **post):
        """Update blog url of original blogs function with SEO url."""
        response = super(WebsiteBlog, self).blogs(page=page, **post)
        response.qcontext.update({'blog_url': QueryURL('', ['blog', 'tag'])})

        return request.website.render(response.template, response.qcontext)

    @http.route()
    def blog(self, blog=None, tag=None, page=1, **opt):
        """Update blog url and pager of original blog function with SEO url."""
        # - request.env.context contains always "'lang': u'en_US'" regardless
        # of the used frontend language which results in not found non english
        # blogs, so we update request.env.context with request.context
        env = request.env(context=request.context)
        blog_post_obj = env['blog.post']
        date_end = opt.get('date_end')
        response = super(WebsiteBlog, self).blog(blog=blog, tag=tag, page=page,
                                                 **opt)
        values = response.qcontext
        blog_url = QueryURL('', ['blog', 'tag'], blog=blog, tag=tag,
                            date_begin=values['date'], date_end=date_end)

        domain = []
        if blog:
            domain += [('blog_id', '=', blog.id)]
        if tag:
            domain += [('tag_ids', 'in', tag.id)]
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
            'blog_url': blog_url,
            'pager': pager
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
            '', ['blog', 'tag'], blog=blog_post.blog_id, tag=values['tag'],
            date_begin=values['date'], date_end=date_end)})

        return request.website.render(response.template, values)
