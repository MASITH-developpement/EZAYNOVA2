/** @odoo-module **/

// EAZYNOVA - Sales Funnel JavaScript

import publicWidget from "@web/legacy/js/public/public_widget";

publicWidget.registry.SalesFunnel = publicWidget.Widget.extend({
    selector: '.funnel-page',

    start: function () {
        this._super.apply(this, arguments);
        console.log('Sales funnel initialized');
    },
});

export default publicWidget.registry.SalesFunnel;
