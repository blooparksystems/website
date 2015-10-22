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
from openerp import api, fields, models
from openerp.osv import expression


class ResLang(models.Model):
    _name = 'res.lang'
    _inherit = 'res.lang'

    short_code = fields.Char('Short code')

    @api.model
    def get_code_from_alias(self, code):
        lang = self.search([('short_code', '=', code)])
        return lang and lang[0].code or code


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
            cr.execute("select column_name from information_schema.columns "
                       "where table_name='res_lang' AND column_name='short_code'")
            res = cr.fetchall()
            if res:
                cr.execute("select code from res_lang where short_code = '%s'" % parse_ctx['lang'])
                res = cr.fetchall()
                if res and res[0]:
                    parse_ctx.update({'lang': res[0][0]})

        # parse the domain expression
        self.parse(cr, uid, context=parse_ctx)

    setattr(expression.expression, '__init__', extended_init)

update_lang_code_from_alias_in_expression()
