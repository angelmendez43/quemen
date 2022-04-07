odoo.define('quemen.models', function (require) {
"use strict";
const { Context } = owl;
var models = require('point_of_sale.models');

// var gui = require('point_of_sale.gui');

var { Gui } = require('point_of_sale.Gui');

var core = require('web.core');
var rpc = require('web.rpc');
var _t = core._t;


var _super_posmodel = models.PosModel.prototype;
models.PosModel = models.PosModel.extend({
    add_new_order: function(){
        var new_order = _super_posmodel.add_new_order.apply(this);
        console.log("Que es esto?")
        if (this.config.cliente_id) {
            new_order.set_client(this.db.get_partner_by_id(this.config.cliente_id[0]))
        }
    }
})


});
