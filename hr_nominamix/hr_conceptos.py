#!/usr/bin/python
# -*- encoding: utf-8 -*-
###########################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#    Copyright (C) DSA Software Sistemas de Gestion, C.A. (<http://dsasoftware.com.ve>).
#    All Rights Reserved
###############Credits######################################################
#    Coded by: DSA Software Sistemas de Gestion, C.A.
#    Planified by: Jonathan Guacaran
#    Audited by: DSA Software Sistemas de Gestion, C.A.
#############################################################################
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
################################################################################
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

class hr_nmconceptos(osv.osv):

        
        
    _name = 'hr.nmconceptos'
    _description = "Conceptos Nomina Mix"
    
    _columns = {
        'name': fields.char('Codigo', size=3, required=True),
        'titulo': fields.char('Titulo', size=35, required=True),
        'condicion': fields.text('Condicion SI', required=True),
        'formula': fields.text('Formula', required=True),
        'resumen': fields.text('Resumen', required=True),
        'es_salario': fields.boolean('Es Salario? '),  
        'aplica_utilidades': fields.boolean('Aplica para Utilidades? '),
        'aplica_vacaciones': fields.boolean('Aplica para Vacaciones? '),  
        'aplica_prestaciones': fields.boolean('Aplica para Prestaciones? '),
        'tipo': fields.selection([('asignacion', 'Asignacion'),
              ('deduccion', 'Deduccion'), ('historico', 'Historico'), ('otro', 'Otro')],
              string='Tipo', required=True),         
    }

    _defaults = {
        'es_salario': True,
        'aplica_utilidades': True,
        'aplica_vacaciones': True, 
        'aplica_prestaciones': True,                           
    }    
