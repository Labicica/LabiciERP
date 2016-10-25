#!/usr/bin/python
# -*- encoding: utf-8 -*-
###########################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#    Copyright (C) OpenERP Venezuela (<http://openerp.com.ve>).
#    All Rights Reserved
###############Credits######################################################
#    Coded by: Vauxoo C.A.
#    Planified by: Nhomar Hernandez
#    Audited by: Vauxoo C.A.
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
#from datetime import datetime
from datetime import date

class hr_cuadropres(osv.osv):
    
    def _devengado_total_fnc(self, cr, uid, ids, name, unknow_none, context=None):
        res = {}
        for record in self.browse(cr, uid, ids, context=context):
            res[record.id] = record.rbasica + record.oasignaciones
        return res

    def _devengado_diario_fnc(self, cr, uid, ids, name, unknow_none, context=None):
        res = {}
        for record in self.browse(cr, uid, ids, context=context):
            res[record.id] = record.tdmensual/30 
        return res
    
    def _alicuota_bono_vacacional_fnc(self, cr, uid, ids, name, unknow_none, context=None):
        res = {}
        for record in self.browse(cr, uid, ids, context=context):
            res[record.id] = ( record.dbvacaciones / 360 ) + 1
        return res    
    
    def _alicuota_utilidad_fnc(self, cr, uid, ids, name, unknow_none, context=None):
        res = {}
        for record in self.browse(cr, uid, ids, context=context):
            res[record.id] = ( record.dutilidades / 360 ) + 1
        return res 
    
    def _salario_diario_integral_fnc(self, cr, uid, ids, name, unknow_none, context=None):
        res = {}
        for record in self.browse(cr, uid, ids, context=context):
            res[record.id] = ( ( ( (record.rbasica + record.oasignaciones)/30) * (( record.dutilidades / 360 ) + 1)) * (( record.dbvacaciones / 360 ) + 1) )
        return res            
    
    def _deposito_garantia_fnc(self, cr, uid, ids, name, unknow_none, context=None):
        res = {}
        for record in self.browse(cr, uid, ids, context=context):
            res[record.id] = ( record.sdintegral * ( record.ddgarantias + record.dagarantias ) )
        return res
    
    def _deposito_garantia_acumulado_fnc(self, cr, uid, ids, name, unknow_none, context=None):
        res = {}
        for record in self.browse(cr, uid, ids, context=context):
            rSIntegral = ( ( ( (record.rbasica + record.oasignaciones)/30) * (( record.dutilidades / 360 ) + 1)) * (( record.dbvacaciones / 360 ) + 1) )
            rDepGar = ( rSIntegral * ( record.ddgarantias + record.dagarantias ) )
            res[record.id] = ( rDepGar - record.apsociales )
        return res    
        
    def _interes_mensual_devengado_fnc(self, cr, uid, ids, name, unknow_none, context=None):
        res = {}
        for record in self.browse(cr, uid, ids, context=context):
            res[record.id] = ( record.dgpacumuladas * ((record.tiprestaciones/100) / 12) )
        return res 
    
    def _promedio_mensual_fnc(self, cr, uid, ids, name, unknow_none, context=None):
        res = {}
        for record in self.browse(cr, uid, ids, context=context):
            v_devengado = 0.00   
            v_periodo = 0     
            res[record.id] = 0.00 
            if record.name.id:
                cr.execute("SELECT tdmensual as devendago FROM hr_cuadropres WHERE name=%s and meses<='%s' ORDER BY meses desc LIMIT 12" % (record.name.id ,record.meses))
                for r in cr.fetchall():
                    if r[0]:
                        v_devengado = v_devengado + r[0]
                        v_periodo = v_periodo + 1  
                    if v_periodo:
                        res[record.id] = float(v_devengado/v_periodo)
                    else:
                        res[record.id] = 0            
        return res     
           
    _name = 'hr.cuadropres'
    _description = "Cuadro de Prestaciones Sociales"
    
    _columns = {
                'name' : fields.many2one('hr.employee', 'Empleado'),
                'meses' : fields.date("Meses"),            
                'rbasica' : fields.float('Remuneracion Basica'),
                'oasignaciones' : fields.float('Otras Asignaciones'),
                'tdmensual' : fields.float('Total Devengado Mensual', readonly=True),
                'tdd' : fields.float('Total Devengado Diario', readonly=True),
                'spromedio' : fields.function(_promedio_mensual_fnc, method=True, type='float', string='Sueldo Promedio', help="Promedio calculado con los ultimos 12 meses laborados"),
                'dbvacaciones' : fields.float('Dias Bono Vacaciones'),
                'abvacaciones' : fields.float('Alicuota Bono Vaciones', readonly=True),
                'dutilidades' : fields.float('Dias Utilidades'),
                'autilidades' : fields.float('Alicuota Utilidades', readonly=True),
                'sdintegral' : fields.float('Salario Diario integral', readonly=True),
                'ddgarantias' : fields.integer("Dias de Garantias"),
                'dagarantias' : fields.integer("Dias Adicionales de Garantias"),
                'dgprestaciones' : fields.float('Deposito de las Garantias de Las Prestaciones S.', readonly=True),
                'apsociales' : fields.float("Anticipos Prestaciones Sociales"),
                'dgpacumuladas' : fields.float('Deposito de la Garantia de las Prestaciones Acumuladas', readonly=True),
                'tiprestaciones' : fields.float('Tasa de intereses Prestaciones Sociales'),
                'islr' : fields.float('% ISLR'),
                'imdevengado' : fields.float('Interes Mensual Devengado', readonly=True),
                'iadevengado' : fields.float('Interes Acumulado Devengado', readonly=True),             
                'es_acumulado': fields.boolean('Usar promedio 6 meses? '),
                'state': fields.selection([('draft', 'Getting Ready'),
                    ('open', 'Approved by Manager'), ('done', 'Seniat Submitted')],
                    string='Status', required=True), 
                'iapagados' : fields.float('Intereses Pagados'),    
                'activo': fields.related('name', 'active', type='boolean', relation='hr.employee', readonly=True, store=True, string='Estatus'),                              
                'foto': fields.related('name', 'image_medium', type='binary', relation='hr.employee', readonly=True, store=True, string='Foto'),
                 }   
    _defaults = {
        'state': 'draft',
        'es_acumulado': False,
        'dutilidades': 120,
        'dbvacaciones':21,
        'meses': date.today().strftime('%Y-%m-%d'),
    }
    _order  =  "meses desc"
    
    #def _compute_age(self, cr, uid, ids, field_name, field_value, context=None):
    #    records = self.browse(cr, uid, ids, context=context)
    #    result={}
    #    for r in records:
    #        age=0
    #        if r.date_birth:
    #            d = strptime(r.date_birth,"%Y-%m-%d")
    #            count = date(d[0],d[1],d[2])-date.today()
    #            age = count.days/365
    #            result[r.id] = age
    #    return result    
    
    def recalculo(self, cr, uid, ids, context=None):
        res = {}
        cr.execute("SELECT id,name,meses,rbasica,oasignaciones FROM hr_cuadropres WHERE 1=1")
        for r in cr.fetchall():
            print r[1],r[2]
            id_rec = r[0]
            res = {'name':r[1],
                   'meses':r[2],
                   'rbasica':r[3],
                   'oasignaciones':r[4],
                   }
            self.write(cr, uid, [id_rec], res, context=context)
        return res      

    def actualizar_sueldo(self, cr, uid, ids, context=None):
        res = {}
        for record in self.browse(cr, uid, ids, context=context):
            cr.execute("UPDATE hr_employee SET sueldo=%s WHERE id=%s" % (record.rbasica,record.name.id))
            print record.rbasica,record.id
        return res                  
      
    def onchange_meses(self, cr, uid, ids, meses_id, employee_id, context=None):
        res = {}
        
        if meses_id:
            cr.execute("SELECT tasa1 FROM hr_tasas WHERE name<='%s' ORDER BY name desc limit 1" % meses_id)
            res['tiprestaciones'] = cr.fetchone()[0]
        
        return {'value': res}     

    def write(self, cr, uid, ids, vals, context=None):
        if context is None:
            context = {}
        result = super(hr_cuadropres,self).write(cr, uid, ids, vals, context=context)    
      
        res = {}
        for record in self.browse(cr, uid, ids, context=context):
            if record.name: 
                cr.execute("SELECT tasa1 FROM hr_tasas WHERE name<='%s' ORDER BY name desc limit 1" %  record.meses)
                vals['tiprestaciones'] = cr.fetchone()[0]    
                v_emp_id = record.name.id
                empleado = self.pool.get('hr.employee').browse(cr, uid, record.name.id, context=context)
                #print 'Empleado: ',empleado.name
                v_acumula = 0.00
                cr.execute("SELECT sum(dgprestaciones) as devengado, sum(apsociales) as anticipo FROM hr_cuadropres WHERE name=%s and meses<'%s' GROUP BY name ORDER BY name desc" % (v_emp_id ,record.meses))
                for r in cr.fetchall():
                    if r[0]:
                        v_acumula = v_acumula + r[0]
                    if r[1]:               
                        v_acumula = v_acumula - r[1] 
    
                v_intacum = 0.00                
                cr.execute("SELECT sum(imdevengado) as iganado, sum(iapagados) as ipagado FROM hr_cuadropres WHERE name=%s and meses<'%s' GROUP BY name ORDER BY name desc" % (v_emp_id ,record.meses))
                for r in cr.fetchall():
                    if r[0]:
                        v_intacum = v_intacum + r[0]
                    if r[1]:
                        v_intacum = v_intacum - r[1] 
                                  
                vals['tdmensual'] = record.rbasica + record.oasignaciones          
                vals['tdd'] = ( record.rbasica + record.oasignaciones) / 30
                if record.es_acumulado:
                    v_devengado = 0.00   
                    v_periodo = 1        
                    cr.execute("SELECT tdmensual as devendago FROM hr_cuadropres WHERE name=%s and meses<'%s' ORDER BY meses desc LIMIT 5" % (v_emp_id ,record.meses))
                    for r in cr.fetchall():
                        if r[0]:
                            v_devengado = v_devengado + r[0]
                            v_periodo = v_periodo + 1                
                    vals['tdd'] = (v_devengado + record.rbasica + record.oasignaciones)/v_periodo /30
                    
                vals['abvacaciones'] = ( record.dbvacaciones / 360 ) + 1
                vals['autilidades'] = ( record.dutilidades / 360 ) + 1
                vals['sdintegral'] = vals['tdd'] * vals['abvacaciones']  * vals['autilidades']
                vals['dgprestaciones'] = vals['sdintegral'] * (record.ddgarantias + record.dagarantias)
                vals['dgpacumuladas'] = v_acumula + vals['dgprestaciones'] - record.apsociales
                v_tiprestaciones = float( ( vals['tiprestaciones'] /100) /12)
                vals['imdevengado'] = vals['dgpacumuladas'] * v_tiprestaciones
                vals['iadevengado'] = v_intacum + vals['imdevengado']
    
                result = super(hr_cuadropres,self).write(cr, uid, ids, vals, context=context)
        return result              