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

class MetelBase(orm.Model):
    """ Model name: MetelBase
    """
    
    _inherit = 'metel.parameter'
    
    def schedule_import_pricelist_action(self, cr, uid, context=None):
        ''' Schedule import of pricelist METEL
        '''
        # --------------------------------------------------------------------- 
        # Read parameter
        # --------------------------------------------------------------------- 
        param_ids = self.search(cr, uid, [], context=context)
        param_proxy = self.browse(cr, uid, param_ids, context=context)[0]
        
        # Pool used:
        product_pool = self.pool.get('product.product') 
        
        # 3 folder used:
        data_folder = os.path.expanduser(param_proxy.root_data_folder)
        history_folder = os.path.expanduser(param_proxy.root_history_folder)
        log_folder = os.path.expanduser(param_proxy.root_log_folder)
        
        # --------------------------------------------------------------------- 
        # Import procecedure:
        # --------------------------------------------------------------------- 
        # 1. Loop pricelist folder:
        # TODO os.walk
        logger = [] # List of error
        for root, dirs, files in os.walk(data_folder):
            for name in files:
                fullname = os.path.join(root, name)
                i = 0
                for line in open(fullname, 'r'):
                    i += 1
                    # ---------------------------------------------------------                    
                    # Header:
                    # ---------------------------------------------------------                    
                    if i == 1:
                        # TODO
                        continue
                    
                    # ---------------------------------------------------------                    
                    # Data row:
                    # ---------------------------------------------------------
                    brand_code = line[0:3] # TODO create also category
                    default_code = line[3:19]
                    ean13 = line[19:32]
                    name = line[32:75]
                    #> q_x_pack = line[75:80]
                    #> q_multipla_ordine= line[80:85]
                    #> order_min = self.parse_text_number(line[85:90])
                    #> order_max = self.parse_text_number(line[90:96])
                    #> leadtime = self.parse_text_number(line[96:97])
                    lst_price = self.parse_text_number(
                        line[97:108], 2, logger) # reseller price
                    #> metel_list_price = self.parse_text_number(
                    #    line[108:119], 2, logger) # Public price
                    #> moltiplicatore_prezzo = line[119:125]
                    #> codice_valuta = line[125:128]
                    #uom = line[128:131]
                    #> prodotto_composto = line[131:132]       
                    #> metel_state = line[132:133]
                    #> last_variation = line[133:141]
                    #> discount_family = line[141:159]
                    #> statistic_family = line[159:177]
                    #> electrocod = line[177:197]
                    #> barcode = line[197:232]
                    #> barcode_move = line[232:233]          
                    
                    data = {
                        'default_code': default_code,
                        'metel_brand_code': brand_code,
                        'ean13': ean13,
                        'name': name,
                        'lst_price': lst_price,
                        }
                    
                    # search
                    
                    # IF
                    #     Write
                    #     Create    
                        
                    
            break # only first root folder    
        
        # 2. Import single file (parse, create/write)
        
        # 3. History 
        
        # 4. Log operation
        
        
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
