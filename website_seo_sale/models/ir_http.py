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