# -*- coding: utf-8 -*-
from odoo import http

# class Products(http.Controller):
#     @http.route('/products/products/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/products/products/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('products.listing', {
#             'root': '/products/products',
#             'objects': http.request.env['products.products'].search([]),
#         })

#     @http.route('/products/products/objects/<model("products.products"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('products.object', {
#             'object': obj
#         })