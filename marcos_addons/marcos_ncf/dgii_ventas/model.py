# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2013-2015 Marcos Organizador de Negocios SRL http://marcos.do
#    Write by Eneldo Serrata (eneldo@marcos.do)
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
from openerp.osv import osv, fields
import base64
from openerp.tools.translate import _
import time

class sale_report(osv.Model):
    """
    607 Purchase of Goods and Services report header.

    """

    _name = 'marcos.dgii.sale.report'
    _description = 'Reporte de Ventas - 607'
    _inherit = ['mail.thread']

    def _line_count(self, cr, uid, ids, context=None):
        sale_report_obj = self.pool.get('marcos.dgii.sale.report')
        sale_report = sale_report_obj.browse(cr, uid, ids, context=context)[0]
        return len(sale_report.sale_report_line_ids)

    def _sum_amount(self, cr, uid, ids, field, context=None):
        sale_report_obj = self.pool.get('marcos.dgii.sale.report')
        sale_report = sale_report_obj.browse(cr, uid, ids, context=context)[0]
        res = 0
        for line in sale_report.sale_report_line_ids:
            res = res + line[field]
        return res

    def _get_updated_fields(self, cr, uid, ids, context=None):
        vals = {}
        vals['line_count'] = self._line_count(cr, uid, ids, context=context)
        vals['billed_amount_total'] = self._sum_amount(cr, uid, ids, u'MONTO_FACTURADO', context=context)
        vals['billed_tax_total'] = self._sum_amount(cr, uid, ids, u'ITBIS_FACTURADO', context=context)
        return vals

    _columns = {
        'period_id': fields.many2one('account.period', u'Período', required=True),
        'company_id': fields.many2one('res.company', u'Compañia', required=True),
        'line_count': fields.integer(u"Total de registros", readonly=True),
        'billed_amount_total': fields.float(u'Total Facturado', readonly=True),
        'billed_tax_total': fields.float(u'Total ITBIS Facturado', readonly=True),
        'report': fields.binary(u"Reporte", readonly=True),
        'report_name': fields.char(u"Nombre de Reporte", 40, readonly=True),
        'sale_report_line_ids': fields.one2many('marcos.dgii.sale.report.line', 'sale_report_id', u'Ventas'),
        }

    _defaults = {
        'company_id': lambda self, cr, uid, c: self.pool.get('res.users').browse(cr, uid, uid, c).company_id.id,
        }

    def create(self, cr, uid, values, context=None):
        """
        Re-write to create sales and to update read-only fields.

        """

        res = super(sale_report, self).create(cr, uid, values, context=context)

        # Loads all sales
        self.create_sales(cr, uid, res, values['period_id'], context=context)

        # Update readonly fields
        vals = self._get_updated_fields(cr, uid, [res], context=None)
        self.write(cr, uid, [res], vals)
        return res

    def write(self, cr, uid, ids, vals, context=None):
        """
        Re-write to update read-only fields.

        """

        super(sale_report, self).write(cr, uid, ids, vals, context)
        vals.update(self._get_updated_fields(cr, uid, ids, context=None))

        result = super(sale_report, self).write(cr, uid, ids, vals, context)
        return result

    def re_create_sales(self, cr, uid, ids, context=None):
        lines_obj = self.pool.get('marcos.dgii.sale.report.line')
        report = self.browse(cr, uid, ids[0])
        line_ids = [line.id for line in report.sale_report_line_ids]
        lines_obj.unlink(cr, uid, line_ids)

        result = self.create_sales(cr, uid, report.id, report.period_id.id, context=context)

        vals = self._get_updated_fields(cr, uid, ids, context=None)
        self.write(cr, uid, ids, vals)

        return result

    def create_sales(self, cr, uid, sale_report_id, period_id, context=None):
        tax_line_obj = self.pool.get('account.invoice.tax')
        tax_obj = self.pool.get('account.tax')
        invoice_obj = self.pool.get('account.invoice')
        cur_obj = self.pool.get('res.currency')
        sale_report_line_obj = self.pool.get('marcos.dgii.sale.report.line')

        draft_sale_inv_ids = invoice_obj.search(cr, uid, [("state", "not in", ["open", "paid", "cancel"]), ("period_id", "=", period_id), ("type", "in", ["out_invoice", "out_refund"])])
        if draft_sale_inv_ids:
            raise osv.except_osv(_(u'Ventas o Notas de Débito en Borrador!'), _(u"Asegúrese que todas sus ventas y notas de débitos este validadas."))

        sale_inv_ids = invoice_obj.search(cr, uid, [("state", "in", ["open", "paid"]), ("period_id", "=", period_id), ("type", "in", ["out_invoice", "out_refund"])])


        line = 1
        for inv_id in sale_inv_ids:
            invoice = invoice_obj.browse(cr, uid, inv_id)

            payment_date = None
            if invoice.payment_ids and not invoice.residual:  # Invoice must be completly payed
                payment_date = invoice.payment_ids[0].date.replace("-", "")
            
            if not invoice.partner_id.ref:
                ref_type = 3
            elif len(invoice.partner_id.ref) == 9:
                ref_type = 1
            elif len(invoice.partner_id.ref) == 11:
                ref_type = 2
            
            tax_line_ids = tax_line_obj.search(cr, uid, [("invoice_id", "=", invoice.id)])

            company_currency = self.pool['res.company'].browse(cr, uid, invoice.company_id.id).currency_id.id
            MONTO_FACTURADO = cur_obj.compute(cr, uid, invoice.currency_id.id, company_currency, invoice.amount_untaxed, context={'date': invoice.date_invoice or time.strftime('%Y-%m-%d')}, round=False)
            ITBIS_FACTURADO = cur_obj.compute(cr, uid, invoice.currency_id.id, company_currency, invoice.amount_tax, context={'date': invoice.date_invoice or time.strftime('%Y-%m-%d')}, round=False)

            values = {
                u'RNC_CEDULA': invoice.partner_id.ref,
                u'TIPO_DE_IDENTIFICACION': ref_type,
                u'NUMERO_COMPROBANTE_FISCAL': invoice.internal_number,
                u'NUMERO_DE_COMPROBANTE_MODIFICADO': invoice.parent_id.internal_number,
                u'FECHA_COMPROBANTE': invoice.date_invoice.replace(u"-", u""),
                u'ITBIS_FACTURADO': abs(ITBIS_FACTURADO),
                u'MONTO_FACTURADO': abs(MONTO_FACTURADO),
                u"line": line,
                u'sale_report_id': sale_report_id
                }
            line += 1
            sale_report_line_obj.create(cr, uid, values, context=context)
        self.action_generate_607(cr, uid, sale_report_id, context=context)
        return True

    def action_generate_607(self, cr, uid, ids, context=None):
        path = '/tmp/607.txt'
        f = open(path,'w')

        # Report Header
        header_obj = self.pool.get('marcos.dgii.sale.report')
        header = header_obj.browse(cr, uid, ids, context=context)
        document_header = header.company_id.vat.replace('-', '').rjust(11)
        period_month = header.period_id.name[:2]
        period_year = header.period_id.name[-4:]
        period = period_year + period_month
        count = str(header.line_count).zfill(12)
        total = ('%.2f' % header.billed_amount_total).zfill(16)
        header_str = '607' + document_header + period + count + total
        f.write(header_str + '\n')

        # Report Detail Lines
        for line in header.sale_report_line_ids:
            document = ''.rjust(11) if not line.RNC_CEDULA else line.RNC_CEDULA.replace('-', '').rjust(11)
            doc_type = str(line.TIPO_DE_IDENTIFICACION)
            ncf = line.NUMERO_COMPROBANTE_FISCAL.rjust(19)
            ref_ncf = line.NUMERO_DE_COMPROBANTE_MODIFICADO.rjust(19) if line.NUMERO_DE_COMPROBANTE_MODIFICADO else u''.rjust(19)  # when line is created manually it returns false instead of u''
            sale_date = line.FECHA_COMPROBANTE
            ITBIS_FACTURADO = ('%.2f' % line.ITBIS_FACTURADO).zfill(12)
            MONTO_FACTURADO = ('%.2f' % line.MONTO_FACTURADO).zfill(12)
            line_str = document + doc_type + ncf + ref_ncf + sale_date + ITBIS_FACTURADO + MONTO_FACTURADO
            f.write(line_str+ '\n')

        f.close()

        f = open(path,'rb')
        report = base64.b64encode(f.read())
        f.close()
        report_name = 'DGII_F_607_' + document_header + '_' + period_year + period_month + '.TXT'
        self.write(cr, uid, [ids], {'report': report, 'report_name': report_name})
        return True


class sale_report_line(osv.Model):
    """
    607 Purchase of Goods and Services report lines.

    """

    _name = 'marcos.dgii.sale.report.line'
    _sord = "line"


    _columns = {
        u"line": fields.integer(u"Linea"),
        u'RNC_CEDULA': fields.char(u"RNC/Cédula", 11, required=False),
        u'TIPO_DE_IDENTIFICACION': fields.selection([(1, u'RNC'), (2, u'Cédula'),(3,u'Solo consumidores finales (RNC en blanco)')], size=1, string=u"Tipo de Documento", required=True),
        u'NUMERO_COMPROBANTE_FISCAL': fields.char(u'NCF', 19, required=True),
        u'NUMERO_DE_COMPROBANTE_MODIFICADO': fields.char(u"Afecta", 19, required=False),
        u'FECHA_COMPROBANTE': fields.char(u"Fecha", 8),
        u'ITBIS_FACTURADO': fields.float(u'Itbis Facturado'),
        u'MONTO_FACTURADO': fields.float(u'Facturado'),
        u'sale_report_id': fields.many2one('marcos.dgii.sale.report', u"Reporte de Ventas", required=True, ondelete="cascade")
        }

