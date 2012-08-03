<form id="re_test_form" data-dojo-type="dijit.form.Form" data-dojo-props="action: '/re_test'">
    <script type="dojo/connect", event="onSubmit">
        dojo.publish('form_submit', [this.domNode, arguments[0]]);
    </script>
    <table>
        <tr>
            <td class="td_label"></td>
            <td>
                <input id="checkbox_use_fetch_text" data-dojo-type="dijit.form.CheckBox" data-dojo-props="name: 're_test_is_fetch_text', value: '1', onChange: re_test_use_fetch_content" /><label for="checkbox_use_fetch_text" >应用抓取到的网页文本</label>
            </td>
        </tr>
        <tr>
            <td class="td_label"><label for="re_test_text">测试字符串:</label></td>
            <td>
                <textarea id="re_test_text" data-dojo-type="dijit.form.SimpleTextarea" data-dojo-props="name: 're_test_text', rows: 4, class:'simple_textarea'"></textarea>
            </td>
        </tr>
        <tr>
            <td class="td_label"><label for="reg">正则表达式:</label></td>
            <td>
                <textarea id="re_test_reg" data-dojo-type="dijit.form.SimpleTextarea" data-dojo-props="name: 'reg', rows: 4, class: 'simple_textarea', onKeyPress: re_test_form_enter"></textarea>
            </td>
        </tr>
        <tr>
            <td class="td_label"><label>标志:</label></td>
            <td>
                <input id="checkbox_re_i" data-dojo-type="dijit.form.CheckBox" data-dojo-props="name: 'flags', value: '2'" /><label for="checkbox_re_i"  title="Perform case-insensitive matching">re.I</label>
                <input id="checkbox_re_l" data-dojo-type="dijit.form.CheckBox" data-dojo-props="name: 'flags', value: '4'" /><label for="checkbox_re_l" title="Make \w, \W, \b, \B, \s and \S dependent on the current locale.">re.L</label>
                <input id="checkbox_re_m" data-dojo-type="dijit.form.CheckBox" data-dojo-props="name: 'flags', value: '8'" /><label for="checkbox_re_m"  title="When specified, the pattern character '^' matches at the beginning of the string and at the beginning of each line (immediately following each newline); and the pattern character '$' matches at the end of the string and at the end of each line (immediately preceding each newline).">re.M</label>
                <input id="checkbox_re_s" data-dojo-type="dijit.form.CheckBox" data-dojo-props="name: 'flags', value: '16'" /><label for="checkbox_re_s"  title="Make the '.' special character match any character at all, including a newline;">re.S</label>
                <input id="checkbox_re_u" data-dojo-type="dijit.form.CheckBox" data-dojo-props="name: 'flags', value: '32'" /><label for="checkbox_re_u"  title="Make \w, \W, \b, \B, \d, \D, \s and \S dependent on the Unicode character properties database.">re.U</label>
                <input id="checkbox_re_x" data-dojo-type="dijit.form.CheckBox" data-dojo-props="name: 'flags', value: '64'" /><label for="checkbox_re_x"  title="This flag allows you to write regular expressions that look nicer. Whitespace within the pattern is ignored, except when in a character class or preceded by an unescaped backslash, and, when a line contains a '#' neither in a character class or preceded by an unescaped backslash, all characters from the leftmost such '#' through the end of the line are ignored.">re.X</label>
            </td>
        </tr>
        <tr>
            <td class="td_label"></td>
            <td>
                <button data-dojo-type="dijit.form.Button" data-dojo-props="type:'submit'">测试</button>
                <button data-dojo-type="dijit.form.Button" data-dojo-props="type:'reset'">重置</button>
            </td>
        </tr>
    </table>
</form>
