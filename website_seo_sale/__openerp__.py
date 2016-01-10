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
{
    'name': 'eCommerce SEO Optimized',
    'category': 'Website',
    'sequence': 55,
    'summary': 'Sell Your Products Online',
    'website': 'http://www.bloopark.de',
    'version': '1.0',
    'author': "bloopark systems GmbH & Co. KG ,"
              "Odoo Community Association (OCA)",
    'description': """
OpenERP E-Commerce SEO Optimized
==================

        """,
    'depends': ['website_seo', 'website_sale'],
    'data': [
        'views/templates.xml',
    ],
    'installable': True,
    'application': False,
}
