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

class hr_vacaciones(osv.osv):

    def _calculate_empleados(self, cr, uid, ids, name, args, context):
        if not ids: return {}
        res = {}
        for record in self.browse(cr, uid, ids, context=context):
            cr.execute("SELECT count(*) as empleados FROM hr_utilidades_lines WHERE utilidades_id=%s group by utilidades_id" % (record.id))
            res[record.id] = float(0)
            for r in cr.fetchall():
                if r[0]:
                    res[record.id] = float(r[0])        
        return res 
    
    def _calculate_utilidades(self, cr, uid, ids, name, args, context):
        if not ids: return {}
        res = {}
        for record in self.browse(cr, uid, ids, context=context):
            cr.execute("SELECT sum(total_vacaciones-total_anticipos) as utilidad_cobrada FROM hr_vacaciones_lines WHERE vacaciones_id=%s group by vacaciones_id" % (record.id))
            res[record.id] = float(0)
            for r in cr.fetchall():
                if r[0]:
                    res[record.id] = float(r[0])        
        return res
    
    def _calculate_sso(self, cr, uid, ids, name, args, context):
        if not ids: return {}
        res = {}
        for record in self.browse(cr, uid, ids, context=context):
            cr.execute("SELECT sum(retencion_sso) as utilidad_cobrada FROM hr_vacaciones_lines WHERE vacaciones_id=%s group by vacaciones_id" % (record.id))
            res[record.id] = float(0)
            for r in cr.fetchall():
                if r[0]:
                    res[record.id] = float(r[0])        
        return res        
   
    def _calculate_faov(self, cr, uid, ids, name, args, context):
        if not ids: return {}
        res = {}
        for record in self.browse(cr, uid, ids, context=context):
            cr.execute("SELECT sum(retencion_faov) as utilidad_cobrada FROM hr_vacaciones_lines WHERE vacaciones_id=%s group by vacaciones_id" % (record.id))
            res[record.id] = float(0)
            for r in cr.fetchall():
                if r[0]:
                    res[record.id] = float(r[0])        
        return res    
    
    def _calculate_islr(self, cr, uid, ids, name, args, context):
        if not ids: return {}
        res = {}
        for record in self.browse(cr, uid, ids, context=context):
            cr.execute("SELECT sum(retencion_islr) as utilidad_cobrada FROM hr_utilidades_lines WHERE utilidades_id=%s group by utilidades_id" % (record.id))
            res[record.id] = float(0)
            for r in cr.fetchall():
                if r[0]:
                    res[record.id] = float(r[0])       
        return res          
        
    _name = 'hr.vacaciones'
    _description = "Calculo de Vacaciones"
    
    _columns = {
        'name': fields.char('Name', size=64, required=True, readonly=True, states={'draft': [('readonly', False)]}),
        'line_ids': fields.one2many('hr.vacaciones.lines', 'vacaciones_id', 'Lineas', required=False, readonly=True, states={'draft': [('readonly', False)]}),
        'state': fields.selection([
            ('draft', 'Draft'),
            ('close', 'Close'),
        ], 'Status', select=True, readonly=True),
        'date_start': fields.date('Date From', required=True, readonly=True, states={'draft': [('readonly', False)]}),
        'date_end': fields.date('Date To', required=True, readonly=True, states={'draft': [('readonly', False)]}),
        'days_holiday':fields.float('Dias de Vacaciones Colectivas'),
        'holiday_status_id': fields.many2one("hr.holidays.status", "Leave Type", required=True),
        'fecha_reintegro': fields.date('Fecha Reintegro', required=True, readonly=True, states={'draft': [('readonly', False)]}),
        'total_empleados':fields.function(_calculate_empleados, method=True, type='float', string='Empleados'),
        'total_vacaciones':fields.function(_calculate_utilidades, method=True, type='float', string='Total Vacaciones'),
        'total_islr':fields.function(_calculate_islr, method=True, type='float', string='Total I.S.L.R.'),
        'total_faov':fields.function(_calculate_faov, method=True, type='float', string='Total FAOV'),
        'total_sso':fields.function(_calculate_sso, method=True, type='float', string='Total S.S.O./P.I.E.'),
        'observaciones': fields.text('Observaciones', readonly=False, states={'draft':[('readonly',False)]}),
    }
    _defaults = {
        'state': 'draft',
        'date_start': lambda *a: time.strftime('%Y-%m-01'),
        'date_end': lambda *a: str(datetime.now() + relativedelta.relativedelta(months=+1, day=1, days=-1))[:10],
        'days_holiday': 15,
    }
    def draft_utilidades(self, cr, uid, ids, context=None):
        return self.write(cr, uid, ids, {'state': 'draft'}, context=context)

    def close_utilidades(self, cr, uid, ids, context=None):
        return self.write(cr, uid, ids, {'state': 'close'}, context=context)       

    def unlink(self, cr, uid, ids, context=None):
        for rec in self.browse(cr, uid, ids, context=context):
            if rec.state != 'draft':
                raise osv.except_osv(_('Warning!'),_('You can only delete draft expenses!'))
        return super(hr_utilidades, self).unlink(cr, uid, ids, context)    
   
    
