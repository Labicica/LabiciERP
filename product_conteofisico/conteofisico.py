# -*- encoding: utf-8 -*-
#########################################################################
#                                                                       #
#                                                                       #
#########################################################################
#                                                                       #
# Copyright (C) 2009  Rapha�l Valyi, S�bastien Beau                     #
#                                                                       #
#This program is free software: you can redistribute it and/or modify   #
#it under the terms of the GNU General Public License as published by   #
#the Free Software Foundation, either version 3 of the License, or      #
#(at your option) any later version.                                    #
#                                                                       #
#This program is distributed in the hope that it will be useful,        #
#but WITHOUT ANY WARRANTY; without even the implied warranty of         #
#MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the          #
#GNU General Public License for more details.                           #
#                                                                       #
#You should have received a copy of the GNU General Public License      #
#along with this program.  If not, see <http://www.gnu.org/licenses/>.  #
#########################################################################

import time
from datetime import date
from datetime import datetime
from datetime import timedelta
from dateutil import relativedelta

from openerp import netsvc
from openerp.osv import fields, osv
from openerp import tools
from openerp.tools.translate import _
import openerp.addons.decimal_precision as dp

from openerp.tools.safe_eval import safe_eval as eval

class cf_ubicacion(osv.osv):
    
    def _total_conteos(self, cr, uid, ids, name, args, context=None):
        res = {}
        for credito in self.browse(cr, uid, ids, context):
            res[credito.id] = {
                'suma_1': 0.0,
                'suma_2':0.0
            }
            if credito.conteos_ids:
                for lineas in credito.conteos_ids:
                    if lineas.conteo_1>-1:
                        res[credito.id]['suma_1'] += lineas.conteo_1
                    if lineas.conteo_2>-1:
                        res[credito.id]['suma_2'] += lineas.conteo_2   
        return res     
    
    _name = "cf.ubicacion"
    _description = "Hojas de Ubicaciones Fisicas"
    _order = 'name'
    _columns = {
    'name': fields.char('Descripcion', size=35, select=1),
    'move_ids':fields.one2many('cf.ubicacion.move', 'ubicacion_id', 'Ubicaciones', required=False), 
    'conteos_ids':fields.one2many('cf.conteo.move', 'hojas_id', 'Conteos', required=False), 
    'suma_1':fields.function(_total_conteos, method=True, digits=(16,0), string='Conteo No. 1', multi='all', help="Total Conteo No. 1"),
    'suma_2':fields.function(_total_conteos, method=True, digits=(16,0), string='Conteo No. 2', multi='all', help="Total Conteo No. 2"),
    }
    
class cf_ubicacion_move(osv.osv):
    _name = "cf.ubicacion.move"
    _description = "Codigos de las ubicaciones por cada Hoja"
    _order = 'name'
    _columns = {
        'name':fields.char('Codigo',size=10,select=1,required=True),
        'product_id':fields.many2one('product.product', 'Producto', required=False),
        'ubicacion_id':fields.many2one('cf.ubicacion', 'Ubicacion', required=False), 
                }

class cf_conteos(osv.osv):
    _name = "cf.conteos"
    _description = "Datos del conteo"
    _order = 'name'
    _columns = {
        'name':fields.char('Descripcion', size=35, required=True, select=1),
        'fecha': fields.date('Fecha'),
        'lineas_id':fields.one2many('cf.conteo.move','conteo_id', 'Movimientos', required=False), 
                }
    
    def action_create_data(self, cr, uid, ids, context={}):
        res = {}
        print 'Conteos'
        conteo_obj = self.pool.get('cf.conteo.move')
        ubica_obj = self.pool.get('cf.ubicacion.move')
        ubica_seek = ubica_obj.search(cr, uid, [('id', '<>', 0 )])
        
        for ubica_plst in ubica_obj.browse(cr, uid, ubica_seek, context):
            if ubica_plst.product_id:
                res = { 
                        'conteo_id': ids[0],
                        'ubica_id':ubica_plst.id,
                        'product_id':ubica_plst.product_id.id,
                        'conteo_1':-1,
                        'conteo_2':-1,
                        'conteo_3':-1,
                        'resultado':-1
                        }
                print ids[0],ubica_plst.id,ubica_plst.product_id.id
                conteo_obj.create(cr, uid, res)
               
        return True
    

class cf_conteos_move(osv.osv):
    _name = "cf.conteo.move"
    _description = "Conteos por producto"
    _order = 'ubica_id'
    _columns = {
        'ubica_id': fields.many2one('cf.ubicacion.move', 'Ubicacion', required=True, select="1"),
        'product_id': fields.many2one('product.product', 'Producto', required=True, select="1"),
        'conteo_1': fields.float('Conteo No. 1', digits=(16, 4)),
        'conteo_2': fields.float('Conteo No. 2', digits=(16, 4)), 
        'conteo_3': fields.float('Conteo No. 3', digits=(16, 4)), 
        'resultado': fields.float('Conteo', digits=(16, 4)), 
        'conteo_id': fields.many2one('cf.conteos', 'Conteo', required=False),  
        'hojas_id':fields.many2one('cf.ubicacion', 'Ubicacion', required=False),  
                 }
    _default = {
        'conteo_1': lambda *a: -1,
        'conteo_2': lambda *a: -1,
        'conteo_3': lambda *a: -1,
        'resultado': lambda *a: -1,
                }
    
    def onchange_ubica_id(self, cr, uid, ids, ubica_id, context=None):
        if not ubica_id:
            return {'value':{'product_id':False}}
        manager = self.pool.get('cf.ubicacion.move').browse(cr, uid, ubica_id)
        return {'value': {'product_id':manager.product_id}} 

    def get_name(self, cr, uid, data, context={}):
        res = {'Ubicacion':self.ubica_id,'Producto':self.product_id}
        return res

