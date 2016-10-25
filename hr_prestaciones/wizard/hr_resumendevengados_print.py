#!/usr/bin/python
# -*- encoding: utf-8 -*-
###############################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#    Copyright (C) OpenERP Venezuela (<http://www.vauxoo.com>).
#    All Rights Reserved
############# Credits #########################################################
#    Coded by: Katherine Zaoral <kathy@vauxoo.com>
#    Planified by: Humberto Arocha <hbto@vauxoo.com>
#    Audited by: Humberto Arocha <hbto@vauxoo.com>
###############################################################################
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
###############################################################################
import time
from datetime import datetime
from dateutil import relativedelta

from openerp.osv import osv, fields
from openerp.tools.translate import _


class hr_resumendevengados_printwizard(osv.osv_memory):

    """
    This wizard will print the islr reports for a given partner.
    """

    _name = 'hr.resumendevengados.print'
     
    _columns = {
        "date_start": fields.date("Start Date", required=True),
        "date_end": fields.date("End Date", required=True),
        'employee_id' : fields.many2one('hr.employee', 'Empleado'),
        'meses' : fields.date("Meses"),            
        'rbasica' : fields.float('Remuneracion Basica'),
        'oasignaciones' : fields.float('Otras Asignaciones'),
        'tdmensual' : fields.float('Total Devengado Mensual'),
        'tdd' : fields.float('Total Devengado Diario'),
        'spromedio' : fields.float('Sueldo Promedio', help="Promedio calculado con los ultimos 12 meses laborados"),
        'dbvacaciones' : fields.float('Dias Bono Vacaciones'),
        'abvacaciones' : fields.float('Alicuota Bono Vaciones'),
        'dutilidades' : fields.float('Dias Utilidades'),
        'autilidades' : fields.float('Alicuota Utilidades'),
        'sdintegral' : fields.float('Salario Diario integral'),
        'ddgarantias' : fields.integer("Dias de Garantias"),
        'dagarantias' : fields.integer("Dias Adicionales de Garantias"),
        'dgprestaciones' : fields.float('Deposito de las Garantias de Las Prestaciones S.'),
        'apsociales' : fields.float("Anticipos Prestaciones Sociales"),
        'dgpacumuladas' : fields.float('Deposito de la Garantia de las Prestaciones Acumuladas'),   
    }

    _defaults = {
        'date_start': lambda *a: time.strftime('%Y-%m-%d'),
        'date_end': lambda *a: time.strftime('%Y-%m-%d'),
        #~ 'type': lambda *a: 'sale',
    }

    def print_report(self, cr, uid, ids, context=None):
        """
        @return an action that will print a report.
        """
        this = self.browse(cr, uid, ids)[0]
        context = context or {}
        slip_pool = self.pool.get('hr.resumendevengados.print')
        data  = {}
        slip_ids = []
        from_date = this.date_start
        to_date = this.date_end
        print 'la fecha',to_date
        #cr.execute("SELECT a.name FROM hr_cuadropres a INNER JOIN hr_employee b ON (a.name=b.id) WHERE a.meses>='%s' and a.meses<='%s' and a.ddgarantias=15 ORDER BY b.name" % (from_date,to_date))
        cr.execute("SELECT a.id FROM hr_employee a INNER JOIN hr_cuadropres b ON (b.name=a.id) WHERE b.meses>='%s' and b.meses<='%s' ORDER BY a.passport_id " % (from_date,to_date))
        res = cr.fetchall()
        if res:
            print res
            oAnt = 0
            for r in res:
                idemp = r[0]
                if oAnt <> idemp:
                    oAnt = idemp
                    sql = '''SELECT name, meses FROM hr_cuadropres 
                    WHERE name=%s and meses>='%s' and meses<='%s' ORDER BY meses desc ''' % (idemp ,from_date, to_date)
                    cr.execute(sql)
                    garantias = cr.fetchall()
                    for emp in garantias:
                        ini_date=emp[1]          
    
                                                  
                    sql = '''SELECT name, meses, rbasica, oasignaciones, tdmensual, tdd,  
                    dbvacaciones, abvacaciones, dutilidades,autilidades,sdintegral,ddgarantias,dagarantias,dgprestaciones,
                    apsociales, dgpacumuladas FROM hr_cuadropres 
                    WHERE name=%s and meses>='%s' and meses<='%s' ORDER BY meses''' % (idemp ,from_date, to_date)
                    #cr.execute("SELECT name,meses,rbasica,oasignaciones,tdmensual,tdd,spromedio,dbvacaciones,abvacaciones,autilidades,sdintegral FROM hr_cuadropres WHERE name=%s and meses<='%s' ORDER BY meses desc LIMIT 12" % (idemp ,to_date))
                    cr.execute(sql)
                    garantias = cr.fetchall()
                    for emp in garantias:
                        print emp[0], emp[1]
                        reg = {
                            'date_start': from_date,
                            'date_end': to_date,  
                            'employee_id': emp[0],
                            'meses': emp[1],
                            'rbasica': emp[2],
                            'oasignaciones': emp[3],
                            'tdmensual': emp[4],
                            'tdd': emp[5],
                            'spromedio': emp[4]/30,   
                            'dbvacaciones': emp[6],
                            'abvacaciones': emp[7],
                            'dutilidades':emp[8],
                            'autilidades':emp[9],
                            'sdintegral':emp[10], 
                            'ddgarantias':emp[11],
                            'dagarantias':emp[12],
                            'dgprestaciones':emp[13],          
                            'apsociales':emp[14], 
                            'dgpacumuladas':emp[15], 
                        }               
                        slip_ids.append(slip_pool.create(cr, uid, reg, context=context))            
        else:
            raise osv.except_osv(_(u'No se encontro informacion'),
                                 _(u'No se encontro informacion'))                       
        data = dict()
        data['ids'] = slip_ids
        
        return {
            'type': 'ir.actions.report.xml',
            'report_name': 'hr.cuadropres.resumendevengado', 'datas': data}