class hr_vacaciones_lines(osv.osv):
    
    def _calculate_total(self, cr, uid, ids, name, args, context):
        if not ids: return {}
        res = {}
        for line in self.browse(cr, uid, ids, context=context):
            res[line.id] = (float(line.monto_disfrute) + float(line.monto_bono) + float(line.monto_adicionales) + float(line.monto_desyfer)) - (float(line.monto_disfrute_pagado) + float(line.monto_bono_pagado)) - float(line.retencion_faov) - float(line.retencion_islr) - float(line.retencion_sso)
        return res
        
    def _calculate_vacaciones(self, cr, uid, ids, name, args, context):
        if not ids: return {}
        res = {}
        for line in self.browse(cr, uid, ids, context=context):
            res[line.id] = float(line.monto_disfrute) + float(line.monto_bono) + float(line.monto_adicionales) + float(line.monto_desyfer)
        return res        
    
    def _calculate_anticipos(self, cr, uid, ids, name, args, context):
        if not ids: return {}
        res = {}
        for line in self.browse(cr, uid, ids, context=context):
            res[line.id] = float(line.monto_disfrute_pagado) + float(line.monto_bono_pagado) 
        return res    

    def _calculate_fecha_reintegro(self, cr, uid, ids, name, args, context):
        # Funcion para calcular la fecha de salida de vacaciones en vase a la fecha de reintegro. 15 dias de ley - dias disfrutados + dias adicionales
        formato_fecha = "%d/%m/%Y"
        fecha1 = raw_input('Introducir fecha reintegro (dd/mm/aaaa): ')  
        fecha1 = datetime.strptime(fecha1, formato_fecha)
        fecha2 = fecha1
        diferencia = 22
        while (diferencia):  
          fecha2 = fecha2 - timedelta(1)
          if datetime.weekday(fecha2) in [5,6]:    #Falta agregar dias feriados. Para el año 2016 no afecta porque 24,25,31 dic y 1 de ene son fin de semana
            continue
          diferencia = diferencia - 1
        return fecha2    

    def _imagen_employee(self, cr, uid, ids, name, args, context):
        if not ids: return {}
        res = {}
        for line in self.browse(cr, uid, ids, context=context):         
            res[line.id] = line.employee_id.image
        return res   
        
    _name = 'hr.vacaciones.lines'
    _description = "Calculo de vacaciones - Lineas"
    _order = 'employee_code'
    
    _columns = {
                'employee_id': fields.many2one('hr.employee', 'Employee', required=True, readonly=False, states={'draft': [('readonly', False)]}),
                'periodos':fields.float('Meses trabajados'),
                'tiempo_servicio':fields.float('Años de Servicio'),
                'dias_disfrute':fields.float('Dias de Disfrute Vacacional'),
                'dias_bono':fields.float('Dias de Bono Vacacional'),
                'dias_adicionales':fields.float('Dias de Vacaciones por antiguedad'),
                'dias_desyfer':fields.float('Dias de Descanso y Feriados'),
                'monto_disfrute':fields.float('Monto por dias de Disfrute Vacacional'),
                'monto_bono':fields.float('Monto por dias de Bono Vacacional'),
                'monto_adicionales':fields.float('Monto por Dias Vacaciones por antiguedad'),
                'monto_desyfer':fields.float('Monto por Dias Descanso y Feriados'),                    
                'sueldo_1':fields.float('Sueldo 1'),
                'sueldo_2':fields.float('Sueldo 2'),
                'sueldo_3':fields.float('Sueldo 3'),
                'sueldo_promedio':fields.float('Sueldo Promedio'),
                'sueldo_diario':fields.float('Sueldo Diario'),
                'dias_disfrute_pagado':fields.float('Dias de Disfrute Pagado'),
                'monto_disfrute_pagado':fields.float('Monto de Disfrute Pagado'),
                'dias_bono_pagado':fields.float('Dias de Bono Pagado'),
                'monto_bono_pagado':fields.float('Monto de Bono Pagado'),                             
                'tasa_islr':fields.float('% I.S.L.R.'),
                'retencion_islr':fields.float('Retencion I.S.L.R.'),
                'retencion_faov':fields.float('Retencion F.A.O.V.'),
                'retencion_sso':fields.float('Retencion S.S.O.'),
                'total_vacaciones':fields.float('Vacaciones'),
                'total_anticipos':fields.float('Anticipos'),
                'neto_cobrar':fields.function(_calculate_total, method=True, type='float', string='Neto a Cobrar'),
                'observaciones': fields.text('Observaciones', readonly=False, states={'draft':[('readonly',False)]}),
                'vacaciones_id': fields.many2one('hr.vacaciones', 'Vacaciones', readonly=True, ondelete='cascade', states={'draft': [('readonly', False)]}),
                'state': fields.selection([
                        ('draft', 'Draft'),
                        ('close', 'Close'),
                    ], 'Status', select=True, readonly=True),  
                'date_from': fields.date('Date From', required=True, readonly=True, states={'draft': [('readonly', False)]}),
                'date_to': fields.date('Date To', required=True, readonly=True, states={'draft': [('readonly', False)]}),
                'fecha_reintegro': fields.date('fecha de Reintegro', required=True, readonly=True, states={'draft': [('readonly', False)]}),
                'employee_code': fields.char('Codigo', size=64,readonly=True),                                          
                }   
    _defaults = {
        'dias_disfrute':0.00,
        'dias_bono':0.00,
        'dias_adicionales':0.00,
        'dias_desyfer':0.00,
        'monto_disfrute':0.00,
        'monto_bono':0.00,
        'monto_adicionales':0.00,
        'monto_desyfer':0.00,                     
        'dias_disfrute_pagado':0.00,
        'monto_disfrute_pagado':0.00,
        'dias_bono_pagado':0.00,
        'monto_bono_pagado':0.00,        
        'tasa_islr':0.00,
        'retencion_islr':0.00,
        'retencion_faov':0.00,
        'retencion_sso':0.00,
        'neto_cobrar':0.00,
        'tiempo_servicio':0.00,
        'sueldo_1':0.00,
        'sueldo_2':0.00,        
        'sueldo_3':0.00,
        'sueldo_promedio':0.00,
        'sueldo_diario':0.00,
        'periodos':0.0,
                 } 
    
    def onchange_employee_id(self, cr, uid, ids, date_from, date_to, employee_id=False, dias_utilidades=60, context=None):
        empolyee_obj = self.pool.get('hr.employee')
        input_obj = self.pool.get('hr.cuadropres')

        if context is None:
            context = {}
        #defaults
        res = {'value':{
                        'dias_disfrute':0.00,
                        'dias_bono':0.00,
                        'dias_adicionales':0.00,
                        'dias_desyfer':0.00,
                        'monto_disfrute':0.00,
                        'monto_bono':0.00,
                        'monto_adicionales':0.00,
                        'monto_desyfer':0.00,                     
                        'dias_disfrute_pagado':0.00,
                        'monto_disfrute_pagado':0.00,
                        'dias_bono_pagado':0.00,
                        'monto_bono_pagado':0.00,
                        'tasa_islr':0.00,
                        'retencion_islr':0.00,
                        'retencion_faov':0.00,
                        'retencion_sso':0.00,
                        'anticipos':0.00,  
                        'neto_cobrar':0.00,
                        'sueldo_1':0.00,
                        'sueldo_2':0.00,
                        'sueldo_3':0.00,
                        'sueldo_promedio':0.00,
                        'sueldo_diario':0.00,
                        'periodos':0.0,
                        } 
            }
        if (not employee_id) or (not date_from) or (not date_to):
            return res

        v_devengado = 0.00   
        v_periodo = 0        
        cr.execute("SELECT tdmensual as devendago FROM hr_cuadropres WHERE name=%s and meses>='%s' and meses<='%s' " % (employee_id ,date_from,date_to))
        for r in cr.fetchall():
            if r[0]:
                v_devengado = v_devengado + r[0]
                v_periodo = v_periodo + 1                
        sueldo_promerdio = (v_devengado)/v_periodo 
        ultimo_sueldo = emp.sueldo    
        utilidades = ( max(sueldo_promerdio,ultimo_sueldo)/ 30 ) * (dias_utilidades/ 12 * v_periodo)
        retencion_ince = utilidades * .5/100
        retencion_islr = utilidades * emp.tasa_islr/100                  
        res = {
            'employee_id': emp.id,
            'name': slip_data['value'].get('name', False),
            'utilidades_id': context.get('active_id', False),
            'date_from': from_date,
            'date_to': to_date,
            'dias_utilidades': dias_utilidades,
            'tasa_islr': emp.tasa_islr,   
            'tasa_ince': 0.5,
            'periodos': v_periodo,
            'devengado_acumulado':v_devengado,
            'sueldo_promedio':sueldo_promedio,
            'ultimo_sueldo':ultimo_sueldo, 
            'retencion_islr':retencion_islr,
            'retencion_ince':retencion_ince,
            'utilidades':utilidades,            
        }        
        
        ttyme = datetime.fromtimestamp(time.mktime(time.strptime(date_from, "%Y-%m-%d")))
        employee_id = empolyee_obj.browse(cr, uid, employee_id, context=context)
        res['value'].update({
                    'name': _('Salary Slip of %s for %s') % (employee_id.name, tools.ustr(ttyme.strftime('%B-%Y'))),
                    'company_id': employee_id.company_id.id
        })

        #computation of the salary input
        worked_days_line_ids = self.get_worked_day_lines(cr, uid, contract_ids, date_from, date_to, context=context)
        input_line_ids = self.get_inputs(cr, uid, contract_ids, date_from, date_to, context=context)
        res['value'].update({
                    'worked_days_line_ids': worked_days_line_ids,
                    'input_line_ids': input_line_ids,
        })
        return res    
    
    def compute_sheet(self, cr, uid, ids, context=None):
        #slip_line_pool = self.pool.get('hr.utilidades.line')
        return True     
              
