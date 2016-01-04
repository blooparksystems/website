from openerp.osv import osv
from openerp.osv import orm
import re


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


class product_public_category(osv.osv):
    _inherit = ["product.public.category"]

    def name_get(self, cr, uid, ids, context=None):
        res = []
        for cat in self.browse(cr, uid, ids, context=context):
            res.append((cat.id, cat.name))
        return res