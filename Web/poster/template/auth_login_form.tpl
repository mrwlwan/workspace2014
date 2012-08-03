<div class="auth_container">
    <form action="/auth_login/{{username}}" method="post" autocomplete="off">
        <fieldset>
            <legend>帐户: {{username}}</legend>
            %if not poster.is_logined():
            <table>
                <tr>
                    <td class="label">用户名:</td>
                    <td class="content"><input type="text" name="{{global_config['login_user_key']}}" value="{{username}}" readonly /></td>
                </tr>
                <tr>
                    <td class="label">密码:</td>
                    <td class="content"><input type="password" name="{{global_config['login_password_key']}}" value="{{password}}" /></td>
                </tr>
                %if global_config['login_code_key']:
                <tr>
                    <td class="label">验证码:</td>
                    <td class="content">
                        <img class="login_code" src="/login_code/{{username}}?5354" title="看不清?点击图片换一张试试 :)"/>
                        <input type="text" name="{{global_config['login_code_key']}}" />
                    </td>
                </tr>
                %end
                <tr>
                    <td class="button" colspan="2">
                        <button class="reset" name="apply" value="reset">重置</button>
                        <button class="login" name="apply" value="login">登录</button>
                    </td>
                </tr>
            </table>
            %end
            <div class="auth_log" style="display:{{'block' if poster.is_logined() else 'none'}}">登录成功</div>
        </fieldset>
    </form>
</div>
