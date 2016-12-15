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
import re

import openerp
from openerp import api, fields, models
from openerp.addons.website.models.website import slugify
from openerp.exceptions import ValidationError
from openerp.osv import orm
from openerp.tools.translate import _
from openerp.http import request


META_ROBOTS = [
    ('INDEX,FOLLOW', 'INDEX,FOLLOW'),
    ('NOINDEX,FOLLOW', 'NOINDEX,FOLLOW'),
    ('INDEX,NOFOLLOW', 'INDEX,NOFOLLOW'),
    ('NOINDEX,NOFOLLOW', 'NOINDEX,NOFOLLOW')
]


def slug(value):
    """Add seo url check in slug handling."""
    if isinstance(value, orm.browse_record):
        # if a seo url field exists in a record and it is not empty return it
        if 'seo_url' in value._fields and value.seo_url:
            return value.seo_url

        # [(id, name)] = value.name_get()
        id, name = value.id, value.display_name
    else:
        # assume name_search result tuple
        id, name = value
    slugname = slugify(name or '').strip().strip('-')
    if not slugname:
        return str(id)
    return "%s-%d" % (slugname, id)


class Website(models.Model):
    _inherit = 'website'

    @openerp.tools.ormcache(skiparg=3)
    def _get_languages(self, cr, uid, id):
        website = self.browse(cr, uid, id)
        return [(lg.short_code or lg.code, lg.name) for lg in website.language_ids]
    
    def get_canonical_url(self, cr, uid, req=None, context=None):
        if req is None:
            req = request.httprequest
        default = self.get_current_website(cr, uid, context=context).default_lang_code
        if request.lang != default:
            url = req.url_root[0:-1] + '/' + request.lang + req.path
            if req.query_string:
                url += '?' + req.query_string
            return url
        return req.url

    def get_alternate_languages(self, cr, uid, ids, req=None, context=None):
        langs = []
        if req is None:
            req = request.httprequest
        default = self.get_current_website(cr, uid, context=context).default_lang_code
        shorts = []
        for code, name in self.get_languages(cr, uid, ids, context=context):
            lg_path = ('/' + code) if code != default else ''
            lg = code.split('_')
            shorts.append(lg[0])
            path = self.get_translated_path(cr, uid, req.path, code, context=context)
            href = req.url_root[0:-1] + lg_path + path
            if req.query_string:
                href += '?' + req.query_string
            lang = {
                'hreflang': ('-'.join(lg)).lower(),
                'short': lg[0],
                'href': href,
            }
            langs.append(lang)
        for lang in langs:
            if shorts.count(lang['short']) == 1:
                lang['hreflang'] = lang['short']
        return langs

    def get_translated_path(self, cr, uid, path, lang, context=None):
        if lang == request.lang:
            return path
        ctx = context.copy()
        ctx.update({'lang': request.lang})
        view = self.pool.get('ir.ui.view')
        view_ids = view.search(cr, uid, [('seo_url', '!=', False)], context=context)
        for obj in view.browse(cr, uid, view_ids, context=ctx):
            if obj.get_seo_path()[0] == path:
                ctx.update({'lang': lang})
                return view.browse(cr, uid, obj.id, context=ctx).get_seo_path()[0]
        return path


