{
    'name': "Dominican Payroll Localization",
    'author': "Open Business Solutions",
    'category': 'Accounting',
    'version': '1.0.3',
    'description': """
        Localization of the requerimients from the Dominican Republic
        authorities regarding payroll structures for all national and international
        companies based in the country.""",
    'depends': ['hr',
                'hr_payroll'],
    'data': ['hr_employee_view.xml',
             'res_bank_view.xml',
             'hr_payslip_batch_sequence.xml',
             'hr_payslip_run_view.xml',
             'res_partner_bank_view.xml'],
    'installabe': True
}
