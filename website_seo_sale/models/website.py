import re
from openerp.osv import orm


_UNSLUG_RE = re.compile(r'(?:(\w{1,2}|\w[A-Za-z0-9-_]+?\w))(?=$|/)')

def slug(value):
    if isinstance(value, orm.browse_record):
        name = value.display_name
    else:
        name = value

    return name.replace(' ', '_')