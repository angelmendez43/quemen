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

    'depends': ['stock','base','point_of_sale'],

    'data': [
        'views/report.xml',
        'views/templates.xml',
        'views/reporte_codigo_barras.xml',
        # 'data/quemen_data.xml',
        'views/res_users_view.xml',
        'data/paperformat_ticket.xml',
        'wizard/reporte_productos_labor_venta_wizard.xml',
        'views/reporte_productos_labor_venta.xml',
        'views/reporte_existencias.xml',
        'wizard/reporte_existencias_wizard.xml',
        'views/stock_picking_views.xml',
        'views/reporte_formato_salidas.xml',
        'wizard/reporte_formato_salidas_wizard.xml',
    ],
}
