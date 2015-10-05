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
from openerp.addons.website.controllers.main import Website


class Website(Website):

    @http.route(['/<path:seo_url>'], type='http', auth="public", website=True)
    def path_page(self, seo_url, **kwargs):
        """Handle SEO urls for ir.ui.views."""
        env = request.env(context=request.context)
        seo_url_parts = kwargs.get('seo_url_parts', False)
        if not seo_url_parts:
            seo_url_parts = [s.encode('utf8') for s in seo_url.split('/')
                             if s != '']

        page = 'website.404'
        views = env['ir.ui.view'].search([('seo_url', 'in', seo_url_parts)],
                                         order='seo_url_level ASC')

        # check for valid SEO url structure of ir.ui.views
        if len(seo_url_parts) == len(views):
            seo_url_check = [v.seo_url.encode('utf8') for v in views]
            seo_url_check = []
            seo_url_parent_id = False
            for v in views:
                if not seo_url_parent_id or v.seo_url_parent and \
                        seo_url_parent_id == v.seo_url_parent.id:
                    seo_url_parent_id = v.id
                    seo_url_check.append(v.seo_url.encode('utf8'))
            current_view = views[-1]
            if (seo_url_parts == seo_url_check
                    and (current_view.seo_url_level + 1) == len(views)):
                page = current_view.xml_id

        if page == 'website.404' and request.website.is_publisher():
            page = 'website.page_404'

        return request.render(page, {})
