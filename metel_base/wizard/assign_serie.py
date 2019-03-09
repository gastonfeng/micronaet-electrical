# -*- coding: utf-8 -*-
###############################################################################
#
# ODOO (ex OpenERP) 
# Open Source Management Solution
# Copyright (C) 2001-2015 Micronaet S.r.l. (<http://www.micronaet.it>)
# Developer: Nicola Riolini @thebrush (<https://it.linkedin.com/in/thebrush>)
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. 
# See the GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.
#
###############################################################################
import os
import sys
import logging
import openerp
import openerp.addons.decimal_precision as dp
from openerp.osv import fields, osv, expression, orm
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from openerp import SUPERUSER_ID
from openerp import tools
from openerp.tools.translate import _

_logger = logging.getLogger(__name__)


class MetelAssignSerieWizard(orm.TransientModel):
    ''' Wizard for assign serie to product.category
    ''' 
    _name = 'metel.assign.serie.wizard'

    # -------------------------------------------------------------------------        
    # Wizard button event:
    # -------------------------------------------------------------------------        
    def action_done(self,  ids, context=None):
        ''' Event for button done
        '''        
        category_pool = self.pool.get('product.category')
        product_pool = self.pool.get('product.product')

        if context is None: 
            context = {}    
        active_ids = context.get('active_ids', [])
        
        wiz_browse = self.browse( ids, context=context)[0]
        serie_id = wiz_browse.serie_id.id
        
        # Update statistic category:
        category_pool.write( active_ids, {
            'metel_serie_id': serie_id,
            }, context=context)
        
        # Update product with that statistic category:
        product_ids = product_pool.search( [
            ('metel_statistic_id', 'in', active_ids),
            ], context=context)
        _logger.info('Update also %s product' % len(product_ids))    
        return product_pool.write( product_ids, {
            'metel_serie_id': serie_id,
            }, context=context)
            
            
    # -------------------------------------------------------------------------        
    # Default functions:
    # -------------------------------------------------------------------------        
    def _get_default_total(self,  context=None):
        ''' Check correct parameters in selected items
        '''
        brand_id = False        

        category_pool = self.pool.get('product.category')
        if context is None: 
            context = {}
        active_ids = context.get('active_ids', [])
        
        if active_ids:
            return len(active_ids)
        else:            
            _logger.warning(
                _('No selected statistic group selected!'))
            return 0            

    def _get_default_brand_id(self,  context=None):
        ''' Check correct parameters in selected items
        '''
        brand_id = False        

        category_pool = self.pool.get('product.category')
        if context is None: 
            context = {}
        active_ids = context.get('active_ids', [])
        
        if not active_ids:
            _logger.warning(
                _('No selected statistic group selected!'))
            return False
        
        # Loop on all statistic category:
        for category in category_pool.browse(
                 active_ids, context=context):
            if category.metel_mode != 'statistic':
                raise osv.except_osv(
                    _('Wrong selection'), 
                    _('Selection is not all statistic category!'),
                    )
                
            if brand_id == False:
                brand_id = category.parent_id
                continue

            if category.parent_id != brand_id:
                raise osv.except_osv(
                    _('Wrong selection'), 
                    _('Selection is not in the same BRAND!'),
                    )                    
        return brand_id
            
    _columns = {
        'serie_id': fields.many2one(
            'product.category', 'Serie', required=True),
        'brand_id': fields.many2one('product.category', 'Brand'),    
        'total': fields.integer('Total'),
        }
        
    _defaults = {
        'brand_id': lambda s,  c: s._get_default_brand_id(
             context=c),
        'total': lambda s,  c: s._get_default_total(
             context=c),
        }    

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
