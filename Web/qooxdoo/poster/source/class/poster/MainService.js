qx.Class.define('poster.MainService', {
    extend: qx.core.Object,

    members: {
        __global: null,

        fetch_global: function(){
            if(this.__global == null){
                var url = 'http://127.0.0.1:8080/fetch_global';
                this.__global = qx.data.store.Jsonp(url, null, 'callback');
                alert(this.__global);
            }
        }
    }
});
