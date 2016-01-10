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
import openerp


ODOO_NOT_FOUND_MESSAGE = '404: Page not found!'


class TestWebsiteBlogSeoController(openerp.tests.HttpCase):

    at_install = False
    post_install = True

    def setUp(self):
        super(TestWebsiteBlogSeoController, self).setUp()

        self.blog = self.env['blog.blog']
        self.post = self.env['blog.post']

    def get_odoo_code(self, response):
        page = response.read()
        if ODOO_NOT_FOUND_MESSAGE in page:
            return 404
        return response.getcode()

    def test_00_website_seo_blog_controller(self):
        """Test valid seo url blog."""
        for blog in self.blog.search([]):
            if blog.seo_url:
                url = '/%s' % blog.seo_url
                r = self.url_open(url)
                code = self.get_odoo_code(r)
                self.assertIn(code, xrange(200, 300), "Fetching %s returned error response (%d)" % (url, code))

    def test_01_website_seo_blog_controller(self):
        """Test valid seo url blog post."""
        for post in self.post.search([]):
            if post.seo_url and post.blog_id.seo_url and post.website_published:
                url = '/%s/%s' % (post.blog_id.seo_url, post.seo_url)
                r = self.url_open(url)
                code = self.get_odoo_code(r)
                self.assertIn(code, xrange(200, 300), "Fetching %s returned error response (%d)" % (url, code))
