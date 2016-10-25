# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
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

import time
from datetime import datetime
from dateutil import relativedelta

from openerp.osv import fields, osv
from openerp.tools.translate import _

class hr_utilidades_employees(osv.osv_memory):

    _name ='hr.utilidades.employees'
    #_description = 'Generate payslips for all selected employees'
    _description = 'Generar utilidades para todos los empleados seleccionados'
    _columns = {
        'employee_ids': fields.many2many('hr.employee', 'hr_employee_group_rel', 'utilidades_id', 'employee_id', 'Employees'),
    }
    
    def compute_sheet(self, cr, uid, ids, context=None):
        emp_pool = self.pool.get('hr.employee')
        slip_pool = self.pool.get('hr.utilidades.lines')
        run_pool = self.pool.get('hr.utilidades')
        slip_ids = []
        if context is None:
            context = {}
        data = self.read(cr, uid, ids, context=context)[0]
        run_data = {}
        if context and context.get('active_id', False):
            run_data = run_pool.read(cr, uid, context['active_id'], ['date_start', 'date_end', 'dias_utilidades','meses_estimados'])
        from_date =  run_data.get('date_start', False)
        to_date = run_data.get('date_end', False)
        dias_utilidades = run_data.get('dias_utilidades', False)    
        meses_estimados = run_data.get('meses_estimados', False)        
        if not data['employee_ids']:
            raise osv.except_osv(_("Warning!"), _("You must select employee(s) to generate payslip(s)."))
        for emp in emp_pool.browse(cr, uid, data['employee_ids'], context=context):
            #slip_data = slip_pool.onchange_employee_id(cr, uid, [], from_date, to_date, emp.id, context=context)
            v_devengado = 0.00   
            #cr.execute("SELECT tdmensual as devendago FROM hr_cuadropres WHERE name=%s and meses>='%s' and meses<='%s' " % (emp.id ,from_date,to_date))
            cr.execute("SELECT tdmensual as devendago FROM hr_cuadropres WHERE name=%s and meses<='%s' ORDER BY meses desc LIMIT 12" % (emp.id ,to_date))
            v_sueldo_promedio = 0
            v_periodo = 0            
            for r in cr.fetchall():
                if r[0]:
                    v_devengado = v_devengado + r[0]
                    v_periodo = v_periodo + 1  
                    v_sueldo_promedio = float( (v_devengado)/v_periodo)
                    print 'Sueldo Promedio:',v_sueldo_promedio,'Periodos:',v_periodo
            cr.execute("SELECT tdmensual as devendago FROM hr_cuadropres WHERE name=%s and meses>='%s' and meses<='%s' ORDER BY meses desc LIMIT 12" % (emp.id, from_date ,to_date))
            v_periodo = 0            
            for r in cr.fetchall():
                if r[0]:
                    v_periodo = v_periodo + 1  
            print 'Periodos para calculo:',v_periodo                    
            cr.execute("SELECT tdmensual as devendago FROM hr_cuadropres WHERE name=%s and meses>='%s' and meses<='%s' " % (emp.id ,from_date,to_date))     
            la_fecha = emp.fechaingreso
            if la_fecha > from_date:
                v_periodo = 0  
                #la_fecha = from_date
                formato_fecha = "%Y-%m-%d"                
                diferencia = datetime.strptime(to_date,formato_fecha) - datetime.strptime(la_fecha,formato_fecha)   
                for r in cr.fetchall():
                    if r[0]:
                        v_periodo = v_periodo + 1        
                v_periodo = round(float(diferencia.days/30), 0)                           
                print 'Dias Trabajados: ',diferencia.days   
                print 'Periodos S/30: ',v_periodo                        
            cr.execute("SELECT (utilidades-anticipos) as utilidad_cobrada FROM hr_utilidades_lines WHERE employee_id=%s and date_from>='%s' and date_to<'%s' " % (emp.id ,from_date,to_date))                    
            print 'Periodos: ',v_periodo
            v_anticipos = 0.00  
            for r in cr.fetchall():
                if r[0]:
                    v_anticipos = v_anticipos + r[0]
                    print 'Anticipos:',v_anticipos    
            if emp.meses_reposo: 
                v_periodo = v_periodo - emp.meses_reposo
            if meses_estimados:
                v_periodo = v_periodo + meses_estimados             
            v_ultimo_sueldo = emp.sueldo  
            v_tasa_ince = 0.5
            v_utilidades = ( max(v_sueldo_promedio,v_ultimo_sueldo)/ 30 ) * (dias_utilidades/ 12 * v_periodo)
            v_retencion_ince = float((v_utilidades-v_anticipos) * v_tasa_ince/100)
            v_retencion_islr = float((v_utilidades-v_anticipos) * emp.tasa_islr/100)      
            v_retencion_faov = float((v_utilidades-v_anticipos) * 1/100) 
            #                'name': slip_data['value'].get('name', False),            
            res = {
                'employee_id': emp.id,
                'employee_code': emp.passport_id,
                'utilidades_id': context.get('active_id', False),
                'date_from': from_date,
                'date_to': to_date,
                'dias_utilidades': dias_utilidades,
                'tasa_islr': emp.tasa_islr,   
                'tasa_ince': v_tasa_ince,
                'periodos': v_periodo,
                'devengado_acumulado':v_devengado,
                'sueldo_promedio':v_sueldo_promedio,
                'ultimo_sueldo':v_ultimo_sueldo, 
                'retencion_islr':v_retencion_islr,
                'retencion_ince':v_retencion_ince,
                'utilidades':v_utilidades,          
                'anticipos':v_anticipos,  
                'retencion_faov':v_retencion_faov,
            }
            slip_ids.append(slip_pool.create(cr, uid, res, context=context))
        slip_pool.compute_sheet(cr, uid, slip_ids, context=context)
        return {'type': 'ir.actions.act_window_close'}

hr_utilidades_employees()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
