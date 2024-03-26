odoo.define('quemen.ProductScreen', function(require) {
    'use strict';

    const Registries = require('point_of_sale.Registries');
    const ProductScreen = require('point_of_sale.ProductScreen');
    var { Gui } = require('point_of_sale.Gui');
    var core = require('web.core');
    var _t = core._t;

    const QuemenProductScreen = ProductScreen =>
        class extends ProductScreen {
            constructor(obj, options) {
                super(...arguments);
            }            
            async _getProductByBarcode(code) {
                console.log('QuemenProductScreen')
                var product_barcode = super._getProductByBarcode(...arguments);

                let NewfoundProductIds = [];
                let FoundProduct = [];
                code.type = 'lot';
                try {
                    NewfoundProductIds = await this.rpc({
                        model: 'stock.production.lot',
                        method: 'search_read',
                        args: [[
                            ['name', '=', code.base_code]
                        ]],
                        context: this.env.session.user_context,
                    });
                    FoundProduct = [NewfoundProductIds[0].product_id[0]]

                } catch (error) {
                    if (isConnectionError(error)) {
                        return this.showPopup('OfflineErrorPopup', {
                            title: this.env._t('Network Error'),
                            body: this.env._t("Product is not loaded. Tried loading the product from the server but there is a network error."),
                        });
                    } else {
                        throw error;
                    }
                }    
                console.log('NewfoundProductIds')
                console.log(NewfoundProductIds)
                console.log(FoundProduct)

                
                if (FoundProduct.length) {
                    var ProductLot = [NewfoundProductIds[0].product_id[0]];
                    var IdLot = NewfoundProductIds[0].id;
                    var ProductStock = [];
                    var location_id = this.env.pos.config.ubicacion_id[0];
                    ProductStock = await this.rpc({
                        model: 'stock.quant',
                        method: 'search_read',
                        args: [[
                            ['lot_id', '=', IdLot],
                            ['location_id', '=', location_id]
                        ]],
                        context: this.env.session.user_context,
                    });
                    
                    console.log('ProductLot')
                    console.log(ProductStock)
                    console.log(this)
                    if (ProductStock.length == 1){

                        if (ProductStock[0].quantity > 0){
                            await this.env.pos._addProducts(FoundProduct, false);
                            // assume that the result is unique.
                            product_barcode = this.env.pos.db.get_product_by_id(FoundProduct[0]);
                            return product_barcode;
                        }else{
                            Gui.showPopup('ErrorPopup', {
                                title: _t('Existencias'),
                                body: _t('No hay existencias de producto')
                            });
                            return
                        }
                        
                    }else{
                            Gui.showPopup('ErrorPopup', {
                                title: _t('Inválido'),
                                body: _t('Lote inválido')
                            });
                            return
                        
                    }
                    

                }                
                
            } 
         
        };

    Registries.Component.extend(ProductScreen, QuemenProductScreen);

            
});