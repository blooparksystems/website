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
from website_seo_sale.models.product import slug


class View(models.Model):

    """Update view model with additional SEO variables."""

    _name = 'ir.ui.view'
    _inherit = ['ir.ui.view', 'website.seo.metadata']


    @api.cr_uid_ids_context
    def render(self, cr, uid, id_or_xml_id, values=None, engine='ir.qweb', context=None):
        """Add additional helper variables.

        Add slug function with additional seo url handling and the query string
        of the http request environment to the values object.
        """
        if values is None:
            values = {}

        values.update({
            'slaag': slug,
        })

        return super(View, self).render(cr, uid, id_or_xml_id, values=values,
                                        engine=engine, context=context)
