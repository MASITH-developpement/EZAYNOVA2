/** @odoo-module **/

// EAZYNOVA - Website Booking JavaScript

import publicWidget from "@web/legacy/js/public/public_widget";

publicWidget.registry.BookingCalendar = publicWidget.Widget.extend({
    selector: '.booking-calendar-widget',

    start: function () {
        this._super.apply(this, arguments);
        this._initializeCalendar();
    },

    _initializeCalendar: function () {
        // Calendar initialization logic
        console.log('Booking calendar initialized');
    },
});

export default publicWidget.registry.BookingCalendar;
