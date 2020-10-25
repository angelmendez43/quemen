odoo.define('quemen.models', function (require) {
"use strict";

var models = require('point_of_sale.models');
var gui = require('point_of_sale.gui');
var core = require('web.core');
var _t = core._t;

models.PosModel = models.PosModel.extend({
    scan_product: function(parsed_code){
        var selectedOrder = this.get_order();
        var lote = String(parsed_code.base_code).substring(11, 18);
        parsed_code.code = String(parsed_code.code).substring(0, 11);
        parsed_code.base_code = String(parsed_code.base_code).substring(0, 11);


        var product = this.db.get_product_by_barcode(parsed_code.base_code);

        if(!product){
            return false;
        }


        if(parsed_code.type === 'price'){
            selectedOrder.add_product(product, {price:parsed_code.value,lote: lote});
        }else if(parsed_code.type === 'weight'){
            selectedOrder.add_product(product, {quantity:parsed_code.value, merge:false,lote: lote});
        }else if(parsed_code.type === 'discount'){
            selectedOrder.add_product(product, {discount:parsed_code.value, merge:false,lote: lote});
        }else{
            selectedOrder.add_product(product,{lote: lote});
        }
        return true;
    },
});


var _super_order = models.Order.prototype;
models.Order = models.Order.extend({

    add_product: function(product, options) {
        var self = this;
        var orden = self.pos.get_order();
        _super_order.add_product.apply(this,arguments)
        var orderline = orden.get_selected_orderline();
        if (orderline.has_product_lot){
            var pack_lot_lines =  orderline.compute_lot_lines();
            pack_lot_lines.models[0]["attributes"]["lot_name"] = options.lote
            this.pos.gui.show_popup('packlotline', {
                'title': _t('Lot/Serial Number(s) Requred'),
                'pack_lot_lines': pack_lot_lines,
                'order_line': orderline,
                'order': this,
            });
            this.pos.gui.current_popup.click_confirm();

        }

    }
});


});
