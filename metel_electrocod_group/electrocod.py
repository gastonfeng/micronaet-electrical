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


class ProductCategory(orm.Model):
    """ Model name: Product cagegory:   
        Create structure: ELECTROCOD
    """
    _inherit = 'product.category'

    # -------------------------------------------------------------------------
    # Utility:
    # -------------------------------------------------------------------------
    def scheduled_electrocod_import_data(self, cr, uid, filename=False, 
            root_name='ELECTROCOD', ec_check=37, context=None):
        ''' Import all electrocod group structure 
            filename: fullname of electrocod csv file            
            root_name: Root group name and code (used as KEY!)
            ec_check: char in file where start code of electrocod
        '''
        # ---------------------------------------------------------------------
        # Get or create root node:
        # ---------------------------------------------------------------------
        group_ids = self.search(cr, uid, [
            ('parent_id', '=', False),
            ('electrocod_code', '=', root_name),
            ], context=context)
        if group_ids:    
            root_id = group_ids[0]        
        else:
            root_id = self.create(cr, uid, {
                'parent_id': False,
                'electrocod_code': root_name,
                'name': root_name,
                }, context=context)

        # ---------------------------------------------------------------------
        # Read all file and save in database:
        # ---------------------------------------------------------------------
        filename = os.path.expanduser(filename)        
        f_code = open(filename, 'r')
        i = 0
        levels = {} # saved with level        
        for line in f_code:
            i += 1
            if line[ec_check + 2: ec_check + 3] != '.': # Dot position
                continue # no data line
            data = line[ec_check:].split('-')
            if len(data) != 2:
                _logger.error('No standard Electrocode line: %s' % line)
                continue
            
            # -----------------------------------------------------------------
            # Manage level:    
            # -----------------------------------------------------------------
            code = data[0].strip()
            name = data[1].strip()            
            code_level = code.split('.')
            level = len(code_level)
            
            # -----------------------------------------------------------------
            # Save record for creation (next loop)
            # -----------------------------------------------------------------
            if level not in levels:
                levels[level] = {}                
            levels[level][code] = name         
        f_code.close()

        nodes = {
            # Master node has no code for search
            root_name: root_id, # Not used only for collect correct key
            '': root_id, # Used with join no level
            }
        for level in sorted(nodes):
            for code, name in nodes[level].iteritems():
                code_part = code.split('.')
                code_parent = '.'.join(code_part[:-1]
                parent_id = nodes.get(code_parent, False)
                if not parent_id:
                    _logger.error('Parent not found: %s' % code_parent)
                    continue
                    
                group_ids = self.search(cr, uid, [
                    ('parent_id', '=', parent_id),
                    ('electrocod_code', '=', code),
                    ], context=context)
                if group_ids:
                    nodes[code] = group_ids[0]      
                else:
                    nodes[code] = self.create(cr, uid, {
                        'parent_id': parent_id,
                        'electrocod_code': code,
                        'name': name,
                        }, context=context)
        return nodes

    _columns = {
        'electrocod_code': fields.char('Electrocod code', size=18, 
            help='Electrocod code'),
        }
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
