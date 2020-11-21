odoo.define('quemen.screens', function (require) {
"use strict";

var screens = require('point_of_sale.screens');
var models = require('point_of_sale.models');
// var pos_db = require('point_of_sale.DB');
var rpc = require('web.rpc');
// var gui = require('point_of_sale.gui');
// var core = require('web.core');
// var PopupWidget = require('point_of_sale.popups');
// var field_utils = require('web.field_utils');
// var QWeb = core.qweb;
// var _t = core._t;

models.load_fields('pos.config', 'efectivo_maximo');

screens.PaymentScreenWidget.include({
    validate_order: function(force_validation) {
        console.log('VALIDATE QUEMEN')
        var self = this;
        var order = this.pos.get_order();
        var order_pagos = order.get_paymentlines();
        var _super = this._super.bind(this)
        var total_efectivo = 0;
        if (this.pos.config.efectivo_maximo > 0){
            var metodos_pago_efectivo = [];
            for (var i = 0; i < order_pagos.length; i++) {
                if (order_pagos[i].payment_method.is_cash_count){
                    metodos_pago_efectivo.push(order_pagos[i].payment_method.id)
                    total_efectivo += order_pagos[i].amount
                }

            }
            console.log(metodos_pago_efectivo)




            rpc.query({
                    model: 'pos.session',
                    method: 'search_read',
                    args: [[['id', '=', this.pos.pos_session.id ]], []],
                })
                .then(function (sesion){
                    rpc.query({
                            model: 'pos.payment',
                            method: 'search_read',
                            args: [[['session_id', '=', self.pos.pos_session.id ],['payment_method_id', 'in', metodos_pago_efectivo ]], []],
                        })
                        .then(function (pagos){
                            console.log(pagos)
                            var efectivo = 0;
                            if (pagos.length > 0 ){

                                for (var i = 0; i < pagos.length; i++) {
                                    efectivo += pagos[i].amount
                                }

                            }

                            if (sesion[0].cash_register_total_entry_encoding > self.pos.config.efectivo_maximo){
                                self.pos.gui.show_popup("error",{
                                    "title": "Límite de efectivo",
                                    "body":  "Límite de efectivo máximo",
                                });
                            }else if ((sesion[0].cash_register_total_entry_encoding+total_efectivo) > self.pos.config.efectivo_maximo) {
                                window.alert('Límite de efectivo, por favor retire efectivo antes de la siguiente venta');
                                _super();
                            }else{
                                _super();
                            }
                            console.log(efectivo+sesion[0].cash_register_balance_start);
                            self.renderElement();
                        });


                });
        }else{
            this._super();
        }


    },
});


// screens.ScreenWidget.include({
//     barcode_product_action: function(code){
//         var self = this;
//         // self._super();
//         // console.log('BARCODE_PRODUCT_ACTION')
//         // console.log(code.code)
//         // // console.log(code.code.length)
//         // console.log(code.code.substring(0, 11))
//         console.log('quemen barcode')
//         code.code = String(code.code).substring(0, 11);
//         code.base_code = String(code.base_code).substring(0, 11);
//         // code = "10900219001"
//         console.log('SELF SCAN PRODUCT')
//         // console.log(self.pos.scan_product(code));
//         console.log('---------------------')
//         if (self.pos.scan_product(code)) {
//             if (self.barcode_product_screen) {
//                 self.gui.show_screen(self.barcode_product_screen, null, null, true);
//             }
//         } else {
//             this.barcode_error_action(code);
//         }
//     },
//
// });


});
