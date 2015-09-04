function marcos_pos_device(instance, module) {

        module.ProxyDevice = module.ProxyDevice.extend({

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

}