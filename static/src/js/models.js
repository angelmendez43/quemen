odoo.define('quemen.models', function (require) {
"use strict";

var models = require('point_of_sale.models');
var gui = require('point_of_sale.gui');
var core = require('web.core');
var rpc = require('web.rpc');
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

var _super_posmodel = models.PosModel.prototype;
models.PosModel = models.PosModel.extend({
    add_new_order: function(){
        var new_order = _super_posmodel.add_new_order.apply(this);
        if (this.config.cliente_id) {
            new_order.set_client(this.db.get_partner_by_id(this.config.cliente_id[0]))
        }
    }
})

var _super_order = models.Order.prototype;
models.Order = models.Order.extend({
    export_as_JSON: function() {
        var json = _super_order.export_as_JSON.apply(this,arguments);
        json.tipo_venta = this.pos.get_tipo_venta();

        return json;
    },
    export_for_printing: function() {
        var json = _super_order.export_for_printing.apply(this,arguments);
        json.tipo_venta = this.pos.get_tipo_venta();
        return json;
    },
    agregar_lote: function(pack_lot_lines,options,orderline) {
        var self = this;
        pack_lot_lines.models[0]["attributes"]["lot_name"] = options.lote
        this.pos.gui.show_popup('packlotline', {
            'title': _t('Lot/Serial Number(s) Requred'),
            'pack_lot_lines': pack_lot_lines,
            'order_line': orderline,
            'order': this,
        });
        this.pos.gui.current_popup.click_confirm();

        return true;
    },
    add_product: function(product, options) {
        var self = this;
        var orden = self.pos.get_order();
        _super_order.add_product.apply(this,arguments)
        var orderline = orden.get_selected_orderline();
        var tipo_ubicacion = this.pos.config.picking_type_id[0];
        if (orderline.has_product_lot && (typeof options !== 'undefined')){
          rpc.query({
                  model: 'pos.order',
                  method: 'obtener_inventario_producto',
                  args: [[],product.id,tipo_ubicacion,options.lote],
              })
              .then(function (existencia){
                  if (existencia > 0){
                      var pack_lot_lines =  orderline.compute_lot_lines();
                      self.agregar_lote(pack_lot_lines,options,orderline)
                  }else {
                      window.alert('No hay existencia')
                      self.pos.gui.close_popup();
                      self.remove_orderline(orderline);
                  }
              });

        }else if(orderline.has_product_lot && (typeof options == 'undefined')){
            return;

        }else{
          rpc.query({
                  model: 'pos.order',
                  method: 'obtener_inventario_producto',
                  args: [[],product.id,tipo_ubicacion,false],
              })
              .then(function (existencia){
                  if (existencia == 0){
                      window.alert('No hay existencia')
                      self.remove_orderline(orderline);
                  }
              });
        }

    },
    remove_orderline: function( line ){
        this.assert_editable();
        this.orderlines.remove(line);
        this.select_orderline(this.get_last_orderline());
        if (this.pos.config.cupones){
            if (line.get_cupon()){
                rpc.query({
                        model: 'pos.order',
                        method: 'habilitar_cupon',
                        args: [[],line.get_cupon()],
                    })
                    .then(function (estado){
                    });
            }
        }
    },
});

models.PosModel = models.PosModel.extend({
    get_tipo_venta: function(){
        var tipo_venta = "mostrador";
        if (this.get('tipo_venta')){
          tipo_venta = this.get('tipo_venta')
        }
        return tipo_venta|| this.tipo_venta;
    },
    set_tipo_venta: function(tipo_venta){
        this.set('tipo_venta', tipo_venta);
        // this.db.set_empleado(this.empleado);
    }
})

var _super_order_line = models.Orderline.prototype;
models.Orderline = models.Orderline.extend({
    initialize: function() {
        _super_order_line.initialize.apply(this,arguments);
        this.cupon = this.cupon || false;
    },
    export_as_JSON: function() {
        var json = _super_order_line.export_as_JSON.apply(this,arguments);

        if (this.get_cupon().length > 0){
            json.cupon = this.get_cupon()[0];
        }else{
            json.cupon = false;
        }
        return json;
    },
    set_cupon: function(cupon){
        this.cupon = cupon;
        this.trigger('change',this);
    },

    get_cupon: function(cupon){
        return this.cupon;
    },
})
});
