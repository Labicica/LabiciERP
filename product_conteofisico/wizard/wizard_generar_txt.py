# -*- encoding: utf-8 -*-
##############################################################################
#
#    HHRR Module
#    Copyright (C) 2009 GnuThink Software  All Rights Reserved
#    info@gnuthink.com
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
#import StringIO
import cStringIO

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

class wizard_generate_txt(osv.osv_memory):
    _name ='cf.generar.txt'
    _description = 'Generar archivo TXT para exportar los conteos realizados'    
    
    def crear_txt(self, cr, uid, ids, context=None):
        this = self.browse(cr, uid, ids)[0]
        conteo_obj = pooler.get_pool(cr.dbname).get('cf.conteo.move')
        res = conteo_obj.search(cr, uid, [('conteo_1','>', -1),('conteo_2','=', -1)])
        #buf = open(file_name, 'w')    
        #buf = StringIO.StringIO()  
        buf = cStringIO.StringIO()           
        #if res:
        #    for conteo_id in res:
        #      rol =  conteo_obj.browse(cr, uid, conteo_id)
        #      cadena = ""     
        #      ced = rol.product_id.default_code
        #      cant = str(rol.conteo_1)
        #      t_cta = rol.ubica_id.name
        #      cadena = ced + "," + cant + "," + t_cta+  '\n'
        #      print cadena
        #      buf.write(cadena)
        res = conteo_obj.search(cr, uid, [('conteo_1','>', -1),('conteo_2','>',-1),('conteo_3','=',-1)])
        file_name = "%s%s.CSV" % ("OERP", '_CF')   
        if res:
            for conteo_id in res:
              rol =  conteo_obj.browse(cr, uid, conteo_id)
              cadena = ""     
              ced = rol.product_id.default_code
              cant = str(rol.conteo_1)
              t_cta = rol.ubica_id.name
              cadena = ced + "," + cant + "," + t_cta+  '\n'
              buf.write(cadena)       
        res = conteo_obj.search(cr, uid, [('conteo_3','>', -1),('conteo_2','>',-1),('conteo_1','>',-1)])
        if res:
            for conteo_id in res:
              rol =  conteo_obj.browse(cr, uid, conteo_id)
              cadena = ""     
              ced = rol.product_id.default_code
              cant = str(rol.conteo_3)
              t_cta = rol.ubica_id.name
              cadena = ced + "," + cant + "," + t_cta+  '\n'
              buf.write(cadena)                             
        out = base64.encodestring(buf.getvalue())      
        buf.close()
        self.write(cr,uid,ids,{
            'data' : out,
            'filename': file_name
        })          
        print "nombre del archivo %s" % file_name
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'cf.generar.txt',
            'view_mode': 'form',
            'view_type': 'form',
            'res_id': this.id,
            'views': [(False, 'form')],
            'target': 'new',
        }

    _columns = {
        'es_ok': fields.boolean('¿Generar TXT para actualizar conteo fisico MixNet?'),        
        'filename': fields.char('Nombre TXT', size=32),
        'data': fields.binary('Archivo TXT')
    }
    _default = {
        'es_ok': True,
                }

wizard_generate_txt()


