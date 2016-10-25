# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution    
#    Copyright (C) 2004-2009 Tiny SPRL (<http://tiny.be>). All Rights Reserved
#    $Id$
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

import base64

try:
    import release
    import pooler
    from osv import osv,fields
    from tools.translate import _
except ImportError:
    import openerp
    from openerp import release
    from openerp import pooler
    from openerp.osv import osv,fields
    from openerp.tools.translate import _

class cf_conteo_uno(osv.osv_memory):

    _name ='cf.conteo.uno'
    _description = 'Generar utilidades para todos los empleados seleccionados'
    
    def conteo_add(self, cr, uid, ids, context=None):
        this = self.browse(cr, uid, ids)[0]
        data = self.pool.get('cf.conteo.uno').read(cr, uid, ids)[0]
        conteo_obj = self.pool.get('cf.conteo.move')    
        conteo_seek = conteo_obj.search(cr, uid, [('ubica_id', '=', data['ubicacion'][0] )])       
        conteo_obj.write(cr, uid, conteo_seek, {'conteo_1': data['cantidad']}, context=context)
        
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'cf.conteo.uno',
            'view_mode': 'form',
            'view_type': 'form',
            'res_id': 0,
            'views': [(False, 'form')],
            'target': 'new',
        }
            
    _columns = {
        'ubicacion': fields.many2one('cf.ubicacion.move', 'Ubicacion', required=True),
        'cantidad': fields.integer('Cantidad'),        
    }
    _default = {
        'cantidad': 1,
                }    
        
cf_conteo_uno()
