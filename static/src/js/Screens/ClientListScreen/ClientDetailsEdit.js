odoo.define('quemen.ClientDetailsEdit', function(require) {
    'use strict';


    const OrderReceipt = require('point_of_sale.OrderReceipt');
    const Registries = require('point_of_sale.Registries');
    const { useState, useContext } = owl.hooks;
    const models = require('point_of_sale.models');
    const pos_db = require('point_of_sale.DB');
    const rpc = require('web.rpc');
    const ClientDetailsEdit = require('point_of_sale.ClientDetailsEdit')


    const QuemenClientDetailsEdit = ClientDetailsEdit =>
        class extends ClientDetailsEdit {
            constructor() {
                super(...arguments);
                console.log('inherit CLIENTE DETAILS EDIT')
                console.log(this)
            }

        };

    Registries.Component.extend(ClientDetailsEdit, QuemenClientDetailsEdit);

            
});