<form id="search_form" data-dojo-type="dijit.form.Form" data-dojo-props="action: '/search'">
    <script type="dojo/connect", event="onSubmit">
        dojo.publish('form_submit', [this.domNode, arguments[0]]);
    </script>
    <table>
        <tr>
            <td class="td_label"></td>
            <td>
                <input id="search_is_fetch_text" data-dojo-type="dijit.form.CheckBox" data-dojo-props="name: 'search_is_fetch_text', value: '1', onChange: search_use_fetch_content" /><label for="search_is_fetch_text" >应用抓取到的网页文本</label>
            </td>
        </tr>
        <tr>
            <td class="td_label"><label for="search_text">搜索字符串:</label></td>
            <td>
                <textarea id="search_text" data-dojo-type="dijit.form.SimpleTextarea" data-dojo-props="name: 'search_text', rows: 4, class:'simple_textarea'"></textarea>
            </td>
        </tr>
        <tr>
            <td class="td_label"><label for="search_target">目标字符串:</label></td>
            <td>
                <textarea id="search_target" data-dojo-type="dijit.form.SimpleTextarea" data-dojo-props="name: 'search_target', rows: 4, class: 'simple_textarea', onKeyPress: search_form_enter"></textarea>
            </td>
        </tr>
        <tr>
            <td class="td_label"><label>附加参数:</label></td>
            <td>
                <label for="start_post">开始</label>
                <input data-dojo-type="dijit.form.TextBox" data-dojo-props="name: 'search_start_pos', class: 'min_text_input'" />
                <label for="end_post">结束</label>
                <input data-dojo-type="dijit.form.TextBox" data-dojo-props="type: 'text', name: 'search_end_pos', class: 'min_text_input'" />
                <input id="search_is_case" data-dojo-type="dijit.form.CheckBox" data-dojo-props="name: 'search_is_case', value: '1'" /><label for="search_is_case" >大小写敏感</label>
            </td>
        </tr>
        <tr>
            <td class="td_label"></td>
            <td>
                <button data-dojo-type="dijit.form.Button" data-dojo-props="type:'submit'">搜索</button>
                <button data-dojo-type="dijit.form.Button" data-dojo-props="type:'reset'">重置</button>
            </td>
        </tr>
    </table>
</form>
