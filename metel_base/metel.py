# -*- coding: utf-8 -*-
###############################################################################
#
#    Copyright (C) 2001-2014 Micronaet SRL (<http://www.micronaet.it>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published
#    by the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
###############################################################################
import os
import sys
import logging
import openerp
import openerp.netsvc as netsvc
import openerp.addons.decimal_precision as dp
from openerp.osv import fields, osv, expression, orm
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from openerp import SUPERUSER_ID, api
from openerp import tools
from openerp.tools.translate import _
from openerp.tools.float_utils import float_round as round
from openerp.tools import (DEFAULT_SERVER_DATE_FORMAT, 
    DEFAULT_SERVER_DATETIME_FORMAT, 
    DATETIME_FORMATS_MAP, 
    float_compare)


_logger = logging.getLogger(__name__)

class MetelMetel(orm.Model):
    """ Model name: MetelMetel
    """
    
    _name = 'metel.parameter'
    _description = 'Metel parameter'
    _order = 'company_id'
    
    # -------------------------------------------------------------------------
    # Utility for manage METEL file:
    # -------------------------------------------------------------------------
    def parse_text(self, text, logger=None):
        ''' Clean text
            logger: logger list for collect error during import     
        '''
        if logger is None:
            logger = []
        try:    
            return text.strip()
        except:
            logger.append('Error converting text %s' % text)
            return '?'

    def parse_text_boolean(self, text, logger=None):
        ''' Clean text
            logger: logger list for collect error during import     
        '''
        if logger is None:
            logger = []
        try:    
            return text.strip() == '1'
        except:
            logger.append('Error converting text boolean %s' % text)
            return False

    def parse_text_number(self, text, decimal=0, logger=None):
        ''' Parse text value for float number according with METEL template           
            In METEL numbers has NN.DD format 
            ex.: 10.2 = total char 10, last 2 is decimal so:
                 NNNNNNNNDD  >> 0000001234 means 12.34
            decimal = DD number, ex.: 10.2 >> 2 is decimal
                if decimal = 0 return interger
            logger: logger list for collect error during import     
        '''
        if logger is None:
            logger = []
            
        try:
            if decimal:
                return float('%s.%s' % (
                    text[:-decimal],
                    text[-decimal:],
                    ))            
            else: 
                return int(text)        
        except:
            logger.append('Error converting float %s (decimal: %s)' % (
                text, decimal))
            return 0.0 # nothing
        
    def parse_text_date(self, text, mode='YYYYMMDD', logger=None):
        ''' Parse text value for date value according with METEL template           
            METEL format YYYYMMDD (Iso without char)
            logger: logger list for collect error during import             
        '''
        if logger is None:
            logger = []

        if not text:
            return False
            
        if mode == 'YYYYMMDD':
            return '%s-%s-%s' % (
                text[:4],
                text[4:6],
                text[6:8],
                )
        #else: # XXX no way always mode is present!
        return False

    def load_parse_text_currency(self, cr, uid, context=None):
        ''' Parse text value for currency ID according with METEL code
        '''
        res = {}
        currency_pool = self.pool.get('res.currency')
        currency_ids = currency_pool.search(cr, uid, [], context=context)
        for currency in currency_pool.browse(cr, uid, currency_ids,
                context=context):
            res[currency.name] = currency.id
        return res

    #def parse_text_country(self, value):
    #    ''' Parse text value for country ID according with METEL template           
    #    '''
    #    return value

    #def parse_text_uom(self, value):
    #    ''' Parse text value for uom ID according with METEL template           
    #    '''
    #    PCE Pezzi
    #    BLI Blister
    #    BRD Cartoni
    #    KGM Chilogrammi
    #    LE Litri
    #    LM Metri lineari
    #    PL Pallet
    #    return value
        
    _columns = {
        'company_id': fields.many2one(
            'res.company', 'Company', required=True),            
        }

    _sql_constraints = [('company_id_uniq', 'unique (company_id)', 
        'Parameter for that company already present!')]

class ProductUom(orm.Model):
    """ Model name: ProductUom
    """    
    _inherit = 'product.uom'
    
    _columns = {
        'metel_code': fields.char('Metel code', size=18),
        }

#class ResPartner(orm.Model):
#    """ Model name: Res Partner
#    """    
#    _inherit = 'res.partner'
#    
#    _columns = {
#        'metel_code': fields.char('Metel code', size=18),
#        }

class ProductCategory(orm.Model):
    """ Model name: Product cagegory:   
        Create structure: METEL / Producer / Brand
    """
    _inherit = 'product.category'

    # -------------------------------------------------------------------------
    # Utility:
    # -------------------------------------------------------------------------
    def get_create_metel_group(self, cr, uid, code, name=False, 
            parent_id=False, context=None):
        ''' Get (or create if not present) producer "code" and "name"
        '''
        group_ids = self.search(cr, uid, [
            ('parent_id', '=', parent_id),
            ('metel_code', '=', code),
            ], context=context)
        if group_ids:
            if len(group_ids) > 1:
                _logger.error('Code present more than one! [%s]' % code)
            return group_ids[0]
        else:
            return self.create(cr, uid, {
                'parent_id': parent_id,
                'metel_code': code,
                'metel_name': name or code or '',
                }, context=context)
    
    # Producer group ID:
    def get_create_producer_group(self, cr, uid, 
            producer_code, producer_name=False, context=None):
        '''
        '''    
        # Parent root:
        metel_id = self.get_create_metel_group(cr, uid, 
            'METEL', context=context)

        # Producer:
        return self.get_create_metel_group(cr, uid, 
            producer_code, producer_name, metel_id, context=context)

    # Brand group ID:
    def get_create_brand_group(self, cr, uid, 
            producer_code, # must exist!
            brand_code, brand_name,
            context=None):
        ''' Get (or create if not present) producer "code" and "name"
        '''
        # Producer (parent):
        producer_id = self.get_create_producer_group(cr, uid, 
            producer_code, context=context)

        # Brand:
        return self.get_create_metel_group(cr, uid, 
            brand_code, brand_name, producer_id, context=context)
        
    _columns = {
        'metel_code': fields.char('Metel code', size=18, 
            help='Metel code: producer of brand'),
        'metel_description': fields.char('Metel description', size=40, 
            help='Metel name: producer or brand'),
        'metel_partner_id': fields.many2one(
            'res.partner', 'Metel Partner', 
            help='If group is a producer element'),
        }

class ProductProduct(orm.Model):
    """ Model name: Product Product
    """    
    _inherit = 'product.product'
    
    _columns = {
        #'metel_code': fields.char('Metel code', size=18),
        'is_metel': fields.boolean('Is Metel'),
        'metel_producer_id': fields.many2one(
            'product.category', 'Metel producer'),
        'metel_brand_id': fields.many2one(
            'product.category', 'Metel brand'),
        'metel_list_price': fields.float('Metel pricelist', 
            digits_compute=dp.get_precision('Product Price')),
            
        'metel_brand_code': fields.char('Brand code', size=10),    
        'metel_producer_code': fields.char('Producer code', size=10),
        'metel_state': fields.selection([
            ('1', 'New product'),
            ('2', 'Finished or to be cancel'),
            ('3', 'Managed with stock'),
            ('4', 'New service'),
            ('5', 'Cancelled service'),
            ('6', 'Produced with order'),
            ('7', 'Produced with order to be cancelled'),
            ('8', 'Service (no material)'),
            ('9', 'Cancel product'),
            ], 'Metel State', help='Status product in METEL'),
        }
        
    _defaults = {
        # Default value:
        'metel_state': lambda *x: '1',
        }    
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
