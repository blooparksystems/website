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
from openerp import tools
from openerp import api, models
from openerp.osv import expression
from openerp.addons.web.http import request

UPDATE_TRANSLATION_DATA = {
    'ir.ui.view,seo_url': {'model': 'ir.ui.view', 'method': 'update_website_menus'}
}

# TODO: need to check copy_translation method from Model
# it has another operation with lang which doesn't use
# the modifications below.


class IrTranslation(models.Model):
    _inherit = 'ir.translation'

    @api.model
    def get_code_from_alias(self, code):
        lang = self.env['res.lang'].search([('iso_code', '=', code)])
        return lang and lang[0].code or code

    @tools.ormcache_multi(skiparg=3, multi=6)
    def _get_ids(self, cr, uid, name, tt, lang, ids):
        lang = self.get_code_from_alias(cr, uid, lang)
        return super(IrTranslation, self)._get_ids(cr, uid, name, tt, lang, ids)

    @api.model
    def _set_ids(self, name, tt, lang, ids, value, src=None):
        lang = self.get_code_from_alias(lang)
        return super(IrTranslation, self)._set_ids(name, tt, lang, ids, value, src)

    @api.model
    def _get_source(self, name, types, lang, source=None, res_id=None):
        lang = self.get_code_from_alias(lang)
        return super(IrTranslation, self)._get_source(name, types, lang, source, res_id)

    @api.model
    def create(self, vals):
        obj = super(IrTranslation, self).create(vals)
        obj.update_translation_data()
        return obj

    @api.multi
    def write(self, vals):
        res = super(IrTranslation, self).write(vals)
        self.update_translation_data()
        return res

    @api.multi
    def update_translation_data(self):
        for obj in self:
            data = UPDATE_TRANSLATION_DATA.get(obj.name, False)
            if data:
                model = self.env[data['model']].browse([obj.res_id])
                model_context = getattr(model, 'with_context')(lang=obj.lang)
                getattr(model_context, data['method'])()


def update_lang_code_from_alias_in_expression():

    def extended_init(self, cr, uid, exp, table, context):

        self._unaccent = expression.get_unaccent_wrapper(cr)
        self.joins = []
        self.root_model = table

        # normalize and prepare the expression for parsing
        self.expression = expression.distribute_not(expression.normalize_domain(exp))

        # look for real lang from context before parse
        parse_ctx = context.copy()
        if parse_ctx.get('lang', False):
            cr.execute("select code from res_lang where iso_code = '%s'" % parse_ctx['lang'])
            res = cr.fetchall()
            if res and res[0]:
                parse_ctx.update({'lang': res[0][0]})

        # parse the domain expression
        self.parse(cr, uid, context=parse_ctx)

    setattr(expression.expression, '__init__', extended_init)

update_lang_code_from_alias_in_expression()
