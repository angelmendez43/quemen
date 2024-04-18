odoo.define('quemen.PedidoEspecialButton', function(require) {
    'use strict';

    const PosComponent = require('point_of_sale.PosComponent');
    const ProductScreen = require('point_of_sale.ProductScreen');
    const { useListener } = require('web.custom_hooks');
    const Registries = require('point_of_sale.Registries');
    const { Gui } = require('point_of_sale.Gui');

    class PedidoEspecialButton extends PosComponent {
        constructor() {
            super(...arguments);
            this.constructor.dontShow = true;
            useListener('click', this.onClick);
        }
        async onClick() {
            const order = this.env.pos.get_order();
            if (order.get_orderlines().length > 0) {
                console.log('Pedido especial')
                const { confirmed, payload } = await Gui.showPopup('PedidoEspecialPopup', {
                                      title: this.env._t('Pedido especial'),

                                  });
                if (confirmed){
                    console.log('Confirmado')
                    console.log(payload)
                    var selectedOrderline = this.env.pos.get_order().get_selected_orderline();
                    selectedOrderline.set_producto_especial(true);
                    var dicc_total = {};
                    var stt_prod=0, tt_prod=0, tt_iva=0;
                    var fecha = document.getElementById("meeting-time");
                    var hora = document.getElementById("field_time");
                    var observaciones = document.getElementById("observaciones_id");
                    var autorizo = document.getElementById("autorizo_id");
                    var sucursal_entrega = document.getElementById("entrega_id");
                    var fecha_hora_actual1 = new Date();
                    console.log('fecha')
                    console.log(fecha.value)
                    var fecha_actual1 = fecha_hora_actual1.getDate();
                    //var formato_correcto_hoy = fecha_actual1.split('-').reverse().join('/');
                    var fecha_hora_correctas = fecha_hora_actual1.getDate()+'/'+(fecha_hora_actual1.getMonth()+1)+'/'+fecha_hora_actual1.getFullYear()+' '+ (fecha_hora_actual1.getHours()+':'+fecha_hora_actual1.getMinutes())
                    var fecha_formato_original = fecha.value;
                    var formato_correcto = fecha_formato_original.split('-').reverse().join('/');
                    document.querySelector('input[type="datetime-local"]');
                    order.set_fecha(fecha.value);
                    order.set_hora(hora.value);
                    var observa = observaciones.value ;
                    observa = observa.replace(/ (\n) + / g, '<br></br>')
                    order.set_observaciones(observa);
                    order.set_autorizo(autorizo.value)
                    order.set_entrega(sucursal_entrega.value);
                    order.set_fecha_formato(formato_correcto);
                    order.set_fecha_hora_actual(fecha_hora_correctas);
                    var terminos_condiciones='';
                    terminos_condiciones = order.pos.config.terminos_condiciones.toString();
                    order.set_terminosCondiciones(terminos_condiciones);
                    order.set_dicc_total(dicc_total);
                }

                var dicc_productos_especiales = {};;


                    if (!(selectedOrderline.product.id in dicc_productos_especiales)) {
                      dicc_productos_especiales[selectedOrderline.product.id]={
                        'nombre_producto':selectedOrderline.product.display_name,
                        'cantidad':0,
                        'precio_unitario':selectedOrderline.get_unit_price(),
                        'precio_unitario_con_iva':selectedOrderline.get_price_with_tax(),
                        'precio_total':0,
                        'total_con_iva':0,
                        'estado': false,
                      }
                    }

                    if (selectedOrderline.product.id in dicc_productos_especiales) {
                      dicc_productos_especiales[selectedOrderline.product.id]['cantidad'] += selectedOrderline.quantity;
                      dicc_productos_especiales[selectedOrderline.product.id]['precio_total'] = (dicc_productos_especiales[selectedOrderline.product.id]['cantidad'] * dicc_productos_especiales[selectedOrderline.product.id]['precio_unitario']);
                      dicc_productos_especiales[selectedOrderline.product.id]['total_con_iva'] = (dicc_productos_especiales[selectedOrderline.product.id]['cantidad'] * dicc_productos_especiales[selectedOrderline.product.id]['precio_unitario_con_iva']);
                    }


                order.dicc_productos_especiales = dicc_productos_especiales
                order.set_dicc_prod_especiales(dicc_productos_especiales);

                // this.trigger('close-popup');
                // this.showScreen('SplitBillScreen');
            }
        }
    }
    PedidoEspecialButton.template = 'PedidoEspecialButton';

    ProductScreen.addControlButton({
        component: PedidoEspecialButton,
        condition: function() {
            return true;
        },
    });

    Registries.Component.add(PedidoEspecialButton);

    return PedidoEspecialButton;
});
