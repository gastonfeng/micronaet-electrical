# -*- coding: utf-8 -*-
##############################################################################
#
#    Author: Francesco Apruzzese <f.apruzzese@apuliasoftware.it>
#    Copyright (C) Francesco Apruzzese
#    Copyright (C) 2014 Agile Business Group (http://www.agilebg.com)
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################


from openerp import _
from openerp import api
from openerp import fields
from openerp import models
from openerp.exceptions import Warning


class DdTFromPickings(models.TransientModel):

    _name = 'ddt.from.pickings'

    def _get_picking_ids(self):
        return self.env['stock.picking'].browse(self.env.context['active_ids'])

    picking_ids = fields.Many2many('stock.picking', default=_get_picking_ids)

    @api.multi
    def create_ddt(self):
        values = {
            'partner_id': False,
            'parcels': 0,
            'carriage_condition_id': False,
            'goods_description_id': False,
            'transportation_reason_id': False,
            'transportation_method_id': False,            
            'payment_term_id': False,
            'used_bank_id': False,
            'default_carrier_id': False,
            'destination_partner_id': False,
            'invoice_partner_id': False,
            #'mx_invoice_id': False, # TODO raise warning!!! remove?
            }
            
        partner = False        
        for picking in self.picking_ids:
            if partner and partner != picking.partner_id:
                raise Warning(
                    _('Selected Pickings have different Partner'))
            partner = picking.partner_id
            values['partner_id'] = partner.id
            
        carriage_condition_id = False
        for picking in self.picking_ids:
            if picking.sale_id and picking.sale_id.carriage_condition_id:
                if carriage_condition_id and (
                        carriage_condition_id != (
                            picking.sale_id.carriage_condition_id)):
                    raise Warning(
                        _('Selected Pickings have'
                          ' different carriage condition'))
                carriage_condition_id = (
                    picking.sale_id.carriage_condition_id)
                values['carriage_condition_id'] = (
                    carriage_condition_id.id)
                    
        goods_description_id = False
        for picking in self.picking_ids:
            if picking.sale_id and picking.sale_id.goods_description_id:
                if goods_description_id and (
                    goods_description_id != (
                        picking.sale_id.goods_description_id)):
                    raise Warning(
                        _('Selected Pickings have '
                          'different goods description'))
                goods_description_id = picking.sale_id.goods_description_id
                values['goods_description_id'] = (
                    goods_description_id.id)
                    
        transportation_reason_id = False
        for picking in self.picking_ids:
            if picking.sale_id and (
                    picking.sale_id.transportation_reason_id):
                if transportation_reason_id and (
                        transportation_reason_id != (
                            picking.sale_id.transportation_reason_id)):
                    raise Warning(
                        _('Selected Pickings have'
                            ' different transportation reason'))
                transportation_reason_id = (
                    picking.sale_id.transportation_reason_id)
                values['transportation_reason_id'] = (
                    transportation_reason_id.id)
                    
        transportation_method_id = False
        for picking in self.picking_ids:
            if picking.sale_id and (
                    picking.sale_id.transportation_method_id):
                if transportation_method_id and (
                    transportation_method_id != (
                        picking.sale_id.transportation_method_id)):
                    raise Warning(
                        _('Selected Pickings have'
                          ' different transportation reason'))
                transportation_method_id = (
                    picking.sale_id.transportation_method_id)
                values['transportation_method_id'] = (
                    transportation_method_id.id)

        # XXX payment_term for sale is used!!!
        payment_term_id = False # XXX Note: save object!!!
        for picking in self.picking_ids:
            if picking.sale_id and picking.sale_id.payment_term:
                if payment_term_id and (
                    payment_term_id != (
                        picking.sale_id.payment_term)):
                    raise Warning(
                        _('Selected Pickings have'
                          ' different payment terms'))
                payment_term_id = picking.sale_id.payment_term
                values['payment_term_id'] = payment_term_id.id

        used_bank_id = False
        for picking in self.picking_ids:
            if picking.sale_id and (
                    picking.sale_id.bank_account_id):
                if used_bank_id and (
                    used_bank_id != (
                        picking.sale_id.bank_account_id)):
                    raise Warning(
                        _('Selected Pickings have'
                          ' different bank account'))
                used_bank_id = (
                    picking.sale_id.bank_account_id)
                values['used_bank_id'] = (
                    used_bank_id.id)

        default_carrier_id = False
        for picking in self.picking_ids:
            if picking.sale_id and (
                    picking.sale_id.carrier_id):
                if default_carrier_id and (
                    default_carrier_id != (
                        picking.sale_id.carrier_id)):
                    raise Warning(
                        _('Selected Pickings have'
                          ' different carrier'))
                default_carrier_id = (
                    picking.sale_id.carrier_id)
                values['default_carrier_id'] = (
                    default_carrier_id.id)

        destination_partner_id = False
        for picking in self.picking_ids:
            if picking.sale_id and (
                    picking.sale_id.destination_partner_id):
                if destination_partner_id and (
                    destination_partner_id != (
                        picking.sale_id.destination_partner_id)):
                    raise Warning(
                        _('Selected Pickings have'
                          ' different destination partner'))
                destination_partner_id = (
                    picking.sale_id.destination_partner_id)
                values['destination_partner_id'] = (
                    destination_partner_id.id)
                    
        invoice_partner_id = False
        for picking in self.picking_ids:
            if picking.sale_id and (
                    picking.sale_id.invoice_partner_id):
                if invoice_partner_id and (
                    invoice_partner_id != (
                        picking.sale_id.invoice_partner_id)):
                    raise Warning(
                        _('Selected Pickings have'
                          ' different invoice partner'))
                invoice_partner_id = (
                    picking.sale_id.invoice_partner_id)
                values['invoice_partner_id'] = (
                    invoice_partner_id.id)

        # Agent:
        mx_agent_id = False
        for picking in self.picking_ids:
            if picking.sale_id and (
                    picking.sale_id.mx_agent_id):
                if mx_agent_id and (
                    mx_agent_id != (
                        picking.sale_id.mx_agent_id)):
                    raise Warning(
                        _('Selected Pickings have'
                          ' different invoice agent'))
                mx_agent_id = (
                    picking.sale_id.mx_agent_id)
                values['mx_agent_id'] = (
                    mx_agent_id.id)
        
        # -------------------------------------
        # Add note header in DDT (all lines!!):
        # -------------------------------------
        # check no repeat note:
        note_list_pre = []
        note_list_post = []
        # Add fields:
        values['text_note_pre'] = ''
        values['text_note_post'] = ''

        for picking in self.picking_ids:
            if picking.text_note_pre:
                if picking.text_note_pre not in note_list_pre:
                    values['text_note_pre'] += '%s\n' % picking.text_note_pre
                    note_list_pre.append(picking.text_note_pre)

            if picking.text_note_post:
                if picking.text_note_post not in note_list_post:
                    values['text_note_post'] += '%s\n' % picking.text_note_post
                    note_list_post.append(picking.text_note_post)
                    
        ddt = self.env['stock.ddt'].create(values)
        for picking in self.picking_ids:
            picking.ddt_id = ddt.id
            
        # Show new ddt:
        ir_model_data = self.env['ir.model.data']
        form_res = ir_model_data.get_object_reference(
            'electrical_l10n_it_ddt',
            'stock_ddt_form')
        form_id = form_res and form_res[1] or False
        tree_res = ir_model_data.get_object_reference(
            'elecrtical_l10n_it_ddt',
            'stock_ddt_tree')
        tree_id = tree_res and tree_res[1] or False
        return {
            'name': 'DdT',
            'view_type': 'form',
            'view_mode': 'form,tree',
            'res_model': 'stock.ddt',
            'res_id': ddt.id,
            'view_id': False,
            'views': [(form_id, 'form'), (tree_id, 'tree')],
            'type': 'ir.actions.act_window',
            }