class WebsiteMenu(models.Model):

    """Add translation possibility to website menu entries."""

    _inherit = 'website.menu'

    url = fields.Char(translate=True)

    @api.one
    def get_seo_url_level(self):
        url_level = 0
        if self.parent_id and self.parent_id != self.env.ref('website.main_menu'):
            url_level = self.parent_id.get_seo_url_level()[0] + 1
        return url_level

    @api.one
    def get_website_view(self):
        view = False
        if self.url:
            view = self.env['ir.ui.view'].find_by_seo_path(self.url)
            if not view:
                url_parts = self.url.split('/')
                xml_id = url_parts[-1]
                if '.' not in xml_id:
                    xml_id = 'website.%s' % xml_id
                view = self.env['ir.model.data'].xmlid_to_object(xml_id)
            if not view:
                xml_id = 'website.%s' % slugify(self.name)
                view = self.env['ir.model.data'].xmlid_to_object(xml_id)
        return view

    @api.model
    def create(self, vals):
        obj = super(WebsiteMenu, self).create(vals)
        obj.update_related_views()
        obj.update_website_menus()
        return obj

    @api.multi
    def write(self, vals):
        self.clear_caches()
        lang = self.env.context.get('lang', False)
        if lang:
            lang = self.env['res.lang'].get_code_from_alias(lang)
        res = super(WebsiteMenu, self.with_context(lang=lang)).write(vals)
        if not self.env.context.get('view_updated', False) \
           and (vals.get('parent_id', False) or vals.get('url', False)):
            self.with_context(lang=lang).update_related_views()
            self.with_context(lang=lang).update_website_menus()
        return res

    @api.multi
    def update_related_views(self):
        for obj in self:
            view = obj.get_website_view()[0]
            if view:
                view_parent_id = False
                if obj.parent_id:
                    view_parent = obj.parent_id.get_website_view()[0]
                    view_parent_id = view_parent and view_parent.id
                seo_url_level = obj.get_seo_url_level()[0]
                view.write({
                    'seo_url_parent': view_parent_id,
                    'seo_url_level': seo_url_level
                })

    @api.multi
    def update_website_menus(self):
        for obj in self:
            vals = {}
            view = obj.get_website_view()[0]
            if view:
                seo_path = view.get_seo_path()[0]
                if seo_path:
                    vals.update({'url': seo_path})
                else:
                    view_name = view.get_xml_id()
                    if view_name:
                        view_name = view_name[view.id].replace('website.', '')
                        vals.update({'url': '/page/%s' % view_name})

                if obj.parent_id.get_website_view()[0] != view.seo_url_parent:
                    # TODO: create a new method to get a menu from a view
                    for menu in self:
                        if menu.get_website_view()[0] == view.seo_url_parent:
                            vals.update({'parent_id': menu.id})
                            break
            if vals:
                obj.with_context(view_updated=True).write(vals)


class WebsiteSeoMetadata(models.Model):

    """Add additional SEO fields which can be used by other models."""

    _inherit = 'website.seo.metadata'

    seo_url = fields.Char(
        string='SEO Url', translate=True, help='If you fill out this field '
        'manually the allowed characters are a-z, A-Z, 0-9, - and _.')
    seo_url_redirect = fields.Char(string='SEO Url Redirect', translate=True)
    website_meta_robots = fields.Selection(META_ROBOTS,
                                           string='Website meta robots',
                                           translate=True)

    @api.model
    def create(self, vals):
        """Add check for correct SEO urls.

        Exceptional cases will be handled in the additional website SEO
        modules. For example have a look at the website_seo_blog module in the
        create() function in website_seo_blog/models/website_blog.py.
        """
        if vals.get('seo_url', False):
            self.validate_seo_url(vals['seo_url'])

        return super(WebsiteSeoMetadata, self).create(vals)

    @api.multi
    def write(self, vals):
        """- Add check for correct SEO urls.
           - Saves old seo_url in seo_url_redirect field
        """
        if vals.get('seo_url', False):
            self.validate_seo_url(vals['seo_url'])
            for obj in self:
                if obj.seo_url:
                    seo_url = obj.get_seo_path()[0]
                    if obj.seo_url_redirect:
                        vals['seo_url_redirect'] = '%s,%s' % (obj.seo_url_redirect, seo_url)
                    else:
                        vals['seo_url_redirect'] = seo_url
                super(WebsiteSeoMetadata, obj).write(vals)
            return True
        return super(WebsiteSeoMetadata, self).write(vals)

    def validate_seo_url(self, seo_url):
        """Validate a manual entered SEO url."""
        if not seo_url or not bool(re.match('^([.a-zA-Z0-9-_]+)$', seo_url)):
            raise ValidationError(_('Only a-z, A-Z, 0-9, - and _ are allowed '
                                    'characters for the SEO url.'))
        return True

    @api.one
    def get_seo_path(self):
        """This method must be override in child classes in order to provide
         a different behavior of the model"""
        self.env['ir.translation'].clear_caches()
        if self.seo_url:
            return "/%s" % self.seo_url
        return False

    @api.model
    def get_information_from(self, field):
        domain = [('field', '=', field)]
        obj = self.env['website.seo.information'].search(domain)
        return obj and obj[0].information or False


class WebsiteSeoRedirect(models.Model):
    """Class used to store old urls for each resource. With these urls the
       website can do redirect 301 if some url has changed.

       The field 'resource' can't be a strong reference because
       the model website.seo.metadata is used to inherit and the fields
       actually are in the resources (eg. ir.ui.view, blog.blog).
    """

    _name = 'website.seo.redirect'

    url = fields.Char(string='URL')
    lang = fields.Char(string='Lang')
    resource = fields.Char(string='Resource', help='This field use the format model,id')



class WebsiteSeoInformation(models.Model):
    _name = 'website.seo.information'

    model = fields.Char('Model')
    field = fields.Char('Field')
    information = fields.Text('Information', translate=True)
