# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
#    Copyright (C) 2011 Serpent Consulting Services (<http://serpentcs.com>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
#                   "wizard/wizard_conteo_uno_view.xml",
#                   "wizard/wizard_conteo_dos_view.xml",
#                   "conteofisico_wizard.xml",
{
    "name" : "conteo fisico",
    "version" : "2.0",
    "author" : "dsasoftwre.com.ve",
    "description": """
    Toma fisica de existencia de productos.
    Implementado para labici, c.a.
    """,
    'website': 'http://www.dsasoftware.com.ve',
    'depends': ["base","product","jasper_reports"],
    'init_xml': [],
    'update_xml': [
                   "wizard/wizard_conteo_uno_view.xml",
                   "wizard/wizard_conteo_dos_view.xml",      
                   "wizard/wizard_generar_txt_view.xml",                                
                   "conteofisico_view.xml",
                   "conteofisico_wizard.xml",                                     
    ],
    'demo_xml': [],
    'installable': True,
    'active': False,
}
