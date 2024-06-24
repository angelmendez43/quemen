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
    'version': '1.01',

    'depends': ['stock','base','point_of_sale','hr_payroll','mrp','sale_stock','l10n_mx_edi_stock', 'pos_coupon','l10n_mx_edi','l10n_mx_edi_40','delivery'],

    'data': [
        'data/paperformat_ticket.xml',
        'data/planificacion_productos_vencidos.xml',
        'data/cfdi.xml',
        # 'security/ir.model.access.csv',
        # 'views/mrp_production_views.xml',
        'data/ir_sequence_data.xml',
        'views/stock_production_lot_views.xml',
        'views/report_deliveryslip_t.xml',
        'views/reporte_ingreso_inventario_pt.xml',
        'views/reporte_codigo_barras_lote.xml',
        'views/reporte_corte_caja_carta.xml',
        'views/reporte_corte_caja_ticket.xml',
        'views/report.xml',
        'views/vale_retiro.xml',
        'views/reporte_planeacion.xml',
        'views/reporte_explosion_insumos.xml',
        'views/reporte_explosion_insumos_costo.xml',
        'views/mrp_bom_views.xml',
        'views/pos_order_view.xml',
        # 'views/templates.xml',
        'views/reporte_codigo_barras.xml',
        'views/reporte_salidas.xml',
        'wizard/reporte_codigo_barras_lote_wizard.xml',
        # 'views/pos_box.xml',
        'views/reporte_entrega_valores.xml',
        'data/quemen_data.xml',
        'views/quemen_views.xml',
        # 'views/stock_quant_views.xml',
        'views/pos_session_view.xml',
        'views/pos_config_view.xml',
        'wizard/reporte_entrega_valores_wizard.xml',
        # 'views/reloj_checador_wizard.xml',
        # 'views/hr_views.xml',
        # 'views/res_users_view.xml',
        'views/reporte_productos_labor_venta.xml',
        'wizard/reporte_productos_labor_venta_wizard.xml',
        'views/reporte_existencias.xml',
        'wizard/reporte_existencias_wizard.xml',
        'views/stock_picking_views.xml',
        # 'views/reporte_formato_salidas.xml',
        # 'views/reporte_salidas.xml',
        # 'wizard/reporte_salidas_wizard.xml',
        # 'wizard/reporte_formato_salidas_wizard.xml',
        # 'views/report_quemen.xml',
        # 'views/reportes_retiro_view.xml',
        # 'views/reporte_retiros_sesion.xml',
        'views/recibo_entrega.xml',
        'views/product_template_extra_fields_views.xml'

    ],
    'qweb': [
        # 'static/src/xml/pos.xml',
    ],
    'assets':{
        'point_of_sale.assets': [
            'quemen/static/src/js/models.js',
            'quemen/static/src/js/Screens/ProductScreen/ProductScreen.js',
            'quemen/static/src/js/Screens/PaymentScreen/PaymentScreen.js',
            'quemen/static/src/js/Screens/ProductScreen/ControlButtons/PedidoEspecialButton.js',
            'quemen/static/src/js/Popups/PedidoEspecialPopup.js',
            'quemen/static/src/js/Screens/ReceiptScreen/SpecialOrderReceipt.js',
            'quemen/static/src/js/Popups/ErrorPopup.js',
            'quemen/static/src/js/coupon.js',
            'quemen/static/src/js/Screens/ClientListScreen/ClientDetailsEdit.js',
            # 'quemen/static/src/js/Misc/AbstractReceiptScreen.js',
            'quemen/static/src/xml/Popups/PedidoEspecialPopup.xml',
            'quemen/static/src/xml/pos_ticket_pedido_especial.xml',
            'quemen/static/src/css/pos.css',
        ],
        'web.assets_qweb': [
            'quemen/static/src/xml/**/*',
            'quemen/static/src/xml/Popups/PedidoEspecialPopup.xml',
            'quemen/static/src/xml/pos_ticket_pedido_especial.xml',
            'quemen/static/src/xml/Screens/ReceiptScreen/SpecialOrderReceipt.xml',
            'quemen/static/src/xml/Screens/ClientListScreen/ClientDetailsEdit.xml',
        ],
        'web.assets_backend': [
            'quemen/static/src/css/navbar.scss',
        ],        
        # 'web.assets_qweb':[
        #     'pos_ticket_mx/static/src/xml/**/*',
        # ],
    },
    'license': 'LGPL-3',
}
