%for auth_login_form in auth_login_forms:
%include auth_login_form global_config=global_config, poster=posters[auth_login_form['username']], **auth_login_form
%end
%if is_action:
<button class="action" name="apply" value="action" style="width:100%;">停止灌水</button>
%else:
<button class="action" name="apply" value="action" style="width:100%;">开始灌水</button>
%end
