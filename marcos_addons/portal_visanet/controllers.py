# -*- coding: utf-8 -*-
from openerp import http

# class PortalVisanet(http.Controller):
#     @http.route('/portal_visanet/portal_visanet/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/portal_visanet/portal_visanet/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('portal_visanet.listing', {
#             'root': '/portal_visanet/portal_visanet',
#             'objects': http.request.env['portal_visanet.portal_visanet'].search([]),
#         })

#     @http.route('/portal_visanet/portal_visanet/objects/<model("portal_visanet.portal_visanet"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('portal_visanet.object', {
#             'object': obj
#         })