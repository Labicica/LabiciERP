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
from datetime import datetime, date, time, timedelta
from dateutil import relativedelta

from openerp.osv import fields, osv
from openerp.tools.translate import _

class hr_vacaciones_employees(osv.osv_memory):

    _name ='hr.vacaciones.employees'
    #_description = 'Generate payslips for all selected employees'
    _description = 'Generar vacaciones para todos los empleados seleccionados'
    _columns = {
        'employee_ids': fields.many2many('hr.employee', 'hr_employee_vacation_rel', 'vacaciones_id', 'employee_id', 'Employees'),
    }
    
    def compute_sheet(self, cr, uid, ids, context=None):
        emp_pool = self.pool.get('hr.employee')
        slip_pool = self.pool.get('hr.vacaciones.lines')
        run_pool = self.pool.get('hr.vacaciones')
        slip_ids = []
        if context is None:
            context = {}
        data = self.read(cr, uid, ids, context=context)[0]
        run_data = {}
        if context and context.get('active_id', False):
            run_data = run_pool.read(cr, uid, context['active_id'], ['date_start', 'date_end', 'days_holiday','fecha_reintegro'])
        from_date =  run_data.get('date_start', False)
        to_date = run_data.get('date_end', False)
        v_days_holiday = run_data.get('days_holiday', False)    
        v_fecha_reintegro = run_data.get('fecha_reintegro', False)
        v_formato_fecha = "%Y-%m-%d"   
        fecha1 = datetime.strptime(v_fecha_reintegro, v_formato_fecha)
        fecha2 = fecha1 - timedelta(1)
        if not data['employee_ids']:
            raise osv.except_osv(_("Warning!"), _("You must select employee(s) to generate payslip(s)."))
        for emp in emp_pool.browse(cr, uid, data['employee_ids'], context=context):
            #slip_data = slip_pool.onchange_employee_id(cr, uid, [], from_date, to_date, emp.id, context=context)
            v_devengado = 0.00   
            #cr.execute("SELECT tdmensual as devendago FROM hr_cuadropres WHERE name=%s and meses>='%s' and meses<='%s' " % (emp.id ,from_date,to_date))
            cr.execute("SELECT tdmensual as devendago FROM hr_cuadropres WHERE name=%s and meses<='%s' ORDER BY meses desc LIMIT 3" % (emp.id ,to_date))
            v_sueldo_promedio = 0
            v_periodo = 0            
            v_sueldo_1 = 0
            v_sueldo_2 = 0
            v_sueldo_3 = 0
            v_pos = 0
            for r in cr.fetchall():
                if r[0]:
                    v_pos = v_pos + 1
                    v_devengado = v_devengado + r[0]
                    v_periodo = v_periodo + 1  
                    v_sueldo_promedio = float( (v_devengado)/v_periodo)
                    if v_pos ==1 :
                        v_sueldo_1 = r[0]
                    if v_pos ==2 :
                        v_sueldo_3 = r[0]
                    if v_pos ==3 :
                        v_sueldo_3 = r[0]
                    print 'Sueldo Promedio:',v_sueldo_promedio,'Periodos:',v_periodo
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
            cr.execute("SELECT (total_vacaciones-total_anticipos) as utilidad_cobrada FROM hr_vacaciones_lines WHERE employee_id=%s and date_from>='%s' and date_to<'%s' " % (emp.id ,from_date,to_date))                    
            print 'Periodos: ',v_periodo
            v_anticipos = 0.00  
            for r in cr.fetchall():
                if r[0]:
                    v_anticipos = v_anticipos + r[0]
                    print 'Anticipos:',v_anticipos    
            if emp.meses_reposo: 
                v_periodo = v_periodo - emp.meses_reposo            
            v_ultimo_sueldo = emp.sueldo
            v_sueldo_diario = v_sueldo_promedio / 30  
            v_tasa_faov = 1
            v_tasa_sso = 4
            v_vacaciones = v_sueldo_diario * v_days_holiday
            v_retencion_faov = float((v_vacaciones-v_anticipos) * v_tasa_faov/100)
            v_retencion_sso = float((v_vacaciones-v_anticipos) * v_tasa_sso/100)
            v_retencion_islr = float((v_vacaciones-v_anticipos) * emp.tasa_islr/100)      
            #                'name': slip_data['value'].get('name', False),            
            res = {
                'employee_id': emp.id,
                'employee_code': emp.passport_id,
                'vacaciones_id': context.get('active_id', False),
                'date_from': from_date,
                'date_to': to_date,
                'fecha_reintegro': v_fecha_reintegro,
                'days_holiday': v_days_holiday,
                'tasa_islr': emp.tasa_islr,   
                'periodos': v_periodo,
                'sueldo_1':v_sueldo_1,
                'sueldo_2':v_sueldo_2,
                'sueldo_3':v_sueldo_3,
                'sueldo_promedio':v_sueldo_promedio,
                'sueldo_promedio':v_sueldo_diario,
                'retencion_islr':v_retencion_islr,
                'retencion_faov':v_retencion_faov,
                'retencion_sso':v_retencion_sso,
                'total_vacaciones':v_vacaciones,          
                'total_anticipos':v_anticipos,  
            }
            slip_ids.append(slip_pool.create(cr, uid, res, context=context))
        slip_pool.compute_sheet(cr, uid, slip_ids, context=context)
        return {'type': 'ir.actions.act_window_close'}

hr_vacaciones_employees()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
