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
import openerp.tests
from openerp.addons.website_seo_sale.models.product import slug


@openerp.tests.common.at_install(False)
@openerp.tests.common.post_install(True)
class TestWebsiteSeoSale(openerp.tests.common.TransactionCase):
    def test_slug_product(self):
        self.assertEqual(slug('Test Product'), 'Test_Product')

    def test_product_url(self):
        self.assertTrue(self.env['product.product'].validate_seo_url('Sample_Product'))
