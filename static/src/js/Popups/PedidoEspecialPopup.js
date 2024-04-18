odoo.define('quemen.PedidoEspecialPopup', function (require) {
    'use strict';

    const AbstractAwaitablePopup = require('point_of_sale.AbstractAwaitablePopup');
    const Registries = require('point_of_sale.Registries');
    const { _lt } = require('@web/core/l10n/translation');

    const { useState } = owl;

    // formerly SelectionPopupWidget
    class PedidoEspecialPopup extends AbstractAwaitablePopup {
        /**
         * Value of the `item` key of the selected element in the Selection
         * Array is the payload of this popup.
         *
         * @param {Object} props
         * @param {String} [props.confirmText='Confirm']
         * @param {String} [props.cancelText='Cancel']
         * @param {String} [props.title='Select']
         * @param {String} [props.body='']
         * @param {Array<Selection>} [props.list=[]]
         *      Selection {
         *          id: integer,
         *          label: string,
         *          isSelected: boolean,
         *          item: any,
         *      }
         */
        setup() {
            super.setup();
            // this.state = useState({ selectedId: this.props.list.find((item) => item.isSelected) });
            console.log('setup popup')
            console.log(this)
        }
        selectItem(itemId) {
            // this.state.selectedId = itemId;
            console.log('selectItem')
            console.log(this)
            this.confirm();
        }
        /**
         * We send as payload of the response the selected item.
         *
         * @override
         */
        getPayload() {
            // const selected = this.props.list.find((item) => this.state.selectedId === item.id);
            // return selected && selected.item;
            console.log('getPayload')
            console.log(this)
            
            return true
        }
    }
    PedidoEspecialPopup.template = 'PedidoEspecialPopup';
    // PedidoEspecialPopup.dontShow = false;
    PedidoEspecialPopup.defaultProps = {
        cancelText: _lt('Cancel'),
        confirmText: _lt('Confirm'),
        title: _lt('Ingrese información'),
        body: '',
        // list: [],
        // confirmKey: false,
    };

    Registries.Component.add(PedidoEspecialPopup);

    return PedidoEspecialPopup;
});