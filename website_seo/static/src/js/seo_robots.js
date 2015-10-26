odoo.define('website_seo.seo_robots', function (require) {
    'use strict';

    var ajax = require('web.ajax');
    var core = require('web.core');
    var Class = require('web.Class');
    var mixins = require('web.mixins');
    var Model = require('web.Model');
    var Widget = require('web.Widget');
    var base = require('web_editor.base');
    var seo = require('website.seo');

    var qweb = core.qweb;

    ajax.loadXML('/website_seo/static/src/xml/website_seo_robots.xml', qweb);

    // This replaces \b, because accents(e.g. à, é) are not seen as word boundaries.
    // Javascript \b is not unicode aware, and words beginning or ending by accents won't match \b
    var WORD_SEPARATORS_REGEX = '([\\u2000-\\u206F\\u2E00-\\u2E7F\'!"#\\$%&\\(\\)\\*\\+,\\-\\.\\/:;<=>\\?¿¡@\\[\\]\\^_`\\{\\|\\}~\\s]+|^|$)';

    var Tip = Widget.extend({
        template: 'website.seo_tip',
        events: {
            'closed.bs.alert': 'destroy',
        },
        init: function (parent, options) {
            this.message = options.message;
            // cf. http://getbootstrap.com/components/#alerts
            // success, info, warning or danger
            this.type = options.type || 'info';
            this._super(parent);
        },
    });

    var HtmlPage = Class.extend(mixins.PropertiesMixin, {
        url: function () {
            var url = window.location.href;
            var hashIndex = url.indexOf('#');
            return hashIndex >= 0 ? url.substring(0, hashIndex) : url;
        },
        title: function () {
            var $title = $('title');
            return ($title.length > 0) && $title.text() && $title.text().trim();
        },
        changeTitle: function (title) {
            // TODO create tag if missing
            $('title').text(title);
            this.trigger('title-changed', title);
        },
        description: function () {
            var $description = $('meta[name=description]');
            return ($description.length > 0) && ($description.attr('content') && $description.attr('content').trim());
        },
        changeDescription: function (description) {
            // TODO create tag if missing
            $('meta[name=description]').attr('content', description);
            this.trigger('description-changed', description);
        },
        keywords: function () {
            var $keywords = $('meta[name=keywords]');
            var parsed = ($keywords.length > 0) && $keywords.attr('content') && $keywords.attr('content').split(",");
            return (parsed && parsed[0]) ? parsed: [];
        },
        changeKeywords: function (keywords) {
            // TODO create tag if missing
            $('meta[name=keywords]').attr('content', keywords.join(","));
            this.trigger('keywords-changed', keywords);
        },
        headers: function (tag) {
            return $('#wrap '+tag).map(function () {
                return $(this).text();
            });
        },
        images: function () {
            return $('#wrap img').map(function () {
                var $img = $(this);
                return  {
                    src: $img.attr('src'),
                    alt: $img.attr('alt'),
                };
            });
        },
        company: function () {
            return $('html').attr('data-oe-company-name');
        },
        bodyText: function () {
            return $('body').children().not('.js_seo_configuration').text();
        },
        isInBody: function (text) {
            return new RegExp(WORD_SEPARATORS_REGEX+text+WORD_SEPARATORS_REGEX, "gi").test(this.bodyText());
        },
        isInTitle: function (text) {
            return new RegExp(WORD_SEPARATORS_REGEX+text+WORD_SEPARATORS_REGEX, "gi").test(this.title());
        },
        isInDescription: function (text) {
            return new RegExp(WORD_SEPARATORS_REGEX+text+WORD_SEPARATORS_REGEX, "gi").test(this.description());
        },
        // Add robots and seo_url
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

    var KeywordList = Widget.extend({
        template: 'website.seo_list',
        maxKeywords: 10,
        init: function (parent, options) {
            this.htmlPage = options.page;
            this._super(parent);
        },
        start: function () {
            var self = this;
            var existingKeywords = self.htmlPage.keywords();
            if (existingKeywords.length > 0) {
                _.each(existingKeywords, function (word) {
                    self.add.call(self, word);
                });
            }
        },
        keywords: function () {
            var result = [];
            this.$('.js_seo_keyword').each(function () {
                result.push($(this).data('keyword'));
            });
            return result;
        },
        isFull: function () {
            return this.keywords().length >= this.maxKeywords;
        },
        exists: function (word) {
            return _.contains(this.keywords(), word);
        },
        add: function (candidate, language) {
            var self = this;
            // TODO Refine
            var word = candidate ? candidate.replace(/[,;.:<>]+/g, " ").replace(/ +/g, " ").trim().toLowerCase() : "";
            if (word && !self.isFull() && !self.exists(word)) {
                var keyword = new Keyword(self, {
                    word: word,
                    language: language,
                    page: this.htmlPage,
                });
                keyword.on('removed', self, function () {
                   self.trigger('list-not-full');
                   self.trigger('removed', word);
                });
                keyword.on('selected', self, function (word, language) {
                    self.trigger('selected', word, language);
                });
                keyword.appendTo(self.$el);
            }
            if (self.isFull()) {
                self.trigger('list-full');
            }
        },
    });

    seo.Configurator.include({
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
            var htmlPage = this.htmlPage = new HtmlPage();
            $modal.find('.js_seo_page_url').text(htmlPage.url());
            $modal.find('input[name=seo_page_title]').val(htmlPage.title());
            $modal.find('textarea[name=seo_page_description]').val(htmlPage.description());
            $modal.find('select[name=seo_page_robots]').val(htmlPage.robots());
            $modal.find('input[name=seo_url]').val(htmlPage.seo_url());
            // self.suggestImprovements();
            // self.imageList = new ImageList(self, { page: htmlPage });
            // if (htmlPage.images().length === 0) {
            //     $modal.find('.js_image_section').remove();
            // } else {
            //     self.imageList.appendTo($modal.find('.js_seo_image_list'));
            // }
            self.keywordList = new KeywordList(self, { page: htmlPage });
            self.keywordList.on('list-full', self, function () {
                $modal.find('input[name=seo_page_keywords]')
                    .attr('readonly', "readonly")
                    .attr('placeholder', "Remove a keyword first");
                $modal.find('button[data-action=add]')
                    .prop('disabled', true).addClass('disabled');
            });
            self.keywordList.on('list-not-full', self, function () {
                $modal.find('input[name=seo_page_keywords]')
                    .removeAttr('readonly').attr('placeholder', "");
                $modal.find('button[data-action=add]')
                    .prop('disabled', false).removeClass('disabled');
            });
            self.keywordList.on('selected', self, function (word, language) {
                self.keywordList.add(word, language);
            });
            self.keywordList.appendTo($modal.find('.js_seo_keywords_list'));
            self.disableUnsavableFields();
            self.renderPreview();
            $modal.modal();
            self.getLanguages();
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
                var model = new Model('website.seo.metadata');
                model.call('get_information_from', [field, base.get_context()]).then(function(data) {
                    if (data.length){
                        new Tip(self, {message: data, type: 'info'}).appendTo(tip);
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
            });
        },
        loadMetaData: function () {
            var self = this;
            var obj = this.getMainObject();
            var def = $.Deferred();
            if (!obj) {
                // return $.Deferred().reject(new Error("No main_object was found."));
                def.resolve(null);
            } else {
                var fields = ['website_meta_title', 'website_meta_description', 'website_meta_keywords', 'website_meta_robots', 'seo_url'];
                var model = new Model(obj.model).call('read', [[obj.id], fields, base.get_context()]).then(function (data) {
                    if (data.length) {
                        var meta = data[0];
                        meta.model = obj.model;
                        def.resolve(meta);
                    } else {
                        def.resolve(null);
                    }
                }).fail(function () {
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

    base.ready().then(function () {
        $(document.body).on('click', '#title_tip', function() {
            new seo.Configurator(this).suggestField('website_meta_title');
        });
        $(document.body).on('click', '#description_tip', function() {
            new seo.Configurator(this).suggestField('website_meta_description');
        });
    });

});