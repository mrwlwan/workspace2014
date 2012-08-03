qx.Class.define("poster.MainPage", {
    extend: qx.ui.tabview.Page,
    
    construct: function(form, options){
        this.base(arguments, options['title']);
        //this.__form = form;
        //this.__model = form.__model;
        this.setLayout(new qx.ui.layout.VBox())
        this.__scroll = new qx.ui.container.Scroll().set({height: 370});
        this.add(this.__scroll);
        this.__root = new qx.ui.container.Composite(new qx.ui.layout.VBox());
        this.__scroll.add(this.__root, {flex:1});
        this.__root.add(form.__render, {flex:1});
    },

    members: {
        __root: null,
        //__form: null,
        //__model: null,
        add_form: function(form){
            this.__root.add(form.__render, {flex:1});
        }
    }
});
