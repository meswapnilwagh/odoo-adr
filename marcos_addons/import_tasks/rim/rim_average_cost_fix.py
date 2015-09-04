# -*- coding: utf-8 -*-
import odoorpc
from pprint import pprint as pp
import json

odoo = odoorpc.ODOO("localhost", "jsonrpc", port=8069)

odoo.login("rim", "eneldo@marcos.do", "Antonio230")

product_obj = odoo.env["product.product"]

po_average = {}

count = 0
for product_id in product_obj.search([]):
    move_ids = odoo.env["stock.move"].search([("product_id", "=", product_id), ('location_id', '=', 8)])
    if not move_ids:
        continue
    moves = [move for move in odoo.env["stock.move"].browse(move_ids)]
    for move in moves:
        if not po_average.get(move.product_id.id, False):
            po_average.update({move.product_id.id: dict(name=move.product_id.name,
                                                        qty=move.product_uom_qty,
                                                        amount=move.product_uom_qty * move.price_unit,
                                                        average=move.price_unit)})
        else:
            qty = po_average[move.product_id.id]["qty"] + move.product_uom_qty
            amount = po_average[move.product_id.id]["amount"] + move.product_uom_qty * move.price_unit

            po_average[move.product_id.id].update({"qty": qty, "amount": amount, "average": amount / qty})

    count += 1
    print count



print json.dumps(po_average)
