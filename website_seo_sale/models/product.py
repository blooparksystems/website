from openerp.osv import osv, fields
from openerp.addons.website_seo_sale.models.website import slug


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

    # Wrappers for call_kw with inherits
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
            names = [cat.name]
            pcat = cat.parent_id
            while pcat:
                names.append(pcat.name)
                pcat = pcat.parent_id
            res.append((cat.id, '|'.join(reversed(names))))
        return res