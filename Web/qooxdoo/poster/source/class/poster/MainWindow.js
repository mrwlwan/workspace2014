qx.Class.define("poster.MainWindow", {
    extend: qx.ui.window.Window,
    construct: function(){
        this.base(arguments, "灌水无罪 :P");
        this.setShowClose(false);
        this.setShowMinimize(false);
        this.setShowMaximize(false);
        this.setResizable(false);
        this.setWidth(450);
        this.setHeight(500);
        //this.setMovable(false);
        var main_layout = new qx.ui.layout.Grid(0, 0);
        main_layout.setRowFlex(0,1);
        main_layout.setColumnFlex(0,1);
        this.setLayout(main_layout);
        this.setContentPadding(0);
        
        var container = new qx.ui.tabview.TabView();
        this.add(container, {row:0, column:0});

        // Global page
        var global_page = new poster.MainPage(new poster.GlobalForm, {title: 'Global'});
        container.add(global_page);

        // Config page
        var config_page = new poster.MainPage(new poster.ConfigForm('Section1'), {title: '配置'});
        config_page.add_form(new poster.ConfigForm('Section2'));
        container.add(config_page);

        var login_page = new qx.ui.tabview.Page("登录");
        var login_layout = new qx.ui.layout.Grid(0, 0);
        login_page.setLayout(login_layout);
        container.add(login_page);
        //container.setSelection([login_page]);

        var act_button = new qx.ui.form.Button("运行");
        this.add(act_button, {row: 1, column: 0});
        
        // 事件处理
        // F12 toggle global_button
        this.addListener('keypress', function(e){
            if(e.getKeyIdentifier() == 'F12'){
                //global_page.toggleEnabled();
            }
        });

    },

    events: {
    },

    members: {
        __global_configs: null,
        __section_configs:  null,
        __login_datas: null
    }
});
