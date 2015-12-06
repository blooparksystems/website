from openerp.osv import osv, fields


class product_template(osv.Model):
    _inherit = ["product.template", "website.seo.metadata", 'website.published.mixin', 'rating.mixin']
    _order = 'website_published desc, website_sequence desc, name'
    _name = 'product.template'
    _mail_post_access = 'read'

    def _website_url(self, cr, uid, ids, field_name, arg, context=None):
        res = super(product_template, self)._website_url(cr, uid, ids, field_name, arg, context=context)
        for product in self.browse(cr, uid, ids, context=context):
            res[product.id] = "/%s" % (product.id,)
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