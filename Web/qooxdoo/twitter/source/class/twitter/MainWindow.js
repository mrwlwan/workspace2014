qx.Class.define("twitter.MainWindow", {
    extend: qx.ui.window.Window,
    construct: function(){
        this.base(arguments, 'twitter');
        this.setShowClose(false);
        this.setShowMaximize(false);
        this.setShowMinimize(false);
        this.setWidth(250);
        this.setHeight(300);
        this.setContentPadding(0);

        var layout =  new qx.ui.layout.Grid(0, 0);
        layout.setRowFlex(1,1);
        layout.setColumnFlex(0,1);
        this.setLayout(layout);
        
        var toolbar = new qx.ui.toolbar.ToolBar();
        var reloadButton = new qx.ui.toolbar.Button('Reload');
        reloadButton.addListener('execute', function(){
            this.fireEvent('reload');
        }, this);
        toolbar.add(reloadButton);
        this.add(toolbar, {row: 0, column: 0, colSpan:2});

        this.__list = new qx.ui.form.List();
        this.add(this.__list, {row:1, column:0, colSpan:2});

        this.__textarea = new qx.ui.form.TextArea();
        this.__textarea.setPlaceholder('Enter your message here ...');
        this.__textarea.addListener('input', function(e){
            var value = e.getData();
            postButton.setEnabled(value.length < 140 && value.length >0);
        }, this);
        this.add(this.__textarea, {row:2, column:0});

        var postButton = new qx.ui.form.Button('Post');
        postButton.setEnabled(false);
        postButton.setWidth(60);
        postButton.addListener('execute', function(){
            this.fireDataEvent('post', this.__textarea.getValue());
        }, this);
        this.add(postButton, {row:2, column:1});
    },
    members: {
        __list: null,
        __textarea: null,

        getList: function(){
            return this.__list;
        },
        clearPostMessage: function(){
            this.__textarea.setValue(null);
        }
    },
    events:{
        'reload': 'qx.event.type.Event',
        'post': 'qx.event.type.Data'
    }
});
