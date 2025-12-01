/** @odoo-module **/

import { registry } from "@web/core/registry";
import { Component } from "@odoo/owl";

class EazynovaDashboard extends Component {
    static template = "eazynova.Dashboard";
}

registry.category("actions").add("eazynova_dashboard", EazynovaDashboard);
