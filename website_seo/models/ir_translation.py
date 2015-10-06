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
from openerp import api, models

UPDATE_TRANSLATION_DATA = {
    'ir.ui.view,seo_url': {'model': 'ir.ui.view', 'method': 'update_menu_url'}
}


class IrTranslation(models.Model):
    _inherit = 'ir.translation'

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

