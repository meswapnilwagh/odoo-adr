# -*- encoding: utf-8 -*-
###########################################################################
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

{
    "name" : "ADR Updates",
    "version" : "1.0",
    "author" : 'Open Business Solutions, SRL.',
    "depends" : ["hr", "hr_payroll", "account_asset"],
    'complexity': 'easy',
    "description": """
    """,
    "website" : "http://obsdr.com",
    "category" : "Generic Modules/Accounting",
    "init_xml" : [
	],
    "demo_xml" : [
    ],
    "data" : [
        'data/employee_number_seq.xml',
        'data/account_asset_asset_seq.xml',
        'data/asset_asset_seq.xml',
        'report/account_asset_report_view.xml',
		'hr_updates.xml',
        'account_asset_updates_view.xml',
    ],
    "test" : [],
    "auto_install": False,
    "application": False,
    "installable": True,
    'license': 'AGPL-3',
}


