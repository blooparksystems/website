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
from openerp.osv import osv
from openerp.osv import orm
import re
from openerp.tools.translate import _
from openerp.exceptions import ValidationError


_UNSLUG_RE = re.compile(r'(?:(\w{1,2}|\w[A-Za-z0-9-_]+?\w))(?=$|/)')

def slug(value):
    if isinstance(value, orm.browse_record):
        name = value.display_name
    else:
        name = value

    return name.replace(' ', '_')


class product_template(osv.Model):
    _inherit = ["product.template", "website.seo.metadata", 'website.published.mixin', 'rating.mixin']
    _order = 'website_published desc, website_sequence desc, name'
    _name = 'product.template'
    _mail_post_access = 'read'

    def _website_url(self, cr, uid, ids, field_name, arg, context=None):
        res = super(product_template, self)._website_url(cr, uid, ids, field_name, arg, context=context)
        for product in self.browse(cr, uid, ids, context=context):
            res[product.id] = "/%s" % slug(product.name)
        return res


class product_product(osv.Model):
    _inherit = "product.product"

    def open_website_url(self, cr, uid, ids, context=None):
        template_id = self.browse(cr, uid, ids, context=context).product_tmpl_id.id
        return self.pool['product.template'].open_website_url(cr, uid, [template_id], context=context)

    def website_publish_button(self, cr, uid, ids, context=None):
        template_id = self.browse(cr, uid, ids, context=context).product_tmpl_id.id
        return self.pool['product.template'].website_publish_button(cr, uid, [template_id], context=context)

    def website_publish_button(self, cr, uid, ids, context=None):
        template_id = self.browse(cr, uid, ids, context=context).product_tmpl_id.id
        return self.pool['product.template'].website_publish_button(cr, uid, [template_id], context=context)

    def validate_seo_url(self, seo_url):
        """Validate a manual entered SEO url."""
        if not seo_url or not bool(re.match('^([.a-zA-Z0-9-_]+)$', seo_url)):
            raise ValidationError(_('Only a-z, A-Z, 0-9, - and _ are allowed '
                                    'characters for the SEO url.'))
        return True


class product_public_category(osv.osv):
    _inherit = ["product.public.category"]

    def name_get(self, cr, uid, ids, context=None):
        res = []
        for cat in self.browse(cr, uid, ids, context=context):
            res.append((cat.id, cat.name))
        return res