odoo.define('whatever.filter_button', function (require) {
    "use strict";


    var core = require('web.core');
    var ListController = require('web.ListController');
    // var ListView = require('web.ListView');
    // var QWeb = core.qweb;


    ListController.include({

        renderButtons: function ($node) {

            this._super.apply(this, arguments);
            if (this.$buttons) {

                let filter_button = this.$buttons.find('.oe_filter_button');

                filter_button && filter_button.click(this.proxy('filter_button'));

                this.$buttons.find('.oe_filter_button2').click(this.proxy('tree_view_action'));

            }

        },

        filter_button: function () {

            console.log('yay filter')

            //implement your click logic here

        },

        tree_view_action: function () {
            console.log('here');
            // this will create form, should extended it
            this.do_action({
                type: "ir.actions.act_window",
                name: "product",
                res_model: "product.template",          // here choose the model to add new entry
                views: [[false, 'form']],
                target: 'current',
                view_type: 'form',
                view_mode: 'form',
                flags: {'form': {'action_buttons': true, 'options': {'mode': 'edit'}}}
            });
            return {'type': 'ir.actions.client', 'tag': 'reload',}
        }

    });

});