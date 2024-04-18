odoo.define('quemen.ReprintReceiptScreen', function (require) {
    'use strict';

    const ReprintReceiptScreen = require('point_of_sale.ReprintReceiptScreen');
    const Registries = require('point_of_sale.Registries');

    const QuemenReprintReceiptScreen = ReprintReceiptScreen =>
        class extends ReprintReceiptScreen {
            async printReceipt() {
                if(this.env.pos.proxy.printer && this.env.pos.config.iface_print_skip_screen) {
                    let result = await this._printReceipt();
                    if(result)
                        this.showScreen('TicketScreen', { reuseSavedUIState: true });
                }
            }
        };

    Registries.Component.extend(ReprintReceiptScreen, QuemenReprintReceiptScreen);
    
    const ReprintReceiptScreen = (AbstractReceiptScreen) => {
        class ReprintReceiptScreen extends AbstractReceiptScreen {
            mounted() {
                this.printReceipt();
            }
            confirm() {
                this.showScreen('TicketScreen', { reuseSavedUIState: true });
            }
            async printReceipt() {
                if(this.env.pos.proxy.printer && this.env.pos.config.iface_print_skip_screen) {
                    let result = await this._printReceipt();
                    if(result)
                        this.showScreen('TicketScreen', { reuseSavedUIState: true });
                }
            }
            async tryReprint() {
                await this._printReceipt();
            }
        }
        ReprintReceiptScreen.template = 'ReprintReceiptScreen';
        return ReprintReceiptScreen;
    };
    Registries.Component.addByExtending(ReprintReceiptScreen, AbstractReceiptScreen);

    return ReprintReceiptScreen;
});
