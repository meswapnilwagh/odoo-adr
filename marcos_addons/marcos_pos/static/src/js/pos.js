openerp.marcos_pos = function (instance, local) {
    var _t = instance.web._t,
        _lt = instance.web._lt;
    var QWeb = instance.web.qweb;

    local.MarcosInputPopupWidget = instance.point_of_sale.PopUpWidget.extend({
        template: 'MarcosInputPopupWidget',
        show: function (options) {
            var self = this;
            this._super();

            this.message = options.message || '';
            this.input_type = options.input_type || '';


            this.renderElement();

            this.$('.button.cancel').click(function () {
                self.pos_widget.screen_selector.close_popup();
                if (options.cancel) {
                    options.cancel.call(self);
                }
            });

            this.$('.button.confirm').click(function () {
                self.pos_widget.screen_selector.close_popup();
                if (options.confirm) {
                    options.confirm.call(self);
                }
            });


            if (this.input_type === "pwd") {
                this.$("#ref_name").hide();
                this.$("#password").show();
                this.$("#password").focus();
            } else {
                this.$("#password").hide();
                this.$("#ref_name").show();
                this.$("#ref_name").focus();
            }

        }
    });

    local.MarcosProductAvailablePopupWidget = instance.point_of_sale.PopUpWidget.extend({
        template: 'MarcosProductAvailablePopupWidget',
        show: function (options) {
            var self = this;
            this._super();

            this.message = options.message || '';
            this.location_qty = options.location_qty || "";


            this.renderElement();

            this.$('.button.cancel').click(function () {
                self.pos_widget.screen_selector.close_popup();
                if (options.cancel) {
                    options.cancel.call(self);
                }
            });

            this.$('.button.confirm').click(function () {
                self.pos_widget.screen_selector.close_popup();
                if (options.confirm) {
                    options.confirm.call(self);
                }
            });


        }
    });

    local.MarcosHeaderButtonWidget = instance.point_of_sale.PosBaseWidget.extend({
        template: 'MarcosHeaderButtonWidget',
        init: function (parent, options) {
            options = options || {};
            this._super(parent, options);
            this.action = options.action;
            this.class = options.class;
        },
        renderElement: function () {
            var self = this;
            this._super();
            if (this.action) {
                this.$el.click(function () {
                    self.action();
                });
            }
        },
        show: function () {
            this.$el.removeClass('oe_hidden');
        },
        hide: function () {
            this.$el.addClass('oe_hidden');
        },
        lock: function () {
            this.$el.find("i").removeClass("fa-unlock");
            this.$el.find("i").addClass("fa-lock");
        },
        unlock: function () {
            this.$el.find("i").removeClass("fa-lock");
            this.$el.find("i").addClass("fa-unlock");
        }
    });


    instance.point_of_sale.PosWidget = instance.point_of_sale.PosWidget.extend({

        build_widgets: function (parent, name) {
            var self = this;
            this._super(parent);
            this.manager = false;
            this.marcos_input_popup_widget = new local.MarcosInputPopupWidget(this, {});
            this.marcos_product_available_popup_widget = new local.MarcosProductAvailablePopupWidget(this, {});
            this.marcos_input_popup_widget.appendTo($(this.$el));
            this.marcos_product_available_popup_widget.appendTo($(this.$el));
            this.screen_selector.popup_set['marcos_input_popup_widget'] = this.marcos_input_popup_widget;
            this.screen_selector.popup_set['marcos_product_available_popup_widget'] = this.marcos_product_available_popup_widget;
            // Hide the popup because all pop up are displayed at the
            // beginning by default
            this.marcos_input_popup_widget.hide();
            this.marcos_product_available_popup_widget.hide();


            this.quotation_button = new local.MarcosHeaderButtonWidget(this, {
                class: 'fa fa-file-text-o fa-lg',
                action: function () {
                    self.quotation();
                }
            });

            this.quotation_button.appendTo(this.$('.pos-rightheader'));

            this.change_user_button = new local.MarcosHeaderButtonWidget(this, {
                class: 'fa fa-lock fa-lg',
                action: function () {
                    self.change_user();
                }
            });

            this.change_user_button.appendTo(this.$('.pos-rightheader'));

            if (!self.pos.config.payment_pos) {

                this.cahier_button = new local.MarcosHeaderButtonWidget(this, {
                    class: 'fa fa-money fa-lg',
                    action: function () {
                        self.get_orders({action: "pay"});
                    }
                });

                this.cahier_button.appendTo(this.$('.pos-rightheader'));
            }

            this.refund_button = new local.MarcosHeaderButtonWidget(this, {
                class: 'fa fa-undo fa-lg',
                action: function () {
                    self.get_orders({action: "refund"});
                }
            });

            this.refund_button.appendTo(this.$('.pos-rightheader'));


        },

        get_orders: function (options) {
            var self = this;
            if (options.action === "refund") {
                var domain = [['state', 'in', ['invoiced']]]
                if (!self.can_refund()) {
                    self.pos.pos_widget.screen_selector.show_popup('error', {
                        'message': _t('Acceso negado'),
                        'comment': _t('No tiene permiso hacer devoluciones!')
                    });
                    return
                }
            } else if (options.action === "pay") {
                var domain = [['state', 'in', ['draft']]]
            }
            pop = new instance.web.form.SelectCreatePopup(this);

            pop.init_dataset = function() {
                var self = this;
                this.created_elements = [];
                this.dataset = new instance.web.ProxyDataSet(this, this.model, this.context);
                this.dataset.read_function = this.options.read_function;
                this.dataset.create_function = function(data, options, sup) {
                    var fct = self.options.create_function || sup;
                    return fct.call(this, data, options).done(function(r) {
                        self.trigger('create_completed saved', r);
                        self.created_elements.push(r);
                    })
                };
                this.dataset.write_function = function(id, data, options, sup) {
                    var fct = self.options.write_function || sup;
                    return fct.call(this, id, data, options).done(function(r) {
                        self.trigger('write_completed saved', r);
                    });
                };
                this.dataset.parent_view = this.options.parent_view;
                this.dataset.child_name = this.options.child_name;
            };
            pop.select_element(
                "pos.order",
                {
                    title: "Buscar orden",
                    initial_view: "search",
                    disable_multiple_selection: true,
                    list_view_options: {limit: 14}
                },
                domain,
                {'search_default_customer': true}
            );

            pop.on("elements_selected", self, function (element_ids) {
                self.load_order(element_ids, options)
            });
        },
        can_refund: function () {
            var self = this;
            var discount_group = self.pos.discount_group;
            var current_user = (self.pos_widget.manager >= 1) ? self.pos_widget.manager : self.pos.user.id;
            var can_refund_product = false
            if (discount_group) {
                _.each(discount_group, function (group) {
                    _.each(group.users, function (user) {
                        if (current_user == user && group.refund) {
                            can_refund_product = true
                        }
                    });
                });
            }
            return can_refund_product
        },
        load_order: function (element_ids, options) {
            var self = this;
            self.pos.get('selectedOrder').destroy();
            var currentOrder = self.pos.get('selectedOrder');
            var action = options.action;

            new instance.web.Model("pos.order")
                .call("search_read", {domain: [["id", "=", element_ids[0]]], fields: []})
                .then(function (result) {
                    if (result && result.length == 1) {
                        var partner = self.pos.db.get_partner_by_id(result[0].partner_id[0]);
                        currentOrder.set_client(partner);
                        currentOrder.set("pos_reference", result[0].pos_reference);
                        currentOrder.set("name", result[0].pos_reference);
                        currentOrder.uid = result[0].pos_reference;
                        if (options.action === "refund") {
                            currentOrder.set("type", "refund");
                        }
                        new instance.web.Model("pos.order.line")
                            .call("search_read", {domain: [["order_id", "=", element_ids[0]]], fields: []})
                            .then(function (result) {
                                if (result) {
                                    var products = [];
                                    _.each(result, function (res) {
                                        var product = self.pos.db.get_product_by_id(res.product_id[0]);
                                        var options = {
                                            quantity: res.qty,
                                            price: res.price_unit,
                                            discount: res.discount
                                        };

                                        if (action === "pay") {

                                            currentOrder.addProduct(product, options);

                                        } else if (action === "refund") {

                                            product.qty_available = res.qty - res.return_qty;

                                        }

                                        products.push(product);

                                    });
                                    self.product_screen.product_list_widget.set_product_list(products);
                                }
                            })
                    }
                })
        },
        change_user: function () {
            var self = this;
            self.screen_selector.show_popup('marcos_input_popup_widget', {
                message: "Introduzca su clave de supervisor",
                input_type: "pwd",
                confirm: function () {
                    self.validate_user(this.$("#password").val());
                }
            });
        },
        validate_user: function (value) {
            var self = this;
            _.each(self.pos.users, function (user) {
                if (user.short_pwd === value) {
                    self.pos.barcode_reader.scan(user.ean13);
                    self.manager = user.id;
                    fast_login = true;
                }
            });

            if (fast_login) {
                return
            } else {
                return self.change_user();
            }
        },
        quotation: function () {
            var self = this;
            var currentOrder = self.pos.get('selectedOrder');

            if (currentOrder.get('orderLines').models.length === 0) {
                pop = new instance.web.form.SelectCreatePopup(this);
                pop.select_element(
                    "sale.order",
                    {
                        title: "Buscar cotización",
                        initial_view: "search",
                        disable_multiple_selection: true,
                        list_view_options: {limit: 14}
                    },
                    [['state', 'in', ['draft', 'sent']]],
                    {'search_default_customer': true}
                );
                pop.on("elements_selected", self, function (element_ids) {
                    self.load_quotation(currentOrder, element_ids)
                });

            } else {
                self.pos_widget.screen_selector.show_popup("confirm", {
                    'message': 'Como desea entregar esta cotización?',
                    'confirm': function () {
                        self.print_quotation();
                    },
                    'cancel': function () {
                        self.mail_quotation()
                    }
                });

            }

            self.$el.find(".popup-confirm").css('height', '130px');
            self.$el.find(".popup-confirm .footer .button.confirm").html("<i class='fa fa-file-text-o'></i> Impresora");
            self.$el.find(".popup-confirm .footer .button.cancel").html("<i class='fa fa-envelope'></i> Correo");
            self.$el.find(".popup-confirm .footer").append("<div class='button close_dialog'><i class='fa fa-ban'></i> Cancelar</div>");
            self.$el.find(".popup-confirm .footer .button.close_dialog").click(function () {
                self.pos_widget.screen_selector.close_popup();
            });


        },
        load_quotation: function (currentOrder, element_ids) {
            var self = this;
            new instance.web.Model("sale.order")
                .call("search_read", {domain: [["id", "=", element_ids[0]]], fields: []})
                .then(function (result) {
                    if (result && result.length == 1) {
                        var partner = self.pos.db.get_partner_by_id(result[0].partner_id[0]);
                        currentOrder.set_client(partner);

                        new instance.web.Model("sale.order.line")
                            .call("search_read", {domain: [["order_id", "=", element_ids[0]]], fields: []})
                            .then(function (result) {
                                if (result) {
                                    var products = [];
                                    _.each(result, function (res) {
                                        var product = self.pos.db.get_product_by_id(res.product_id[0]);
                                        var options = {
                                            quantity: res.product_uom_qty,
                                            price: res.price_unit,
                                            discount: res.discount,
                                            quotation: true
                                        };
                                        currentOrder.addProduct(product, options);
                                        products.push(product);

                                    });
                                    self.product_screen.product_list_widget.set_product_list(products);

                                }
                            });
                    }
                })
                .fail(function(err, event){
                       event.preventDefault();
                        self.pos_widget.screen_selector.show_popup('error',{
                            'message':_t('Funcionalidad inactiva'),
                            'comment':_t('Es accion requiere conexion al servidor!.')
                        });
                    });;

        },
        print_quotation: function () {
            var self = this;
            self.pos_widget.payment_screen.validate_order({action: "print_quotation"});
        },
        mail_quotation: function () {
            var self = this;
            self.pos_widget.payment_screen.validate_order({action: "send_quotation"});
        }
    });

    instance.point_of_sale.PaymentScreenWidget = instance.point_of_sale.PaymentScreenWidget.extend({

        validate_order: function (options) {
            var self = this;
            options = options || {};

            var currentOrder = this.pos.get('selectedOrder');

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


            if (!options.action) {
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
                    this.pos.push_order(currentOrder);
                    self.pos_widget.screen_selector.set_current_screen(this.next_screen);
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
        }
    });

    instance.point_of_sale.PosModel = instance.point_of_sale.PosModel.extend({

        push_order: function (order) {
            var self = this;
            if (order) {
                this.proxy.log('push_order', order.export_as_JSON());
                this.db.add_order(order.export_as_JSON());
            }

            var pushed = new $.Deferred();

            this.flush_mutex.exec(function () {
                var flushed = self._flush_orders(self.db.get_orders());

                flushed.always(function (ids) {
                    pushed.resolve();
                });
            });

            return pushed;
        },

        push_and_quotation_order: function (order, action) {
            var self = this;
            var invoiced = new $.Deferred();

            if (!order.get_client()) {
                invoiced.reject('error-no-client');
                return invoiced;
            }

            var order_id = this.db.add_order(order.export_as_JSON());

            this.flush_mutex.exec(function () {
                var done = new $.Deferred(); // holds the mutex

                // send the order to the server
                // we have a 30 seconds timeout on this push.
                // FIXME: if the server takes more than 30 seconds to accept the order,
                // the client will believe it wasn't successfully sent, and very bad
                // things will happen as a duplicate will be sent next time
                // so we must make sure the server detects and ignores duplicated orders

                var transfer = self._flush_orders([self.db.get_order(order_id)], {timeout: 30000, to_invoice: action});

                transfer.fail(function () {
                    invoiced.reject('error-transfer');
                    done.reject();
                });

                // on success, get the order id generated by the server
                transfer.pipe(function (order_server_id) {
                    self.pos_widget.do_action(order_server_id);
                    invoiced.resolve();
                    done.resolve();
                });
                return done;

            });

            return invoiced;
        },
        //do_reload_needaction: function () {
        //
        //},
        models: [
            {
                model: 'res.users',
                fields: ['name', 'company_id'],
                ids: function (self) {
                    return [self.session.uid];
                },
                loaded: function (self, users) {
                    self.user = users[0];
                }
            }, {
                model: 'pos.group.discount',
                fields: [],
                domain: null,
                loaded: function (self, discount_group) {
                    self.discount_group = discount_group;
                }

            }, {
                model: 'res.company',
                fields: ['currency_id', 'email', 'website', 'company_registry', 'vat', 'name', 'phone', 'partner_id', 'country_id'],
                ids: function (self) {
                    return [self.user.company_id[0]]
                },
                loaded: function (self, companies) {
                    self.company = companies[0];
                }
            }, {
                model: 'decimal.precision',
                fields: ['name', 'digits'],
                loaded: function (self, dps) {
                    self.dp = {};
                    for (var i = 0; i < dps.length; i++) {
                        self.dp[dps[i].name] = dps[i].digits;
                    }
                }
            }, {
                model: 'product.uom',
                fields: [],
                domain: null,
                loaded: function (self, units) {
                    self.units = units;
                    var units_by_id = {};
                    for (var i = 0, len = units.length; i < len; i++) {
                        units_by_id[units[i].id] = units[i];
                        units[i].groupable = ( units[i].category_id[0] === 1 );
                        units[i].is_unit = ( units[i].id === 1 );
                    }
                    self.units_by_id = units_by_id;
                }
            }, {
                model: 'res.users',
                fields: ['name', 'ean13', 'short_pwd'],
                domain: null,
                loaded: function (self, users) {
                    self.users = users;
                }
            }, {
                model: 'res.partner',
                fields: ['name', 'street', 'city', 'state_id', 'country_id', 'ref', 'phone', 'zip', 'mobile', 'email', 'ean13', 'write_date'],
                domain: [['customer', '=', true]],
                loaded: function (self, partners) {
                    self.partners = partners;
                    self.db.add_partners(partners);
                }
            }, {
                model: 'res.country',
                fields: ['name'],
                loaded: function (self, countries) {
                    self.countries = countries;
                    self.company.country = null;
                    for (var i = 0; i < countries.length; i++) {
                        if (countries[i].id === self.company.country_id[0]) {
                            self.company.country = countries[i];
                        }
                    }
                }
            }, {
                model: 'account.tax',
                fields: ['name', 'amount', 'price_include', 'include_base_amount', 'type'],
                domain: null,
                loaded: function (self, taxes) {
                    self.taxes = taxes;
                    self.taxes_by_id = {};
                    for (var i = 0; i < taxes.length; i++) {
                        self.taxes_by_id[taxes[i].id] = taxes[i];
                    }
                }
            }, {
                model: 'pos.session',
                fields: ['id', 'journal_ids', 'name', 'user_id', 'config_id', 'start_at', 'stop_at', 'sequence_number', 'login_number'],
                domain: function (self) {
                    return [['state', '=', 'opened'], ['user_id', '=', self.session.uid]];
                },
                loaded: function (self, pos_sessions) {
                    self.pos_session = pos_sessions[0];

                    var orders = self.db.get_orders();
                    for (var i = 0; i < orders.length; i++) {
                        self.pos_session.sequence_number = Math.max(self.pos_session.sequence_number, orders[i].data.sequence_number + 1);
                    }
                }
            }, {
                model: 'pos.config',
                fields: [],
                domain: function (self) {
                    return [['id', '=', self.pos_session.config_id[0]]];
                },
                loaded: function (self, configs) {
                    self.config = configs[0];
                    self.config.use_proxy = self.config.iface_payment_terminal ||
                    self.config.iface_electronic_scale ||
                    self.config.iface_print_via_proxy ||
                    self.config.iface_scan_via_proxy ||
                    self.config.iface_cashdrawer;

                    self.barcode_reader.add_barcode_patterns({
                        'product': self.config.barcode_product,
                        'cashier': self.config.barcode_cashier,
                        'client': self.config.barcode_customer,
                        'weight': self.config.barcode_weight,
                        'discount': self.config.barcode_discount,
                        'price': self.config.barcode_price
                    });

                    if (self.config.company_id[0] !== self.user.company_id[0]) {
                        throw new Error(_t("Error: The Point of Sale User must belong to the same company as the Point of Sale. You are probably trying to load the point of sale as an administrator in a multi-company setup, with the administrator account set to the wrong company."));
                    }
                }
            }, {
                model: 'stock.location',
                fields: [],
                ids: function (self) {
                    return [self.config.stock_location_id[0]];
                },
                loaded: function (self, locations) {
                    self.shop = locations[0];
                }
            }, {
                model: 'product.pricelist',
                fields: ['currency_id'],
                ids: function (self) {
                    return [self.config.pricelist_id[0]];
                },
                loaded: function (self, pricelists) {
                    self.pricelist = pricelists[0];
                }
            }, {
                model: 'res.currency',
                fields: ['symbol', 'position', 'rounding', 'accuracy'],
                ids: function (self) {
                    return [self.pricelist.currency_id[0]];
                },
                loaded: function (self, currencies) {
                    self.currency = currencies[0];
                    if (self.currency.rounding > 0) {
                        self.currency.decimals = Math.ceil(Math.log(1.0 / self.currency.rounding) / Math.log(10));
                    } else {
                        self.currency.decimals = 0;
                    }

                }
            }, {
                model: 'product.packaging',
                fields: ['ean', 'product_tmpl_id'],
                domain: null,
                loaded: function (self, packagings) {
                    self.db.add_packagings(packagings);
                }
            }, {
                model: 'pos.category',
                fields: ['id', 'name', 'parent_id', 'child_id', 'image'],
                domain: null,
                loaded: function (self, categories) {
                    self.db.add_categories(categories);
                }
            }, {
                model: 'product.product',
                fields: ['display_name', 'list_price', 'price', 'pos_categ_id', 'taxes_id', 'ean13', 'default_code',
                    'to_weight', 'uom_id', 'uos_id', 'uos_coeff', 'mes_type', 'description_sale', 'description',
                    'product_tmpl_id'],
                domain: [['sale_ok', '=', true], ['available_in_pos', '=', true]],
                context: function (self) {
                    return {pricelist: self.pricelist.id, display_default_code: false};
                },
                loaded: function (self, products) {
                    self.db.add_products(products);
                }
            }, {
                model: 'account.bank.statement',
                fields: ['account_id', 'currency', 'journal_id', 'state', 'name', 'user_id', 'pos_session_id'],
                domain: function (self) {
                    return [['state', '=', 'open'], ['pos_session_id', '=', self.pos_session.id]];
                },
                loaded: function (self, bankstatements, tmp) {
                    self.bankstatements = bankstatements;

                    tmp.journals = [];
                    _.each(bankstatements, function (statement) {
                        tmp.journals.push(statement.journal_id[0]);
                    });
                }
            },
            {
                model: 'account.journal',
                fields: [],
                domain: function (self, tmp) {
                    return [['id', 'in', tmp.journals]];
                },
                loaded: function (self, journals) {
                    self.journals = journals;

                    // associate the bank statements with their journals.
                    var bankstatements = self.bankstatements;
                    for (var i = 0, ilen = bankstatements.length; i < ilen; i++) {
                        for (var j = 0, jlen = journals.length; j < jlen; j++) {
                            if (bankstatements[i].journal_id[0] === journals[j].id) {
                                bankstatements[i].journal = journals[j];
                            }
                        }
                    }
                    self.cashregisters = bankstatements;
                }
            }, {
                label: 'fonts',
                loaded: function (self) {
                    var fonts_loaded = new $.Deferred();

                    // Waiting for fonts to be loaded to prevent receipt printing
                    // from printing empty receipt while loading Inconsolata
                    // ( The font used for the receipt )
                    waitForWebfonts(['Lato', 'Inconsolata'], function () {
                        fonts_loaded.resolve();
                    });

                    // The JS used to detect font loading is not 100% robust, so
                    // do not wait more than 5sec
                    setTimeout(function () {
                        fonts_loaded.resolve();
                    }, 5000);

                    return fonts_loaded;
                }
            }, {
                label: 'pictures',
                loaded: function (self) {
                    self.company_logo = new Image();
                    var logo_loaded = new $.Deferred();
                    self.company_logo.onload = function () {
                        var img = self.company_logo;
                        var ratio = 1;
                        var targetwidth = 300;
                        var maxheight = 150;
                        if (img.width !== targetwidth) {
                            ratio = targetwidth / img.width;
                        }
                        if (img.height * ratio > maxheight) {
                            ratio = maxheight / img.height;
                        }
                        var width = Math.floor(img.width * ratio);
                        var height = Math.floor(img.height * ratio);
                        var c = document.createElement('canvas');
                        c.width = width;
                        c.height = height
                        var ctx = c.getContext('2d');
                        ctx.drawImage(self.company_logo, 0, 0, width, height);

                        self.company_logo_base64 = c.toDataURL();
                        logo_loaded.resolve();
                    };
                    self.company_logo.onerror = function () {
                        logo_loaded.reject();
                    };
                    self.company_logo.crossOrigin = "anonymous";
                    self.company_logo.src = '/web/binary/company_logo' + '?_' + Math.random();

                    return logo_loaded;
                }
            },
        ]
    });

    instance.point_of_sale.PosDB = instance.point_of_sale.PosDB.extend({
        _partner_search_string: function (partner) {
            var str = partner.name;

            if (partner.ean13) {
                str += '|' + partner.ean13;
            }
            if (partner.address) {
                str += '|' + partner.address;
            }
            if (partner.phone) {
                str += '|' + partner.phone.split(' ').join('');
            }
            if (partner.mobile) {
                str += '|' + partner.mobile.split(' ').join('');
            }
            if (partner.email) {
                str += '|' + partner.email;
            }
            if (partner.ref) {
                str += '|' + partner.ref;
            }
            str = '' + partner.id + ':' + str.replace(':', '') + '\n';
            return str;
        }
    });

    instance.point_of_sale.OrderWidget = instance.point_of_sale.OrderWidget.extend({
        init: function (parent, options) {
            var self = this;
            this._super(parent, options);
            this.summary_selected = false;

            var line_click_handler = this.line_click_handler;
            this.line_click_handler = function (event) {
                self.deselect_summary();
                line_click_handler.call(this, event)
            }
        },
        select_summary: function () {
            if (this.summary_selected)
                return;
            this.deselect_summary();
            this.summary_selected = true;
            $('.order .summary').addClass('selected')
            this.pos_widget.numpad.state.reset();
            this.pos_widget.numpad.state.changeMode('discount');
        },
        deselect_summary: function () {
            this.summary_selected = false;
            $('.order .summary').removeClass('selected')
        },
        set_value: function (val) {
            if (!this.summary_selected)
                return this._super(val);
            var mode = this.numpad_state.get('mode');
            if (mode == 'discount') {
                var order = this.pos.get('selectedOrder');
                $.each(order.get('orderLines').models, function (k, line) {
                    line.set_discount(val)
                })
            }
        },
        renderElement: function (scrollbottom) {
            var self = this;
            this._super(scrollbottom);

            $('.order .summary').click(function (event) {
                if (!self.editable) {
                    return;
                }
                self.pos.get('selectedOrder').deselectLine(this.orderline);
                self.pos_widget.numpad.state.reset();

                self.select_summary()
            })
        }
    });

    instance.web.View.include({
        //Override by Eneldo to prevent exception
        do_execute_action: function (action_data, dataset, record_id, on_closed) {
            var self = this;
            var result_handler = function () {
                if (on_closed) {
                    on_closed.apply(null, arguments);
                }
                if (self.getParent() && self.getParent().on_action_executed) {
                    return self.getParent().on_action_executed.apply(null, arguments);
                }
            };
            var context = new instance.web.CompoundContext(dataset.get_context(), action_data.context || {});

            // response handler
            var handler = function (action) {
                if (action && action.constructor == Object) {
                    // filter out context keys that are specific to the current action.
                    // Wrong default_* and search_default_* values will no give the expected result
                    // Wrong group_by values will simply fail and forbid rendering of the destination view
                    var ncontext = new instance.web.CompoundContext(
                        _.object(_.reject(_.pairs(dataset.get_context().eval()), function (pair) {
                            return pair[0].match('^(?:(?:default_|search_default_).+|.+_view_ref|group_by|group_by_no_leaf|active_id|active_ids)$') !== null;
                        }))
                    );
                    ncontext.add(action_data.context || {});
                    ncontext.add({active_model: dataset.model});
                    if (record_id) {
                        ncontext.add({
                            active_id: record_id,
                            active_ids: [record_id]
                        });
                    }
                    ncontext.add(action.context || {});
                    action.context = ncontext;
                    return self.do_action(action, {
                        on_close: result_handler
                    });
                } else {
                    self.do_action({"type": "ir.actions.act_window_close"});
                    return result_handler();
                }
            };

            if (action_data.special === 'cancel') {
                return handler({"type": "ir.actions.act_window_close"});
            } else if (action_data.type == "object") {
                var args = [[record_id]];
                if (action_data.args) {
                    try {
                        // Warning: quotes and double quotes problem due to json and xml clash
                        // Maybe we should force escaping in xml or do a better parse of the args array
                        var additional_args = JSON.parse(action_data.args.replace(/'/g, '"'));
                        args = args.concat(additional_args);
                    } catch (e) {
                        console.error("Could not JSON.parse arguments", action_data.args);
                    }
                }
                args.push(context);

                return dataset.call_button(action_data.name, args).then(handler)
                    .then(function () {
                        //Override by Eneldo to prevent exception when instance.webclient.menu.do_reload_needaction === undefined
                        try {
                            if (instance.webclient) {
                                instance.webclient.menu.do_reload_needaction();
                            }
                        } catch (err) {
                            console.error(err);
                        };

                    });
            } else if (action_data.type == "action") {
                return this.rpc('/web/action/load', {
                    action_id: action_data.name,
                    context: _.extend(instance.web.pyeval.eval('context', context), {
                        'active_model': dataset.model,
                        'active_ids': dataset.ids,
                        'active_id': record_id
                    }),
                    do_not_eval: true
                }).then(handler);
            } else {
                return dataset.exec_workflow(record_id, action_data.name).then(handler);
            }
        }
    });

    instance.point_of_sale.Orderline = instance.point_of_sale.Orderline.extend({


        set_note: function (note) {
            this.set('note', note)
        },
        get_note: function () {
            return this.get('note');
        },

        set_discount: function (discount) {
            var self = this;
            var can_discount = self.validate_discount(discount);
            if (can_discount) {
                var disc = Math.min(Math.max(parseFloat(discount) || 0, 0), 100);
                this.discount = disc;
                this.discountStr = '' + disc;
                this.trigger('change', this);
            }
        },
        validate_discount: function (discount) {
            var self = this;
            var amount_list = [];
            var discount_group = self.pos.discount_group;
            var current_user = (self.pos.pos_widget.manager >= 1) ? self.pos.pos_widget.manager : self.pos.user.id;
            if (discount_group) {
                var max_disc = 0;
                _.each(discount_group, function (group) {
                    _.each(group.users, function (user) {
                        if (current_user == user) {
                            amount_list.push(group.max_disc);
                        }
                    })
                });

                if (amount_list.length > 1) {
                    max_disc = _.max(amount_list);
                } else {
                    max_disc = amount_list[0]
                }
                var msg = "";
                if (max_disc) {
                    msg = 'Usted no esta autorizado a dar descuentos de mas de un ' + max_disc.toString() + "% !"
                } else {
                    msg = "Usted no esta autorizado a dar descuentos!"
                }

                if (discount <= max_disc) {
                    return true
                } else {
                    self.pos.pos_widget.screen_selector.show_popup('error', {
                        'message': _t('Descuento rechazado'),
                        'comment': _t(msg)
                    });
                    return;
                }

            } else {
                return false
            }

        }
    });

    instance.point_of_sale.NumpadWidget = instance.point_of_sale.NumpadWidget.extend({

        clickChangeMode: function (event) {
            var self = this;
            var newMode = event.currentTarget.attributes['data-mode'].nodeValue;
            if (newMode != 'price') {
                return this.state.changeMode(newMode);
            }
            else if (newMode === 'price' && self.can_change_price()) {
                return this.state.changeMode(newMode);
            } else {
                self.pos.pos_widget.screen_selector.show_popup('error', {
                    'message': _t('Acceso negado'),
                    'comment': _t('No tiene permiso para cambiar el precio!')
                });
            }
        },
        can_change_price: function () {
            var self = this;
            var discount_group = self.pos.discount_group;
            var current_user = (self.pos_widget.manager >= 1) ? self.pos_widget.manager : self.pos.user.id;
            var can_change_price = false
            if (discount_group) {
                _.each(discount_group, function (group) {
                    _.each(group.users, function (user) {
                        if (current_user == user && group.change_price) {
                            can_change_price = true
                        }
                    });
                });
            }
            return can_change_price
        }
    });

    local.MarcosPaypadButtonWidget = instance.point_of_sale.PosBaseWidget.extend({
        template: 'MarcosPaypadButtonWidget',
        init: function (parent, options) {
            options = options || {};
            this._super(parent, options);
            this.action = options.action;
            this.class = options.class;
            this.caption = options.caption;
        },
        renderElement: function () {
            var self = this;
            this._super();
            if (this.action) {

                this.$el.click(function () {
                    self.action();
                });
            }
        }
    });

    instance.point_of_sale.PaypadWidget = instance.point_of_sale.PosBaseWidget.extend({
        template: 'PaypadWidget',
        renderElement: function () {
            var self = this;
            this._super();

            var payment_pos = self.pos.config.payment_pos

            // sort cashregisters by sequence
            this.pos.cashregisters.sort(function (obj1, obj2) {
                return obj1.journal.sequence - obj2.journal.sequence;
            });

            if (payment_pos) {
                var button = new local.MarcosPaypadButtonWidget(this, {
                    caption: "Enviar a caja",
                    action: function () {
                        self.to_cashier();
                    }
                });

                button.appendTo(self.$el);

            } else {

                _.each(this.pos.cashregisters, function (cashregister) {

                    var button = new instance.point_of_sale.PaypadButtonWidget(self, {
                        pos: self.pos,
                        pos_widget: self.pos_widget,
                        cashregister: cashregister
                    });
                    button.appendTo(self.$el);
                });
            }

        },
        to_cashier: function () {
            var self = this;
            var currentOrder = self.pos.get('selectedOrder');
            if (currentOrder.get("client")) {
                self.send_to_cashier({action: "send_to_cashier"});
            } else {
                self.pos_widget.screen_selector.show_popup(
                    'marcos_input_popup_widget', {
                        message: "Introduzca un nombre que identifique al cliente para el cajero",
                        confirm: function () {
                            self.validate_before_send(this.$("#ref_name").val());
                        }

                    });

            }
        },
        validate_before_send: function (ref_name) {
            var self = this;
            if (ref_name.length > 0) {
                self.send_to_cashier({action: "send_to_cashier_with_ref_name", ref_name: ref_name});

            } else {
                self.to_cashier({})

            }
        },
        send_to_cashier: function (options) {
            var self = this;
            if (options.action === "send_to_cashier_with_ref_name") {
                self.pos_widget.payment_screen.validate_order({
                    action: "send_to_cashier_with_ref_name",
                    ref_name: options.ref_name
                });
            } else {
                self.pos_widget.payment_screen.validate_order({action: "send_to_cashier"});
            }

        }
    });

    instance.point_of_sale.OrderWidget = instance.point_of_sale.OrderWidget.extend({
        render_orderline: function (orderline) {
            var self = this;
            var el_str = openerp.qweb.render('Orderline', {widget: this, line: orderline});
            var el_node = document.createElement('div');
            el_node.innerHTML = _.str.trim(el_str);
            el_node = el_node.childNodes[0];
            el_node.orderline = orderline;
            el_node.addEventListener('click', this.line_click_handler);
            new instance.web.Model("stock.quant")
                .call("get_product_qty_in_location", [orderline.product.id, self.pos.shop.id])
                .then(function (result) {
                    _.each(result, function (item) {
                        if (item) {
                            $(el_node).find("li.info")
                                .append('<a class="product-available">(de <span>' + item[4] + '</span>)</a>')
                                .on("click", function () {
                                    self.showProductAvailablePop(orderline)
                                });
                        }
                    });
                })
                .fail(function(err, event){
                    event.preventDefault();
                });
            orderline.node = el_node;
            return el_node;
        },
        showProductAvailablePop: function (orderline) {
            var self = this;
            new instance.web.Model("stock.quant")
                .call("get_product_qty_by_location", [orderline.product.id])
                .then(function (result) {
                    var li_node = "";
                    _.each(result, function (li) {
                        li_node += "<li>" + li[1] + " -- " + li[4] + "</li><br/>"
                    });
                    self.pos_widget.screen_selector.show_popup('marcos_product_available_popup_widget', {
                        message: "Inventario por almacen",
                        location_qty: li_node
                    });

                })
                .fail(function(err, event){
                       event.preventDefault();
                        self.pos_widget.screen_selector.show_popup('error',{
                            'message':_t('Funcionalidad inactiva'),
                            'comment':_t('Es accion requiere conexion al servidor!.')
                        });
                });
        }
    });



    instance.point_of_sale.ProxyDevice = instance.point_of_sale.ProxyDevice.extend({

        print_receipt: function(receipt){
            var self = this;
            if(receipt){
                this.receipt_queue.push(receipt);
            }
            var aborted = false;
            function send_printing_job(){
                if (self.receipt_queue.length > 0){
                    var r = self.receipt_queue.shift();
                    self.message('print_xml_receipt',{ receipt: r },{ timeout: 5000 })
                        .then(function(){
                            send_printing_job();
                        },function(error){
                            if (error) {
                                self.pos.pos_widget.screen_selector.show_popup('error-traceback',{
                                    'message': _t('Printing Error: ') + error.data.message,
                                    'comment': error.data.debug
                                });
                                return;
                            }
                            self.receipt_queue.unshift(r)
                        });
                }
            }
            if (self.pos.config.ipf_printer){
                var order = self.pos.get('selectedOrder')
                new instance.web.Model("ipf.printer.config")
                .call("print_precuenta", [order.export_as_JSON()])
            } else {
                send_printing_job();
            }

        }
    });
};