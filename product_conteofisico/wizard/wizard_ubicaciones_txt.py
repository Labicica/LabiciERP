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

import wizard
import base64
import StringIO
import pooler
from time import strftime
from string import upper
from string import join


pay_form = """<?xml version="1.0"?>
<form string="Ubicaciones de Conteo Fisico">
    <separator string="Generacion de TXT para actualizar ubicaciones de conteo fisico MixNet" colspan="4"/>
    <field name="respuesta"/>
</form>
"""

pay_fields = {
    'respuesta' : {'string' : 'Respuesta', 'type' : 'string' , 'required' : False},
    }

view_form_finish="""<?xml version="1.0"?>
<form string="Exportar TXT">
    <image name="gtk-dialog-info" colspan="2"/>
    <group colspan="2" col="4">
        <separator string="Archivo Generado" colspan="4"/>
        <field name="data" readonly="1" colspan="3"/>
        <separator  string="Guardar este Documento como TXT\nConfirmar la info !" colspan="4"/>
    </group>
</form>"""

fields_form_finish={
    'data': {'string':'Archivo', 'type':'binary', 'readonly': True,},
    'name': {'string':'Nombre', 'type':'string', 'readonly': True,},
}

class wizard_ubicaciones_txt(wizard.interface):
    
    def crear_txt(self, cr, uid, data, context):
        buf = StringIO.StringIO()
        conteo_obj = pooler.get_pool(cr.dbname).get('cf.conteo.move')
        res = conteo_obj.search(cr, uid, [('conteo_1','>', -1),('conteo_2','=', -1)])
        if res:
            for conteo_id in res:
              rol =  conteo_obj.browse(cr, uid, conteo_id)
              cadena = ""     
              ced = rol.product_id.default_code
              cant = str(rol.conteo_1)
              t_cta = rol.ubica_id.name
              #nombre = str(rol.employee_id.name.encode('UTF-8'))
              #cadena = t_cta +"," +ced + "," + cant +  '\n'
              cadena = ced + "," + cant +  '\n'
              buf.write(upper(cadena))
        res = conteo_obj.search(cr, uid, [('conteo_1','>', -1),('conteo_2','=','conteo_1')])
        if res:
            for conteo_id in res:
              rol =  conteo_obj.browse(cr, uid, conteo_id)
              cadena = ""     
              ced = rol.product_id.default_code
              cant = str(rol.conteo_1)
              t_cta = rol.ubica_id.name
              #nombre = str(rol.employee_id.name.encode('UTF-8'))
              #cadena = t_cta +"," +ced + "," + cant +  '\n'
              cadena = ced + "," + cant +  '\n'
              buf.write(upper(cadena))        
        res = conteo_obj.search(cr, uid, [('conteo_3','>', -1),('conteo_2','<>','conteo_1')])
        if res:
            for conteo_id in res:
              rol =  conteo_obj.browse(cr, uid, conteo_id)
              cadena = ""     
              ced = rol.product_id.default_code
              cant = str(rol.conteo_3)
              t_cta = rol.ubica_id.name
              #nombre = str(rol.employee_id.name.encode('UTF-8'))
              #cadena = t_cta +"," +ced + "," + cant +  '\n'
              cadena = ced + "," + cant +  '\n'
              buf.write(upper(cadena))                             
        out = base64.encodestring(buf.getvalue())
        buf.close()
        name = "%s%s.CSV" % ("OERP", '_UBI')
        print "nombre del archivo %s" % name
        return {'data': out, 'name': name}

    states = {
           'init': {
                'actions': [],
                'result': {'type': 'form',
                           'arch': pay_form,
                           'fields': pay_fields,
                           'state' : [('end', 'Cancelar', 'gtk-cancel', True),('generate', 'Generar TXT')]}
                },
           'generate': {
                'actions': [crear_txt],
                'result': { 'type': 'form',
                            'arch': view_form_finish,
                            'fields' : fields_form_finish,
                            'state': [
                            ('end', 'Cerrar', 'gtk-cancel', True)
                        ]
                }
          },
    }
wizard_ubicaciones_txt('cf_generate_txt')
