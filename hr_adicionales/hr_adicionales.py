#!/usr/bin/python
# -*- encoding: utf-8 -*-
###########################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#    Copyright (C) labicica.cin.ve/dsasoftware.com.ve.
#    All Rights Reserved
###############Credits######################################################
#    Coded by: DSA Software Sistemas de Gestion, C.A.
#    Planified by: Jonathan J. Guacarán Rivero
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
from openerp.osv import fields, osv

class hr_employee(osv.osv):
    
    _inherit = 'hr.employee' 
    #Do not touch _name it must be same as _inherit
    
    _columns = {
                'fechaingreso' : fields.date("Fecha de Ingreso")           
                 }   
    
    