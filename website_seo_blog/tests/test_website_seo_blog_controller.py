# -*- coding: utf-8 -*-
import openerp


class TestWebsiteBlogSeoController(openerp.tests.HttpCase):

    at_install = False
    post_install = True

    def setUp(self):
        super(TestWebsiteBlogSeoController, self).setUp()
        blog_id = self.registry['blog.blog'].create(self.cr, self.uid, {
            'name': 'Main Blog',
            'seo_url': 'main-blog'
        })
        self.registry['blog.post'].create(self.cr, self.uid, {
           'name': 'My First Blog Post',
           'seo_url': 'first-blogpost',
           'blog_id': blog_id
        })

    def test_00_website_seo_blog_controller(self):
        """Test valid seo url blog."""
        url = '/main-blog'
        r = self.url_open(url)
        code = r.getcode()
        self.assertIn(code, xrange(200, 300), "Fetching %s returned error response (%d)" % (url, code))

    def test_01_website_seo_blog_controller(self):
        """Test valid seo url blog post."""
        url = '/main-blog/first-blogpost'
        r = self.url_open(url)
        code = r.getcode()
        self.assertIn(code, xrange(200, 300), "Fetching %s returned error response (%d)" % (url, code))

    def test_02_website_seo_blog_controller(self):
        """Test invalid seo url blog post."""
        url = '/blog-main-blog/first-blogpost'
        r = self.url_open(url)
        code = r.getcode()
        self.assertTrue(code > 400, "Bad url %s returned good response (%d)" % (url, code))

