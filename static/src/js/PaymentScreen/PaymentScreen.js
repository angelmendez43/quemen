odoo.define('quemen.PaymentScreen', function(require) {
    'use strict';

    const Registries = require('point_of_sale.Registries');
    const PaymentScreen = require('point_of_sale.PaymentScreen');
    var { Gui } = require('point_of_sale.Gui');
    var core = require('web.core');
    var _t = core._t;

    const QuemenPaymentScreen = PaymentSreen =>
        class extends PaymentScreen {



            async validateOrder(isForceValidate) {
                var res = super.validateOrder(...arguments);
                console.log('Validate order inherit')
                
                // if(this.env.pos.config.cash_rounding) {
                //     if(!this.env.pos.get_order().check_paymentlines_rounding()) {
                //         this.showPopup('ErrorPopup', {
                //             title: this.env._t('Rounding error in payment lines'),
                //             body: this.env._t("The amount of your payment lines must be rounded to validate the transaction."),
                //         });
                //         return;
                //     }
                // }
                // if (await this._isOrderValid(isForceValidate)) {
                //     // remove pending payments before finalizing the validation
                //     for (let line of this.paymentLines) {
                //         if (!line.is_done()) this.currentOrder.remove_paymentline(line);
                //     }
                //     await this._finalizeValidation();
                // }
                return res
            }
        };

    Registries.Component.extend(PaymentScreen, QuemenPaymentScreen);

            
});