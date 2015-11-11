// Override necessary parts of website/static/src/js/website.seo.js to enable
// META robots management via promote panel.
//
// We need to override all needed function. We don't can use the super function
// here.

(function () {
    'use strict';

    var website = openerp.website;
    website.add_template_file('/website_seo/static/src/xml/website_seo_robots.xml');

    website.seo.HtmlPage.include({
        robots: function() {
            var $robots = $('meta[name=robots]');
            return ($robots.length > 0) && ($robots.attr('content') && $robots.attr('content').trim());
        },
        changeRobots: function(robots) {
            $('meta[name=robots]').attr('content', robots);
            this.trigger('robots-changed', robots);
        },
        seo_url: function () {
            var $seo_url = $('meta[name=seo_url]');
            return ($seo_url.length > 0) && ($seo_url.attr('content') && $seo_url.attr('content').trim());
        },
        changeSeoUrl: function (seo_url) {
            $('meta[name=seo_url]').attr('content', seo_url);
            this.trigger('seo_url-changed', seo_url);
        },
    });

    website.seo.Configurator.include({
        events: {
            'keyup input[name=seo_page_keywords]': 'confirmKeyword',
            'keyup input[name=seo_page_title]': 'titleChanged',
            'keyup textarea[name=seo_page_description]': 'descriptionChanged',
            'change select[name=seo_page_robots]': 'robotsChanged',
            'keyup input[name=seo_url]': 'seoUrlChanged',
            'click button[data-action=add]': 'addKeyword',
            'click button[data-action=update]': 'update',
            'hidden.bs.modal': 'destroy'
        },
        canEditRobots: false,
        canEditSeoUrl: false,
        start: function() {
            var self = this;
            var $modal = self.$el;
            var htmlPage = this.htmlPage = new website.seo.HtmlPage();
            $modal.find('.js_seo_page_url').text(htmlPage.url());
            $modal.find('input[name=seo_page_title]').val(htmlPage.title());
            $modal.find('textarea[name=seo_page_description]').val(htmlPage.description());
            $modal.find('select[name=seo_page_robots]').val(htmlPage.robots());
            $modal.find('input[name=seo_url]').val(htmlPage.seo_url());

            self.keywordList = new website.seo.KeywordList(self, { page: htmlPage });
            self.keywordList.on('list-full', self, function() {
                $modal.find('input[name=seo_page_keywords]')
                    .attr('readonly', "readonly")
                    .attr('placeholder', "Remove a keyword first");
                $modal.find('button[data-action=add]')
                    .prop('disabled', true).addClass('disabled');
            });
            self.keywordList.on('list-not-full', self, function() {
                $modal.find('input[name=seo_page_keywords]')
                    .removeAttr('readonly').attr('placeholder', "");
                $modal.find('button[data-action=add]')
                    .prop('disabled', false).removeClass('disabled');
            });
            self.keywordList.on('selected', self, function(word) {
                self.keywordList.add(word);
            });
            self.keywordList.appendTo($modal.find('.js_seo_keywords_list'));
            self.disableUnsavableFields();
            self.renderPreview();
            $modal.modal();
        },
        disableUnsavableFields: function () {
            var self = this;
            var $modal = self.$el;
            self.loadMetaData().then(function(data) {
                self.canEditTitle = data && ('website_meta_title' in data);
                self.canEditDescription = data && ('website_meta_description' in data);
                self.canEditKeywords = data && ('website_meta_keywords' in data);
                // Allow editing the meta robots only for pages that have
                self.canEditRobots = data && ('website_meta_robots' in data);
                self.canEditSeoUrl = data && ('seo_url' in data);
                if (!self.canEditTitle) {
                    $modal.find('input[name=seo_page_title]').attr('disabled', true);
                }
                if (!self.canEditDescription) {
                    $modal.find('textarea[name=seo_page_description]').attr('disabled', true);
                }
                if (!self.canEditTitle && !self.canEditDescription && !self.canEditKeywords) {
                    $modal.find('button[data-action=update]').attr('disabled', true);
                }
                if (!self.canEditRobots) {
                    $modal.find('select[name=seo_page_robots]').attr('disabled', true);
                }
                if (!self.canEditSeoUrl) {
                    $modal.find('input[name=seo_url]').attr('disabled', true);
                }
            });
        },
        suggestField: function (field) {
            var tip = self.$('.js_seo_' + field + '_tips');
            if (tip.children().length === 0) {
                var model = website.session.model('website.seo.metadata');
                model.call('get_information_from', [field, website.get_context()]).then(function(data) {
                    if (data.length){
                        new website.seo.Tip(self, {
                            message: data,
                            type: 'info'
                        }).appendTo(tip);
                    }
                });
            }
            else {
                tip.children()[0].remove();
            }
        },
        update: function () {
            var self = this;
            var data = {};
            if (self.canEditTitle) {
                data.website_meta_title = self.htmlPage.title();
            }
            if (self.canEditDescription) {
                data.website_meta_description = self.htmlPage.description();
            }
            if (self.canEditKeywords) {
                data.website_meta_keywords = self.keywordList.keywords().join(", ");
            }
            if (self.canEditRobots) {
                data.website_meta_robots = self.htmlPage.robots();
            }
            if (self.canEditSeoUrl) {
                data.seo_url = self.htmlPage.seo_url();
            }

            self.saveMetaData(data).then(function() {
                self.$el.modal('hide');
                location.replace(data.seo_url, 301);
            });
        },
        loadMetaData: function () {
            var self = this;
            var obj = this.getMainObject();
            var def = $.Deferred();
            if (!obj) {
                def.resolve(null);
            } else {
                var fields = ['website_meta_title', 'website_meta_description', 'website_meta_keywords', 'website_meta_robots', 'seo_url'];
                var model = website.session.model(obj.model);
                model.call('read', [[obj.id], fields, website.get_context()]).then(function(data) {
                    if (data.length) {
                        var meta = data[0];
                        meta.model = obj.model;
                        def.resolve(meta);
                    } else {
                        def.resolve(null);
                    }
                }).fail(function() {
                        def.reject();
                });
            }
            return def;
        },
        robotsChanged: function () {
            var self = this;
            setTimeout(function () {
                var robots = self.$('select[name=seo_page_robots]').val();
                self.htmlPage.changeRobots(robots);
                self.renderPreview();
            }, 0);
        },
        seoUrlChanged: function () {
            var self = this;
            setTimeout(function () {
                var seo_url = self.$('input[name=seo_url]').val();
                self.htmlPage.changeSeoUrl(seo_url);
                self.renderPreview();
            }, 0);
        },
    });

    website.ready().done(function() {
        $(document.body).on('click', '#title_tip', function() {
            new website.seo.Configurator(this).suggestField('website_meta_title');
        });
        $(document.body).on('click', '#description_tip', function() {
            new website.seo.Configurator(this).suggestField('website_meta_description');
        });
    });

})();