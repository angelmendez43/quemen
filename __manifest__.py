# -*- coding: utf-8 -*-
{
    'name': "Quemen",

    'summary': """ Desarrollo extra quemen """,

    'description': """
        Desarrollo extra pra quemen
    """,

    'author': "JS",
    'website': "",

    'category': 'Uncategorized',
    'version': '0.1',

    'depends': ['stock','base','point_of_sale','hr_payroll'],

    'data': [
        'data/paperformat_ticket.xml',
        'views/report.xml',
        'views/templates.xml',
        'views/reporte_codigo_barras.xml',
        # 'data/quemen_data.xml',
        'views/quemen_views.xml',
        'views/pos_config_view.xml',
        'views/reloj_checador_wizard.xml',
        'views/hr_views.xml',
        'views/res_users_view.xml',
        'wizard/reporte_productos_labor_venta_wizard.xml',
        'views/reporte_productos_labor_venta.xml',
        'views/reporte_existencias.xml',
        'wizard/reporte_existencias_wizard.xml',
        'views/stock_picking_views.xml',
        'views/reporte_formato_salidas.xml',
        'wizard/reporte_formato_salidas_wizard.xml',
    ],
}
