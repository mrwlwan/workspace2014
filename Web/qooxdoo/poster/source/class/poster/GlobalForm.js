qx.Class.define("poster.GlobalForm", {
    extend: qx.ui.form.Form,
    
    construct: function(){
        this.base(arguments);
        this.addGroupHeader('Login');
        this.add(new qx.ui.form.TextField().set({width: 300}), 'Url', null, 'login_url');
        this.add(new qx.ui.form.TextField().set({width: 300}), 'User Key', null, 'login_user_key');
        this.add(new qx.ui.form.TextField().set({width: 300}), 'Password Key', null, 'login_password_key');
        this.add(new qx.ui.form.TextField().set({width: 300}), 'Code Key', null, 'login_code_key');
        this.add(new qx.ui.form.TextField().set({width: 300}), 'Code Url', null, 'login_code_url');
        this.add(new qx.ui.form.TextField().set({width: 300}), 'Check Url', null, 'check_url');
        this.add(new qx.ui.form.TextField().set({width: 300}), 'Check Data', null, 'check_data');
        this.addGroupHeader('Post');
        this.add(new qx.ui.form.TextField().set({width: 300}), 'Post Url', null, 'post_url');
        this.add(new qx.ui.form.TextField().set({width: 300}), 'Pre Data', null, 'pre_post_data');
        this.add(new qx.ui.form.TextField().set({width: 300}), 'Reg', null, 'post_data_reg');
        this.add(new qx.ui.form.TextField().set({width: 300}), 'Content Key', null, 'post_content_key');
        this.addGroupHeader('Misc')
        this.add(new qx.ui.form.TextField().set({width: 300}), 'Charset', null, 'charset');
        this.add(new qx.ui.form.TextField().set({width: 300}), 'Timeout', null, 'timeout');
        this.add(new qx.ui.form.TextField().set({width: 300}), 'Cookie File', null, 'cookie_filename');
        this.__render = new qx.ui.form.renderer.Single(this);
        var controller = new qx.data.controller.Form(null, this);
        this.__model = controller.createModel();
    },

    members: {
        __model: null,
        __render: null
    }
});
