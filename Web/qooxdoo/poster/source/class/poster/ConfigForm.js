qx.Class.define("poster.ConfigForm", {
    extend: qx.ui.form.Form,
    
    construct: function(header){
        this.base(arguments);
        this.addGroupHeader(header);
        var section_field = new qx.ui.form.TextField();
        this.add(section_field, '', null, header);
        section_field.hide();
        section_field.setVisibility('excluded');
        this.add(new qx.ui.form.TextArea().set({width: 300, height:50}), '账号', null, 'auths');
        this.add(new qx.ui.form.TextArea().set({width: 300, height:50}), '灌水帖子', null, 'target_urls');
        this.add(new qx.ui.form.Spinner().set({width: 50, minimum:0}), '时间间隔', null, 'delay');
        this.add(new qx.ui.form.CheckBox().set({width: 300}), '重复', null, 'is_repeat');
        this.add(new qx.ui.form.CheckBox().set({width: 300}), '随机', null, 'is_random');
        this.add(new qx.ui.form.TextField().set({width: 300}), '灌水文件', null, 'target_filename');

        var apply_button = new qx.ui.form.Button('应用');
        this.addButton(apply_button.set({width:100}), '', null, 'apply');

        this.__render = new qx.ui.form.renderer.Single(this);
        this.__controller = new qx.data.controller.Form(null, this);

        apply_button.addListener('click', function(){
            alert(123);
            this.fetch_global();
            alert(456);
        }, this);
    },

    properties: {
        tweets: {
            nullable: true,
            event: "changeTweets"
        }
    },

    members: {
        __model: null,
        __render: null,
        __store: null,
        __controller: null,

        fetch_global: function(){
            if(this.__global == null){
                var url = 'http://127.0.0.1:8080/fetch_global';
                var store = new qx.data.store.Jsonp(url);
                alert(store.getModel());
                //this.__store = qx.data.marshal.Json.createModel({auths:'abcdefg'});
                //alert(this.__store.getState());
                //alert(this.__store.getModel());
                //this.__store.bind('model', this.__controller, 'model');
                //alert(this.__controller.createModel().getAuths());
                //this.bind('tweets', this, '__model');
            }
        }
    },

    events: {
    }
});
