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
import urlparse
from openerp import api, fields, models
from openerp.addons.website.models.website import is_multilang_url
from openerp.addons.website_seo.models.website import slug
from openerp.http import request


def url_for(path_or_uri, lang=None):
    if isinstance(path_or_uri, unicode):
        path_or_uri = path_or_uri.encode('utf-8')
    current_path = request.httprequest.path
    if isinstance(current_path, unicode):
        current_path = current_path.encode('utf-8')
    location = path_or_uri.strip()
    force_lang = lang is not None
    url = urlparse.urlparse(location)

    if request and not url.netloc and not url.scheme and (url.path or force_lang):
        location = urlparse.urljoin(current_path, location)

        lang = lang or request.context.get('lang')
        langs = [lg[0] for lg in request.website.get_languages()]

        if (len(langs) > 1 or force_lang) and is_multilang_url(location, langs):
            if lang != request.context.get('lang'):
                location = url_for_lang(location, lang)
            ps = location.split('/')
            if ps[1] in langs:
                # Replace the language only if we explicitly provide a language to url_for
                if force_lang:
                    ps[1] = lang
                # Remove the default language unless it's explicitly provided
                elif ps[1] == request.website.default_lang_code:
                    ps.pop(1)
            # Insert the context language or the provided language
            elif lang != request.website.default_lang_code or force_lang:
                ps.insert(1, lang)
            location = '/'.join(ps)

    return location.decode('utf-8')


def url_for_lang(location, lang):
    menu = request.registry['website.menu']
    ctx = request.context.copy()
    menu_ids = menu.search(request.cr, request.uid, [('url', '=', location)], context=ctx)
    if menu_ids:
        ctx.update({'lang': lang})
        location = menu.browse(request.cr, request.uid, menu_ids[0], context=ctx).url
    return location


class View(models.Model):

    """Update view model with additional SEO variables."""

    _name = 'ir.ui.view'
    _inherit = ['ir.ui.view', 'website.seo.metadata']

    # ToDo: if the automatically setup of the field seo_url_level is done when
    # the seo_url_parent is changed set readonly to True
    # ToDo: check and move if needed the two fields to website.seo.metadata,
    # I think it will be necessary when the website_seo_blog module is updated
    # with the same seo url handling like in the website_seo module
    seo_url_level = fields.Integer(
        string='SEO Url Level', readonly=False,
        help='Indicates the SEO url level. It starts with the root level 0.')
    seo_url_parent = fields.Many2one(
        'ir.ui.view', string='SEO Parent',
        domain=[('type', '=', 'qweb'), ('inherit_id', '=', False)],
        help='The SEO Parent field is used to describe hierarchical urls like '
        '"/ecommerce/study/how-to-do-it-right". Taking this as example you '
        'have to create 3 pages (ir.ui.view records) for "ecommerce", "study" '
        'and "how-to-do-it-right". The "ecommerce" page is the first level '
        'part and it doesn\'t need a SEO parent. The "study" page is the '
        'second level part and it needs the parent page "ecommerce". The '
        '"how-to-do-it-right" page is the third part and it needs the parent '
        'page "study". If all pages are configured correct the page '
        '"how-to-do-it-right" is rendered when calling '
        '"/ecommerce/study/how-to-do-it-right".'
    )
    seo_url_children = fields.One2many('ir.ui.view', 'seo_url_parent', 'SEO Children')

    @api.onchange('seo_url_parent')
    def onchange_seo_url_parent(self):
        url_level = 0
        if self.seo_url_parent:
            url_level = self.seo_url_parent.seo_url_level + 1
        self.seo_url_level = url_level

    @api.multi
    def write(self, vals):
        lang = self.env.context.get('lang', False)
        if lang:
            lang = self.env['res.lang'].get_code_from_alias(lang)
        res = super(View, self.with_context(lang=lang)).write(vals)
        fields = ['seo_url', 'seo_url_parent', 'seo_url_level']
        if set(fields).intersection(set(vals.keys())):
            self.with_context(lang=lang).update_related_views()
            self.with_context(lang=lang).update_website_menus()
        return res

    @api.multi
    def update_related_views(self):
        for obj in self:
            if obj.seo_url_children:
                obj.seo_url_children.write({'seo_url_level': obj.seo_url_level + 1})

    @api.multi
    def update_website_menus(self):
        self.env['website.menu'].search([]).update_website_menus()

    @api.one
    def get_seo_url_parts(self):
        seo_url_parts = []
        if self.seo_url:
            seo_url_parts.append(self.seo_url)
            if self.seo_url_parent:
                seo_url_parts += self.seo_url_parent.get_seo_url_parts()[0]
        return seo_url_parts

    @api.one
    def get_seo_path(self):
        seo_url_parts = self.get_seo_url_parts()[0]
        if len(seo_url_parts) == self.seo_url_level + 1:
            seo_url_parts.reverse()
            return '/' + '/'.join(seo_url_parts)
        return False

    @api.model
    def find_by_seo_path(self, path):
        url_parts = path.split('/')
        views = self.search([('seo_url', 'in', url_parts)],
                            order='seo_url_level ASC')
        if len(url_parts) == len(views):
            view = views[-1]
            if len(views) == view.seo_url_level + 1:
                return view
        return False

    @api.cr_uid_ids_context
    def render(self, cr, uid, id_or_xml_id, values=None, engine='ir.qweb',
               context=None):
        """Add additional helper variables.

        Add slug function with additional seo url handling and the query string
        of the http request environment to the values object.
        """
        if values is None:
            values = {}

        values.update({
            'slug': slug,
            'request_query_string': request.httprequest.environ['QUERY_STRING'],
            'url_for': url_for
        })

        return super(View, self).render(cr, uid, id_or_xml_id, values=values,
                                        engine=engine, context=context)
