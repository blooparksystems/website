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
        url_parts = location.split('/')
        seo_url = url_parts.pop(0)
        while seo_url in ['', 'blog'] and len(url_parts):
            seo_url = url_parts.pop(0)

        ctx = request.context.copy()
        cr, uid, reg = request.cr, request.uid, request.registry
        domain = [('seo_url', '=', seo_url)]
        models = ['blog.blog', 'blog.post']
        for model in models:
            obj_ids = reg[model].search(cr, uid, domain, context=ctx)
            if obj_ids:
                ctx.update({'lang': lang})
                obj = reg[model].browse(cr, uid, obj_ids[0], context=ctx)
                location = '/blog/%s' % obj.seo_url
                break
    else:
        location = translated_location
    return location


# change method url_for_lang to use the one redefined here
setattr(ir_ui_view, 'url_for_lang', url_for_lang)
