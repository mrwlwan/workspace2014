<form action="/section/{{section_name}}" method="post" autocomplete="off">
    <fieldset>
        <legend>{{' '.join(section_name.capitalize().split('_'))}}</legend>
        <table>
            <tr>
                <td class="label">帐号:</td>
                <td class="content"><textarea name="auths">{{auths}}</textarea></td>
            </tr>
            <tr>
                <td class="label">目标帖子:</td>
                <td class="content"><textarea name="target_urls">{{target_urls}}</textarea></td>
            </tr>
            <tr>
                <td class="label">时间间隔:</td>
                <td class="content"><input type="text" name="delay" value="{{delay}}" /></td>
            </tr>
            <tr>
                <td class="label">重复:</td>
                <td class="content"><input type="checkbox" name="is_repeat" value="1" {{"checked" if is_repeat else ""}}/></td>
            </tr>
            <tr>
                <td class="label">循环:</td>
                <td class="content"><input type="checkbox" name="is_random" value="1" {{"checked" if is_random else ""}}/></td>
            </tr>
            <tr>
                <td class="label">灌水文本:</td>
                <td class="content"><input type="text" name="target_filename" value="{{target_filename}}" /></td>
            </tr>
        <tr>
            <td class="button" colspan="2">
                <button class="reset" name="apply" value="reset">重置</button>
                <button class="delete" name="apply" value="delete">删除</button>
                <button class="submit" name="apply" value="submit">应用</button>
            </td>
        </tr>
        </table>
    </fieldset>
</form>
