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
import shutil
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

class MetelBase(orm.Model):
    """ Model name: MetelBase
    """
    
    _inherit = 'metel.parameter'
    
    def schedule_import_pricelist_action(self, cr, uid, verbose=True, 
            context=None):
        ''' Schedule import of pricelist METEL
        '''
        # Pool used:
        product_pool = self.pool.get('product.product') 

        # --------------------------------------------------------------------- 
        # Read parameter
        # --------------------------------------------------------------------- 
        # Database parameters:
        param_ids = self.search(cr, uid, [], context=context)
        param_proxy = self.browse(cr, uid, param_ids, context=context)[0]

        # 3 folder used:
        data_folder = os.path.expanduser(param_proxy.root_data_folder)
        history_folder = os.path.expanduser(param_proxy.root_history_folder)
        log_folder = os.path.expanduser(param_proxy.root_log_folder)

        # Now for name log:
        now = '%s' % datetime.now()
        now = now.replace('-', '_').replace(':', '.').replace('/', '.')

        # Mode list for file:        
        file_mode = [
            'LSP', #Public pricelist
            #'LSG', #Reseller pricelist
            #'FST', #Statistic family
            #'FSC', #Discount family
            #'RIC', #Recode
            #'BAR', #Barcode
            ]
        
        # Currency database:    
        currency_db = self.load_parse_text_currency(cr, uid, context=context)
        uom_db = self.load_parse_text_uom(cr, uid, context=context)
        
        # --------------------------------------------------------------------- 
        # Import procecedure:
        # --------------------------------------------------------------------- 
        # 1. Loop pricelist folder:
        # TODO os.walk
        logger = [] # List of error
        for root, dirs, files in os.walk(data_folder):
            for filename in files:
                # Parse filename:
                file_producer_code = filename[3:6]
                file_brand_code = filename[3:6]
                # TODO version?
                currency = (filename.split('.')[0])[6:]
                
                if file_brand_code not in file_mode:
                    if verbose:
                        _logger.info('Jump METEL file: %s (not in %s)' % (
                            fullname, file_mode,
                            ))
                    continue    
                    
                fullname = os.path.join(root, filename)                
                if verbose:
                    _logger.info('Read METEL file: %s' % fullname)
                i = upd = new = 0
                uom_missed = []
                f_metel = open(fullname, 'r')
                for line in f_metel:
                    i += 1
                    # ---------------------------------------------------------                    
                    # Header:
                    # ---------------------------------------------------------                    
                    if i == 1:
                        if verbose:
                            _logger.info('%s. Read header METEL' % i)
                        # TODO
                        continue
                    
                    # ---------------------------------------------------------                    
                    # Data row:
                    # ---------------------------------------------------------
                    brand_code = self.parse_text(line[0:3], logger) # TODO create also category
                    default_code = self.parse_text(line[3:19], logger)
                    ean13 = self.parse_text(line[19:32], logger)
                    name = self.parse_text(line[32:75], logger)
                    metel_q_x_pack = self.parse_text(line[75:80], logger)
                    metel_order_lot = self.parse_text_number(
                        line[80:85], logger)
                    metel_order_min = self.parse_text_number(line[85:90], logger)
                    metel_order_max = self.parse_text_number(line[90:96], logger)
                    metel_order_leadtime = self.parse_text_number(line[96:97], logger)
                    lst_price = self.parse_text_number(
                        line[97:108], 2, logger) # reseller price
                    metel_list_price = self.parse_text_number(
                        line[108:119], 2, logger) # public price
                    metel_multi_price = self.parse_text_number(
                        line[119:125], logger)
                    currency = self.parse_text(line[125:128], logger)
                    uom = self.parse_text_number(line[128:131], logger)
                    metel_kit = self.parse_text_boolean(line[131:132], logger)     
                    metel_state = self.parse_text(line[132:133], logger)
                    metel_last_variation = self.parse_text_dateline[133:141], 
                        logger=logger)
                    metel_discount = self.parse_text(line[141:159], logger)
                    metel_statistic = self.parse_text(line[159:177], logger)
                    metel_electrocod = self.parse_text(
                        line[177:197], logger)
                    
                    # Alternate value for EAN code:
                    metel_alternate_barcode = self.parse_text(
                        line[197:232], logger)
                    metel_alternate_barcode_type = self.parse_text(
                        line[232:233], logger)
                    
                    # TODO manage multi price value:
                    #if metel_multi_price:
                    #    metel_list_price /= metel_multi_price
                    #    lst_price /= metel_multi_price
                    
                    # TODO use currency    
                    
                    # ---------------------------------------------------------
                    # Create record data:
                    # ---------------------------------------------------------
                    data = {
                        'default_code': default_code,
                        'metel_brand_code': brand_code,
                        'ean13': ean13,
                        'name': name,
                        'lst_price': lst_price,
                        'type': 'product', 
                        'metel_q_x_pack': metel_q_x_pack,
                        'metel_order_lot': metel_order_lot,
                        'metel_order_min': metel_order_min,
                        'metel_order_max': metel_order_max,
                        'metel_order_leadtime': metel_order_leadtime,
                        'metel_multi_price': metel_multi_price,    
                        'metel_list_price': metel_list_price,
                        'metel_kit': metel_kit,
                        'metel_state': metel_state,
                        'metel_last_variation': metel_last_variation,
                        'metel_electrocod': metel_electrocod,
                        'metel_alternate_barcode': 
                            metel_alternate_barcode,
                        'metel_alternate_barcode_type': 
                            metel_alternate_barcode_type,
                        }

                    # Add uom:
                    uom_id = uom_db.get(uom, False)
                    if uom_id:
                        data['uom_id'] = uom_id
                    elif uom not in uom_missed:
                        uom_missed.append(uom)
                    
                    product_ids = product_pool.search(cr, uid, [
                         ('default_code','=', default_code),
                         ('metel_brand_code', '=', brand_code),
                         ], context=context)

                    if product_ids: 
                        product_pool.write(
                            cr, uid, product_ids, data, context=context)
                        if verbose:
                            upd += 1
                            _logger.info('%s. Update %s-%s' % (
                                i, brand_code, default_code))
                    else:        
                        product_pool.create(
                            cr, uid, data, context=context)
                        if verbose:
                            new += 1
                            _logger.info('%s. Create %s-%s' % (
                                i, brand_code, default_code))
                
                f_metel.close()
                
                # -------------------------------------------------------------
                # History log file
                # -------------------------------------------------------------
                if log_folder:
                    log_fullname = os.path.join(
                        log_folder, 
                        '%s.%s' % (now, filename)
                        )
                    shutil.move(fullname, log_fullname)
                    
            break # only first root folder    
            if verbose:
                _logger.info(
                    'File: %s record: %s [UPD %s NEW %s]' % (
                        filename, i, upd, new,
                        ))
                _logger.info('UOM missed [%s]' % (uom_missed, ))
            if uom_missed:
                logger.append(_('Missed UOM code: %s') % uom_missed)
    
        
        # ---------------------------------------------------------------------    
        # Log operation
        # ---------------------------------------------------------------------    
        if logger:
            log_file = os.path.join(log_folder, filename)                
            
        
        
        return True
        
    _columns = {
        'root_data_folder': fields.char('Root folder', size=120, 
            help='~/.filestore/metel'),
        'root_history_folder': fields.char('History folder', size=120,
            help='~/.filestore/metel/history'),
        'root_log_folder': fields.char('Log folder', size=120,
            help='~/.filestore/metel/log (every import create log)'),            
        }
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
