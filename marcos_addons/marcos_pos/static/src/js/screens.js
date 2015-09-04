function marcos_pos_screens(instance, module) {

    var QWeb = instance.web.qweb,
    _t = instance.web._t;

    module.PaymentScreenWidget = module.PaymentScreenWidget.extend({
        show: function() {
            this._super();
            var self = this;

            //add check credit button
            this.add_action_button({
                    label: _t('Notas de créditos'),
                    name: 'load_credits',
                    icon: '/marcos_pos/static/src/img/refund.png',
                    click: function(){
                        self.load_credits();
                    }
                });

        },
        validate_refound_cash_from_credit_note: function(currentOrder){
            var self = this;
            var credit_paid = currentOrder.get_credit_paid();
            var TotalTaxIncluded = currentOrder.getTotalTaxIncluded();

            if (credit_paid > TotalTaxIncluded) {
                self.pos.validate_manager();
                if (self.pos.manger_validated) {
                    if (self.pos.manger_permission.cash_refund) {
                        return true
                    } else {
                        return false
                    }

                } else {
                    return false;
                }
            } else {
                return true
            }

        },
        validate_order: function (options) {
            var self = this;
            options = options || {};

            var currentOrder = this.pos.get('selectedOrder');

            if (!self.validate_refound_cash_from_credit_note(currentOrder)) {
                self.pos.pos_widget.screen_selector.show_popup('error', {
                    'message': _t('Acceso negado'),
                    'comment': _t('No tiene permiso para devolver dinero de una nota de crédito!')
                });
                return
            }

            if (options.action === "send_to_cashier_with_ref_name") {
                var name = currentOrder.get("name") + "-" + options.ref_name;
                currentOrder.set("name", name);
            }

            if (currentOrder.get('orderLines').models.length === 0) {
                this.pos_widget.screen_selector.show_popup('error', {
                    'message': _t('Empty Order'),
                    'comment': _t('There must be at least one product in your order before it can be validated')
                });
                return;
            }

            //check payment if receipt is standard
            if (!options.action && currentOrder.get("type") !== "refund") {
                var plines = currentOrder.get('paymentLines').models;
                for (var i = 0; i < plines.length; i++) {
                    if (plines[i].get_type() === 'bank' && plines[i].get_amount() < 0) {
                        this.pos_widget.screen_selector.show_popup('error', {
                            'message': _t('Negative Bank Payment'),
                            'comment': _t('You cannot have a negative amount in a Bank payment. Use a cash payment method to return money to the customer.')
                        });
                        return;
                    }
                }

                if (!this.is_paid()) {
                    return;
                }

                // The exact amount must be paid if there is no cash payment method defined.
                if (Math.abs(currentOrder.getTotalTaxIncluded() - currentOrder.getPaidTotal()) > 0.00001) {
                    var cash = false;
                    for (var i = 0; i < this.pos.cashregisters.length; i++) {
                        cash = cash || (this.pos.cashregisters[i].journal.type === 'cash');
                    }
                    if (!cash) {
                        this.pos_widget.screen_selector.show_popup('error', {
                            message: _t('Cannot return change without a cash payment method'),
                            comment: _t('There is no cash payment method available in this point of sale to handle the change.\n\n Please pay the exact amount or add a cash payment method in the point of sale configuration')
                        });
                        return;
                    }
                }
            } // end if quotation

            if (this.pos.config.iface_cashdrawer) {
                this.pos.proxy.open_cashbox();
            }

            if (options.action === "print_quotation" || options.action === "send_quotation") {
                // deactivate the validation button while we try to send the order
                this.pos_widget.action_bar.set_button_disabled('validation', true);
                this.pos_widget.action_bar.set_button_disabled('invoice', true);

                var invoiced = this.pos.push_and_quotation_order(currentOrder, options.action);

                invoiced.fail(function (error) {
                    if (error === 'error-no-client') {
                        self.pos_widget.screen_selector.set_current_screen("clientlist");
                        //self.pos_widget.screen_selector.show_popup('error', {
                        //    message: _t('An anonymous order cannot be invoiced'),
                        //    comment: _t('Please select a client for this order. This can be done by clicking the order tab')
                        //});
                    } else {
                        self.pos_widget.screen_selector.set_current_screen("clientlist");
                        //self.pos_widget.screen_selector.show_popup('error', {
                        //    message: _t('The order could not be sent'),
                        //    comment: _t('Check your internet connection and try again.')
                        //});
                    }
                    self.pos_widget.action_bar.set_button_disabled('validation', false);
                    self.pos_widget.action_bar.set_button_disabled('invoice', false);
                });

                invoiced.done(function () {
                    self.pos_widget.action_bar.set_button_disabled('validation', false);
                    self.pos_widget.action_bar.set_button_disabled('invoice', false);
                    self.pos.get('selectedOrder').destroy();
                });
            }
            else if (options.invoice) {
                // deactivate the validation button while we try to send the order
                this.pos_widget.action_bar.set_button_disabled('validation', true);
                this.pos_widget.action_bar.set_button_disabled('invoice', true);

                var invoiced = this.pos.push_and_invoice_order(currentOrder);

                invoiced.fail(function (error) {
                    if (error === 'error-no-client') {
                        self.pos_widget.screen_selector.show_popup('error', {
                            message: _t('An anonymous order cannot be invoiced'),
                            comment: _t('Please select a client for this order. This can be done by clicking the order tab')
                        });
                    } else {
                        self.pos_widget.screen_selector.show_popup('error', {
                            message: _t('The order could not be sent'),
                            comment: _t('Check your internet connection and try again.')
                        });
                    }
                    self.pos_widget.action_bar.set_button_disabled('validation', false);
                    self.pos_widget.action_bar.set_button_disabled('invoice', false);
                });

                invoiced.done(function () {
                    self.pos_widget.action_bar.set_button_disabled('validation', false);
                    self.pos_widget.action_bar.set_button_disabled('invoice', false);
                    self.pos.get('selectedOrder').destroy();
                });

            } else {
                //get default user configure on pos_config
                if (currentOrder.get_client() === null) {
                    var partner = self.pos.db.get_partner_by_id(self.pos.config.default_partner_id[0]);
                    if (partner === undefined) {
                        return self.pos_widget.screen_selector.show_popup('error', {
                            message: _t('Advertencia'),
                            comment: _t('Debe asignar un cliente a la factura!.')
                        });

                    } else {
                        currentOrder.set_client(partner);
                    }

                }

                if (self.pos.config.ipf_printer === true) {

                    this.pos.push_order(currentOrder)
                        .then(function () {
                            var active_model = "pos_order_ui";
                            var active_id = currentOrder.get("name");
                            return new openerp.web.Model("ipf.printer.config").call("ipf_print", [], {
                                context: new instance.web.CompoundContext({
                                    active_model: active_model,
                                    active_id: active_id
                                })
                            })
                                .then(function (data) {
                                    return self.print_on_ipf(data)
                                })
                                .then(function () {
                                    self.pos.get('selectedOrder').destroy();
                                });
                        });

                } else if (self.pos.config.iface_print_via_proxy) {
                    var receipt = currentOrder.export_for_printing();
                    self.pos.proxy.print_receipt(QWeb.render('XmlReceipt', {
                        receipt: receipt, widget: self
                    }));
                    self.pos.get('selectedOrder').destroy();    //finish order and go back to scan screen

                } else if (!self.pos.config.payment_pos) {
                    //finish order and go back to scan screen
                    currentOrder.set("next_screen", true);
                    this.pos.push_order(currentOrder);
                    //self.pos_widget.screen_selector.set_current_screen(this.next_screen);
                } else {
                    this.pos.push_order(currentOrder);
                    self.pos.get('selectedOrder').destroy();    //finish order and go back to scan screen
                }
            }

            // hide onscreen (iOS) keyboard
            setTimeout(function () {
                document.activeElement.blur();
                $("input").blur();
            }, 250);
        },
        print_on_ipf_done: function () {
            var self = this;
            return new openerp.web.Model("ipf.printer.config").call("print_done", [[self.invoice_id, self.nif]], {context: new instance.web.CompoundContext()})
                .then(function (response) {
                    return response;
                })
        },
        print_on_ipf: function (data) {
            var self = this;
            this.invoice_id = data.invoice_id;
            $.ajax({
                type: 'POST',
                url: data.host + "/invoice",
                data: JSON.stringify(data)
            })
                .done(function (response) {
                    var message = JSON.parse(response);
                    self.nif = message.response.nif;
                    self.print_on_ipf_done();
                })
                .fail(function (response) {
                    var message = JSON.parse(response.responseText);
                    if (message.message === "Missing payment type.") {
                        return alert("Los tipos de pagos para la impresora fiscal, debe de configurarlos en los diarios de pago.")
                    } else if (message.message === "Payment incomplete.") {
                        return alert("Debe actualizar el total de factura en el botón actualizar al que se encuenta al lado del total.")
                    } else if (message.message === "The printer is not connected.") {
                        return alert("El sistenma no puede comunicarse con la impresora.")
                    }

                });
        },
        is_paid: function(){
            var currentOrder = this.pos.get('selectedOrder');
            return (currentOrder.getTotalTaxIncluded() < 0.000001
                   || currentOrder.getPaidTotal() + currentOrder.get_credit_paid() +0.000001 >= currentOrder.getTotalTaxIncluded());

        },
        update_payment_summary: function() {
            var currentOrder = this.pos.get('selectedOrder');
            var dueTotal = currentOrder.getTotalTaxIncluded();
            var credit_paid = currentOrder.get_credit_paid();
            var paidTotal = currentOrder.getPaidTotal();
            var remaining = dueTotal > (paidTotal + credit_paid) ? dueTotal - (paidTotal+credit_paid) : 0;
            var change = (paidTotal+credit_paid) > dueTotal ? (paidTotal+credit_paid) - dueTotal : 0;
            currentOrder.set("remaining", remaining);

            this.$('.payment-due-total').html(this.format_currency(dueTotal));
            this.$('.credit-paid-total').html(this.format_currency(credit_paid));
            this.$('.payment-paid-total').html(this.format_currency(paidTotal));
            this.$('.payment-remaining').html(this.format_currency(remaining));
            this.$('.payment-change').html(this.format_currency(change));
            if(currentOrder.selected_orderline === undefined){
                remaining = 1;  // What is this ?
            }

            if(this.pos_widget.action_bar){
                this.pos_widget.action_bar.set_button_disabled('validation', !this.is_paid());
                this.pos_widget.action_bar.set_button_disabled('invoice', !this.is_paid());
            }
        },
        load_credits: function(){
            var self = this;
            var currentOrder = this.pos.get('selectedOrder');
            var paymentLines = currentOrder.get("paymentLines");
            var defaul_client = self.pos.db.get_partner_by_id(self.pos.config.default_partner_id[0]);
            var client = currentOrder.has("client") ? currentOrder.get("client") : defaul_client;
            if (client && client.id === defaul_client.id) {
                self.pos_widget.screen_selector.show_popup(
                    'marcos_input_popup_widget', {
                        message: "Digité el NCF de la nota de crédito.",
                        confirm: function () {
                            self.load_credit_note(this.$("#ref_name").val());
                        }

                    });
            } else
            if (client) {
                var client_id = currentOrder.get_client();
                self.load_credit_note(client_id.id);
            } else{
                self.pos_widget.screen_selector.set_current_screen("clientlist");
                return
            }
        },
        load_credit_note: function(value) {
            var self = this;
            var currentOrder = self.pos.get('selectedOrder');
            var paymentLines = currentOrder.get("paymentLines");
            if (value.length == 19) {
                return new instance.web.Model("account.invoice").query(["partner_id", "residual"])
                    .filter([['number','=', value], ['type','=','out_refund'], ['state','=','open']])
                    .first()
                    .then(function(result){
                        currentOrder.set_credit_paid(result.residual);
                        currentOrder.set_credit_note_ncf(value);
                        partner = self.pos.db.get_partner_by_id(result.partner_id[0]);
                        currentOrder.set_client(partner);
                        _.each(paymentLines.models, function (payment) {
                            currentOrder.removePaymentline(payment);
                        });
                    }).then(function(){
                        self.update_payment_summary();
                    });
            } else if (value) {
                console.log(value);
                return new instance.web.Model("account.invoice").query(["residual"])
                    .filter([['partner_id','=', value], ['type','=','out_refund'], ['state','=','open']])
                    .all()
                    .then(function(results){
                        var residual = 0.00;
                        _.each(results, function(value){
                            residual += value.residual;
                        });
                        currentOrder.set_credit_paid(residual);
                        _.each(paymentLines.models, function (payment) {
                            currentOrder.removePaymentline(payment);
                        });
                    }).then(function(){
                        self.update_payment_summary();
                    });
            }

        }
    });

    module.ClientListScreenWidget = module.ClientListScreenWidget.extend({
        save_changes: function () {
            this._super();
            if (this.has_client_changed()) {
                var currentOrder = this.pos.get('selectedOrder');
                var orderLines = currentOrder.get('orderLines').models;
                var partner = currentOrder.get_client();
                this.pos.pricelist_engine.update_products_ui(partner);
                this.pos.pricelist_engine.update_ticket(partner, orderLines);
            }
        }
    });

    module.ReceiptScreenWidget = module.ReceiptScreenWidget.extend({
       refresh: function() {
            var order = this.pos.get('selectedOrder');
            console.log("======================")
            console.log(order);
            $('.pos-receipt-container', this.$el).html(QWeb.render('PosTicket',{
                    widget:this,
                    order: order,
                    orderlines: order.get('orderLines').models,
                    paymentlines: order.get('paymentLines').models,
                }));
        }
    });

}