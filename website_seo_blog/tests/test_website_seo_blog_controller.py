# -*- coding: utf-8 -*-
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
