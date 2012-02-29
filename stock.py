from datetime import datetime
from dateutil.relativedelta import relativedelta
import time
from operator import itemgetter
from itertools import groupby

from osv import fields, osv
from tools.translate import _
import netsvc
import tools
import decimal_precision as dp
import logging

class stock_move(osv.osv):
    _inherit =  "stock.move"
    
    def onchange_quantity(self, cr, uid, ids, product_id, product_qty,
                          product_uom, product_uos):
        """ On change of product quantity finds UoM and UoS quantities
        @param product_id: Product id
        @param product_qty: Changed Quantity of product
        @param product_uom: Unit of measure of product
        @param product_uos: Unit of sale of product
        @return: Dictionary of values
        """
        result = {
                  'product_uos_qty': 0.00
          }

        if (not product_id) or (product_qty <=0.0):
            return {'value': result}

        product_obj = self.pool.get('product.product').browse(cr,uid,product_id)
        um_obj = self.pool.get('product.uom')
        # RAGIONIAMO SU UNITA' DI ACQUISTO O UNITA' DI BASE QUELLA DI VENDITA LA IGNORIAmO PER ORA
        if product_obj.uom_id.id <> product_uom:
             # sono diverse quindi PRIMA CONTROLLASE e DI ACQUISTO, SE NON LO e  VA IN ERRORE CON UNA RAISE ALTRIMENTI FA IL CALCOLO
             # PRENDENDO IL COEFFICENTE RISPETTO ALLA PRINCIPALE
             #uom_po_id
             result['product_uos_qty'] = um_obj._compute_qty(cr, uid, product_uom, product_qty, to_uom_id=product_obj.uom_id.id)
        else:
             result['product_uos_qty'] = product_qty
             
             
        #uos_coeff = product_obj.read(cr, uid, product_id, ['uos_coeff'])

        #if product_uos and product_uom and (product_uom != product_uos):
        #    result['product_uos_qty'] = product_qty * uos_coeff['uos_coeff']
        #else:
        #    result['product_uos_qty'] = product_qty

        return {'value': result}
    
    
    
    def onchange_product_id(self, cr, uid, ids, prod_id=False, loc_id=False,
                            loc_dest_id=False, address_id=False):
        """ On change of product id, if finds UoM, UoS, quantity and UoS quantity.
        @param prod_id: Changed Product id
        @param loc_id: Source location id
        @param loc_id: Destination location id
        @param address_id: Address id of partner
        @return: Dictionary of values
        """
        if not prod_id:
            return {}
        lang = False
        if address_id:
            addr_rec = self.pool.get('res.partner.address').browse(cr, uid, address_id)
            if addr_rec:
                lang = addr_rec.partner_id and addr_rec.partner_id.lang or False
                
        ctx = {'lang': lang}
        product = self.pool.get('product.product').browse(cr, uid, [prod_id], context=ctx)[0]
        uom_id = False
        if addr_rec.partner_id.id:
            for riga in product.seller_ids:
                if addr_rec.partner_id.id == riga.name.id:
                    uom_id = riga.product_uom.id
        if uom_id:
            pass
        else:
            uom_id = product.uom_id.id
        uos_id  = product.uos_id and product.uos_id.id or False
        result = {
            'product_uom': uom_id,
            'product_uos': uos_id,
            'product_qty': 1.00,
            'product_uos_qty' : self.pool.get('stock.move').onchange_quantity(cr, uid, ids, prod_id, 1.00, product.uom_id.id, uos_id)['value']['product_uos_qty']
        }
        if not ids:
            result['name'] = product.partner_ref
        if loc_id:
            result['location_id'] = loc_id
        if loc_dest_id:
            result['location_dest_id'] = loc_dest_id
        return {'value': result}    

stock_move()

