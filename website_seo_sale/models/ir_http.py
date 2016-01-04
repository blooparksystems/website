from openerp.osv import orm
from openerp.addons.website.models.ir_http import ModelConverter, RequestUID
from product import slug, _UNSLUG_RE
from openerp.http import request
import re


class IrHttp(orm.TransientModel):
    _inherit = 'ir.http'

    def _get_converters(self):
        res = super(IrHttp, self)._get_converters()
        res['model'] = UnderscoredModelConverter
        return res

class UnderscoredModelConverter(ModelConverter):

    def __init__(self, url_map, model=False, domain='[]'):
        super(ModelConverter, self).__init__(url_map, model)
        self.domain = domain
        self.regex = _UNSLUG_RE.pattern

    def to_url(self, value):
        return slug(value)

    def to_python(self, value):
        m = re.match(self.regex, value)
        _uid = RequestUID(value=value, match=m, converter=self)

        res = request.registry[self.model].search(request.cr, 1, [('name', '=', value.replace('_', ' '))])
        if res:
            return request.registry[self.model].browse(request.cr, _uid, res, context=request.context)