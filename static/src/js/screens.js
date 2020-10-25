odoo.define('quemen.screens', function (require) {
"use strict";

var screens = require('point_of_sale.screens');
// var models = require('point_of_sale.models');
// var pos_db = require('point_of_sale.DB');
// var rpc = require('web.rpc');
// var gui = require('point_of_sale.gui');
// var core = require('web.core');
// var PopupWidget = require('point_of_sale.popups');
// var field_utils = require('web.field_utils');
// var QWeb = core.qweb;
// var _t = core._t;




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
