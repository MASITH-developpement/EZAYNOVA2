odoo.define('eazynova_trust.review_widget', function (require) {
    'use strict';

    const publicWidget = require('web.public.widget');

    publicWidget.registry.EazynovaTrustReviewWidget = publicWidget.Widget.extend({
        selector: '.eazynova-trust-review-widget',
        start: function () {
            return this._super.apply(this, arguments);
        },
    });
});

