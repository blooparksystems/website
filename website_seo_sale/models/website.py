import re
from openerp.osv import orm
from openerp.addons.website.models.website import slugify


_UNSLUG_RE = re.compile(r'(?:(\w{1,2}|\w[A-Za-z0-9-_]+?\w))(?=$|/)')

def slug(value):
    if isinstance(value, orm.browse_record):
        name = value.display_name
    else:
        name = value

    if value._name == 'product.public.category':
        return name.replace('|', '/').replace(' ', '_')
    else:
        return name.replace(' ', '_')