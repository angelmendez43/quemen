odoo.define('quemen.AbstractReceiptScreen', function(require) {
    'use strict';

    const AbstractReceiptScreen = require('point_of_sale.AbstractReceiptScreen')
    const Registries = require('point_of_sale.Registries');
    var { Gui } = require('point_of_sale.Gui');
    const { useRef } = owl.hooks;
    const { nextFrame } = require('point_of_sale.utils');
    var core = require('web.core');
    const { isConnectionError } = require('point_of_sale.utils');

    var _t = core._t;
    
    
    const QuemenAbstractReceiptScreen = AbstractReceiptScreen =>
        class extends AbstractReceiptScreen {
            constructor() {
                super(...arguments);
                this.SpecialorderReceipt = useRef('order-receipt-special');
            }
            async _printReceipt() {
                super._printReceipt();
                if (this.env.pos.proxy.printer) {
                    const printResultSpecial = await this.env.pos.proxy.printer.print_receipt(this.SpecialorderReceipt.el.outerHTML);
                    if (printResultSpecial.successful) {
                        return true;
                    } else {
                        await this.showPopup('ErrorPopup', {
                            title: printResultSpecial.message.title,
                            body: printResultSpecial.message.body,
                        });
                        const { confirmed } = await this.showPopup('ConfirmPopup', {
                            title: printResultSpecial.message.title,
                            body: this.env._t('Do you want to print using the web printer?'),
                        });
                        if (confirmed) {
                            // We want to call the _printWeb when the popup is fully gone
                            // from the screen which happens after the next animation frame.
                            await nextFrame();
                            return await this._printWeb();
                        }
                        return false;
                    }
                } else {
                    return await this._printWeb();
                }
            }
        }

    Registries.Component.extend(AbstractReceiptScreen, QuemenAbstractReceiptScreen);

});