<form id="general_form" data-dojo-type="dijit.form.Form" data-dojo-props="action: '/general/update', method: 'post'">
    <script type="dojo/connect", event="onSubmit">
        dojo.publish('form_submit', [this.domNode, arguments[0]]);
    </script>
    <table>
        <tr>
            <td class="left_td_label"><label for="general_charset">编码:</label></td>
            <td><input id="general_charset" data-dojo-type="dijit.form.TextBox" data-dojo-props="name: 'charset', class: 'wide_input', value:'utf8'" /></td>
        </tr>
        <tr>
            <td class="left_td_label"><label for="general_headers">Headers:</label></td>
            <td><textarea id="general_headers" data-dojo-type="dijit.form.SimpleTextarea" data-dojo-props="name: 'headers', cols: 3, class: 'simple_textarea'"></textarea></td>
        </tr>
        <tr>
            <td class="left_td_label"></td>
            <td>
                <button data-dojo-type="dijit.form.Button" data-dojo-props="type:'submit'">应用</button>
                <button data-dojo-type="dijit.form.Button" data-dojo-props="type:'reset'">重置</button>
            </td>
        </tr>
    </table>
</form>
