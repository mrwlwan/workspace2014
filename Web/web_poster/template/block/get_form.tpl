<form id="get_form" data-dojo-type="dijit.form.Form" data-dojo-props="action: '/fetch/content', method: 'post'">
    <script type="dojo/connect", event="onSubmit">
        dojo.publish('form_submit', [this.domNode, arguments[0]]);
    </script>
    <table>
        <tr>
            <td class="left_td_label"><label for="get_method">方法:</label></td>
            <td>
                <select id="get_method" data-dojo-type="dijit.form.ComboBox" data-dojo-props="name: 'method', style:'width:5em', onChange: is_change_method"/>
                    <option value="GET" selected>GET</option>
                    <option value="POST">POST</option>
                </select>
            </td>
        </tr>
        <tr>
            <td class="left_td_label"><label for="get_url">目标链接:</label></td>
            <td><input id="get_url" data-dojo-type="dijit.form.SimpleTextarea" data-dojo-props="name: 'url', rows: 3, class: 'simple_textarea'" /></td>
        </tr>
        <tr>
            <td class="left_td_label"><label for="get_data">附加数据:</label></td>
            <td><input id="get_data" data-dojo-type="dijit.form.SimpleTextarea" data-dojo-props="name: 'data', rows: 3, class: 'simple_textarea', disabled: true" /></td>
        </tr>
        <tr>
            <td class="left_td_label"></td>
            <td><input id="get_is_has_code" data-dojo-type="dijit.form.CheckBox" data-dojo-props="value: 1, name: 'is_has_code', onChange: is_has_code, disabled: true"/><label for="get_is_has_code">需要验证码</label></td>
        </tr>
        <tr>
            <td class="left_td_label"><label for="get_image_url">图片链接:</label></td>
            <td><input id="get_code_image_url" data-dojo-type="dijit.form.TextBox" data-dojo-props="name: 'code_image_url', class: 'wide_input', disabled: true" /></td>
        </tr>
        <tr>
        <tr>
            <td class="left_td_label"><label for="get_code_image">图片:</label></td>
            <td>
                <img id="get_code_image" />
                <button id="get_code_image_bn" data-dojo-type="dijit.form.Button" data-dojo-props="disabled: true, onClick: refresh_code_image">获取图片</button>
            </td>
        </tr>
        <tr>
            <td class="left_td_label"><label for="get_code_key">验证码Key:</label></td>
            <td><input id="get_code_key" data-dojo-type="dijit.form.TextBox" data-dojo-props="name: 'code_key', class: 'wide_input', disabled: true" /></td>
        </tr>
        <tr>
            <td class="left_td_label"><label for="get_code">验证码:</label></td>
            <td><input id="get_code" data-dojo-type="dijit.form.TextBox" data-dojo-props="name: 'code', class: 'wide_input', disabled: true" /></td>
        </tr>
        <tr>
            <td class="left_td_label"></td>
            <td>
                <button data-dojo-type="dijit.form.Button" data-dojo-props="type:'submit'">抓取</button>
                <button data-dojo-type="dijit.form.Button" data-dojo-props="type:'reset'">重置</button>
                <button data-dojo-type="dijit.form.Button" data-dojo-props="onClick: simple_xhr('/show/content?raw=')">显示内容</button>
                <button data-dojo-type="dijit.form.Button" data-dojo-props="onClick: simple_xhr('/show/request_info')">Request Info</button>
                <button data-dojo-type="dijit.form.Button" data-dojo-props="onClick: simple_xhr('/show/response_info')">Response Info</button>
                <button data-dojo-type="dijit.form.Button" data-dojo-props="onClick: simple_xhr('/show/request_headers')">Request Headers</button>
            </td>
        </tr>
    </table>
</form>
