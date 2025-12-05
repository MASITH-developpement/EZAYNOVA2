# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import request

class AccountingController(http.Controller):
    
    @http.route('/accounting/dashboard', type='http', auth='user', website=True)
    def dashboard(self, **kwargs):
        return request.render('eazynova_comptabilite.dashboard_template')
