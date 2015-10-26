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
from openerp.addons.web.http import request
from openerp.addons.website_seo.models import ir_ui_view


view_url_for_lang = ir_ui_view.url_for_lang


def url_for_lang(location, lang):
    translated_location = view_url_for_lang(location, lang)
    if translated_location == location:
        if not request.registry.get('blog.blog', False):
            return location
        blog_obj = request.registry['blog.blog']
        ctx = request.context.copy()
        url_parts = location.split('/')
        blog_url = url_parts.pop(0)
        while blog_url in ['', 'blog']:
            blog_url = url_parts.pop(0)
        blogs = blog_obj.search(request.cr, request.uid,
                                [('seo_url', '=', blog_url)],
                                context=ctx)
        if blogs and url_parts:
            post_obj = request.registry['blog.post']
            posts = post_obj.search(request.cr, request.uid,
                                    [('blog_id', '=', blogs[0]),
                                     ('seo_url', '=', url_parts[0])],
                                    context=ctx)
            if posts:
                ctx.update({'lang': lang})
                post = post_obj.browse(request.cr, request.uid,
                                       posts[0], context=ctx)
                location = '/%s/%s' % (post.blog_id.seo_url, post.seo_url)
        elif blogs:
            ctx.update({'lang': lang})
            blog = blog_obj.browse(request.cr, request.uid,
                                   blogs[0], context=ctx)
            location = '/%s' % blog.seo_url
    else:
        location = translated_location
    return location


# change method url_for_lang to use the one redefined here
setattr(ir_ui_view, 'url_for_lang', url_for_lang)
