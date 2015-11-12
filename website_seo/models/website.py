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

    @openerp.tools.ormcache('id')
    def _get_languages(self, cr, uid, id):
        website = self.browse(cr, uid, id)
        return [(lg.short_code or lg.code, lg.name) for lg in website.language_ids]
    
    def get_alternate_languages(self, cr, uid, ids, req=None, context=None):
        # TODO: do something here to show url translated in HEAD, current show wrong URL
        return super(Website, self).get_alternate_languages(cr, uid, ids, req, context)


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
                view = self.env['ir.ui.view'].search([('key', '=', xml_id)])
            if not view:
                xml_id = 'website.%s' % slugify(self.name)
                view = self.env['ir.ui.view'].search([('key', '=', xml_id)])
        return view

    @api.model
    def create(self, vals):
        obj = super(WebsiteMenu, self).create(vals)
        obj.update_related_views()
        obj.update_website_menus()
        return obj

    @api.multi
    def write(self, vals):
        res = super(WebsiteMenu, self).write(vals)
        if not self.env.context.get('view_updated', False) \
           and (vals.get('parent_id', False) or vals.get('url', False)):
            self.update_related_views()
            self.update_website_menus()
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
                    vals.update({'url': '/page/%s' % view.key.replace('website.', '')})
                if view.seo_url_parent and obj.parent_id.get_website_view()[0] != view.seo_url_parent:
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
    seo_url_redirect = fields.Char(string='SEO Url Redirect')
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
        """Add check for correct SEO urls."""
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
        if self.seo_url:
            return "/%s" % self.seo_url
        return False

    @api.model
    def get_information_from(self, field):
        domain = [('field', '=', field)]
        obj = self.env['website.seo.information'].search(domain)
        return obj and obj[0].information or False


class WebsiteSeoInformation(models.Model):
    _name = 'website.seo.information'

    model = fields.Char('Model')
    field = fields.Char('Field')
    information = fields.Text('Information', translate=True)
