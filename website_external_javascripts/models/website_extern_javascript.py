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
from openerp import fields, models


class WebsiteExternJavaScript(models.Model):

    _name = 'website.extern.javascript'

    _order = 'sequence'

    activated = fields.Boolean('Activated')

    sequence = fields.Integer('Sequence',
                              help='Used for the order of the JavaScripts. '
                                   'The higher the number the later the code '
                                   'is embedded.')

    description = fields.Char('Description')

    type = fields.Selection([('url', 'URL'), ('code', 'Code')], 'Type')

    url = fields.Char('URL', help='URL of the JavaScript to embed.')

    code = fields.Text('Code', help='JavaScript to embed into the html code.')
