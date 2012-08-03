<div jsId="session_json" id="session_json" data-dojo-type="dojo.data.ItemFileReadStore" data-dojo-props="url: '/session/json', clearOnClose: true, urlPreventCache: true"></div>
<form id="session_form" data-dojo-type="dijit.form.Form" data-dojo-props="action: '/session/load', method: 'post'">
    <script type="dojo/connect", event="onSubmit">
        dojo.publish('form_submit', [this.domNode, arguments[0]]);
    </script>
    <table>
        <tr>
            <td class="left_td_label"><label for="session_session">Sessions:</label></td>
            <td><select id="session_session" data-dojo-type="dijit.form.ComboBox" data-dojo-props="name: 'session', class: 'wide_input', store: session_json, searchAttr: 'name'"></select></td>
        </tr>
        <tr>
            <td class="left_td_label"></td>
            <td>
                <button data-dojo-type="dijit.form.Button" data-dojo-props="onClick: save_session">保存</button>
                <button data-dojo-type="dijit.form.Button" data-dojo-props="onClick: load_session">加载</button>
                <button data-dojo-type="dijit.form.Button" data-dojo-props="onClick: remove_session">删除</button>
                <button data-dojo-type="dijit.form.Button" data-dojo-props="onClick: clear_session">清空</button>
            </td>
        </tr>
    </table>
</form>
