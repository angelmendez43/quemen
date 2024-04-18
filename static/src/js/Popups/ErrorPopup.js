odoo.define('quemen.ErrorPopup', function(require) {
    'use strict';

    const Registries = require('point_of_sale.Registries');
    const ErrorPopup = require('point_of_sale.ErrorPopup');
    const PaymentScreen = require('point_of_sale.PaymentScreen');
    var { Gui } = require('point_of_sale.Gui');
    var core = require('web.core');
    const { isConnectionError } = require('point_of_sale.utils');

    var _t = core._t;
    
    
    const QuemenErrorPopup = ErrorPopup =>
        class extends ErrorPopup {
                mounted() {
                    console.log('no sound error')
                }
        }

    Registries.Component.extend(ErrorPopup, QuemenErrorPopup);

});