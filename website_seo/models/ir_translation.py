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

UPDATE_TRANSLATION_DATA = {
    'ir.ui.view,seo_url': {'model': 'ir.ui.view', 'method': 'update_website_menus'}
}


class IrTranslation(models.Model):
    _inherit = 'ir.translation'

    @api.model
    def _get_ids(self, cr, uid, name, tt, lang, ids):
        lang = self.pool.get('res.lang').get_code_from_alias(cr, uid, lang)
        return super(IrTranslation, self)._get_ids(cr, uid, name, tt, lang, ids)

    @api.model
    def _set_ids(self, name, tt, lang, ids, value, src=None):
        lang = self.env['res.lang'].get_code_from_alias(lang)
        return super(IrTranslation, self)._set_ids(name, tt, lang, ids, value, src)

    @api.model
    def _get_source(self, name, types, lang, source=None, res_id=None):
        lang = self.env['res.lang'].get_code_from_alias(lang)
        return super(IrTranslation, self)._get_source(name, types, lang, source, res_id)

    @api.model
    def _get_terms_query(self, field, records):
        lang = self.env['res.lang'].get_code_from_alias(records.env.lang)
        query = """ SELECT * FROM ir_translation
                    WHERE lang=%s AND type=%s AND name=%s AND res_id IN %s """
        name = "%s,%s" % (field.model_name, field.name)
        params = (lang, 'model', name, tuple(records.ids))
        return query, params

    def translate_fields(self, cr, uid, model, id, field=None, context=None):
        res = super(IrTranslation, self).translate_fields(cr, uid, model, id, field, context)
        # the translate_fields method does not set module field, it is needed because if you are going to
        # translate in frontend the system wont't find the existing translation
        domain = [('module', '=', False), ('type', '=', 'model')]
        translation_ids = self.search(cr, uid, domain, context=context)
        if translation_ids:
            for translation in self.browse(cr, uid, translation_ids):
                model = translation.name.split(',')[0]
                module = self.pool.get(model)._original_module
                self.write(cr, uid, translation.id, {'module': module}, context)
        return res

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
