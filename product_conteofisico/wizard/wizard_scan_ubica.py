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

import pooler
import wizard


_form = '''<?xml version="1.0"?>
    <form string="Add product :">
        <field name="ubicacion"/>
        <newline/>
        <field name="cantidad"/>
    </form>
    '''

_fields = {
    'ubicacion': {
        'string': 'Ubicacion',
        'type': 'many2one',
        'relation': 'cf.ubicacion.move',
        'required': True,
        'default': False
    },

    'cantidad': {
        'string': 'Cantidad',
        'type': 'integer',
        'required': True,
        'default': 1},
}


def _add(self, cr, uid, data, context):
    pool = pooler.get_pool(cr.dbname)
    conteo_obj = pool.get('cf.conteo.move')
    id_ubica = data['form']['ubicacion']
    id_cant =  data['form']['cantidad']  
    conteo_seek = pool.get('cf.conteo.move').search(cr, uid, [('ubica_id', '=', id_ubica )])
    conteo_obj.write(cr, uid,conteo_seek, {'conteo_1': id_cant})
    return {}


def _pre_init(self, cr, uid, data, context):
    return {'ubicacion': False, 'cantidad': 1}


class add_conteo1(wizard.interface):

    states = {
        'init': {
            'actions': [_pre_init],
            'result': {
                'type': 'form',
                'arch': _form,
                'fields': _fields,
                'state': [('end', 'Cancel'), ('add', 'Conteo No. 1', 'gtk-ok', True)
                ]
            }
        },
        'add': {
            'actions': [_add],
            'result': {
                'type': 'state',
                'state': 'init',
            }
        },
    }

add_conteo1('cf_conteo1')
