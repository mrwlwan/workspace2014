# coding=utf8

import pytop.topstruct as topstruct
import xml.etree.ElementTree as etree
import json

class TOPRequest(topstruct.TOPDict):
    """ TOP 请求基类. """
    REQUEST = {}
    RESPONSE = {}
    API = None
    is_alert = True # 设置属性时时否即时显示警告信息. 方便于调试.

    def _befor_init(self, *args, **kwargs):
        # 设置默认值
        dict.__init__(self, ((param_name, param.get('default')) for param_name, param in self.REQUEST.items() if 'default' in param))

    def __setitem__(self, param_name, param):
        if param_name not in self.REQUEST:
            self.is_alert and print('警告: 该调用不支持参数 %s' % param_name)
        else:
            param_type = self.REQUEST.get(param_name).get('type')
            param = param_type(param)
            self.is_alert and 'optional' in self.REQUEST.get(param_name) and  param not in self.REQUEST.get(param_name).get('optional') and print('警告: 参数 %s 无效值 %s' % (param_name, param))
        super().__setitem__(param_name, param)

    @property
    def api(self):
        """ 返回当前api名称. """
        return self.API

    def update(self, *args, **kwargs):
        # 子对象则直接调用dict的__init__.
        if args:
            if isinstance(args[0], self.__class__):
                super().__init__(args[0])
                return
            else:
                kwargs = args[0] if isinstance(args[0], dict) else dict(args)
        for k, v in kwargs.items():
            self[k] = v

    def clean(self):
        """ 清除无效的request 参数. 并给出提示. 其中会对args的值进行类型转换.
        @return dict
        """
        for key, value in self.items():
            if key not in self.REQUEST:
                del self[key]
            elif 'optional' in self.REQUEST.get(key) and value not in self.REQUEST.get(key).get('optional'):
                del self[key]

    def check_required(self):
        """ 检查是否缺少必须的参数. """
        result = True
        for param_name, param in self.REQUEST.items():
            if param.get('is_required') and param_name not in self:
                print('缺少参数 %s!' % param_name)
                result = False
        return result

    def response(self, http_response, format='json', is_transform=False):
        """ 返回一个TOPResponse对象.
        @param: response(requests.Response): requests.Response 对象.
        """
        return TOPResponse(http_response, self.RESPONSE, format=format, is_transform=is_transform)


class TOPResponse:
    """ TOP 请求返回类."""

    def __init__(self, http_response, response_format, format, is_transform=False):
        """ @param http_response(requests.Response): requests 返回的 response 对象.
        @param response_format(dict): 数据结构.
        @param format(string): 'json' or 'xml', 用于 self.response
        @param is_transform(bool): 是否将相应的dict对象转换为TOPObject对象.
        """
        self.http_response = http_response
        self.response_format = response_format
        self.format = format.lower()
        self.is_transform = is_transform
        self._response = None
        # 是否成功的 TOP 调用.
        self.is_error = False

    def _transform(self, json_obj):
        if self.is_error:
            return topstruct.TOPError(json_obj)
        result = {}
        for key, value in json_obj.items():
            obj_type = self.response_format.get(key).get('type')
            is_list = self.response_format.get(key).get('is_list')
            if is_list:
                value = (obj_type(item_value) for item_name, item_value in value.items()[0])
            else:
                value = obj_type(value)
        result[key] = value
        return result

    @property
    def text(self):
        """ TOP调用返回的文本字符串. """
        return self.http_response.text

    @property
    def response(self):
        """ 将TOP调用返回的文本转换为相应的对象(dict 或者 xml). """
        if self._response==None:
            if self.format=='json':
                json_obj = json.loads(self.text)
                self.is_error = 'error_response' in json_obj
                json_obj = json_obj.popitem()[1]
                self._response = json_obj if not self.is_transform else self._transform(json_obj)
            elif self.format=='xml':
                self._response = etree.fromstring(self.text)
                self.is_error = self._response.tag == 'error_response'
        return self._response



class UserGetRequest(TOPRequest):
    """ 得到单个用户

    @response user(User): 用户信息

    @request fields(FieldList): (required)需返回的字段列表。可选值：User结构体中的所有字段；以半角逗号(,)分隔。不支持：地址，真实姓名，身份证，手机，电话
    @request nick(String): (optional)用户昵称，如果昵称为中文，请使用UTF-8字符集对昵称进行URL编码。
        <br><font color="red">注：在传入session的情况下,可以不传nick，表示取当前用户信息；否则nick必须传.<br>
        自用型应用不需要传入nick
        </font>
    """
    REQUEST = {
        'fields': {'type': topstruct.FieldList, 'is_required': True, 'optional': topstruct.Set({'buyer_credit', 'uid', 'user_id', 'vip_info', 'sex', 'last_visit', 'seller_credit', 'has_shop', 'prop_img_num', 'status', 'magazine_subscribe', 'consumer_protection', 'type', 'alipay_bind', 'birthday', 'is_lightning_consignment', 'online_gaming', 'location', 'auto_repost', 'alipay_no', 'sign_food_seller_promise', 'avatar', 'created', 'alipay_account', 'prop_img_size', 'promoted_type', 'is_golden_seller', 'liangpin', 'nick', 'vertical_market', 'has_more_pic', 'email', 'has_sub_stock', 'item_img_num', 'item_img_size'})},
        'nick': {'type': topstruct.String, 'is_required': False}
    }

    RESPONSE = {
        'user': {'type': topstruct.User, 'is_list': False}
    }

    API = 'taobao.user.get'


class UsersGetRequest(TOPRequest):
    """ 传入多个淘宝会员帐号返回多个用户公开信息

    @response users(User): 用户信息列表

    @request fields(FieldList): (required)查询字段：User数据结构的公开信息字段列表，以半角逗号(,)分隔
    @request nicks(String): (required)用户昵称，多个以半角逗号(,)分隔，最多40个
    """
    REQUEST = {
        'fields': {'type': topstruct.FieldList, 'is_required': True, 'optional': topstruct.Set({'buyer_credit', 'uid', 'user_id', 'vip_info', 'sex', 'last_visit', 'seller_credit', 'has_shop', 'prop_img_num', 'status', 'magazine_subscribe', 'consumer_protection', 'type', 'alipay_bind', 'birthday', 'is_lightning_consignment', 'online_gaming', 'location', 'auto_repost', 'alipay_no', 'sign_food_seller_promise', 'avatar', 'created', 'alipay_account', 'prop_img_size', 'promoted_type', 'is_golden_seller', 'liangpin', 'nick', 'vertical_market', 'has_more_pic', 'email', 'has_sub_stock', 'item_img_num', 'item_img_size'})},
        'nicks': {'type': topstruct.String, 'is_required': True}
    }

    RESPONSE = {
        'users': {'type': topstruct.User, 'is_list': False}
    }

    API = 'taobao.users.get'


class ItemcatsAuthorizeGetRequest(TOPRequest):
    """ 查询B商家被授权品牌列表、类目列表和 c 商家新品类目列表

    @response seller_authorize(SellerAuthorize): 里面有3个数组：
        Brand[]品牌列表,
        ItemCat[] 类目列表
        XinpinItemCat[] 针对于C卖家新品类目列表

    @request fields(FieldList): (required)需要返回的字段。目前支持有：
        brand.vid, brand.name,
        item_cat.cid, item_cat.name, item_cat.status,item_cat.sort_order,item_cat.parent_cid,item_cat.is_parent,
        xinpin_item_cat.cid,
        xinpin_item_cat.name,
        xinpin_item_cat.status,
        xinpin_item_cat.sort_order,
        xinpin_item_cat.parent_cid,
        xinpin_item_cat.is_parent
    """
    REQUEST = {
        'fields': {'type': topstruct.FieldList, 'is_required': True, 'optional': topstruct.Set({'item_cat.cid', 'item_cat.status', 'item_cat.name', 'item_cat.is_parent', 'item_cat.parent_cid', 'xinpin_item_cat.name', 'item_cat.sort_order', 'xinpin_item_cat.status', 'xinpin_item_cat.is_parent', 'brand.name', 'xinpin_item_cat.cid', 'brand.vid', 'xinpin_item_cat.parent_cid', 'xinpin_item_cat.sort_order'})}
    }

    RESPONSE = {
        'seller_authorize': {'type': topstruct.SellerAuthorize, 'is_list': False}
    }

    API = 'taobao.itemcats.authorize.get'


class ItemcatsGetRequest(TOPRequest):
    """ 获取后台供卖家发布商品的标准商品类目

    @response item_cats(ItemCat): 增量类目信息,根据fields传入的参数返回相应的结果
    @response last_modified(Date): 最近修改时间(如果取增量，会返回该字段)。格式:yyyy-MM-dd HH:mm:ss

    @request cids(Number): (special)商品所属类目ID列表，用半角逗号(,)分隔 例如:(18957,19562,) (cids、parent_cid至少传一个)
    @request fields(FieldList): (optional)需要返回的字段列表，见ItemCat，默认返回：cid,parent_cid,name,is_parent
    @request parent_cid(Number): (special)父商品类目 id，0表示根节点, 传输该参数返回所有子类目。 (cids、parent_cid至少传一个)
    """
    REQUEST = {
        'cids': {'type': topstruct.Number, 'is_required': False},
        'fields': {'type': topstruct.FieldList, 'is_required': False, 'optional': topstruct.Set({'sort_order', 'is_parent', 'features', 'modified_time', 'parent_cid', 'status', 'name', 'modified_type', 'cid'}), 'default': {'cid', 'parent_cid', 'name', 'is_parent'}},
        'parent_cid': {'type': topstruct.Number, 'is_required': False}
    }

    RESPONSE = {
        'item_cats': {'type': topstruct.ItemCat, 'is_list': False},
        'last_modified': {'type': topstruct.Date, 'is_list': False}
    }

    API = 'taobao.itemcats.get'


class ItempropsGetRequest(TOPRequest):
    """ 通过设置必要的参数，来获取商品后台标准类目属性，以及这些属性里面详细的属性值prop_values。

    @response item_props(ItemProp): 类目属性信息(如果是取全量或者增量，不包括属性值),根据fields传入的参数返回相应的结果
    @response last_modified(Date): 最近修改时间(只有取全量或增量的时候会返回该字段)。格式:yyyy-MM-dd HH:mm:ss

    @request child_path(String): (optional)类目子属性路径,由该子属性上层的类目属性和类目属性值组成,格式pid:vid;pid:vid.取类目子属性需要传child_path,cid
    @request cid(Number): (required)叶子类目ID，如果只传cid，则只返回一级属性,通过taobao.itemcats.get获得叶子类目ID
    @request fields(FieldList): (optional)需要返回的字段列表，见：ItemProp，默认返回：pid, name, must, multi, prop_values
    @request is_color_prop(Boolean): (optional)是否颜色属性。可选值:true(是),false(否) (删除的属性不会匹配和返回这个条件)
    @request is_enum_prop(Boolean): (optional)是否枚举属性。可选值:true(是),false(否) (删除的属性不会匹配和返回这个条件)。如果返回true，属性值是下拉框选择输入，如果返回false，属性值是用户自行手工输入。
    @request is_input_prop(Boolean): (optional)在is_enum_prop是true的前提下，是否是卖家可以自行输入的属性（注：如果is_enum_prop返回false，该参数统一返回false）。可选值:true(是),false(否) (删除的属性不会匹配和返回这个条件)
    @request is_item_prop(Boolean): (optional)是否商品属性，这个属性只能放于发布商品时使用。可选值:true(是),false(否)
    @request is_key_prop(Boolean): (optional)是否关键属性。可选值:true(是),false(否)
    @request is_sale_prop(Boolean): (optional)是否销售属性。可选值:true(是),false(否)
    @request parent_pid(Number): (optional)父属性ID
    @request pid(Number): (optional)属性id (取类目属性时，传pid，不用同时传PID和parent_pid)
    """
    REQUEST = {
        'child_path': {'type': topstruct.String, 'is_required': False},
        'cid': {'type': topstruct.Number, 'is_required': True},
        'fields': {'type': topstruct.FieldList, 'is_required': False, 'optional': topstruct.Set({'sort_order', 'is_input_prop', 'modified_type', 'is_allow_alias', 'type', 'parent_vid', 'prop_values', 'parent_pid', 'is_color_prop', 'pid', 'multi', 'is_key_prop', 'modified_time', 'status', 'is_item_prop', 'child_template', 'is_enum_prop', 'must', 'name', 'is_sale_prop'}), 'default': {'pid', 'name', 'must', 'prop_values', 'multi'}},
        'is_color_prop': {'type': topstruct.Boolean, 'is_required': False},
        'is_enum_prop': {'type': topstruct.Boolean, 'is_required': False},
        'is_input_prop': {'type': topstruct.Boolean, 'is_required': False},
        'is_item_prop': {'type': topstruct.Boolean, 'is_required': False},
        'is_key_prop': {'type': topstruct.Boolean, 'is_required': False},
        'is_sale_prop': {'type': topstruct.Boolean, 'is_required': False},
        'parent_pid': {'type': topstruct.Number, 'is_required': False},
        'pid': {'type': topstruct.Number, 'is_required': False}
    }

    RESPONSE = {
        'item_props': {'type': topstruct.ItemProp, 'is_list': False},
        'last_modified': {'type': topstruct.Date, 'is_list': False}
    }

    API = 'taobao.itemprops.get'


class ItempropvaluesGetRequest(TOPRequest):
    """ 传入类目ID,必需是叶子类目，通过taobao.itemcats.get获取类目ID
        返回字段目前支持有：cid,pid,prop_name,vid,name,name_alias,status,sort_order
        作用:获取标准类目属性值

    @response last_modified(Date): 最近修改时间。格式:yyyy-MM-dd HH:mm:ss
    @response prop_values(PropValue): 属性值,根据fields传入的参数返回相应的结果

    @request cid(Number): (required)叶子类目ID ,通过taobao.itemcats.get获得叶子类目ID
    @request fields(FieldList): (required)需要返回的字段。目前支持有：cid,pid,prop_name,vid,name,name_alias,status,sort_order
    @request pvs(String): (special)属性和属性值 id串，格式例如(pid1;pid2)或(pid1:vid1;pid2:vid2)或(pid1;pid2:vid2)
    """
    REQUEST = {
        'cid': {'type': topstruct.Number, 'is_required': True},
        'fields': {'type': topstruct.FieldList, 'is_required': True, 'optional': topstruct.Set({'sort_order', 'vid', 'name_alias', 'prop_name', 'pid', 'status', 'cid', 'name'})},
        'pvs': {'type': topstruct.String, 'is_required': False}
    }

    RESPONSE = {
        'last_modified': {'type': topstruct.Date, 'is_list': False},
        'prop_values': {'type': topstruct.PropValue, 'is_list': False}
    }

    API = 'taobao.itempropvalues.get'


class ShopcatsListGetRequest(TOPRequest):
    """ 获取淘宝面向买家的浏览导航类目（跟后台卖家商品管理的类目有差异）

    @response shop_cats(ShopCat): 店铺类目列表信息

    @request fields(FieldList): (optional)需要返回的字段列表，见ShopCat，默认返回：cid,parent_cid,name,is_parent
    """
    REQUEST = {
        'fields': {'type': topstruct.FieldList, 'is_required': False, 'optional': topstruct.Set({'cid', 'parent_cid', 'name', 'is_parent'}), 'default': {'cid', 'parent_cid', 'name', 'is_parent'}}
    }

    RESPONSE = {
        'shop_cats': {'type': topstruct.ShopCat, 'is_list': False}
    }

    API = 'taobao.shopcats.list.get'


class AftersaleGetRequest(TOPRequest):
    """ 查询用户设置的售后服务模板，仅返回标题和id

    @response after_sales(AfterSale): 售后服务返回对象
    """
    REQUEST = {}

    RESPONSE = {
        'after_sales': {'type': topstruct.AfterSale, 'is_list': False}
    }

    API = 'taobao.aftersale.get'


class ItemAddRequest(TOPRequest):
    """ 此接口用于新增一个商品
        商品所属的卖家是当前会话的用户
        商品的属性和sku的属性有包含的关系，商品的价格要位于sku的价格区间之中（例如，sku价格有5元、10元两种，那么商品的价格就需要大于等于5元，小于等于10元，否则新增商品会失败）
        商品的类目和商品的价格、sku的价格都有一定的相关性（具体的关系要通过类目属性查询接口获得）
        商品的运费承担方式和邮费设置有相关性，卖家承担运费不用设置邮费，买家承担运费需要设置邮费
        当关键属性值选择了“其他”的时候，需要输入input_pids和input_str商品才能添加成功。

    @response item(Item): 商品结构,仅有numIid和created返回

    @request after_sale_id(Number): (optional)售后说明模板id
    @request approve_status(String): (optional)商品上传后的状态。可选值:onsale(出售中),instock(仓库中);默认值:onsale
    @request auction_point(Number): (optional)商品的积分返点比例。如:5,表示:返点比例0.5%. 注意：返点比例必须是>0的整数，而且最大是90,即为9%.B商家在发布非虚拟商品时，返点必须是 5的倍数，即0.5%的倍数。其它是1的倍数，即0.1%的倍数。无名良品商家发布商品时，复用该字段记录积分宝返点比例，返点必须是对应类目的返点步长的整数倍，默认是5，即0.5%。注意此时该字段值依旧必须是>0的整数，最高值不超过500，即50%
    @request auto_fill(String): (optional)代充商品类型。在代充商品的类目下，不传表示不标记商品类型（交易搜索中就不能通过标记搜到相关的交易了）。可选类型：
        no_mark(不做类型标记)
        time_card(点卡软件代充)
        fee_card(话费软件代充)
    @request cid(Number): (required)叶子类目id
    @request cod_postage_id(Number): (optional)此为货到付款运费模板的ID，对应的JAVA类型是long,如果COD卖家应用了货到付款运费模板，此值要进行设置。
    @request desc(String): (required)宝贝描述。字数要大于5个字符，小于25000个字符，受违禁词控制
    @request ems_fee(Price): (optional)ems费用。取值范围:0.01-999.00;精确到2位小数;单位:元。如:25.07，表示:25元7分
    @request express_fee(Price): (optional)快递费用。取值范围:0.01-999.00;精确到2位小数;单位:元。如:15.07，表示:15元7分
    @request freight_payer(String): (optional)运费承担方式。可选值:seller（卖家承担）,buyer(买家承担);默认值:seller。卖家承担不用设置邮费和postage_id.买家承担的时候，必填邮费和postage_id
        如果用户设置了运费模板会优先使用运费模板，否则要同步设置邮费（post_fee,express_fee,ems_fee）
    @request has_discount(Boolean): (optional)支持会员打折。可选值:true,false;默认值:false(不打折)
    @request has_invoice(Boolean): (optional)是否有发票。可选值:true,false (商城卖家此字段必须为true);默认值:false(无发票)
    @request has_showcase(Boolean): (optional)橱窗推荐。可选值:true,false;默认值:false(不推荐)
    @request has_warranty(Boolean): (optional)是否有保修。可选值:true,false;默认值:false(不保修)
    @request image(Image): (optional)商品主图片。类型:JPG,GIF;最大长度:500K
    @request increment(Price): (optional)加价幅度。如果为0，代表系统代理幅度
    @request input_pids(String): (optional)用户自行输入的类目属性ID串。结构："pid1,pid2,pid3"，如："20000"（表示品牌） 注：通常一个类目下用户可输入的关键属性不超过1个。
    @request input_str(String): (optional)用户自行输入的子属性名和属性值，结构:"父属性值;一级子属性名;一级子属性值;二级子属性名;自定义输入值,....",如：“耐克;耐克系列;科比系列;科比系列;2K5,Nike乔丹鞋;乔丹系列;乔丹鞋系列;乔丹鞋系列;json5”，多个自定义属性用','分割，input_str需要与input_pids一一对应，注：通常一个类目下用户可输入的关键属性不超过1个。所有属性别名加起来不能超过3999字节
    @request is_3D(Boolean): (optional)是否是3D
    @request is_ex(Boolean): (optional)是否在外店显示
    @request is_lightning_consignment(Boolean): (optional)实物闪电发货
    @request is_taobao(Boolean): (optional)是否在淘宝上显示（如果传FALSE，则在淘宝主站无法显示该商品）
    @request is_xinpin(Boolean): (optional)商品是否为新品。只有在当前类目开通新品,并且当前用户拥有该类目下发布新品权限时才能设置is_xinpin为true，否则设置true后会返回错误码:isv.invalid-permission:add-xinpin。同时只有一口价全新的宝贝才能设置为新品，否则会返回错误码：isv.invalid-parameter:xinpin。不设置该参数值或设置为false效果一致。
    @request lang(String): (optional)商品文字的字符集。繁体传入"zh_HK"，简体传入"zh_CN"，不传默认为简体
    @request list_time(Date): (optional)定时上架时间。(时间格式：yyyy-MM-dd HH:mm:ss)
    @request location.city(String): (required)所在地城市。如杭州 。可以通过http://dl.open.taobao.com/sdk/商品城市列表.rar查询
    @request location.state(String): (required)所在地省份。如浙江，具体可以下载http://dl.open.taobao.com/sdk/商品城市列表.rar  取到
    @request num(Number): (required)商品数量，取值范围:0-999999的整数。且需要等于Sku所有数量的和
    @request outer_id(String): (optional)商品外部编码，该字段的最大长度是512个字节
    @request pic_path(String): (optional)商品主图需要关联的图片空间的相对url。这个url所对应的图片必须要属于当前用户。pic_path和image只需要传入一个,如果两个都传，默认选择pic_path
    @request post_fee(Price): (optional)平邮费用。取值范围:0.01-999.00;精确到2位小数;单位:元。如:5.07，表示:5元7分. 注:post_fee,express_fee,ems_fee需要一起填写
    @request postage_id(Number): (optional)宝贝所属的运费模板ID。取值范围：整数且必须是该卖家的运费模板的ID（可通过taobao.delivery.template.get获得当前会话用户的所有邮费模板）
    @request price(Price): (required)商品价格。取值范围:0-100000000;精确到2位小数;单位:元。如:200.07，表示:200元7分。需要在正确的价格区间内。
    @request product_id(Number): (optional)商品所属的产品ID(B商家发布商品需要用)
    @request property_alias(String): (optional)属性值别名。如pid:vid:别名;pid1:vid1:别名1 ，其中：pid是属性id vid是属性值id。总长度不超过511字节
    @request props(String): (optional)商品属性列表。格式:pid:vid;pid:vid。属性的pid调用taobao.itemprops.get取得，属性值的vid用taobao.itempropvalues.get取得vid。 如果该类目下面没有属性，可以不用填写。如果有属性，必选属性必填，其他非必选属性可以选择不填写.属性不能超过35对。所有属性加起来包括分割符不能超过549字节，单个属性没有限制。 如果有属性是可输入的话，则用字段input_str填入属性的值
    @request sell_promise(Boolean): (optional)是否承诺退换货服务!虚拟商品无须设置此项!
    @request seller_cids(String): (optional)商品所属的店铺类目列表。按逗号分隔。结构:",cid1,cid2,...,"，如果店铺类目存在二级类目，必须传入子类目cids。
    @request sku_outer_ids(String): (optional)Sku的外部id串，结构如：1234,1342,…
        sku_properties, sku_quantities, sku_prices, sku_outer_ids在输入数据时要一一对应，如果没有sku_outer_ids也要写上这个参数，入参是","(这个是两个sku的示列，逗号数应该是sku个数减1)；该参数最大长度是512个字节
    @request sku_prices(String): (optional)Sku的价格串，结构如：10.00,5.00,… 精确到2位小数;单位:元。如:200.07，表示:200元7分
    @request sku_properties(String): (optional)更新的Sku的属性串，调用taobao.itemprops.get获取类目属性，如果属性是销售属性，再用taobao.itempropvalues.get取得vid。格式:pid:vid;pid:vid,多个sku之间用逗号分隔。该字段内的销售属性（自定义的除外）也需要在props字段填写。sku的销售属性需要一同选取，如:颜色，尺寸。如果新增商品包含了sku，则此字段一定要传入。这个字段的长度要控制在512个字节以内。
        如果有自定义销售属性，则格式为pid:vid;pid2:vid2;$pText:vText , 其中$pText:vText为自定义属性。限制：其中$pText的’$’前缀不能少，且pText和vText文本中不可以存在冒号:和分号;以及逗号，
    @request sku_quantities(String): (optional)Sku的数量串，结构如：num1,num2,num3 如：2,3
    @request stuff_status(String): (required)新旧程度。可选值：new(新)，second(二手)，unused(闲置)。B商家不能发布二手商品。
        如果是二手商品，特定类目下属性里面必填新旧成色属性
    @request sub_stock(Number): (optional)商品是否支持拍下减库存:1支持;2取消支持(付款减库存);0(默认)不更改
        集市卖家默认拍下减库存;
        商城卖家默认付款减库存
    @request title(String): (required)宝贝标题。不能超过60字符，受违禁词控制
    @request type(String): (required)发布类型。可选值:fixed(一口价),auction(拍卖)。B商家不能发布拍卖商品，而且拍卖商品是没有SKU的
    @request valid_thru(Number): (optional)有效期。可选值:7,14;单位:天;默认值:14
    @request weight(Number): (optional)商品的重量(商超卖家专用字段)
    """
    REQUEST = {
        'after_sale_id': {'type': topstruct.Number, 'is_required': False},
        'approve_status': {'type': topstruct.String, 'is_required': False},
        'auction_point': {'type': topstruct.Number, 'is_required': False},
        'auto_fill': {'type': topstruct.String, 'is_required': False},
        'cid': {'type': topstruct.Number, 'is_required': True},
        'cod_postage_id': {'type': topstruct.Number, 'is_required': False},
        'desc': {'type': topstruct.String, 'is_required': True},
        'ems_fee': {'type': topstruct.Price, 'is_required': False},
        'express_fee': {'type': topstruct.Price, 'is_required': False},
        'freight_payer': {'type': topstruct.String, 'is_required': False},
        'has_discount': {'type': topstruct.Boolean, 'is_required': False},
        'has_invoice': {'type': topstruct.Boolean, 'is_required': False},
        'has_showcase': {'type': topstruct.Boolean, 'is_required': False},
        'has_warranty': {'type': topstruct.Boolean, 'is_required': False},
        'image': {'type': topstruct.Image, 'is_required': False},
        'increment': {'type': topstruct.Price, 'is_required': False},
        'input_pids': {'type': topstruct.String, 'is_required': False},
        'input_str': {'type': topstruct.String, 'is_required': False},
        'is_3D': {'type': topstruct.Boolean, 'is_required': False},
        'is_ex': {'type': topstruct.Boolean, 'is_required': False},
        'is_lightning_consignment': {'type': topstruct.Boolean, 'is_required': False},
        'is_taobao': {'type': topstruct.Boolean, 'is_required': False},
        'is_xinpin': {'type': topstruct.Boolean, 'is_required': False},
        'lang': {'type': topstruct.String, 'is_required': False},
        'list_time': {'type': topstruct.Date, 'is_required': False},
        'location.city': {'type': topstruct.String, 'is_required': True},
        'location.state': {'type': topstruct.String, 'is_required': True},
        'num': {'type': topstruct.Number, 'is_required': True},
        'outer_id': {'type': topstruct.String, 'is_required': False},
        'pic_path': {'type': topstruct.String, 'is_required': False},
        'post_fee': {'type': topstruct.Price, 'is_required': False},
        'postage_id': {'type': topstruct.Number, 'is_required': False},
        'price': {'type': topstruct.Price, 'is_required': True},
        'product_id': {'type': topstruct.Number, 'is_required': False},
        'property_alias': {'type': topstruct.String, 'is_required': False},
        'props': {'type': topstruct.String, 'is_required': False},
        'sell_promise': {'type': topstruct.Boolean, 'is_required': False},
        'seller_cids': {'type': topstruct.String, 'is_required': False},
        'sku_outer_ids': {'type': topstruct.String, 'is_required': False},
        'sku_prices': {'type': topstruct.String, 'is_required': False},
        'sku_properties': {'type': topstruct.String, 'is_required': False},
        'sku_quantities': {'type': topstruct.String, 'is_required': False},
        'stuff_status': {'type': topstruct.String, 'is_required': True},
        'sub_stock': {'type': topstruct.Number, 'is_required': False},
        'title': {'type': topstruct.String, 'is_required': True},
        'type': {'type': topstruct.String, 'is_required': True},
        'valid_thru': {'type': topstruct.Number, 'is_required': False},
        'weight': {'type': topstruct.Number, 'is_required': False}
    }

    RESPONSE = {
        'item': {'type': topstruct.Item, 'is_list': False}
    }

    API = 'taobao.item.add'


class ItemDeleteRequest(TOPRequest):
    """ 删除单条商品

    @response item(Item): 被删除商品的相关信息

    @request num_iid(Number): (required)商品数字ID，该参数必须
    """
    REQUEST = {
        'num_iid': {'type': topstruct.Number, 'is_required': True}
    }

    RESPONSE = {
        'item': {'type': topstruct.Item, 'is_list': False}
    }

    API = 'taobao.item.delete'


class ItemGetRequest(TOPRequest):
    """ 获取单个商品的详细信息
        卖家未登录时只能获得这个商品的公开数据，卖家登录后可以获取商品的所有数据

    @response item(Item): 获取的商品 具体字段根据权限和设定的fields决定

    @request fields(FieldList): (required)需要返回的商品对象字段。可选值：Item商品结构体中所有字段均可返回；多个字段用“,”分隔。如果想返回整个子对象，那字段为item_img，如果是想返回子对象里面的字段，那字段为item_img.url。新增返回字段：second_kill（是否秒杀商品）、auto_fill（代充商品类型）,props_name（商品属性名称）
    @request num_iid(Number): (required)商品数字ID
    """
    REQUEST = {
        'fields': {'type': topstruct.FieldList, 'is_required': True, 'optional': topstruct.Set({'item_imgs.position', 'created', 'desc', 'product_id', 'approve_status', 'detail_url', 'cod_postage_id', 'score', 'second_kill', 'is_timing', 'is_virtual', 'modified', 'is_taobao', 'list_time', 'input_str', 'props_name', 'item_imgs.created', 'item_imgs.id', 'type', 'is_xinpin', 'is_fenxiao', 'increment', 'outer_shop_auction_template_id', 'sub_stock', 'ww_status', 'num', 'nick', 'auto_fill', 'pic_url', 'cid', 'input_pids', 'skus', 'is_lightning_consignment', 'one_station', 'location', 'wap_detail_url', 'has_warranty', 'num_iid', 'post_fee', 'freight_payer', 'outer_id', 'ems_fee', 'inner_shop_auction_template_id', 'stuff_status', 'price', 'has_showcase', 'postage_id', 'prop_imgs', 'sell_promise', 'props', 'is_prepay', 'delist_time', 'valid_thru', 'seller_cids', 'promoted_service', 'auction_point', 'is_ex', 'has_invoice', 'property_alias', 'videos', 'volume', 'template_id', 'violation', 'title', 'item_imgs', 'is_3D', 'express_fee', 'item_imgs.url', 'wap_desc', 'after_sale_id', 'has_discount'})},
        'num_iid': {'type': topstruct.Number, 'is_required': True}
    }

    RESPONSE = {
        'item': {'type': topstruct.Item, 'is_list': False}
    }

    API = 'taobao.item.get'


class ItemImgDeleteRequest(TOPRequest):
    """ 删除itemimg_id 所指定的商品图片
        传入的num_iid所对应的商品必须属于当前会话的用户
        itemimg_id对应的图片需要属于num_iid对应的商品

    @response item_img(ItemImg): 商品图片结构

    @request id(Number): (required)商品图片ID
    @request num_iid(Number): (required)商品数字ID，必选
    """
    REQUEST = {
        'id': {'type': topstruct.Number, 'is_required': True},
        'num_iid': {'type': topstruct.Number, 'is_required': True}
    }

    RESPONSE = {
        'item_img': {'type': topstruct.ItemImg, 'is_list': False}
    }

    API = 'taobao.item.img.delete'


class ItemImgUploadRequest(TOPRequest):
    """ 添加一张商品图片到num_iid指定的商品中
        传入的num_iid所对应的商品必须属于当前会话的用户
        如果更新图片需要设置itemimg_id，且该itemimg_id的图片记录需要属于传入的num_iid对应的商品。如果新增图片则不用设置
        商品图片有数量和大小上的限制，根据卖家享有的服务（如：卖家订购了多图服务等），商品图片数量限制不同。

    @response item_img(ItemImg): 商品图片结构

    @request id(Number): (optional)商品图片id(如果是更新图片，则需要传该参数)
    @request image(Image): (optional)商品图片内容类型:JPG,GIF;最大长度:500K 。支持的文件类型：gif,jpg,jpeg,png
    @request is_major(Boolean): (optional)是否将该图片设为主图,可选值:true,false;默认值:false(非主图)
    @request num_iid(Number): (required)商品数字ID，该参数必须
    @request position(Number): (optional)图片序号
    """
    REQUEST = {
        'id': {'type': topstruct.Number, 'is_required': False},
        'image': {'type': topstruct.Image, 'is_required': False},
        'is_major': {'type': topstruct.Boolean, 'is_required': False},
        'num_iid': {'type': topstruct.Number, 'is_required': True},
        'position': {'type': topstruct.Number, 'is_required': False}
    }

    RESPONSE = {
        'item_img': {'type': topstruct.ItemImg, 'is_list': False}
    }

    API = 'taobao.item.img.upload'


class ItemJointImgRequest(TOPRequest):
    """ * 关联一张商品图片到num_iid指定的商品中
        * 传入的num_iid所对应的商品必须属于当前会话的用户
        * 商品图片关联在卖家身份和图片来源上的限制，卖家要是B卖家或订购了多图服务才能关联图片，并且图片要来自于卖家自己的图片空间才行
        * 商品图片数量有限制。不管是上传的图片还是关联的图片，他们的总数不能超过一定限额

    @response item_img(ItemImg): 商品图片信息

    @request id(Number): (optional)商品图片id(如果是更新图片，则需要传该参数)
    @request is_major(Boolean): (optional)上传的图片是否关联为商品主图
    @request num_iid(Number): (required)商品数字ID，必选
    @request pic_path(String): (required)图片URL,图片空间图片的相对地址
    @request position(Number): (optional)图片序号
    """
    REQUEST = {
        'id': {'type': topstruct.Number, 'is_required': False},
        'is_major': {'type': topstruct.Boolean, 'is_required': False},
        'num_iid': {'type': topstruct.Number, 'is_required': True},
        'pic_path': {'type': topstruct.String, 'is_required': True},
        'position': {'type': topstruct.Number, 'is_required': False}
    }

    RESPONSE = {
        'item_img': {'type': topstruct.ItemImg, 'is_list': False}
    }

    API = 'taobao.item.joint.img'


class ItemJointPropimgRequest(TOPRequest):
    """ * 关联一张商品属性图片到num_iid指定的商品中
        * 传入的num_iid所对应的商品必须属于当前会话的用户
        * 图片的属性必须要是颜色的属性，这个在前台显示的时候需要和sku进行关联的
        * 商品图片关联在卖家身份和图片来源上的限制，卖家要是B卖家或订购了多图服务才能关联图片，并且图片要来自于卖家自己的图片空间才行
        * 商品图片数量有限制。不管是上传的图片还是关联的图片，他们的总数不能超过一定限额，最多不能超过24张（每个颜色属性都有一张）

    @response prop_img(PropImg): 属性图片对象信息

    @request id(Number): (optional)属性图片ID。如果是新增不需要填写
    @request num_iid(Number): (required)商品数字ID，必选
    @request pic_path(String): (required)图片地址
    @request position(Number): (optional)图片序号
    @request properties(String): (required)属性列表。调用taobao.itemprops.get.v2获取类目属性，属性必须是颜色属性，再用taobao.itempropvalues.get取得vid。格式:pid:vid。
    """
    REQUEST = {
        'id': {'type': topstruct.Number, 'is_required': False},
        'num_iid': {'type': topstruct.Number, 'is_required': True},
        'pic_path': {'type': topstruct.String, 'is_required': True},
        'position': {'type': topstruct.Number, 'is_required': False},
        'properties': {'type': topstruct.String, 'is_required': True}
    }

    RESPONSE = {
        'prop_img': {'type': topstruct.PropImg, 'is_list': False}
    }

    API = 'taobao.item.joint.propimg'


class ItemPriceUpdateRequest(TOPRequest):
    """ 更新商品价格

    @response item(Item): 商品结构里的num_iid，modified

    @request after_sale_id(Number): (optional)售后服务说明模板id
    @request approve_status(String): (optional)商品上传后的状态。可选值:onsale（出售中）,instock（库中），如果同时更新商品状态为出售中及list_time为将来的时间，则商品还是处于定时上架的状态, 此时item.is_timing为true
    @request auction_point(Number): (optional)商品的积分返点比例。如：5 表示返点比例0.5%. 注意：返点比例必须是>0的整数，而且最大是90,即为9%.B商家在发布非虚拟商品时，返点必须是 5的倍数，即0.5%的倍数。其它是1的倍数，即0.1%的倍数。无名良品商家发布商品时，复用该字段记录积分宝返点比例，返点必须是对应类目的返点步长的整数倍，默认是5，即0.5%。注意此时该字段值依旧必须是>0的整数，注意此时该字段值依旧必须是>0的整数，最高值不超过500，即50%
    @request auto_fill(String): (optional)代充商品类型。只有少数类目下的商品可以标记上此字段，具体哪些类目可以上传可以通过taobao.itemcat.features.get获得。在代充商品的类目下，不传表示不标记商品类型（交易搜索中就不能通过标记搜到相关的交易了）。可选类型：
        no_mark(不做类型标记)
        time_card(点卡软件代充)
        fee_card(话费软件代充)
    @request cid(Number): (optional)叶子类目id
    @request cod_postage_id(Number): (optional)货到付款运费模板ID
    @request desc(String): (optional)商品描述. 字数要大于5个字符，小于25000个字符 ，受违禁词控制
    @request ems_fee(Price): (optional)ems费用。取值范围:0.01-999.00;精确到2位小数;单位:元。如:25.07，表示:25元7分
    @request express_fee(Price): (optional)快递费用。取值范围:0.01-999.00;精确到2位小数;单位:元。如:15.07，表示:15元7分
    @request freight_payer(String): (optional)运费承担方式。运费承担方式。可选值:seller（卖家承担）,buyer(买家承担);
    @request has_discount(Boolean): (optional)支持会员打折。可选值:true,false;
    @request has_invoice(Boolean): (optional)是否有发票。可选值:true,false (商城卖家此字段必须为true)
    @request has_showcase(Boolean): (optional)橱窗推荐。可选值:true,false;
    @request has_warranty(Boolean): (optional)是否有保修。可选值:true,false;
    @request image(Image): (optional)商品图片。类型:JPG,GIF;最大长度:500k
    @request increment(Price): (optional)加价幅度 如果为0，代表系统代理幅度
    @request input_pids(String): (optional)用户自行输入的类目属性ID串，结构："pid1,pid2,pid3"，如："20000"（表示品牌） 注：通常一个类目下用户可输入的关键属性不超过1个。
    @request input_str(String): (optional)用户自行输入的子属性名和属性值，结构:"父属性值;一级子属性名;一级子属性值;二级子属性名;自定义输入值,....",如：“耐克;耐克系列;科比系列;科比系列;2K5,Nike乔丹鞋;乔丹系列;乔丹鞋系列;乔丹鞋系列;json5”，多个自定义属性用','分割，input_str需要与input_pids一一对应，注：通常一个类目下用户可输入的关键属性不超过1个。所有属性别名加起来不能超过3999字节。此处不可以使用“其他”、“其它”和“其她”这三个词。
    @request is_3D(Boolean): (optional)是否是3D
    @request is_ex(Boolean): (optional)是否在外店显示
    @request is_lightning_consignment(Boolean): (optional)实物闪电发货。注意：在售的闪电发货产品不允许取消闪电发货，需要先下架商品才能取消闪电发货标记
    @request is_replace_sku(Boolean): (optional)是否替换sku
    @request is_taobao(Boolean): (optional)是否在淘宝上显示
    @request is_xinpin(Boolean): (optional)商品是否为新品。只有在当前类目开通新品,并且当前用户拥有该类目下发布新品权限时才能设置is_xinpin为true，否则设置true后会返回错误码:isv.invalid-permission:xinpin。同时只有一口价全新的宝贝才能设置为新品，否则会返回错误码：isv.invalid-parameter:xinpin。不设置参数就保持原有值。
    @request lang(String): (optional)商品文字的版本，繁体传入”zh_HK”，简体传入”zh_CN”
    @request list_time(Date): (optional)上架时间。不论是更新架下的商品还是出售中的商品，如果这个字段小于当前时间则直接上架商品，并且上架的时间为更新商品的时间，此时item.is_timing为false，如果大于当前时间则宝贝会下架进入定时上架的宝贝中。
    @request location.city(String): (optional)所在地城市。如杭州 具体可以下载http://dl.open.taobao.com/sdk/商品城市列表.rar 取到
    @request location.state(String): (optional)所在地省份。如浙江 具体可以下载http://dl.open.taobao.com/sdk/商品城市列表.rar 取到
    @request num(Number): (optional)商品数量，取值范围:0-999999的整数。且需要等于Sku所有数量的和
    @request num_iid(Number): (required)商品数字ID，该参数必须
    @request outer_id(String): (optional)商家编码
    @request pic_path(String): (optional)商品主图需要关联的图片空间的相对url。这个url所对应的图片必须要属于当前用户。pic_path和image只需要传入一个,如果两个都传，默认选择pic_path
    @request post_fee(Price): (optional)平邮费用。取值范围:0.01-999.00;精确到2位小数;单位:元。如:5.07，表示:5元7分, 注:post_fee,express_fee,ems_fee需一起填写
    @request postage_id(Number): (optional)宝贝所属的运费模板ID。取值范围：整数且必须是该卖家的运费模板的ID（可通过taobao.postages.get获得当前会话用户的所有邮费模板）
    @request price(Price): (optional)商品价格。取值范围:0-100000000;精确到2位小数;单位:元。如:200.07，表示:200元7分。需要在正确的价格区间内。
    @request product_id(Number): (optional)商品所属的产品ID(B商家发布商品需要用)
    @request property_alias(String): (optional)属性值别名。如pid:vid:别名;pid1:vid1:别名1， pid:属性id vid:值id。总长度不超过512字节
    @request props(String): (optional)商品属性列表。格式:pid:vid;pid:vid。属性的pid调用taobao.itemprops.get取得，属性值的vid用taobao.itempropvalues.get取得vid。 如果该类目下面没有属性，可以不用填写。如果有属性，必选属性必填，其他非必选属性可以选择不填写.属性不能超过35对。所有属性加起来包括分割符不能超过549字节，单个属性没有限制。 如果有属性是可输入的话，则用字段input_str填入属性的值。
    @request sell_promise(Boolean): (optional)是否承诺退换货服务!虚拟商品无须设置此项!
    @request seller_cids(String): (optional)重新关联商品与店铺类目，结构:",cid1,cid2,...,"，如果店铺类目存在二级类目，必须传入子类目cids。
    @request sku_outer_ids(String): (optional)Sku的外部id串，结构如：1234,1342,… sku_properties, sku_quantities, sku_prices, sku_outer_ids在输入数据时要一一对应，如果没有sku_outer_ids也要写上这个参数，入参是","(这个是两个sku的示列，逗号数应该是sku个数减1)；该参数最大长度是512个字节
    @request sku_prices(String): (optional)更新的Sku的价格串，结构如：10.00,5.00,… 精确到2位小数;单位:元。如:200.07，表示:200元7分
    @request sku_properties(String): (optional)更新的Sku的属性串，调用taobao.itemprops.get获取类目属性，如果属性是销售属性，再用taobao.itempropvalues.get取得vid。格式:pid:vid;pid:vid。该字段内的销售属性也需要在props字段填写 。如果更新时有对Sku进行操作，则Sku的properties一定要传入。
    @request sku_quantities(String): (optional)更新的Sku的数量串，结构如：num1,num2,num3 如:2,3,4
    @request stuff_status(String): (optional)商品新旧程度。可选值:new（全新）,unused（闲置）,second（二手）。
    @request sub_stock(Number): (optional)商品是否支持拍下减库存:1支持;2取消支持(付款减库存);0(默认)不更改 集市卖家默认拍下减库存; 商城卖家默认付款减库存
    @request title(String): (optional)宝贝标题. 不能超过60字符,受违禁词控制
    @request valid_thru(Number): (optional)有效期。可选值:7,14;单位:天;
    @request weight(Number): (optional)商品的重量(商超卖家专用字段)
    """
    REQUEST = {
        'after_sale_id': {'type': topstruct.Number, 'is_required': False},
        'approve_status': {'type': topstruct.String, 'is_required': False},
        'auction_point': {'type': topstruct.Number, 'is_required': False},
        'auto_fill': {'type': topstruct.String, 'is_required': False},
        'cid': {'type': topstruct.Number, 'is_required': False},
        'cod_postage_id': {'type': topstruct.Number, 'is_required': False},
        'desc': {'type': topstruct.String, 'is_required': False},
        'ems_fee': {'type': topstruct.Price, 'is_required': False},
        'express_fee': {'type': topstruct.Price, 'is_required': False},
        'freight_payer': {'type': topstruct.String, 'is_required': False},
        'has_discount': {'type': topstruct.Boolean, 'is_required': False},
        'has_invoice': {'type': topstruct.Boolean, 'is_required': False},
        'has_showcase': {'type': topstruct.Boolean, 'is_required': False},
        'has_warranty': {'type': topstruct.Boolean, 'is_required': False},
        'image': {'type': topstruct.Image, 'is_required': False},
        'increment': {'type': topstruct.Price, 'is_required': False},
        'input_pids': {'type': topstruct.String, 'is_required': False},
        'input_str': {'type': topstruct.String, 'is_required': False},
        'is_3D': {'type': topstruct.Boolean, 'is_required': False},
        'is_ex': {'type': topstruct.Boolean, 'is_required': False},
        'is_lightning_consignment': {'type': topstruct.Boolean, 'is_required': False},
        'is_replace_sku': {'type': topstruct.Boolean, 'is_required': False},
        'is_taobao': {'type': topstruct.Boolean, 'is_required': False},
        'is_xinpin': {'type': topstruct.Boolean, 'is_required': False},
        'lang': {'type': topstruct.String, 'is_required': False},
        'list_time': {'type': topstruct.Date, 'is_required': False},
        'location.city': {'type': topstruct.String, 'is_required': False},
        'location.state': {'type': topstruct.String, 'is_required': False},
        'num': {'type': topstruct.Number, 'is_required': False},
        'num_iid': {'type': topstruct.Number, 'is_required': True},
        'outer_id': {'type': topstruct.String, 'is_required': False},
        'pic_path': {'type': topstruct.String, 'is_required': False},
        'post_fee': {'type': topstruct.Price, 'is_required': False},
        'postage_id': {'type': topstruct.Number, 'is_required': False},
        'price': {'type': topstruct.Price, 'is_required': False},
        'product_id': {'type': topstruct.Number, 'is_required': False},
        'property_alias': {'type': topstruct.String, 'is_required': False},
        'props': {'type': topstruct.String, 'is_required': False},
        'sell_promise': {'type': topstruct.Boolean, 'is_required': False},
        'seller_cids': {'type': topstruct.String, 'is_required': False},
        'sku_outer_ids': {'type': topstruct.String, 'is_required': False},
        'sku_prices': {'type': topstruct.String, 'is_required': False},
        'sku_properties': {'type': topstruct.String, 'is_required': False},
        'sku_quantities': {'type': topstruct.String, 'is_required': False},
        'stuff_status': {'type': topstruct.String, 'is_required': False},
        'sub_stock': {'type': topstruct.Number, 'is_required': False},
        'title': {'type': topstruct.String, 'is_required': False},
        'valid_thru': {'type': topstruct.Number, 'is_required': False},
        'weight': {'type': topstruct.Number, 'is_required': False}
    }

    RESPONSE = {
        'item': {'type': topstruct.Item, 'is_list': False}
    }

    API = 'taobao.item.price.update'


class ItemPropimgDeleteRequest(TOPRequest):
    """ 删除propimg_id 所指定的商品属性图片
        传入的num_iid所对应的商品必须属于当前会话的用户
        propimg_id对应的属性图片需要属于num_iid对应的商品

    @response prop_img(PropImg): 属性图片结构

    @request id(Number): (required)商品属性图片ID
    @request num_iid(Number): (required)商品数字ID，必选
    """
    REQUEST = {
        'id': {'type': topstruct.Number, 'is_required': True},
        'num_iid': {'type': topstruct.Number, 'is_required': True}
    }

    RESPONSE = {
        'prop_img': {'type': topstruct.PropImg, 'is_list': False}
    }

    API = 'taobao.item.propimg.delete'


class ItemPropimgUploadRequest(TOPRequest):
    """ 添加一张商品属性图片到num_iid指定的商品中
        传入的num_iid所对应的商品必须属于当前会话的用户
        图片的属性必须要是颜色的属性，这个在前台显示的时候需要和sku进行关联的
        商品属性图片只有享有服务的卖家（如：淘宝大卖家、订购了淘宝多图服务的卖家）才能上传
        商品属性图片有数量和大小上的限制，最多不能超过24张（每个颜色属性都有一张）。

    @response prop_img(PropImg): PropImg属性图片结构

    @request id(Number): (optional)属性图片ID。如果是新增不需要填写
    @request image(Image): (optional)属性图片内容。类型:JPG,GIF;最大长度:500K;图片大小不超过:1M
    @request num_iid(Number): (required)商品数字ID，必选
    @request position(Number): (optional)图片位置
    @request properties(String): (required)属性列表。调用taobao.itemprops.get获取类目属性，属性必须是颜色属性，再用taobao.itempropvalues.get取得vid。格式:pid:vid。
    """
    REQUEST = {
        'id': {'type': topstruct.Number, 'is_required': False},
        'image': {'type': topstruct.Image, 'is_required': False},
        'num_iid': {'type': topstruct.Number, 'is_required': True},
        'position': {'type': topstruct.Number, 'is_required': False},
        'properties': {'type': topstruct.String, 'is_required': True}
    }

    RESPONSE = {
        'prop_img': {'type': topstruct.PropImg, 'is_list': False}
    }

    API = 'taobao.item.propimg.upload'


class ItemQuantityUpdateRequest(TOPRequest):
    """ 提供按照全量或增量形式修改宝贝/SKU库存的功能

    @response item(Item): iid、numIid、num和modified，skus中每个sku的skuId、quantity和modified

    @request num_iid(Number): (required)商品数字ID，必填参数
    @request outer_id(String): (optional)SKU的商家编码，可选参数。如果不填则默认修改宝贝的库存，如果填了则按照商家编码搜索出对应的SKU并修改库存。当sku_id和本字段都填写时以sku_id为准搜索对应SKU
    @request quantity(Number): (required)库存修改值，必选。当全量更新库存时，quantity必须为大于等于0的正整数；当增量更新库存时，quantity为整数，可小于等于0。若增量更新时传入的库存为负数且绝对值大于当前实际库存，则库存改为0。比如当前实际库存为1，传入增量更新quantity=-5，库存改为0
    @request sku_id(Number): (optional)要操作的SKU的数字ID，可选。如果不填默认修改宝贝的库存，如果填上则修改该SKU的库存
    @request type(Number): (optional)库存更新方式，可选。1为全量更新，2为增量更新。如果不填，默认为全量更新
    """
    REQUEST = {
        'num_iid': {'type': topstruct.Number, 'is_required': True},
        'outer_id': {'type': topstruct.String, 'is_required': False},
        'quantity': {'type': topstruct.Number, 'is_required': True},
        'sku_id': {'type': topstruct.Number, 'is_required': False},
        'type': {'type': topstruct.Number, 'is_required': False}
    }

    RESPONSE = {
        'item': {'type': topstruct.Item, 'is_list': False}
    }

    API = 'taobao.item.quantity.update'


class ItemRecommendAddRequest(TOPRequest):
    """ 将当前用户指定商品设置为橱窗推荐状态
        橱窗推荐需要用户有剩余橱窗位才可以顺利执行
        这个Item所属卖家从传入的session中获取，需要session绑定
        需要判断橱窗推荐是否已满，橱窗推荐已满停止调用橱窗推荐接口，2010年1月底开放查询剩余橱窗推荐数后可以按数量橱窗推荐商品

    @response item(Item): 被推荐的商品的信息

    @request num_iid(Number): (required)商品数字ID，该参数必须
    """
    REQUEST = {
        'num_iid': {'type': topstruct.Number, 'is_required': True}
    }

    RESPONSE = {
        'item': {'type': topstruct.Item, 'is_list': False}
    }

    API = 'taobao.item.recommend.add'


class ItemRecommendDeleteRequest(TOPRequest):
    """ 取消当前用户指定商品的橱窗推荐状态
        这个Item所属卖家从传入的session中获取，需要session绑定

    @response item(Item): 被取消橱窗推荐的商品信息

    @request num_iid(Number): (required)商品数字ID，该参数必须
    """
    REQUEST = {
        'num_iid': {'type': topstruct.Number, 'is_required': True}
    }

    RESPONSE = {
        'item': {'type': topstruct.Item, 'is_list': False}
    }

    API = 'taobao.item.recommend.delete'


class ItemSkuAddRequest(TOPRequest):
    """ 新增一个sku到num_iid指定的商品中
        传入的iid所对应的商品必须属于当前会话的用户

    @response sku(Sku): sku

    @request item_price(Price): (optional)sku所属商品的价格。当用户新增sku，使商品价格不属于sku价格之间的时候，用于修改商品的价格，使sku能够添加成功
    @request lang(String): (optional)Sku文字的版本。可选值:zh_HK(繁体),zh_CN(简体);默认值:zh_CN
    @request num_iid(Number): (required)Sku所属商品数字id，可通过 taobao.item.get 获取。必选
    @request outer_id(String): (optional)Sku的商家外部id
    @request price(Price): (required)Sku的销售价格。商品的价格要在商品所有的sku的价格之间。精确到2位小数;单位:元。如:200.07，表示:200元7分
    @request properties(String): (required)Sku属性串。格式:pid:vid;pid:vid,如:1627207:3232483;1630696:3284570,表示:机身颜色:军绿色;手机套餐:一电一充。
        如果包含自定义属性则格式为pid:vid;pid2:vid2;$pText:vText , 其中$pText:vText为自定义属性。限制：其中$pText的‘$’前缀不能少，且pText和vText文本中不可以存在 冒号:和分号;以及逗号，
    @request quantity(Number): (required)Sku的库存数量。sku的总数量应该小于等于商品总数量(Item的NUM)。取值范围:大于零的整数
    """
    REQUEST = {
        'item_price': {'type': topstruct.Price, 'is_required': False},
        'lang': {'type': topstruct.String, 'is_required': False},
        'num_iid': {'type': topstruct.Number, 'is_required': True},
        'outer_id': {'type': topstruct.String, 'is_required': False},
        'price': {'type': topstruct.Price, 'is_required': True},
        'properties': {'type': topstruct.String, 'is_required': True},
        'quantity': {'type': topstruct.Number, 'is_required': True}
    }

    RESPONSE = {
        'sku': {'type': topstruct.Sku, 'is_list': False}
    }

    API = 'taobao.item.sku.add'


class ItemSkuDeleteRequest(TOPRequest):
    """ 删除一个sku的数据
        需要删除的sku通过属性properties进行匹配查找

    @response sku(Sku): Sku结构

    @request item_num(Number): (optional)sku所属商品的数量,大于0的整数。当用户删除sku，使商品数量不等于sku数量之和时候，用于修改商品的数量，使sku能够删除成功。特别是删除最后一个sku的时候，一定要设置商品数量到正常的值，否则删除失败
    @request item_price(Price): (optional)sku所属商品的价格。当用户删除sku，使商品价格不属于sku价格之间的时候，用于修改商品的价格，使sku能够删除成功
    @request lang(String): (optional)Sku文字的版本。可选值:zh_HK(繁体),zh_CN(简体);默认值:zh_CN
    @request num_iid(Number): (required)Sku所属商品数字id，可通过 taobao.item.get 获取。必选
    @request properties(String): (required)Sku属性串。格式:pid:vid;pid:vid,如: 1627207:3232483;1630696:3284570,表示机身颜色:军绿色;手机套餐:一电一充
    """
    REQUEST = {
        'item_num': {'type': topstruct.Number, 'is_required': False},
        'item_price': {'type': topstruct.Price, 'is_required': False},
        'lang': {'type': topstruct.String, 'is_required': False},
        'num_iid': {'type': topstruct.Number, 'is_required': True},
        'properties': {'type': topstruct.String, 'is_required': True}
    }

    RESPONSE = {
        'sku': {'type': topstruct.Sku, 'is_list': False}
    }

    API = 'taobao.item.sku.delete'


class ItemSkuGetRequest(TOPRequest):
    """ 获取sku_id所对应的sku数据
        sku_id对应的sku要属于传入的nick对应的卖家

    @response sku(Sku): Sku

    @request fields(FieldList): (required)需返回的字段列表。可选值：Sku结构体中的所有字段；字段之间用“,”分隔。
    @request nick(String): (special)卖家nick(num_iid和nick必传一个)
    @request num_iid(Number): (special)商品的数字IID（num_iid和nick必传一个，推荐用num_iid）
    @request sku_id(Number): (required)Sku的id。可以通过taobao.item.get得到
    """
    REQUEST = {
        'fields': {'type': topstruct.FieldList, 'is_required': True, 'optional': topstruct.Set({'iid', 'num_iid', 'quantity', 'status', 'outer_id', 'properties_name', 'properties', 'sku_id', 'created', 'price', 'modified'})},
        'nick': {'type': topstruct.String, 'is_required': False},
        'num_iid': {'type': topstruct.Number, 'is_required': False},
        'sku_id': {'type': topstruct.Number, 'is_required': True}
    }

    RESPONSE = {
        'sku': {'type': topstruct.Sku, 'is_list': False}
    }

    API = 'taobao.item.sku.get'


class ItemSkuPriceUpdateRequest(TOPRequest):
    """ 更新商品SKU的价格

    @response sku(Sku): 商品SKU信息（只包含num_iid和modified）

    @request item_price(Price): (optional)sku所属商品的价格。当用户更新sku，使商品价格不属于sku价格之间的时候，用于修改商品的价格，使sku能够更新成功
    @request lang(String): (optional)Sku文字的版本。可选值:zh_HK(繁体),zh_CN(简体);默认值:zh_CN
    @request num_iid(Number): (required)Sku所属商品数字id，可通过 taobao.item.get 获取
    @request outer_id(String): (optional)Sku的商家外部id
    @request price(Price): (optional)Sku的销售价格。精确到2位小数;单位:元。如:200.07，表示:200元7分。修改后的sku价格要保证商品的价格在所有sku价格所形成的价格区间内（例如：商品价格为6元，sku价格有5元、10元两种，如果要修改5元sku的价格，那么修改的范围只能是0-6元之间；如果要修改10元的sku，那么修改的范围只能是6到无穷大的区间中）
    @request properties(String): (required)Sku属性串。格式:pid:vid;pid:vid,如: 1627207:3232483;1630696:3284570,表示机身颜色:军绿色;手机套餐:一电一充
    @request quantity(Number): (optional)Sku的库存数量。sku的总数量应该小于等于商品总数量(Item的NUM)，sku数量变化后item的总数量也会随着变化。取值范围:大于等于零的整数
    """
    REQUEST = {
        'item_price': {'type': topstruct.Price, 'is_required': False},
        'lang': {'type': topstruct.String, 'is_required': False},
        'num_iid': {'type': topstruct.Number, 'is_required': True},
        'outer_id': {'type': topstruct.String, 'is_required': False},
        'price': {'type': topstruct.Price, 'is_required': False},
        'properties': {'type': topstruct.String, 'is_required': True},
        'quantity': {'type': topstruct.Number, 'is_required': False}
    }

    RESPONSE = {
        'sku': {'type': topstruct.Sku, 'is_list': False}
    }

    API = 'taobao.item.sku.price.update'


class ItemSkuUpdateRequest(TOPRequest):
    """ *更新一个sku的数据
        *需要更新的sku通过属性properties进行匹配查找
        *商品的数量和价格必须大于等于0
        *sku记录会更新到指定的num_iid对应的商品中
        *num_iid对应的商品必须属于当前的会话用户

    @response sku(Sku): 商品Sku

    @request item_price(Price): (optional)sku所属商品的价格。当用户更新sku，使商品价格不属于sku价格之间的时候，用于修改商品的价格，使sku能够更新成功
    @request lang(String): (optional)Sku文字的版本。可选值:zh_HK(繁体),zh_CN(简体);默认值:zh_CN
    @request num_iid(Number): (required)Sku所属商品数字id，可通过 taobao.item.get 获取
    @request outer_id(String): (optional)Sku的商家外部id
    @request price(Price): (optional)Sku的销售价格。精确到2位小数;单位:元。如:200.07，表示:200元7分。修改后的sku价格要保证商品的价格在所有sku价格所形成的价格区间内（例如：商品价格为6元，sku价格有5元、10元两种，如果要修改5元sku的价格，那么修改的范围只能是0-6元之间；如果要修改10元的sku，那么修改的范围只能是6到无穷大的区间中）
    @request properties(String): (required)Sku属性串。格式:pid:vid;pid:vid,如: 1627207:3232483;1630696:3284570,表示机身颜色:军绿色;手机套餐:一电一充。
        如果包含自定义属性，则格式为pid:vid;pid2:vid2;$pText:vText , 其中$pText:vText为自定义属性。限制：其中$pText的’$’前缀不能少，且pText和vText文本中不可以存在 冒号:和分号;以及逗号，
    @request quantity(Number): (optional)Sku的库存数量。sku的总数量应该小于等于商品总数量(Item的NUM)，sku数量变化后item的总数量也会随着变化。取值范围:大于等于零的整数
    """
    REQUEST = {
        'item_price': {'type': topstruct.Price, 'is_required': False},
        'lang': {'type': topstruct.String, 'is_required': False},
        'num_iid': {'type': topstruct.Number, 'is_required': True},
        'outer_id': {'type': topstruct.String, 'is_required': False},
        'price': {'type': topstruct.Price, 'is_required': False},
        'properties': {'type': topstruct.String, 'is_required': True},
        'quantity': {'type': topstruct.Number, 'is_required': False}
    }

    RESPONSE = {
        'sku': {'type': topstruct.Sku, 'is_list': False}
    }

    API = 'taobao.item.sku.update'


class ItemSkusGetRequest(TOPRequest):
    """ * 获取多个商品下的所有sku

    @response skus(Sku): Sku列表

    @request fields(FieldList): (required)需返回的字段列表。可选值：Sku结构体中的所有字段；字段之间用“,”分隔。
    @request num_iids(String): (required)sku所属商品数字id，必选。num_iid个数不能超过40个
    """
    REQUEST = {
        'fields': {'type': topstruct.FieldList, 'is_required': True, 'optional': topstruct.Set({'iid', 'num_iid', 'quantity', 'status', 'outer_id', 'properties_name', 'properties', 'sku_id', 'created', 'price', 'modified'})},
        'num_iids': {'type': topstruct.String, 'is_required': True}
    }

    RESPONSE = {
        'skus': {'type': topstruct.Sku, 'is_list': False}
    }

    API = 'taobao.item.skus.get'


class ItemTemplatesGetRequest(TOPRequest):
    """ 查询当前登录用户的店铺的宝贝详情页的模板名称

    @response item_template_list(ItemTemplate): 返回宝贝模板对象。包含模板id，模板name，还有模板的类别（0表示外店，1表示内店）
    """
    REQUEST = {}

    RESPONSE = {
        'item_template_list': {'type': topstruct.ItemTemplate, 'is_list': False}
    }

    API = 'taobao.item.templates.get'


class ItemUpdateRequest(TOPRequest):
    """ 根据传入的num_iid更新对应的商品的数据
        传入的num_iid所对应的商品必须属于当前会话的用户
        商品的属性和sku的属性有包含的关系，商品的价格要位于sku的价格区间之中（例如，sku价格有5元、10元两种，那么商品的价格就需要大于等于5元，小于等于10元，否则更新商品会失败）
        商品的类目和商品的价格、sku的价格都有一定的相关性（具体的关系要通过类目属性查询接口获得）
        当关键属性值更新为“其他”的时候，需要输入input_pids和input_str商品才能更新成功。该接口不支持产品属性修改。

    @response item(Item): 商品结构里的num_iid，modified

    @request after_sale_id(Number): (optional)售后服务说明模板id
    @request approve_status(String): (optional)商品上传后的状态。可选值:onsale（出售中）,instock（库中），如果同时更新商品状态为出售中及list_time为将来的时间，则商品还是处于定时上架的状态, 此时item.is_timing为true
    @request auction_point(Number): (optional)商品的积分返点比例。如：5 表示返点比例0.5%. 注意：返点比例必须是>0的整数，而且最大是90,即为9%.B商家在发布非虚拟商品时，返点必须是 5的倍数，即0.5%的倍数。其它是1的倍数，即0.1%的倍数。无名良品商家发布商品时，复用该字段记录积分宝返点比例，返点必须是对应类目的返点步长的整数倍，默认是5，即0.5%。注意此时该字段值依旧必须是>0的整数，注意此时该字段值依旧必须是>0的整数，最高值不超过500，即50%
    @request auto_fill(String): (optional)代充商品类型。只有少数类目下的商品可以标记上此字段，具体哪些类目可以上传可以通过taobao.itemcat.features.get获得。在代充商品的类目下，不传表示不标记商品类型（交易搜索中就不能通过标记搜到相关的交易了）。可选类型：
        no_mark(不做类型标记)
        time_card(点卡软件代充)
        fee_card(话费软件代充)
    @request cid(Number): (optional)叶子类目id
    @request cod_postage_id(Number): (optional)货到付款运费模板ID
    @request desc(String): (optional)商品描述. 字数要大于5个字符，小于25000个字符 ，受违禁词控制
    @request ems_fee(Price): (optional)ems费用。取值范围:0.01-999.00;精确到2位小数;单位:元。如:25.07，表示:25元7分
    @request express_fee(Price): (optional)快递费用。取值范围:0.01-999.00;精确到2位小数;单位:元。如:15.07，表示:15元7分
    @request freight_payer(String): (optional)运费承担方式。运费承担方式。可选值:seller（卖家承担）,buyer(买家承担);
    @request has_discount(Boolean): (optional)支持会员打折。可选值:true,false;
    @request has_invoice(Boolean): (optional)是否有发票。可选值:true,false (商城卖家此字段必须为true)
    @request has_showcase(Boolean): (optional)橱窗推荐。可选值:true,false;
    @request has_warranty(Boolean): (optional)是否有保修。可选值:true,false;
    @request image(Image): (optional)商品图片。类型:JPG,GIF;最大长度:500k
    @request increment(Price): (optional)加价幅度 如果为0，代表系统代理幅度
    @request input_pids(String): (optional)用户自行输入的类目属性ID串，结构："pid1,pid2,pid3"，如："20000"（表示品牌） 注：通常一个类目下用户可输入的关键属性不超过1个。
    @request input_str(String): (optional)用户自行输入的子属性名和属性值，结构:"父属性值;一级子属性名;一级子属性值;二级子属性名;自定义输入值,....",如：“耐克;耐克系列;科比系列;科比系列;2K5,Nike乔丹鞋;乔丹系列;乔丹鞋系列;乔丹鞋系列;json5”，多个自定义属性用','分割，input_str需要与input_pids一一对应，注：通常一个类目下用户可输入的关键属性不超过1个。所有属性别名加起来不能超过3999字节。此处不可以使用“其他”、“其它”和“其她”这三个词。
    @request is_3D(Boolean): (optional)是否是3D
    @request is_ex(Boolean): (optional)是否在外店显示
    @request is_lightning_consignment(Boolean): (optional)实物闪电发货。注意：在售的闪电发货产品不允许取消闪电发货，需要先下架商品才能取消闪电发货标记
    @request is_replace_sku(Boolean): (optional)是否替换sku
    @request is_taobao(Boolean): (optional)是否在淘宝上显示（如果传FALSE，则在淘宝主站无法显示该商品）
    @request is_xinpin(Boolean): (optional)商品是否为新品。只有在当前类目开通新品,并且当前用户拥有该类目下发布新品权限时才能设置is_xinpin为true，否则设置true后会返回错误码:isv.invalid-permission:xinpin。同时只有一口价全新的宝贝才能设置为新品，否则会返回错误码：isv.invalid-parameter:xinpin。不设置参数就保持原有值。
    @request lang(String): (optional)商品文字的版本，繁体传入”zh_HK”，简体传入”zh_CN”
    @request list_time(Date): (optional)上架时间。不论是更新架下的商品还是出售中的商品，如果这个字段小于当前时间则直接上架商品，并且上架的时间为更新商品的时间，此时item.is_timing为false，如果大于当前时间则宝贝会下架进入定时上架的宝贝中。
    @request location.city(String): (optional)所在地城市。如杭州 具体可以下载http://dl.open.taobao.com/sdk/商品城市列表.rar 取到
    @request location.state(String): (optional)所在地省份。如浙江 具体可以下载http://dl.open.taobao.com/sdk/商品城市列表.rar 取到
    @request num(Number): (optional)商品数量，取值范围:0-999999的整数。且需要等于Sku所有数量的和
    @request num_iid(Number): (required)商品数字ID，该参数必须
    @request outer_id(String): (optional)商家编码
    @request pic_path(String): (optional)商品主图需要关联的图片空间的相对url。这个url所对应的图片必须要属于当前用户。pic_path和image只需要传入一个,如果两个都传，默认选择pic_path
    @request post_fee(Price): (optional)平邮费用。取值范围:0.01-999.00;精确到2位小数;单位:元。如:5.07，表示:5元7分, 注:post_fee,express_fee,ems_fee需一起填写
    @request postage_id(Number): (optional)宝贝所属的运费模板ID。取值范围：整数且必须是该卖家的运费模板的ID（可通过taobao.postages.get获得当前会话用户的所有邮费模板）
    @request price(Price): (optional)商品价格。取值范围:0-100000000;精确到2位小数;单位:元。如:200.07，表示:200元7分。需要在正确的价格区间内。
    @request product_id(Number): (optional)商品所属的产品ID(B商家发布商品需要用)
    @request property_alias(String): (optional)属性值别名。如pid:vid:别名;pid1:vid1:别名1， pid:属性id vid:值id。总长度不超过512字节
    @request props(String): (optional)商品属性列表。格式:pid:vid;pid:vid。属性的pid调用taobao.itemprops.get取得，属性值的vid用taobao.itempropvalues.get取得vid。 如果该类目下面没有属性，可以不用填写。如果有属性，必选属性必填，其他非必选属性可以选择不填写.属性不能超过35对。所有属性加起来包括分割符不能超过549字节，单个属性没有限制。 如果有属性是可输入的话，则用字段input_str填入属性的值。
    @request sell_promise(Boolean): (optional)是否承诺退换货服务!虚拟商品无须设置此项!
    @request seller_cids(String): (optional)重新关联商品与店铺类目，结构:",cid1,cid2,...,"，如果店铺类目存在二级类目，必须传入子类目cids。
    @request sku_outer_ids(String): (optional)Sku的外部id串，结构如：1234,1342,… sku_properties, sku_quantities, sku_prices, sku_outer_ids在输入数据时要一一对应，如果没有sku_outer_ids也要写上这个参数，入参是","(这个是两个sku的示列，逗号数应该是sku个数减1)；该参数最大长度是512个字节
    @request sku_prices(String): (optional)更新的Sku的价格串，结构如：10.00,5.00,… 精确到2位小数;单位:元。如:200.07，表示:200元7分
    @request sku_properties(String): (optional)更新的Sku的属性串，调用taobao.itemprops.get获取类目属性，如果属性是销售属性，再用taobao.itempropvalues.get取得vid。格式:pid:vid;pid:vid,多个sku之间用逗号分隔。该字段内的销售属性(自定义的除外)也需要在props字段填写 . 规则：如果该SKU存在旧商品，则修改；否则新增Sku。如果更新时有对Sku进行操作，则Sku的properties一定要传入。如果存在自定义销售属性，则格式为pid:vid;pid2:vid2;$pText:vText，其中$pText:vText为自定义属性。限制：其中$pText的’$’前缀不能少，且pText和vText文本中不可以存在 冒号:和分号;以及逗号
    @request sku_quantities(String): (optional)更新的Sku的数量串，结构如：num1,num2,num3 如:2,3,4
    @request stuff_status(String): (optional)商品新旧程度。可选值:new（全新）,unused（闲置）,second（二手）。
    @request sub_stock(Number): (optional)商品是否支持拍下减库存:1支持;2取消支持(付款减库存);0(默认)不更改
        集市卖家默认拍下减库存;
        商城卖家默认付款减库存
    @request title(String): (optional)宝贝标题. 不能超过60字符,受违禁词控制
    @request valid_thru(Number): (optional)有效期。可选值:7,14;单位:天;
    @request weight(Number): (optional)商品的重量(商超卖家专用字段)
    """
    REQUEST = {
        'after_sale_id': {'type': topstruct.Number, 'is_required': False},
        'approve_status': {'type': topstruct.String, 'is_required': False},
        'auction_point': {'type': topstruct.Number, 'is_required': False},
        'auto_fill': {'type': topstruct.String, 'is_required': False},
        'cid': {'type': topstruct.Number, 'is_required': False},
        'cod_postage_id': {'type': topstruct.Number, 'is_required': False},
        'desc': {'type': topstruct.String, 'is_required': False},
        'ems_fee': {'type': topstruct.Price, 'is_required': False},
        'express_fee': {'type': topstruct.Price, 'is_required': False},
        'freight_payer': {'type': topstruct.String, 'is_required': False},
        'has_discount': {'type': topstruct.Boolean, 'is_required': False},
        'has_invoice': {'type': topstruct.Boolean, 'is_required': False},
        'has_showcase': {'type': topstruct.Boolean, 'is_required': False},
        'has_warranty': {'type': topstruct.Boolean, 'is_required': False},
        'image': {'type': topstruct.Image, 'is_required': False},
        'increment': {'type': topstruct.Price, 'is_required': False},
        'input_pids': {'type': topstruct.String, 'is_required': False},
        'input_str': {'type': topstruct.String, 'is_required': False},
        'is_3D': {'type': topstruct.Boolean, 'is_required': False},
        'is_ex': {'type': topstruct.Boolean, 'is_required': False},
        'is_lightning_consignment': {'type': topstruct.Boolean, 'is_required': False},
        'is_replace_sku': {'type': topstruct.Boolean, 'is_required': False},
        'is_taobao': {'type': topstruct.Boolean, 'is_required': False},
        'is_xinpin': {'type': topstruct.Boolean, 'is_required': False},
        'lang': {'type': topstruct.String, 'is_required': False},
        'list_time': {'type': topstruct.Date, 'is_required': False},
        'location.city': {'type': topstruct.String, 'is_required': False},
        'location.state': {'type': topstruct.String, 'is_required': False},
        'num': {'type': topstruct.Number, 'is_required': False},
        'num_iid': {'type': topstruct.Number, 'is_required': True},
        'outer_id': {'type': topstruct.String, 'is_required': False},
        'pic_path': {'type': topstruct.String, 'is_required': False},
        'post_fee': {'type': topstruct.Price, 'is_required': False},
        'postage_id': {'type': topstruct.Number, 'is_required': False},
        'price': {'type': topstruct.Price, 'is_required': False},
        'product_id': {'type': topstruct.Number, 'is_required': False},
        'property_alias': {'type': topstruct.String, 'is_required': False},
        'props': {'type': topstruct.String, 'is_required': False},
        'sell_promise': {'type': topstruct.Boolean, 'is_required': False},
        'seller_cids': {'type': topstruct.String, 'is_required': False},
        'sku_outer_ids': {'type': topstruct.String, 'is_required': False},
        'sku_prices': {'type': topstruct.String, 'is_required': False},
        'sku_properties': {'type': topstruct.String, 'is_required': False},
        'sku_quantities': {'type': topstruct.String, 'is_required': False},
        'stuff_status': {'type': topstruct.String, 'is_required': False},
        'sub_stock': {'type': topstruct.Number, 'is_required': False},
        'title': {'type': topstruct.String, 'is_required': False},
        'valid_thru': {'type': topstruct.Number, 'is_required': False},
        'weight': {'type': topstruct.Number, 'is_required': False}
    }

    RESPONSE = {
        'item': {'type': topstruct.Item, 'is_list': False}
    }

    API = 'taobao.item.update'


class ItemUpdateDelistingRequest(TOPRequest):
    """ * 单个商品下架
        * 输入的num_iid必须属于当前会话用户

    @response item(Item): 返回商品更新信息：返回的结果是:num_iid和modified

    @request num_iid(Number): (required)商品数字ID，该参数必须
    """
    REQUEST = {
        'num_iid': {'type': topstruct.Number, 'is_required': True}
    }

    RESPONSE = {
        'item': {'type': topstruct.Item, 'is_list': False}
    }

    API = 'taobao.item.update.delisting'


class ItemUpdateListingRequest(TOPRequest):
    """ * 单个商品上架
        * 输入的num_iid必须属于当前会话用户

    @response item(Item): 上架后返回的商品信息：返回的结果就是:num_iid和modified

    @request num(Number): (required)需要上架的商品的数量。取值范围:大于零的整数。如果商品有sku，则上架数量默认为所有sku数量总和，不可修改。否则商品数量根据设置数量调整为num
    @request num_iid(Number): (required)商品数字ID，该参数必须
    """
    REQUEST = {
        'num': {'type': topstruct.Number, 'is_required': True},
        'num_iid': {'type': topstruct.Number, 'is_required': True}
    }

    RESPONSE = {
        'item': {'type': topstruct.Item, 'is_list': False}
    }

    API = 'taobao.item.update.listing'


class ItemsCustomGetRequest(TOPRequest):
    """ 跟据卖家设定的商品外部id获取商品
        这个商品对应卖家从传入的session中获取，需要session绑定

    @response items(Item): 商品列表，具体返回字段以fields决定

    @request fields(FieldList): (required)需返回的字段列表。可选值：Item商品结构体中的所有字段；多个字段之间用“,”分隔。如果想返回整个子对象，那字段为item_img，如果是想返回子对象里面的字段，那字段为item_img.url。新增返回字段：one_station标记商品是否淘1站商品
    @request outer_id(String): (required)商品的外部商品ID
    """
    REQUEST = {
        'fields': {'type': topstruct.FieldList, 'is_required': True, 'optional': topstruct.Set({'item_imgs.position', 'created', 'desc', 'product_id', 'approve_status', 'detail_url', 'cod_postage_id', 'score', 'second_kill', 'is_timing', 'is_virtual', 'modified', 'is_taobao', 'list_time', 'input_str', 'props_name', 'item_imgs.created', 'item_imgs.id', 'type', 'is_xinpin', 'is_fenxiao', 'increment', 'outer_shop_auction_template_id', 'sub_stock', 'ww_status', 'num', 'nick', 'auto_fill', 'pic_url', 'cid', 'input_pids', 'skus', 'is_lightning_consignment', 'one_station', 'location', 'wap_detail_url', 'has_warranty', 'num_iid', 'post_fee', 'freight_payer', 'outer_id', 'ems_fee', 'inner_shop_auction_template_id', 'stuff_status', 'price', 'has_showcase', 'postage_id', 'prop_imgs', 'sell_promise', 'props', 'is_prepay', 'delist_time', 'valid_thru', 'seller_cids', 'promoted_service', 'auction_point', 'is_ex', 'has_invoice', 'property_alias', 'videos', 'volume', 'template_id', 'violation', 'title', 'item_imgs', 'is_3D', 'express_fee', 'item_imgs.url', 'wap_desc', 'after_sale_id', 'has_discount'})},
        'outer_id': {'type': topstruct.String, 'is_required': True}
    }

    RESPONSE = {
        'items': {'type': topstruct.Item, 'is_list': False}
    }

    API = 'taobao.items.custom.get'


class ItemsGetRequest(TOPRequest):
    """ 根据传入的搜索条件，获取商品列表（类似于淘宝页面上的商品搜索功能，但是只有搜索到的商品列表，不包含商品的ItemCategory列表）
        只能获得商品的部分信息，商品的详细信息请通过taobao.item.get获取
        如果只输入fields其他条件都不输入，系统会因为搜索条件不足而报错。
        不能通过设置cid=0来查询。

    @response items(Item): 搜索到的商品列表，具体字段根据权限和设定的fields决定
    @response total_results(Number): 搜索到符合条件的结果总数

    @request cid(Number): (special)商品所属类目Id,ItemCat中的cid字段。可以通过taobao.itemcats.get取到
    @request end_price(Number): (optional)商品最高价格。单位:元。正整数，取值范围:0-100000000
    @request end_score(Number): (optional)商品所属卖家的最大信用等级数，1表示1心，2表示2心……，设置此条件表示搜索结果里的商品，所属的卖家信用必须小于等于设置的end_score
    @request end_volume(Number): (optional)商品最近成交量最大值，设置此条件表示搜索结果里的商品，最近成交量必须小于等于设置的end_volume
    @request fields(FieldList): (required)需返回的商品结构字段列表。可选值为Item中的以下字段：num_iid,title,nick,pic_url,cid,price,type,delist_time,post_fee;多个字段用“,”分隔。如：num_iid,title。新增字段score(卖家信用等级数),volume(最近成交量),location（卖家地址，可以分别获取location.city,location.state）,num_iid商品数字id。此接口返回的post_fee是快递费用，volume对应搜索商品列表页的最近成交量
    @request genuine_security(Boolean): (optional)是否正品保障商品(既是如实描述，又是7天无理由退换货的商品，设置了这个属性时：is_prepay和promoted_service不能再行设置)，设置为true表示该商品是正品保障的商品，设置为false或不设置表示不判断这个属性
    @request is_3D(Boolean): (optional)是否是3D淘宝的商品,置为false或为空表示不对是否3D商品进行判断
    @request is_cod(Boolean): (optional)是否支持货到付款，设置为true表示支持货到付款，设置为false或不设置表示不判断这个属性
    @request is_mall(Boolean): (optional)表示是否搜索商城的商品这一搜索条件。
        值含义：true：搜索商城商品，false：搜素集市商品，若为null，则搜索全部的商品（默认值）
    @request is_prepay(Boolean): (optional)是否如实描述(即:先行赔付)商品，设置为true表示该商品是如实描述的商品，设置为false或不设置表示不判断这个属性
    @request is_xinpin(Boolean): (optional)表示是否新品这一搜索条件。
        值含义：true-是新品，false-无限制，null-无限制
    @request location.city(String): (optional)所在市。如：杭州。具体可以根据taobao.areas.get取到
    @request location.state(String): (optional)所在省。如：浙江。具体可以根据taobao.areas.get 取到
    @request nicks(String): (special)卖家昵称列表。多个之间以“,”分隔;最多支持5个卖家昵称。如：nick1,nick2,nick3
    @request one_station(Boolean): (optional)是否淘1站代购商品，设置为true表示淘1站商品，设置为false或不设置表示不判断这个属性
    @request order_by(String): (optional)排序方式。格式为column:asc/desc,column可选值为: price（价格）, delist_time（下架时间）, seller_credit（卖家信用）,popularity(人气)。如按价格升序排列表示为：price:asc。新增排序字段：volume（最近成交量）
    @request page_no(Number): (optional)页码。取值范围:大于零的整数。默认值为1,即默认返回第一页数据。用此接口获取数据时，当翻页获取的条数（page_no*page_size）超过10240,为了保护后台搜索引擎，接口将报错。所以请大家尽可能的细化自己的搜索条件，例如根据修改时间分段获取商品
    @request page_size(Number): (optional)每页条数。取值范围:大于零的整数;最大值:200;默认值:40
    @request post_free(Boolean): (optional)免运费（不设置包含所有邮费状态，设置为true结果只有卖家包邮的商品）。不能单独使用，要和其他条件一起用才行
    @request product_id(Number): (special)可以根据产品Id搜索属于这个spu的商品。这个字段可以通过查询 taobao.products.get 取到
    @request promoted_service(String): (optional)是否提供保障服务的商品。可选入参有：2、4。设置为2表示该商品是“假一赔三”的商品，设置为4表示该商品是“7天无理由退换货”的商品
    @request props(String): (special)商品属性。可以搜到拥有和输入的属性一样的商品列表。字段格式为：pid1:vid1;pid2:vid2.属性的pid调用taobao.itemprops.get取得，属性值的vid用taobao.itempropvalues.get取得vid。
    @request q(String): (special)搜索字段。 用来搜索商品的title以及商品所对应的产品的title
    @request start_price(Number): (optional)商品最低价格。单位:元。正整数，取值范围:0-100000000。
    @request start_score(Number): (optional)商品所属卖家的最小信用等级数，1表示1心，2表示2心……，设置此条件表示搜索结果里的商品，所属的卖家信用必须大于等于设置的start_score。
    @request start_volume(Number): (optional)商品最近成交量最小值，设置此条件表示搜索结果里的商品，最近成交量必须大于等于设置的start_volume。
    @request stuff_status(String): (optional)商品的新旧状态。可选入参有：new、second、unused 。设置为new表示该商品是全新的商品，设置为second表示该商品是二手的商品，设置为unused表示该商品是闲置的商品
    @request ww_status(Boolean): (optional)旺旺在线状态（不设置结果包含所有状态，设置为true结果只有旺旺在线卖家的商品）。不能单独使用，要和其他条件一起用才行
    """
    REQUEST = {
        'cid': {'type': topstruct.Number, 'is_required': False},
        'end_price': {'type': topstruct.Number, 'is_required': False},
        'end_score': {'type': topstruct.Number, 'is_required': False},
        'end_volume': {'type': topstruct.Number, 'is_required': False},
        'fields': {'type': topstruct.FieldList, 'is_required': True, 'optional': topstruct.Set({'delist_time', 'location', 'num_iid', 'type', 'post_fee', 'title', 'volume', 'location.city', 'nick', 'score', 'price', 'pic_url', 'location.state', 'cid'})},
        'genuine_security': {'type': topstruct.Boolean, 'is_required': False},
        'is_3D': {'type': topstruct.Boolean, 'is_required': False},
        'is_cod': {'type': topstruct.Boolean, 'is_required': False},
        'is_mall': {'type': topstruct.Boolean, 'is_required': False},
        'is_prepay': {'type': topstruct.Boolean, 'is_required': False},
        'is_xinpin': {'type': topstruct.Boolean, 'is_required': False},
        'location.city': {'type': topstruct.String, 'is_required': False},
        'location.state': {'type': topstruct.String, 'is_required': False},
        'nicks': {'type': topstruct.String, 'is_required': False},
        'one_station': {'type': topstruct.Boolean, 'is_required': False},
        'order_by': {'type': topstruct.String, 'is_required': False},
        'page_no': {'type': topstruct.Number, 'is_required': False},
        'page_size': {'type': topstruct.Number, 'is_required': False},
        'post_free': {'type': topstruct.Boolean, 'is_required': False},
        'product_id': {'type': topstruct.Number, 'is_required': False},
        'promoted_service': {'type': topstruct.String, 'is_required': False},
        'props': {'type': topstruct.String, 'is_required': False},
        'q': {'type': topstruct.String, 'is_required': False},
        'start_price': {'type': topstruct.Number, 'is_required': False},
        'start_score': {'type': topstruct.Number, 'is_required': False},
        'start_volume': {'type': topstruct.Number, 'is_required': False},
        'stuff_status': {'type': topstruct.String, 'is_required': False},
        'ww_status': {'type': topstruct.Boolean, 'is_required': False}
    }

    RESPONSE = {
        'items': {'type': topstruct.Item, 'is_list': False},
        'total_results': {'type': topstruct.Number, 'is_list': False}
    }

    API = 'taobao.items.get'


class ItemsInventoryGetRequest(TOPRequest):
    """ 获取当前用户作为卖家的仓库中的商品列表，并能根据传入的搜索条件对仓库中的商品列表进行过滤
        只能获得商品的部分信息，商品的详细信息请通过taobao.item.get获取

    @response items(Item): 搜索到底商品列表，具体字段根据设定的fields决定，不包括desc,stuff_status字段
    @response total_results(Number): 搜索到符合条件的结果总数

    @request banner(String): (optional)分类字段。可选值:
        regular_shelved(定时上架)
        never_on_shelf(从未上架)
        sold_out(全部卖完)
        off_shelf(我下架的)
        for_shelved(等待所有上架)
        violation_off_shelf(违规下架的)
        默认查询的是for_shelved(等待所有上架)这个状态的商品
    @request cid(Number): (optional)商品类目ID。ItemCat中的cid字段。可以通过taobao.itemcats.get取到
    @request end_modified(Date): (optional)商品结束修改时间
    @request fields(FieldList): (required)需返回的字段列表。可选值：Item商品结构体中的以下字段：
        approve_status,num_iid,title,nick,type,cid,pic_url,num,props,valid_thru,
        list_time,price,has_discount,has_invoice,has_warranty,has_showcase,
        modified,delist_time,postage_id,seller_cids,outer_id；字段之间用“,”分隔。
        不支持其他字段，如果需要获取其他字段数据，调用taobao.item.get。
    @request has_discount(Boolean): (optional)是否参与会员折扣。可选值：true，false。默认不过滤该条件
    @request is_ex(Boolean): (optional)商品是否在外部网店显示
    @request is_taobao(Boolean): (optional)商品是否在淘宝显示
    @request order_by(String): (optional)排序方式。格式为column:asc/desc ，column可选值:list_time(上架时间),delist_time(下架时间),num(商品数量)，modified(最近修改时间);默认上架时间降序(即最新上架排在前面)。如按照上架时间降序排序方式为list_time:desc
    @request page_no(Number): (optional)页码。取值范围:大于零小于等于101的整数;默认值为1，即返回第一页数据。当页码超过101页时系统就会报错，故请大家在用此接口获取数据时尽可能的细化自己的搜索条件，例如根据修改时间分段获取商品。
    @request page_size(Number): (optional)每页条数。取值范围:大于零的整数;最大值：200；默认值：40。
    @request q(String): (optional)搜索字段。搜索商品的title。
    @request seller_cids(String): (optional)卖家店铺内自定义类目ID。多个之间用“,”分隔。可以根据taobao.sellercats.list.get获得.(<font color="red">注：目前最多支持32个ID号传入</font>)
    @request start_modified(Date): (optional)商品起始修改时间
    """
    REQUEST = {
        'banner': {'type': topstruct.String, 'is_required': False},
        'cid': {'type': topstruct.Number, 'is_required': False},
        'end_modified': {'type': topstruct.Date, 'is_required': False},
        'fields': {'type': topstruct.FieldList, 'is_required': True, 'optional': topstruct.Set({'list_time', 'delist_time', 'valid_thru', 'has_warranty', 'num_iid', 'postage_id', 'type', 'outer_id', 'title', 'has_discount', 'nick', 'has_showcase', 'props', 'has_invoice', 'price', 'pic_url', 'cid', 'modified', 'approve_status', 'num', 'seller_cids'})},
        'has_discount': {'type': topstruct.Boolean, 'is_required': False},
        'is_ex': {'type': topstruct.Boolean, 'is_required': False},
        'is_taobao': {'type': topstruct.Boolean, 'is_required': False},
        'order_by': {'type': topstruct.String, 'is_required': False},
        'page_no': {'type': topstruct.Number, 'is_required': False},
        'page_size': {'type': topstruct.Number, 'is_required': False},
        'q': {'type': topstruct.String, 'is_required': False},
        'seller_cids': {'type': topstruct.String, 'is_required': False},
        'start_modified': {'type': topstruct.Date, 'is_required': False}
    }

    RESPONSE = {
        'items': {'type': topstruct.Item, 'is_list': False},
        'total_results': {'type': topstruct.Number, 'is_list': False}
    }

    API = 'taobao.items.inventory.get'


class ItemsListGetRequest(TOPRequest):
    """ 查看非公开属性时需要用户登录

    @response items(Item): 获取的商品 具体字段根据权限和设定的fields决定

    @request fields(FieldList): (required)需要返回的商品对象字段。可选值：Item商品结构体中所有字段均可返回；多个字段用“,”分隔。如果想返回整个子对象，那字段为itemimg，如果是想返回子对象里面的字段，那字段为itemimg.url。
    @request num_iids(String): (required)商品数字id列表，多个num_iid用逗号隔开，一次不超过20个。
    """
    REQUEST = {
        'fields': {'type': topstruct.FieldList, 'is_required': True, 'optional': topstruct.Set({'item_imgs.position', 'created', 'desc', 'product_id', 'approve_status', 'detail_url', 'cod_postage_id', 'score', 'second_kill', 'is_timing', 'is_virtual', 'modified', 'is_taobao', 'list_time', 'input_str', 'props_name', 'item_imgs.created', 'item_imgs.id', 'type', 'is_xinpin', 'is_fenxiao', 'increment', 'outer_shop_auction_template_id', 'sub_stock', 'ww_status', 'num', 'nick', 'auto_fill', 'pic_url', 'cid', 'input_pids', 'skus', 'is_lightning_consignment', 'one_station', 'location', 'wap_detail_url', 'has_warranty', 'num_iid', 'post_fee', 'freight_payer', 'outer_id', 'ems_fee', 'inner_shop_auction_template_id', 'stuff_status', 'price', 'has_showcase', 'postage_id', 'prop_imgs', 'sell_promise', 'props', 'is_prepay', 'delist_time', 'valid_thru', 'seller_cids', 'promoted_service', 'auction_point', 'is_ex', 'has_invoice', 'property_alias', 'videos', 'volume', 'template_id', 'violation', 'title', 'item_imgs', 'is_3D', 'express_fee', 'item_imgs.url', 'wap_desc', 'after_sale_id', 'has_discount'})},
        'num_iids': {'type': topstruct.String, 'is_required': True}
    }

    RESPONSE = {
        'items': {'type': topstruct.Item, 'is_list': False}
    }

    API = 'taobao.items.list.get'


class ItemsOnsaleGetRequest(TOPRequest):
    """ 获取当前用户作为卖家的出售中的商品列表，并能根据传入的搜索条件对出售中的商品列表进行过滤
        只能获得商品的部分信息，商品的详细信息请通过taobao.item.get获取

    @response items(Item): 搜索到的商品列表，具体字段根据设定的fields决定，不包括desc字段
    @response total_results(Number): 搜索到符合条件的结果总数

    @request cid(Number): (optional)商品类目ID。ItemCat中的cid字段。可以通过taobao.itemcats.get取到
    @request end_modified(Date): (optional)结束的修改时间
    @request fields(FieldList): (required)需返回的字段列表。可选值：Item商品结构体中的以下字段：
        approve_status,num_iid,title,nick,type,cid,pic_url,num,props,valid_thru,list_time,price,has_discount,has_invoice,has_warranty,has_showcase,modified,delist_time,postage_id,seller_cids,outer_id；字段之间用“,”分隔。
        不支持其他字段，如果需要获取其他字段数据，调用taobao.item.get。
    @request has_discount(Boolean): (optional)是否参与会员折扣。可选值：true，false。默认不过滤该条件
    @request has_showcase(Boolean): (optional)是否橱窗推荐。 可选值：true，false。默认不过滤该条件
    @request is_ex(Boolean): (optional)商品是否在外部网店显示
    @request is_taobao(Boolean): (optional)商品是否在淘宝显示
    @request order_by(String): (optional)排序方式。格式为column:asc/desc ，column可选值:list_time(上架时间),delist_time(下架时间),num(商品数量)，modified(最近修改时间);默认上架时间降序(即最新上架排在前面)。如按照上架时间降序排序方式为list_time:desc
    @request page_no(Number): (optional)页码。取值范围:大于零的整数。默认值为1,即默认返回第一页数据。用此接口获取数据时，当翻页获取的条数（page_no*page_size）超过10万,为了保护后台搜索引擎，接口将报错。所以请大家尽可能的细化自己的搜索条件，例如根据修改时间分段获取商品
    @request page_size(Number): (optional)每页条数。取值范围:大于零的整数;最大值：200；默认值：40。用此接口获取数据时，当翻页获取的条数（page_no*page_size）超过10万,为了保护后台搜索引擎，接口将报错。所以请大家尽可能的细化自己的搜索条件，例如根据修改时间分段获取商品
    @request q(String): (optional)搜索字段。搜索商品的title。
    @request seller_cids(String): (optional)卖家店铺内自定义类目ID。多个之间用“,”分隔。可以根据taobao.sellercats.list.get获得.(<font color="red">注：目前最多支持32个ID号传入</font>)
    @request start_modified(Date): (optional)起始的修改时间
    """
    REQUEST = {
        'cid': {'type': topstruct.Number, 'is_required': False},
        'end_modified': {'type': topstruct.Date, 'is_required': False},
        'fields': {'type': topstruct.FieldList, 'is_required': True, 'optional': topstruct.Set({'list_time', 'delist_time', 'valid_thru', 'has_warranty', 'num_iid', 'postage_id', 'type', 'outer_id', 'title', 'has_discount', 'nick', 'has_showcase', 'props', 'has_invoice', 'price', 'pic_url', 'cid', 'modified', 'approve_status', 'num', 'seller_cids'})},
        'has_discount': {'type': topstruct.Boolean, 'is_required': False},
        'has_showcase': {'type': topstruct.Boolean, 'is_required': False},
        'is_ex': {'type': topstruct.Boolean, 'is_required': False},
        'is_taobao': {'type': topstruct.Boolean, 'is_required': False},
        'order_by': {'type': topstruct.String, 'is_required': False},
        'page_no': {'type': topstruct.Number, 'is_required': False},
        'page_size': {'type': topstruct.Number, 'is_required': False},
        'q': {'type': topstruct.String, 'is_required': False},
        'seller_cids': {'type': topstruct.String, 'is_required': False},
        'start_modified': {'type': topstruct.Date, 'is_required': False}
    }

    RESPONSE = {
        'items': {'type': topstruct.Item, 'is_list': False},
        'total_results': {'type': topstruct.Number, 'is_list': False}
    }

    API = 'taobao.items.onsale.get'


class ItemsSearchRequest(TOPRequest):
    """ * 根据传入的搜索条件，获取商品列表和商品类目信息ItemCategory列表（类似于淘宝页面上的商品搜索功能，与 taobao.items.get的区别在于：这个方法得到的结果既有商品列表，又有类目信息列表）
        * 商品列表里只能获得商品的部分信息，商品的详细信息请通过taobao.item.get获取
        * 商品类目信息列表里只包含类目id和该类目下商品的数量
        * 不能通过设置cid=0来查询

    @response item_search(ItemSearch): 搜索到的商品，具体字段根据权限和设定的fields决定
    @response total_results(Number): 搜索到符合条件的结果总数

    @request auction_flag(Boolean): (optional)商品是否为虚拟商品
        true：是虚拟商品
        false：不是虚拟商品
    @request auto_post(Boolean): (optional)商品是否为自动发货
        true：自动发货
        false：非自动发货
    @request cid(Number): (special)商品所属类目Id。ItemCat中的cid。 可以通过taobao.itemcats.get取到
    @request end_price(Number): (optional)商品最高价格。单位:元。正整数，取值范围:0-100000000
    @request end_score(Number): (optional)商品所属卖家的最大信用等级数，1表示1心，2表示2心……，设置此条件表示搜索结果里的商品，所属的卖家信用必须小于等于设置的end_score
    @request end_volume(Number): (optional)商品30天内最大销售数，设置此条件表示搜索结果里的商品，最近成交量必须小于等于设置的end_volume
    @request fields(FieldList): (required)需返回的商品结构字段列表。可选值为Item中的以下字段：num_iid,title,nick,pic_url,cid,price,type,delist_time,post_fee；多个字段之间用“,” 分隔。如：num_iid,title。新增字段location（卖家地址，可以分别获取location.city,location.state）；score(卖家信用等级数),volume(最近成交量)
        新增字段：has_discount, num, is_prepay, promoted_service, ww_status, list_time
    @request genuine_security(Boolean): (optional)是否正品保障商品(既是如实描述，又是7天无理由退换货的商品，设置了这个属性时：is_prepay和promoted_service不能再行设置)，设置为true表示该商品是正品保障的商品，设置为false或不设置表示不判断这个属性
    @request has_discount(Boolean): (optional)商品是否对会员打折
    @request is_3D(Boolean): (optional)是否是3D淘宝的商品,置为false或为空表示不对是否3D商品进行判断
    @request is_cod(Boolean): (optional)是否支持货到付款，设置为true表示支持货到付款，设置为false或不设置表示不判断这个属性
    @request is_mall(Boolean): (optional)表示是否搜索商城的商品这一搜索条件。 值含义：true：搜索商城商品，false：搜素集市商品，若为null，则搜索全部的商品（默认值）
    @request is_prepay(Boolean): (optional)是否如实描述(即:先行赔付)商品，设置为true表示该商品是如实描述的商品，设置为false或不设置表示不判断这个属性
    @request is_xinpin(Boolean): (optional)表示是否新品这一搜索条件。 值含义：true-是新品，false-无限制，不输入(null)-无限制
    @request location.city(String): (optional)所在市。如：杭州
    @request location.state(String): (optional)所在省。如：浙江
    @request nicks(String): (special)卖家昵称列表。多个之间用“,”分隔；最多支持5个卖家昵称。如:nick1,nick2,nick3。
    @request one_station(Boolean): (optional)是否淘1站代购商品，设置为true表示淘1站商品，设置为false或不设置表示不判断这个属性
    @request order_by(String): (optional)排序方式。格式为column:asc/desc,column可选值为: price, delist_time, seller_credit；如按价格升序排列表示为：price:asc。新增排序字段：volume（最近成交量）；新增排序字段：popularity(商品的人气值)
    @request page_no(Number): (optional)页码。取值范围:大于零的整数。默认值为1,即默认返回第一页数据。用此接口获取数据时，当翻页获取的条数（page_no*page_size）超过10240,为了保护后台搜索引擎，接口将报错。所以请大家尽可能的细化自己的搜索条件，例如根据修改时间分段获取商品
    @request page_size(Number): (optional)每页条数。取值范围:大于零的整数;最大值：200；默认值：40
    @request post_free(Boolean): (optional)免运费（不设置或设置为false为包含所有邮费状态，设置为true结果只有卖家包邮的商品）不能单独使用，要和其他条件一起用才行。
    @request product_id(Number): (special)可以根据产品Id搜索属于这个spu的商品。这个字段可以通过查询 taobao.products.get 取到
    @request promoted_service(String): (optional)是否提供保障服务的商品。可选入参有：2、4。设置为2表示该商品是“假一赔三”的商品，设置为4表示该商品是“7天无理由退换货”的商品
    @request props(String): (special)商品属性。商品属性。可以搜到拥有和输入属性一样的商品列表。字段格式为：pid1:vid1;pid2:vid2.属性的pid调用 taobao.itemprops.get.v2取得，属性值的vid用taobao.itempropvalues.get取得vid。
    @request q(String): (special)搜索字段。 用来搜索商品的title以及对应产品的title。
    @request start_price(Number): (optional)商品最低价格。单位:元。正整数，取值范围:0-100000000。
    @request start_score(Number): (optional)商品所属卖家的最小信用等级数，1表示1心，2表示2心……，设置此条件表示搜索结果里的商品，所属的卖家信用必须大于等于设置的 start_score。
    @request start_volume(Number): (optional)商品30天内最小销售数，设置此条件表示搜索结果里的商品，最近成交量必须大于等于设置的start_volume。
    @request stuff_status(String): (optional)商品的新旧状态。可选入参有：new、second、unused 。设置为new表示该商品是全新的商品，设置为second表示该商品是二手的商品，设置为unused表示该商品是闲置的商品
    @request ww_status(Boolean): (optional)旺旺在线状态（不设置结果包含所有状态，设置为true结果只有旺旺在线卖家的商品）不能单独使用，要和其他条件一起用才行。
    """
    REQUEST = {
        'auction_flag': {'type': topstruct.Boolean, 'is_required': False},
        'auto_post': {'type': topstruct.Boolean, 'is_required': False},
        'cid': {'type': topstruct.Number, 'is_required': False},
        'end_price': {'type': topstruct.Number, 'is_required': False},
        'end_score': {'type': topstruct.Number, 'is_required': False},
        'end_volume': {'type': topstruct.Number, 'is_required': False},
        'fields': {'type': topstruct.FieldList, 'is_required': True, 'optional': topstruct.Set({'is_prepay', 'delist_time', 'location', 'num_iid', 'promoted_service', 'list_time', 'type', 'post_fee', 'title', 'volume', 'location.city', 'nick', 'ww_status', 'score', 'price', 'pic_url', 'location.state', 'cid', 'has_discount', 'num'})},
        'genuine_security': {'type': topstruct.Boolean, 'is_required': False},
        'has_discount': {'type': topstruct.Boolean, 'is_required': False},
        'is_3D': {'type': topstruct.Boolean, 'is_required': False},
        'is_cod': {'type': topstruct.Boolean, 'is_required': False},
        'is_mall': {'type': topstruct.Boolean, 'is_required': False},
        'is_prepay': {'type': topstruct.Boolean, 'is_required': False},
        'is_xinpin': {'type': topstruct.Boolean, 'is_required': False},
        'location.city': {'type': topstruct.String, 'is_required': False},
        'location.state': {'type': topstruct.String, 'is_required': False},
        'nicks': {'type': topstruct.String, 'is_required': False},
        'one_station': {'type': topstruct.Boolean, 'is_required': False},
        'order_by': {'type': topstruct.String, 'is_required': False},
        'page_no': {'type': topstruct.Number, 'is_required': False},
        'page_size': {'type': topstruct.Number, 'is_required': False},
        'post_free': {'type': topstruct.Boolean, 'is_required': False},
        'product_id': {'type': topstruct.Number, 'is_required': False},
        'promoted_service': {'type': topstruct.String, 'is_required': False},
        'props': {'type': topstruct.String, 'is_required': False},
        'q': {'type': topstruct.String, 'is_required': False},
        'start_price': {'type': topstruct.Number, 'is_required': False},
        'start_score': {'type': topstruct.Number, 'is_required': False},
        'start_volume': {'type': topstruct.Number, 'is_required': False},
        'stuff_status': {'type': topstruct.String, 'is_required': False},
        'ww_status': {'type': topstruct.Boolean, 'is_required': False}
    }

    RESPONSE = {
        'item_search': {'type': topstruct.ItemSearch, 'is_list': False},
        'total_results': {'type': topstruct.Number, 'is_list': False}
    }

    API = 'taobao.items.search'


class ProductAddRequest(TOPRequest):
    """ 获取类目ID，必需是叶子类目ID；调用taobao.itemcats.get.v2获取
        传入关键属性,结构:pid:vid;pid:vid.调用taobao.itemprops.get.v2获取pid,
        调用taobao.itempropvalues.get获取vid;如果碰到用户自定义属性,请用customer_props.

    @response product(Product): 产品结构

    @request binds(String): (optional)非关键属性结构:pid:vid;pid:vid.非关键属性不包含关键属性、销售属性、用户自定义属性、商品属性;调用taobao.itemprops.get获取pid,调用taobao.itempropvalues.get获取vid.<br><font color=red>注:支持最大长度为512字节</font>
    @request cid(Number): (required)商品类目ID.调用taobao.itemcats.get获取;注意:必须是叶子类目 id.
    @request customer_props(String): (special)用户自定义属性,结构：pid1:value1;pid2:value2，如果有型号，系列,货号等用: 隔开 例如：“20000:优衣库:型号:001:632501:1234”，表示“品牌:优衣库:型号:001:货号:1234”
    @request desc(String): (optional)产品描述.最大25000个字节
    @request image(Image): (required)产品主图片.最大1M,目前仅支持GIF,JPG.
    @request major(Boolean): (optional)是不是主图
    @request market_time(Date): (optional)上市时间。目前只支持鞋城类目传入此参数
    @request name(String): (required)产品名称,最大60个字节.
    @request outer_id(String): (optional)外部产品ID
    @request price(String): (required)产品市场价.精确到2位小数;单位为元.如：200.07
    @request property_alias(String): (optional)销售属性值别名。格式为pid1:vid1:alias1;pid1:vid2:alia2。只有少数销售属性值支持传入别名，比如颜色和尺寸
    @request props(String): (special)关键属性 结构:pid:vid;pid:vid.调用taobao.itemprops.get获取pid,调用taobao.itempropvalues.get获取vid;如果碰到用户自定义属性,请用customer_props.
    @request sale_props(String): (optional)销售属性结构:pid:vid;pid:vid.调用taobao.itemprops.get获取is_sale_prop＝true的pid,调用taobao.itempropvalues.get获取vid.
    """
    REQUEST = {
        'binds': {'type': topstruct.String, 'is_required': False},
        'cid': {'type': topstruct.Number, 'is_required': True},
        'customer_props': {'type': topstruct.String, 'is_required': False},
        'desc': {'type': topstruct.String, 'is_required': False},
        'image': {'type': topstruct.Image, 'is_required': True},
        'major': {'type': topstruct.Boolean, 'is_required': False},
        'market_time': {'type': topstruct.Date, 'is_required': False},
        'name': {'type': topstruct.String, 'is_required': True},
        'outer_id': {'type': topstruct.String, 'is_required': False},
        'price': {'type': topstruct.String, 'is_required': True},
        'property_alias': {'type': topstruct.String, 'is_required': False},
        'props': {'type': topstruct.String, 'is_required': False},
        'sale_props': {'type': topstruct.String, 'is_required': False}
    }

    RESPONSE = {
        'product': {'type': topstruct.Product, 'is_list': False}
    }

    API = 'taobao.product.add'


class ProductGetRequest(TOPRequest):
    """ 两种方式查看一个产品详细信息:
        传入product_id来查询
        传入cid和props来查询

    @response product(Product): 返回具体信息为入参fields请求的字段信息

    @request cid(Number): (special)商品类目id.调用taobao.itemcats.get获取;必须是叶子类目id,如果没有传product_id,那么cid和props必须要传.
    @request fields(FieldList): (required)需返回的字段列表.可选值:Product数据结构中的所有字段;多个字段之间用","分隔.
    @request product_id(Number): (special)Product的id.两种方式来查看一个产品:1.传入product_id来查询 2.传入cid和props来查询
    @request props(String): (special)比如:诺基亚N73这个产品的关键属性列表就是:品牌:诺基亚;型号:N73,对应的PV值就是10005:10027;10006:29729.
    """
    REQUEST = {
        'cid': {'type': topstruct.Number, 'is_required': False},
        'fields': {'type': topstruct.FieldList, 'is_required': True, 'optional': topstruct.Set({'cat_name', 'product_imgs', 'desc', 'product_id', 'props_str', 'vertical_market', 'status', 'modified', 'sale_props_str', 'pic_url', 'cid', 'level', 'tsc', 'pic_path', 'outer_id', 'price', 'binds_str', 'collect_num', 'created', 'name', 'props', 'customer_props', 'sale_props', 'property_alias', 'binds', 'product_prop_imgs'})},
        'product_id': {'type': topstruct.Number, 'is_required': False},
        'props': {'type': topstruct.String, 'is_required': False}
    }

    RESPONSE = {
        'product': {'type': topstruct.Product, 'is_list': False}
    }

    API = 'taobao.product.get'


class ProductImgDeleteRequest(TOPRequest):
    """ 1.传入非主图ID
        2.传入产品ID
        删除产品非主图

    @response product_img(ProductImg): 返回productimg中的：id,product_id

    @request id(Number): (required)非主图ID
    @request product_id(Number): (required)产品ID.Product的id,通过taobao.product.add接口新增产品的时候会返回id.
    """
    REQUEST = {
        'id': {'type': topstruct.Number, 'is_required': True},
        'product_id': {'type': topstruct.Number, 'is_required': True}
    }

    RESPONSE = {
        'product_img': {'type': topstruct.ProductImg, 'is_list': False}
    }

    API = 'taobao.product.img.delete'


class ProductImgUploadRequest(TOPRequest):
    """ 1.传入产品ID
        2.传入图片内容
        注意：图片最大为500K,只支持JPG,GIF格式,如果需要传多张，可调多次

    @response product_img(ProductImg): 返回产品图片结构中的：url,id,created,modified

    @request id(Number): (optional)产品图片ID.修改图片时需要传入
    @request image(Image): (required)图片内容.图片最大为500K,只支持JPG,GIF格式.
    @request is_major(Boolean): (optional)是否将该图片设为主图.可选值:true,false;默认值:false.
    @request position(Number): (optional)图片序号
    @request product_id(Number): (required)产品ID.Product的id
    """
    REQUEST = {
        'id': {'type': topstruct.Number, 'is_required': False},
        'image': {'type': topstruct.Image, 'is_required': True},
        'is_major': {'type': topstruct.Boolean, 'is_required': False},
        'position': {'type': topstruct.Number, 'is_required': False},
        'product_id': {'type': topstruct.Number, 'is_required': True}
    }

    RESPONSE = {
        'product_img': {'type': topstruct.ProductImg, 'is_list': False}
    }

    API = 'taobao.product.img.upload'


class ProductPropimgDeleteRequest(TOPRequest):
    """ 1.传入属性图片ID
        2.传入产品ID
        删除一个产品的属性图片

    @response product_prop_img(ProductPropImg): 返回product_prop_img数据结构中的：product_id,id

    @request id(Number): (required)属性图片ID
    @request product_id(Number): (required)产品ID.Product的id.
    """
    REQUEST = {
        'id': {'type': topstruct.Number, 'is_required': True},
        'product_id': {'type': topstruct.Number, 'is_required': True}
    }

    RESPONSE = {
        'product_prop_img': {'type': topstruct.ProductPropImg, 'is_list': False}
    }

    API = 'taobao.product.propimg.delete'


class ProductPropimgUploadRequest(TOPRequest):
    """ 传入产品ID
        传入props,目前仅支持颜色属性.调用taobao.itemprops.get.v2取得颜色属性pid,
        再用taobao.itempropvalues.get取得vid;格式:pid:vid,只能传入一个颜色pid:vid串;
        传入图片内容
        注意：图片最大为2M,只支持JPG,GIF,如果需要传多张，可调多次

    @response product_prop_img(ProductPropImg): 支持返回产品属性图片中的：url,id,created,modified

    @request id(Number): (optional)产品属性图片ID
    @request image(Image): (required)图片内容.图片最大为2M,只支持JPG,GIF.
    @request position(Number): (optional)图片序号
    @request product_id(Number): (required)产品ID.Product的id
    @request props(String): (required)属性串.目前仅支持颜色属性.调用taobao.itemprops.get获取类目属性,取得颜色属性pid,再用taobao.itempropvalues.get取得vid;格式:pid:vid,只能传入一个颜色pid:vid串;
    """
    REQUEST = {
        'id': {'type': topstruct.Number, 'is_required': False},
        'image': {'type': topstruct.Image, 'is_required': True},
        'position': {'type': topstruct.Number, 'is_required': False},
        'product_id': {'type': topstruct.Number, 'is_required': True},
        'props': {'type': topstruct.String, 'is_required': True}
    }

    RESPONSE = {
        'product_prop_img': {'type': topstruct.ProductPropImg, 'is_list': False}
    }

    API = 'taobao.product.propimg.upload'


class ProductUpdateRequest(TOPRequest):
    """ 传入产品ID
        可修改字段：outer_id,binds,sale_props,name,price,desc,image
        注意：1.可以修改主图,不能修改子图片,主图最大500K,目前仅支持GIF,JPG
        2.商城卖家产品发布24小时后不能作删除或修改操作

    @response product(Product): 返回product数据结构中的：product_id,modified

    @request binds(String): (optional)非关键属性.调用taobao.itemprops.get获取pid,调用taobao.itempropvalues.get获取vid;格式:pid:vid;pid:vid
    @request desc(String): (optional)产品描述.最大25000个字节
    @request image(Image): (optional)产品主图.最大500K,目前仅支持GIF,JPG
    @request major(Boolean): (optional)是否是主图
    @request name(String): (optional)产品名称.最大60个字节
    @request native_unkeyprops(String): (optional)自定义非关键属性
    @request outer_id(String): (optional)外部产品ID
    @request price(String): (optional)产品市场价.精确到2位小数;单位为元.如:200.07
    @request product_id(Number): (required)产品ID
    @request sale_props(String): (optional)销售属性.调用taobao.itemprops.get获取pid,调用taobao.itempropvalues.get获取vid;格式:pid:vid;pid:vid
    """
    REQUEST = {
        'binds': {'type': topstruct.String, 'is_required': False},
        'desc': {'type': topstruct.String, 'is_required': False},
        'image': {'type': topstruct.Image, 'is_required': False},
        'major': {'type': topstruct.Boolean, 'is_required': False},
        'name': {'type': topstruct.String, 'is_required': False},
        'native_unkeyprops': {'type': topstruct.String, 'is_required': False},
        'outer_id': {'type': topstruct.String, 'is_required': False},
        'price': {'type': topstruct.String, 'is_required': False},
        'product_id': {'type': topstruct.Number, 'is_required': True},
        'sale_props': {'type': topstruct.String, 'is_required': False}
    }

    RESPONSE = {
        'product': {'type': topstruct.Product, 'is_list': False}
    }

    API = 'taobao.product.update'


class ProductsGetRequest(TOPRequest):
    """ 根据淘宝会员帐号搜索所有产品信息
        注意：支持分页，每页最多返回100条,默认值为40,页码从1开始，默认为第一页

    @response products(Product): 返回具体信息为入参fields请求的字段信息

    @request fields(FieldList): (required)需返回的字段列表.可选值:Product数据结构中的所有字段;多个字段之间用","分隔
    @request nick(String): (required)用户昵称
    @request page_no(Number): (optional)页码.传入值为1代表第一页,传入值为2代表第二页,依此类推.默认返回的数据是从第一页开始.
    @request page_size(Number): (optional)每页条数.每页返回最多返回100条,默认值为40
    """
    REQUEST = {
        'fields': {'type': topstruct.FieldList, 'is_required': True, 'optional': topstruct.Set({'cat_name', 'product_imgs', 'desc', 'product_id', 'props_str', 'vertical_market', 'status', 'modified', 'sale_props_str', 'pic_url', 'cid', 'level', 'tsc', 'pic_path', 'outer_id', 'price', 'binds_str', 'collect_num', 'created', 'name', 'props', 'customer_props', 'sale_props', 'property_alias', 'binds', 'product_prop_imgs'})},
        'nick': {'type': topstruct.String, 'is_required': True},
        'page_no': {'type': topstruct.Number, 'is_required': False},
        'page_size': {'type': topstruct.Number, 'is_required': False}
    }

    RESPONSE = {
        'products': {'type': topstruct.Product, 'is_list': False}
    }

    API = 'taobao.products.get'


class ProductsSearchRequest(TOPRequest):
    """ 两种方式搜索所有产品信息(二种至少传一种):
        传入关键字q搜索
        传入cid和props搜索
        返回值支持:product_id,name,pic_path,cid,props,price,tsc
        当用户指定了cid并且cid为垂直市场（3C电器城、鞋城）的类目id时，默认只返回小二确认的产品。如果用户没有指定cid，或cid为普通的类目，默认返回商家确认或小二确认的产品。如果用户自定了status字段，以指定的status类型为准

    @response products(Product): 返回具体信息为入参fields请求的字段信息
    @response total_results(Number): 结果总数

    @request cid(Number): (special)商品类目ID.调用taobao.itemcats.get获取.
    @request fields(FieldList): (required)需返回的字段列表.可选值:Product数据结构中的以下字段:product_id,name,pic_url,cid,props,price,tsc;多个字段之间用","分隔.新增字段status(product的当前状态)
    @request page_no(Number): (optional)页码.传入值为1代表第一页,传入值为2代表第二页,依此类推.默认返回的数据是从第一页开始.
    @request page_size(Number): (optional)每页条数.每页返回最多返回100条,默认值为40.
    @request props(String): (special)属性,属性值的组合.格式:pid:vid;pid:vid;调用taobao.itemprops.get获取类目属性pid
        ,再用taobao.itempropvalues.get取得vid.
    @request q(String): (special)搜索的关键词是用来搜索产品的title.　注:q,cid和props至少传入一个
    @request status(String): (optional)想要获取的产品的状态列表，支持多个状态并列获取，多个状态之间用","分隔，最多同时指定5种状态。例如，只获取小二确认的spu传入"3",只要商家确认的传入"0"，既要小二确认又要商家确认的传入"0,3"。目前只支持者两种类型的状态搜索，输入其他状态无效。
    @request vertical_market(Number): (optional)传入值为：3表示3C表示3C垂直市场产品，4表示鞋城垂直市场产品，8表示网游垂直市场产品。一次只能指定一种垂直市场类型
    """
    REQUEST = {
        'cid': {'type': topstruct.Number, 'is_required': False},
        'fields': {'type': topstruct.FieldList, 'is_required': True, 'optional': topstruct.Set({'tsc', 'product_id', 'status', 'price', 'pic_url', 'name', 'cid', 'props'})},
        'page_no': {'type': topstruct.Number, 'is_required': False},
        'page_size': {'type': topstruct.Number, 'is_required': False},
        'props': {'type': topstruct.String, 'is_required': False},
        'q': {'type': topstruct.String, 'is_required': False},
        'status': {'type': topstruct.String, 'is_required': False},
        'vertical_market': {'type': topstruct.Number, 'is_required': False}
    }

    RESPONSE = {
        'products': {'type': topstruct.Product, 'is_list': False},
        'total_results': {'type': topstruct.Number, 'is_list': False}
    }

    API = 'taobao.products.search'


class SkusCustomGetRequest(TOPRequest):
    """ 跟据卖家设定的Sku的外部id获取商品，如果一个outer_id对应多个Sku会返回所有符合条件的sku
        这个Sku所属卖家从传入的session中获取，需要session绑定(注：iid标签里是num_iid的值，可以用作num_iid使用)

    @response skus(Sku): Sku对象，具体字段以fields决定

    @request fields(FieldList): (required)需返回的字段列表。可选值：Sku结构体中的所有字段；字段之间用“,”隔开
    @request outer_id(String): (required)Sku的外部商家ID
    """
    REQUEST = {
        'fields': {'type': topstruct.FieldList, 'is_required': True, 'optional': topstruct.Set({'iid', 'num_iid', 'quantity', 'status', 'outer_id', 'properties_name', 'properties', 'sku_id', 'created', 'price', 'modified'})},
        'outer_id': {'type': topstruct.String, 'is_required': True}
    }

    RESPONSE = {
        'skus': {'type': topstruct.Sku, 'is_list': False}
    }

    API = 'taobao.skus.custom.get'


class UmpPromotionGetRequest(TOPRequest):
    """ 商品优惠详情查询，可查询商品设置的详细优惠。包括限时折扣，满就送等官方优惠以及第三方优惠。

    @response promotions(PromotionDisplayTop): 优惠详细信息

    @request channel_key(String): (optional)渠道来源，第三方站点
    @request item_id(Number): (required)商品id
    """
    REQUEST = {
        'channel_key': {'type': topstruct.String, 'is_required': False},
        'item_id': {'type': topstruct.Number, 'is_required': True}
    }

    RESPONSE = {
        'promotions': {'type': topstruct.PromotionDisplayTop, 'is_list': False}
    }

    API = 'taobao.ump.promotion.get'


class TopatsTradesFullinfoGetRequest(TOPRequest):
    """ 提供异步批量获取订单详情功能<br/>
        1. 一次可以查询的订单数量为1~100笔，强烈建议一次请求尽可能多的订单<br/>
        2. 提交任务后会生成task_id，后继通过此task_id调用taobao.topats.result.get接口获取任务的结果<br/>
        3. 如果订阅了Comet长连接推送方式，则直接通过Comet推送到长连接客户端<br/>
        4. 这个任务ID有效时间为2天。

    @response task(Task): 创建任务信息。里面只包含task_id和created

    @request fields(FieldList): (required)可以返回taobao.trade.fullinfo.get允许的所有字段。
    @request tids(String): (required)交易订单号tid列表，多个tid之间用半角分号分隔。tid个数的取值范围是：1~100个。由于这个接口限制每个应用的调用量是1万次/天，所以强烈建议采用尽可能多的tid，以取到更多的交易数据。
    """
    REQUEST = {
        'fields': {'type': topstruct.FieldList, 'is_required': True, 'optional': topstruct.Set({'orders.timeout_action_time，orders.sku_properties_name', 'tid', 'end_time', 'post_fee', 'buyer_email', 'seller_name', 'buyer_rate', 'num', 'receiver_mobile', 'seller_memo', 'orders.seller_rate', 'has_post_fee', 'seller_alipay_no', 'alipay_id', 'alipay_no', 'receiver_phone', 'payment', 'orders.num_iid', 'snapshot_url', 'available_confirm_fee', 'trade_from', 'trade_memo', 'buyer_message', 'commission_fee', 'orders', 'receiver_name', 'invoice_name', 'total_fee', 'promotion_details', 'cod_status', 'orders.adjust_fee', 'cod_fee', 'orders.snapshot_url', 'modified', 'discount_fee', 'orders.pic_path', 'orders.seller_type', 'point_fee', 'timeout_action_time', 'buyer_alipay_no', 'price', 'receiver_zip', 'num_iid', 'seller_mobile', 'created', 'orders.payment', 'buyer_cod_fee', 'is_lgtype', 'is_3D', 'orders.discount_fee', 'receiver_district', 'orders.oid', 'orders.outer_iid', 'orders.total_fee', 'seller_rate', 'buyer_nick', 'orders.item_meal_name', 'orders.is_oversold', 'orders.buyer_rate', 'seller_flag', 'receiver_address', 'buyer_flag', 'buyer_area', 'buyer_memo', 'orders.outer_sku_id', 'seller_cod_fee', 'is_brand_sale', 'seller_nick', 'seller_email', 'orders.price', 'orders.refund_status', 'status', 'orders.title', 'orders.num', 'orders.status', 'orders.sku_id', 'orders.refund_id', 'type', 'is_force_wlb', 'express_agency_fee', 'seller_phone', 'service_orders', 'pic_path', 'receiver_city', 'shipping_type', 'receiver_state', 'adjust_fee', 'pay_time', 'buyer_obtain_point_fee', 'consign_time', 'title', 'received_payment', 'real_point_fee', 'orders.item_meal_id，item_memo'})},
        'tids': {'type': topstruct.String, 'is_required': True}
    }

    RESPONSE = {
        'task': {'type': topstruct.Task, 'is_list': False}
    }

    API = 'taobao.topats.trades.fullinfo.get'


class TradeAmountGetRequest(TOPRequest):
    """ 卖家查询该笔交易订单的资金帐务相关的数据；
        1. 只供卖家使用，买家不可使用
        2. 可查询所有的状态的订单，但不同状态时订单的相关数据可能会有不同

    @response trade_amount(TradeAmount): 主订单的财务信息详情

    @request fields(FieldList): (required)订单帐务详情需要返回的字段信息，可选值如下：
        1. TradeAmount中可指定的fields：
        tid,alipay_no,created,pay_time,end_time,total_fee,payment,post_fee,cod_fee,commission_fee,buyer_obtain_point_fee
        2. OrderAmount中可指定的fields：order_amounts.oid,order_amounts.title,order_amounts.num_iid,
        order_amounts.sku_properties_name,order_amounts.sku_id,order_amounts.num,order_amounts.price,order_amounts.discount_fee,order_amounts.adjust_fee,order_amounts.payment,order_amounts.promotion_name
        3. order_amounts(返回OrderAmount的所有内容)
        4. promotion_details(指定该值会返回主订单的promotion_details中除id之外的所有字段)
    @request tid(Number): (required)订单交易编号
    """
    REQUEST = {
        'fields': {'type': topstruct.FieldList, 'is_required': True, 'optional': topstruct.Set({'order_amounts.payment', 'total_fee', 'tid', 'promotion_details', 'order_amounts.sku_properties_name', 'end_time', 'post_fee', 'order_amounts.num_iid', 'cod_fee', 'order_amounts.promotion_name', 'order_amounts.title', 'order_amounts.num', 'order_amounts.discount_fee', 'alipay_no', 'order_amounts', 'payment', 'order_amounts.adjust_fee', 'created', 'pay_time', 'order_amounts.sku_id', 'order_amounts.oid', 'buyer_obtain_point_fee', 'order_amounts.price', 'commission_fee'})},
        'tid': {'type': topstruct.Number, 'is_required': True}
    }

    RESPONSE = {
        'trade_amount': {'type': topstruct.TradeAmount, 'is_list': False}
    }

    API = 'taobao.trade.amount.get'


class TradeCloseRequest(TOPRequest):
    """ 关闭一笔订单，可以是主订单或子订单。当订单从创建到关闭时间小于10s的时候，会报“CLOSE_TRADE_TOO_FAST”错误。

    @response trade(Trade): 关闭交易时返回的Trade信息，可用字段有tid和modified

    @request close_reason(String): (required)交易关闭原因。
        可以选择的理由有：
        1、买家不想买了
        2、信息填写错误，重新拍
        3、卖家缺货
        4、同城见面交易
        5、其他原因
        注：尽量不要传入自定义的关闭理由
    @request tid(Number): (required)主订单或子订单编号。
    """
    REQUEST = {
        'close_reason': {'type': topstruct.String, 'is_required': True},
        'tid': {'type': topstruct.Number, 'is_required': True}
    }

    RESPONSE = {
        'trade': {'type': topstruct.Trade, 'is_list': False}
    }

    API = 'taobao.trade.close'


class TradeConfirmfeeGetRequest(TOPRequest):
    """ 获取交易确认收货费用
        可以获取主订单或子订单的确认收货费用

    @response trade_confirm_fee(TradeConfirmFee): 获取到的交易确认收货费用

    @request is_detail(String): (required)是否是子订单。可选值:IS_FATHER(父订单),IS_CHILD(子订单)
    @request tid(Number): (required)交易编号，或子订单编号
    """
    REQUEST = {
        'is_detail': {'type': topstruct.String, 'is_required': True},
        'tid': {'type': topstruct.Number, 'is_required': True}
    }

    RESPONSE = {
        'trade_confirm_fee': {'type': topstruct.TradeConfirmFee, 'is_list': False}
    }

    API = 'taobao.trade.confirmfee.get'


class TradeFullinfoGetRequest(TOPRequest):
    """ 获取单笔交易的详细信息
        1.只有在交易成功的状态下才能取到交易佣金，其它状态下取到的都是零或空值
        2.只有单笔订单的情况下Trade数据结构中才包含商品相关的信息
        3.获取到的Order中的payment字段在单笔子订单时包含物流费用，多笔子订单时不包含物流费用
        注：包含以下字段的返回会增加TOP的后台压力，请仅在确实需要的情况下才去获取：commission_fee, buyer_alipay_no, seller_alipay_no, buyer_email, seller_mobile, seller_phone, seller_name, seller_email, timeout_action_time, item_memo, trade_memo, title, available_confirm_fee

    @response trade(Trade): 搜索到的交易信息列表，返回的Trade和Order中包含的具体信息为入参fields请求的字段信息

    @request fields(FieldList): (required)1.Trade中可以指定返回的fields：seller_nick, buyer_nick, title, type, created, tid, seller_rate,buyer_flag, buyer_rate, status, payment, adjust_fee, post_fee, total_fee, pay_time, end_time, modified, consign_time, buyer_obtain_point_fee, point_fee, real_point_fee, received_payment, commission_fee, buyer_memo, seller_memo, alipay_no,alipay_id,buyer_message, pic_path, num_iid, num, price, buyer_alipay_no, receiver_name, receiver_state, receiver_city, receiver_district, receiver_address, receiver_zip, receiver_mobile, receiver_phone,seller_flag, seller_alipay_no, seller_mobile, seller_phone, seller_name, seller_email, available_confirm_fee, has_post_fee, timeout_action_time, snapshot_url, cod_fee, cod_status, shipping_type, trade_memo, is_3D,buyer_email,buyer_area, trade_from,is_lgtype,is_force_wlb,is_brand_sale,buyer_cod_fee,discount_fee,seller_cod_fee,express_agency_fee,invoice_name,service_orders(注：当该授权用户为卖家时不能查看买家buyer_memo,buyer_flag)
        2.Order中可以指定返回fields：orders.title, orders.pic_path, orders.price, orders.num, orders.num_iid, orders.sku_id, orders.refund_status, orders.status, orders.oid, orders.total_fee, orders.payment, orders.discount_fee, orders.adjust_fee, orders.snapshot_url, orders.timeout_action_time，orders.sku_properties_name, orders.item_meal_name, orders.item_meal_id，item_memo,orders.buyer_rate, orders.seller_rate, orders.outer_iid, orders.outer_sku_id, orders.refund_id, orders.seller_type, orders.is_oversold
        3.fields：orders（返回Order的所有内容）
        4.flelds：promotion_details(返回promotion_details所有内容，优惠详情),invoice_name(发票抬头)
    @request tid(Number): (required)交易编号
    """
    REQUEST = {
        'fields': {'type': topstruct.FieldList, 'is_required': True, 'optional': topstruct.Set({'orders.timeout_action_time，orders.sku_properties_name', 'tid', 'end_time', 'post_fee', 'buyer_email', 'seller_name', 'buyer_rate', 'num', 'receiver_mobile', 'seller_memo', 'orders.seller_rate', 'has_post_fee', 'seller_alipay_no', 'alipay_id', 'alipay_no', 'receiver_phone', 'payment', 'orders.num_iid', 'snapshot_url', 'available_confirm_fee', 'trade_from', 'trade_memo', 'buyer_message', 'commission_fee', 'orders', 'receiver_name', 'invoice_name', 'total_fee', 'promotion_details', 'cod_status', 'orders.adjust_fee', 'cod_fee', 'orders.snapshot_url', 'modified', 'discount_fee', 'orders.pic_path', 'orders.seller_type', 'point_fee', 'timeout_action_time', 'buyer_alipay_no', 'price', 'receiver_zip', 'num_iid', 'seller_mobile', 'created', 'orders.payment', 'buyer_cod_fee', 'is_lgtype', 'is_3D', 'orders.discount_fee', 'receiver_district', 'orders.oid', 'orders.outer_iid', 'orders.total_fee', 'seller_rate', 'buyer_nick', 'orders.item_meal_name', 'orders.is_oversold', 'orders.buyer_rate', 'seller_flag', 'receiver_address', 'buyer_flag', 'buyer_area', 'buyer_memo', 'orders.outer_sku_id', 'seller_cod_fee', 'is_brand_sale', 'seller_nick', 'seller_email', 'orders.price', 'orders.refund_status', 'status', 'orders.title', 'orders.num', 'orders.status', 'orders.sku_id', 'orders.refund_id', 'type', 'is_force_wlb', 'express_agency_fee', 'seller_phone', 'service_orders', 'pic_path', 'receiver_city', 'shipping_type', 'receiver_state', 'adjust_fee', 'pay_time', 'buyer_obtain_point_fee', 'consign_time', 'title', 'received_payment', 'real_point_fee', 'orders.item_meal_id，item_memo'})},
        'tid': {'type': topstruct.Number, 'is_required': True}
    }

    RESPONSE = {
        'trade': {'type': topstruct.Trade, 'is_list': False}
    }

    API = 'taobao.trade.fullinfo.get'


class TradeGetRequest(TOPRequest):
    """ 获取单笔交易的部分信息

    @response trade(Trade): 搜索到的交易信息列表，返回的Trade和Order中包含的具体信息为入参fields请求的字段信息

    @request fields(FieldList): (required)需要返回的字段。目前支持有：<br>
        1. Trade中可以指定返回的fields:seller_nick, buyer_nick, title, type, created, tid, seller_rate, buyer_rate, status, payment, discount_fee, adjust_fee, post_fee, total_fee, pay_time, end_time, modified, consign_time, buyer_obtain_point_fee, point_fee, real_point_fee, received_payment, commission_fee, buyer_memo, seller_memo, alipay_no, buyer_message, pic_path, num_iid, num, price, cod_fee, cod_status, shipping_type <br>
        2. Order中可以指定返回fields:orders.title, orders.pic_path, orders.price, orders.num, orders.num_iid, orders.sku_id, orders.refund_status, orders.status, orders.oid, orders.total_fee, orders.payment, orders.discount_fee, orders.adjust_fee, orders.sku_properties_name, orders.item_meal_name, orders.outer_sku_id, orders.outer_iid, orders.buyer_rate, orders.seller_rate <br>
        3. fields：orders（返回Order中的所有允许返回的字段）
    @request tid(Number): (required)交易编号
    """
    REQUEST = {
        'fields': {'type': topstruct.FieldList, 'is_required': True, 'optional': topstruct.Set({'total_fee', 'tid', 'orders.sku_properties_name', 'end_time', 'post_fee', 'orders.discount_fee', 'cod_status', 'orders.price', 'orders.adjust_fee', 'cod_fee', 'orders.buyer_rate', 'status', 'buyer_rate', 'orders.title', 'modified', 'discount_fee', 'orders.num', 'orders.status', 'num_iid', 'orders.payment', 'orders.pic_path', 'seller_memo', 'type', 'orders.oid', 'orders.seller_rate', 'orders.outer_iid', 'num', 'price', 'seller_rate', 'orders.total_fee', 'buyer_nick', 'orders.item_meal_name', 'alipay_no', 'pic_path', 'shipping_type', 'payment', 'orders.sku_id', 'orders.num_iid', 'adjust_fee', 'created', 'pay_time', 'buyer_memo', 'orders.outer_sku_id', 'buyer_obtain_point_fee', 'consign_time', 'seller_nick', 'buyer_message', 'title', 'commission_fee', 'point_fee', 'orders', 'received_payment', 'real_point_fee', 'orders.refund_status'})},
        'tid': {'type': topstruct.Number, 'is_required': True}
    }

    RESPONSE = {
        'trade': {'type': topstruct.Trade, 'is_list': False}
    }

    API = 'taobao.trade.get'


class TradeMemoAddRequest(TOPRequest):
    """ 根据登录用户的身份（买家或卖家），自动添加相应的交易备注,不能重复调用些接口添加备注，需要更新备注请用taobao.trade.memo.update

    @response trade(Trade): 对一笔交易添加备注后返回其对应的Trade，Trade中可用的返回字段有tid和created

    @request flag(Number): (optional)交易备注旗帜，可选值为：0(灰色), 1(红色), 2(黄色), 3(绿色), 4(蓝色), 5(粉红色)，默认值为0
    @request memo(String): (required)交易备注。最大长度: 1000个字节
    @request tid(Number): (required)交易编号
    """
    REQUEST = {
        'flag': {'type': topstruct.Number, 'is_required': False},
        'memo': {'type': topstruct.String, 'is_required': True},
        'tid': {'type': topstruct.Number, 'is_required': True}
    }

    RESPONSE = {
        'trade': {'type': topstruct.Trade, 'is_list': False}
    }

    API = 'taobao.trade.memo.add'


class TradeMemoUpdateRequest(TOPRequest):
    """ 需要商家或以上权限才可调用此接口，可重复调用本接口更新交易备注，本接口同时具有添加备注的功能

    @response trade(Trade): 更新交易的备注信息后返回的Trade，其中可用字段为tid和modified

    @request flag(Number): (optional)交易备注旗帜，可选值为：0(灰色), 1(红色), 2(黄色), 3(绿色), 4(蓝色), 5(粉红色)，默认值为0
    @request memo(String): (optional)交易备注。最大长度: 1000个字节
    @request reset(Boolean): (optional)是否对memo的值置空
        若为true，则不管传入的memo字段的值是否为空，都将会对已有的memo值清空，慎用；
        若用false，则会根据memo是否为空来修改memo的值：若memo为空则忽略对已有memo字段的修改，若memo非空，则使用新传入的memo覆盖已有的memo的值
    @request tid(Number): (required)交易编号
    """
    REQUEST = {
        'flag': {'type': topstruct.Number, 'is_required': False},
        'memo': {'type': topstruct.String, 'is_required': False},
        'reset': {'type': topstruct.Boolean, 'is_required': False},
        'tid': {'type': topstruct.Number, 'is_required': True}
    }

    RESPONSE = {
        'trade': {'type': topstruct.Trade, 'is_list': False}
    }

    API = 'taobao.trade.memo.update'


class TradeOrderskuUpdateRequest(TOPRequest):
    """ 只能更新发货前子订单的销售属性
        只能更新价格相同的销售属性。对于拍下减库存的交易会同步更新销售属性的库存量。对于旺店的交易，要使用商品扩展信息中的SKU价格来比较。
        必须使用sku_id或sku_props中的一个参数来更新，如果两个都传的话，sku_id优先

    @response order(Order): 只返回oid和modified

    @request oid(Number): (required)子订单编号（对于单笔订单的交易可以传交易编号）。
    @request sku_id(Number): (special)销售属性编号，可以通过taobao.item.skus.get获取订单对应的商品的所有销售属性。
    @request sku_props(String): (special)销售属性组合串，格式：p1:v1;p2:v2，如：1627207:28329;20509:28314。可以通过taobao.item.skus.get获取订单对应的商品的所有销售属性。
    """
    REQUEST = {
        'oid': {'type': topstruct.Number, 'is_required': True},
        'sku_id': {'type': topstruct.Number, 'is_required': False},
        'sku_props': {'type': topstruct.String, 'is_required': False}
    }

    RESPONSE = {
        'order': {'type': topstruct.Order, 'is_list': False}
    }

    API = 'taobao.trade.ordersku.update'


class TradePostageUpdateRequest(TOPRequest):
    """ 修改订单邮费接口，通过传入订单编号和邮费价格，修改订单的邮费，返回修改时间modified,邮费post_fee,总费用total_fee。

    @response trade(Trade): 返回trade类型，其中包含修改时间modified，修改邮费post_fee，修改后的总费用total_fee和买家实付款payment

    @request post_fee(String): (required)邮费价格(邮费单位是元）
    @request tid(Number): (required)主订单编号
    """
    REQUEST = {
        'post_fee': {'type': topstruct.String, 'is_required': True},
        'tid': {'type': topstruct.Number, 'is_required': True}
    }

    RESPONSE = {
        'trade': {'type': topstruct.Trade, 'is_list': False}
    }

    API = 'taobao.trade.postage.update'


class TradeReceivetimeDelayRequest(TOPRequest):
    """ 延长交易收货时间

    @response trade(Trade): 更新后的交易数据，只包括tid和modified两个字段。

    @request days(Number): (required)延长收货的天数，可选值为：3, 5, 7, 10。
    @request tid(Number): (required)主订单号
    """
    REQUEST = {
        'days': {'type': topstruct.Number, 'is_required': True},
        'tid': {'type': topstruct.Number, 'is_required': True}
    }

    RESPONSE = {
        'trade': {'type': topstruct.Trade, 'is_list': False}
    }

    API = 'taobao.trade.receivetime.delay'


class TradeShippingaddressUpdateRequest(TOPRequest):
    """ 只能更新一笔交易里面的买家收货地址
        只能更新发货前（即买家已付款，等待卖家发货状态）的交易的买家收货地址
        更新后的发货地址可以通过taobao.trade.fullinfo.get查到
        参数中所说的字节为GBK编码的（英文和数字占1字节，中文占2字节）

    @response trade(Trade): 交易结构

    @request receiver_address(String): (optional)收货地址。最大长度为228个字节。
    @request receiver_city(String): (optional)城市。最大长度为32个字节。如：杭州
    @request receiver_district(String): (optional)区/县。最大长度为32个字节。如：西湖区
    @request receiver_mobile(String): (optional)移动电话。最大长度为30个字节。
    @request receiver_name(String): (optional)收货人全名。最大长度为50个字节。
    @request receiver_phone(String): (optional)固定电话。最大长度为30个字节。
    @request receiver_state(String): (optional)省份。最大长度为32个字节。如：浙江
    @request receiver_zip(String): (optional)邮政编码。必须由6个数字组成。
    @request tid(Number): (required)交易编号。
    """
    REQUEST = {
        'receiver_address': {'type': topstruct.String, 'is_required': False},
        'receiver_city': {'type': topstruct.String, 'is_required': False},
        'receiver_district': {'type': topstruct.String, 'is_required': False},
        'receiver_mobile': {'type': topstruct.String, 'is_required': False},
        'receiver_name': {'type': topstruct.String, 'is_required': False},
        'receiver_phone': {'type': topstruct.String, 'is_required': False},
        'receiver_state': {'type': topstruct.String, 'is_required': False},
        'receiver_zip': {'type': topstruct.String, 'is_required': False},
        'tid': {'type': topstruct.Number, 'is_required': True}
    }

    RESPONSE = {
        'trade': {'type': topstruct.Trade, 'is_list': False}
    }

    API = 'taobao.trade.shippingaddress.update'


class TradeSnapshotGetRequest(TOPRequest):
    """ 交易快照查询
        目前只支持类型为“旺店标准版(600)”或“旺店入门版(610)”的交易
        对于“旺店标准版”类型的交易，返回的snapshot字段为交易快照编号
        对于“旺店入门版”类型的交易，返回的snapshot字段为JSON结构的数据(其中的shopPromotion包含了优惠，积分等信息）

    @response trade(Trade): 只包含Trade中的tid和snapshot、子订单Order中的oid和snapshot

    @request fields(FieldList): (required)需要返回的字段列表。现只支持："snapshot"字段
    @request tid(Number): (required)交易编号
    """
    REQUEST = {
        'fields': {'type': topstruct.FieldList, 'is_required': True, 'optional': topstruct.Set({'snapshot'})},
        'tid': {'type': topstruct.Number, 'is_required': True}
    }

    RESPONSE = {
        'trade': {'type': topstruct.Trade, 'is_list': False}
    }

    API = 'taobao.trade.snapshot.get'


class TradesSoldGetRequest(TOPRequest):
    """ 搜索当前会话用户作为卖家已卖出的交易数据(只能获取到三个月以内的交易信息)

    @response has_next(Boolean): 是否存在下一页
    @response total_results(Number): 搜索到的交易信息总数
    @response trades(Trade): 搜索到的交易信息列表，返回的Trade和Order中包含的具体信息为入参fields请求的字段信息

    @request buyer_nick(String): (optional)买家昵称
    @request end_created(Date): (optional)查询交易创建时间结束。格式:yyyy-MM-dd HH:mm:ss
    @request ext_type(String): (optional)可选值有ershou(表示二手市场的订单）,service（商城服务子订单）
    @request fields(FieldList): (required)需要返回的字段。目前支持有：<br>
        1. Trade中可以指定返回的fields:<br>
        seller_nick, buyer_nick, title, type, created,  tid, seller_rate, buyer_rate, status, payment, discount_fee, adjust_fee, post_fee, total_fee, pay_time, end_time, modified, consign_time, buyer_obtain_point_fee, point_fee, real_point_fee, received_payment, commission_fee, pic_path, num_iid, num, price, cod_fee, cod_status, shipping_type, receiver_name, receiver_state, receiver_city, receiver_district, receiver_address, receiver_zip, receiver_mobile, receiver_phone,seller_flag,alipay_id,alipay_no,is_lgtype,is_force_wlb,is_brand_sale,buyer_area,has_buyer_message <br>
        2. Order中可以指定返回fields：orders.title, orders.pic_path, orders.price, orders.num, orders.num_iid, orders.sku_id, orders.refund_status, orders.status, orders.oid, orders.total_fee, orders.payment, orders.discount_fee, orders.adjust_fee, orders.sku_properties_name, orders.item_meal_name, orders.buyer_rate, orders.seller_rate, orders.outer_iid, orders.outer_sku_id, orders.refund_id, orders.seller_type <br>
        3. fields：orders（返回2中Order的所有内容）
    @request page_no(Number): (optional)页码。取值范围:大于零的整数; 默认值:1
    @request page_size(Number): (optional)每页条数。取值范围:大于零的整数; 默认值:40;最大值:100
    @request rate_status(String): (optional)评价状态，默认查询所有评价状态的数据，除了默认值外每次只能查询一种状态。<br>
        可选值：
        RATE_UNBUYER(买家未评)
        RATE_UNSELLER(卖家未评)
        RATE_BUYER_UNSELLER(买家已评，卖家未评)
        RATE_UNBUYER_SELLER(买家未评，卖家已评)
    @request start_created(Date): (optional)查询三个月内交易创建时间开始。格式:yyyy-MM-dd HH:mm:ss
    @request status(String): (optional)交易状态，默认查询所有交易状态的数据，除了默认值外每次只能查询一种状态。
        可选值：
        TRADE_NO_CREATE_PAY(没有创建支付宝交易)
        WAIT_BUYER_PAY(等待买家付款)
        WAIT_SELLER_SEND_GOODS(等待卖家发货,即:买家已付款)
        WAIT_BUYER_CONFIRM_GOODS(等待买家确认收货,即:卖家已发货)
        TRADE_BUYER_SIGNED(买家已签收,货到付款专用)
        TRADE_FINISHED(交易成功)
        TRADE_CLOSED(交易关闭)
        TRADE_CLOSED_BY_TAOBAO(交易被淘宝关闭)
        ALL_WAIT_PAY(包含：WAIT_BUYER_PAY、TRADE_NO_CREATE_PAY)
        ALL_CLOSED(包含：TRADE_CLOSED、TRADE_CLOSED_BY_TAOBAO)
    @request tag(String): (optional)卖家对交易的自定义分组标签，目前可选值为：time_card（点卡软件代充），fee_card（话费软件代充）
    @request type(String): (optional)交易类型列表，同时查询多种交易类型可用逗号分隔。默认同时查询guarantee_trade, auto_delivery, ec, cod的4种交易类型的数据 。
        可选值：
        fixed(一口价)
        auction(拍卖)
        guarantee_trade(一口价、拍卖)
        independent_simple_trade(旺店入门版交易)
        independent_shop_trade(旺店标准版交易)
        auto_delivery(自动发货)
        ec(直冲)
        cod(货到付款)
        game_equipment(游戏装备)
        shopex_trade(ShopEX交易)
        netcn_trade(万网交易)
        external_trade(统一外部交易)
        instant_trade (即时到账)
        b2c_cod(大商家货到付款)
        hotel_trade(酒店类型交易)
        super_market_trade(商超交易)
        super_market_cod_trade(商超货到付款交易)
        taohua(淘花网交易类型）
        waimai(外卖交易类型）
        nopaid（即时到帐/趣味猜交易类型）
        注：guarantee_trade是一个组合查询条件，并不是一种交易类型，获取批量或单个订单中不会返回此种类型的订单。
    @request use_has_next(Boolean): (optional)是否启用has_next的分页方式，如果指定true,则返回的结果中不包含总记录数，但是会新增一个是否存在下一页的的字段，通过此种方式获取增量交易，接口调用成功率在原有的基础上有所提升。
    """
    REQUEST = {
        'buyer_nick': {'type': topstruct.String, 'is_required': False},
        'end_created': {'type': topstruct.Date, 'is_required': False},
        'ext_type': {'type': topstruct.String, 'is_required': False},
        'fields': {'type': topstruct.FieldList, 'is_required': True, 'optional': topstruct.Set({'total_fee', 'tid', 'orders.sku_properties_name', 'end_time', 'post_fee', 'orders.discount_fee', 'cod_status', 'orders.price', 'orders.adjust_fee', 'cod_fee', 'orders.buyer_rate', 'status', 'buyer_rate', 'receiver_district', 'modified', 'discount_fee', 'orders.num', 'orders.status', 'num_iid', 'receiver_mobile', 'orders.pic_path', 'orders.title', 'type', 'is_force_wlb', 'orders.oid', 'orders.seller_rate', 'orders.outer_iid', 'num', 'price', 'is_brand_sale', 'seller_rate', 'alipay_id', 'orders.total_fee', 'buyer_nick', 'orders.item_meal_name', 'alipay_no', 'pic_path', 'receiver_city', 'has_buyer_message', 'shipping_type', 'receiver_phone', 'payment', 'orders.sku_id', 'orders.num_iid', 'adjust_fee', 'seller_flag', 'receiver_address', 'created', 'pay_time', 'buyer_area', 'receiver_state', 'orders', 'orders.outer_sku_id', 'receiver_name', 'buyer_obtain_point_fee', 'orders.payment', 'consign_time', 'orders.refund_id', 'seller_nick', 'is_lgtype', 'title', 'commission_fee', 'receiver_zip', 'point_fee', 'orders.seller_type', 'received_payment', 'real_point_fee', 'orders.refund_status'})},
        'page_no': {'type': topstruct.Number, 'is_required': False},
        'page_size': {'type': topstruct.Number, 'is_required': False},
        'rate_status': {'type': topstruct.String, 'is_required': False},
        'start_created': {'type': topstruct.Date, 'is_required': False},
        'status': {'type': topstruct.String, 'is_required': False},
        'tag': {'type': topstruct.String, 'is_required': False},
        'type': {'type': topstruct.String, 'is_required': False},
        'use_has_next': {'type': topstruct.Boolean, 'is_required': False}
    }

    RESPONSE = {
        'has_next': {'type': topstruct.Boolean, 'is_list': False},
        'total_results': {'type': topstruct.Number, 'is_list': False},
        'trades': {'type': topstruct.Trade, 'is_list': False}
    }

    API = 'taobao.trades.sold.get'


class TradesSoldIncrementGetRequest(TOPRequest):
    """ 1. 搜索当前会话用户作为卖家已卖出的增量交易数据
        2. 只能查询时间跨度为一天的增量交易记录：start_modified：2011-7-1 16:00:00 end_modified： 2011-7-2 15:59:59（注意不能写成16:00:00）
        3. 返回数据结果为创建订单时间的倒序
        4. 只能查询3个月内修改过的数据，超过这个时间的数据无法通过taobao.trade.fullinfo.get获取详情。

    @response has_next(Boolean): 是否存在下一页
    @response total_results(Number): 搜索到的交易信息总数
    @response trades(Trade): 搜索到的交易信息列表，返回的Trade和Order中包含的具体信息为入参fields请求的字段信息

    @request end_modified(Date): (required)查询修改结束时间，必须大于修改开始时间(修改时间跨度不能大于一天)，格式:yyyy-MM-dd HH:mm:ss。<span style="color:red;font-weight: bold;">建议使用30分钟以内的时间跨度，能大大提高响应速度和成功率</span>。
    @request ext_type(String): (optional)可选值有ershou(二手市场的订单）,service（商城服务子订单）作为扩展类型筛选只能做单个ext_type查询，不能全部查询所有的ext_type类型
    @request fields(FieldList): (required)需要返回的字段。目前支持有：
        1.Trade中可以指定返回的fields:seller_nick, buyer_nick, title, type, created, tid, seller_rate, buyer_rate, status, payment, discount_fee, adjust_fee, post_fee, total_fee, pay_time, end_time, modified, consign_time, buyer_obtain_point_fee, point_fee, real_point_fee, received_payment, commission_fee, pic_path, num_iid, num, price, cod_fee, cod_status, shipping_type, receiver_name, receiver_state, receiver_city, receiver_district, receiver_address, receiver_zip, receiver_mobile, receiver_phone,alipay_id,alipay_no,is_lgtype,is_force_wlb,is_brand_sale,has_buyer_message
        2.Order中可以指定返回fields：
        orders.title, orders.pic_path, orders.price, orders.num, orders.num_iid, orders.sku_id, orders.refund_status, orders.status, orders.oid, orders.total_fee, orders.payment, orders.discount_fee, orders.adjust_fee, orders.sku_properties_name, orders.item_meal_name, orders.buyer_rate, orders.seller_rate, orders.outer_iid, orders.outer_sku_id, orders.refund_id, orders.seller_type
        3.fields：orders（返回Order的所有内容）
    @request page_no(Number): (optional)页码。取值范围:大于零的整数;默认值:1
    @request page_size(Number): (optional)每页条数。取值范围：1~100，默认值：40。<span style="color:red;font-weight: bold;">建议使用40~50，可以提高成功率，减少超时数量</span>。
    @request start_modified(Date): (required)查询修改开始时间(修改时间跨度不能大于一天)。格式:yyyy-MM-dd HH:mm:ss
    @request status(String): (optional)交易状态，默认查询所有交易状态的数据，除了默认值外每次只能查询一种状态。 可选值 TRADE_NO_CREATE_PAY(没有创建支付宝交易) WAIT_BUYER_PAY(等待买家付款) WAIT_SELLER_SEND_GOODS(等待卖家发货,即:买家已付款) WAIT_BUYER_CONFIRM_GOODS(等待买家确认收货,即:卖家已发货) TRADE_BUYER_SIGNED(买家已签收,货到付款专用) TRADE_FINISHED(交易成功) TRADE_CLOSED(交易关闭) TRADE_CLOSED_BY_TAOBAO(交易被淘宝关闭) ALL_WAIT_PAY(包含：WAIT_BUYER_PAY、TRADE_NO_CREATE_PAY) ALL_CLOSED(包含：TRADE_CLOSED、TRADE_CLOSED_BY_TAOBAO)
    @request tag(String): (optional)卖家对交易的自定义分组标签，目前可选值为：time_card（点卡软件代充），fee_card（话费软件代充）
    @request type(String): (optional)交易类型列表，同时查询多种交易类型可用逗号分隔。默认同时查询guarantee_trade, auto_delivery, ec, cod的4种交易类型的数据 。
        可选值：
        fixed(一口价)
        auction(拍卖)
        guarantee_trade(一口价、拍卖)
        independent_simple_trade(旺店入门版交易)
        independent_shop_trade(旺店标准版交易)
        auto_delivery(自动发货)
        ec(直冲) cod(货到付款)
        fenxiao(分销)
        game_equipment(游戏装备)
        shopex_trade(ShopEX交易)
        netcn_trade(万网交易)
        external_trade(统一外部交易)
        instant_trade (即时到账)
        b2c_cod(大商家货到付款)
        hotel_trade(酒店类型交易)
        super_market_trade(商超交易),
        super_market_cod_trade(商超货到付款交易)
        taohua(桃花网交易类型）
        waimai(外卖交易类型）
        nopaid（即时到帐/趣味猜交易类型）
        注：guarantee_trade是一个组合查询条件，并不是一种交易类型，获取批量或单个订单中不会返回此种类型的订单。
    @request use_has_next(Boolean): (optional)是否启用has_next的分页方式，如果指定true,则返回的结果中不包含总记录数，但是会新增一个是否存在下一页的的字段，<span style="color:red;font-weight: bold;">通过此种方式获取增量交易，效率在原有的基础上有80%的提升</span>。
    """
    REQUEST = {
        'end_modified': {'type': topstruct.Date, 'is_required': True},
        'ext_type': {'type': topstruct.String, 'is_required': False},
        'fields': {'type': topstruct.FieldList, 'is_required': True, 'optional': topstruct.Set({'total_fee', 'tid', 'orders.sku_properties_name', 'end_time', 'post_fee', 'orders.discount_fee', 'cod_status', 'orders.price', 'orders.adjust_fee', 'cod_fee', 'orders.buyer_rate', 'status', 'buyer_rate', 'receiver_district', 'modified', 'discount_fee', 'orders.num', 'orders.status', 'num_iid', 'receiver_mobile', 'orders.pic_path', 'orders.title', 'type', 'is_force_wlb', 'orders.oid', 'orders.seller_rate', 'orders.outer_iid', 'num', 'price', 'is_brand_sale', 'seller_rate', 'alipay_id', 'orders.total_fee', 'buyer_nick', 'orders.item_meal_name', 'alipay_no', 'pic_path', 'receiver_city', 'has_buyer_message', 'shipping_type', 'receiver_phone', 'payment', 'orders.sku_id', 'orders.num_iid', 'adjust_fee', 'receiver_address', 'created', 'pay_time', 'receiver_state', 'orders', 'orders.outer_sku_id', 'receiver_name', 'buyer_obtain_point_fee', 'orders.payment', 'consign_time', 'orders.refund_id', 'seller_nick', 'is_lgtype', 'title', 'commission_fee', 'receiver_zip', 'point_fee', 'orders.seller_type', 'received_payment', 'real_point_fee', 'orders.refund_status'})},
        'page_no': {'type': topstruct.Number, 'is_required': False},
        'page_size': {'type': topstruct.Number, 'is_required': False},
        'start_modified': {'type': topstruct.Date, 'is_required': True},
        'status': {'type': topstruct.String, 'is_required': False},
        'tag': {'type': topstruct.String, 'is_required': False},
        'type': {'type': topstruct.String, 'is_required': False},
        'use_has_next': {'type': topstruct.Boolean, 'is_required': False}
    }

    RESPONSE = {
        'has_next': {'type': topstruct.Boolean, 'is_list': False},
        'total_results': {'type': topstruct.Number, 'is_list': False},
        'trades': {'type': topstruct.Trade, 'is_list': False}
    }

    API = 'taobao.trades.sold.increment.get'


class TraderateAddRequest(TOPRequest):
    """ 新增单个评价(<font color="red">注：在评价之前需要对订单成功的时间进行判定（end_time）,如果超过15天，不能再通过该接口进行评价</font>)

    @response trade_rate(TradeRate): 返回tid、oid、create

    @request anony(Boolean): (optional)是否匿名,卖家评不能匿名。可选值:true(匿名),false(非匿名)。注意：输入非可选值将会自动转为false
    @request content(String): (optional)评价内容,最大长度: 500个汉字 .注意：当评价结果为good时就不用输入评价内容.评价内容为neutral/bad的时候需要输入评价内容
    @request oid(Number): (optional)子订单ID
    @request result(String): (required)评价结果,可选值:good(好评),neutral(中评),bad(差评)
    @request role(String): (required)评价者角色,可选值:seller(卖家),buyer(买家)
    @request tid(Number): (required)交易ID
    """
    REQUEST = {
        'anony': {'type': topstruct.Boolean, 'is_required': False},
        'content': {'type': topstruct.String, 'is_required': False},
        'oid': {'type': topstruct.Number, 'is_required': False},
        'result': {'type': topstruct.String, 'is_required': True},
        'role': {'type': topstruct.String, 'is_required': True},
        'tid': {'type': topstruct.Number, 'is_required': True}
    }

    RESPONSE = {
        'trade_rate': {'type': topstruct.TradeRate, 'is_list': False}
    }

    API = 'taobao.traderate.add'


class TraderateListAddRequest(TOPRequest):
    """ 针对父子订单新增批量评价(<font color="red">注：在评价之前需要对订单成功的时间进行判定（end_time）,如果超过15天，不用再通过该接口进行评价</font>)

    @response trade_rate(TradeRate): 返回的评论的信息，仅返回tid和created字段

    @request anony(Boolean): (optional)是否匿名，卖家评不能匿名。可选值:true(匿名),false(非匿名)。 注意：输入非可选值将会自动转为false；
    @request content(String): (optional)评价内容,最大长度: 500个汉字 .注意：当评价结果为good时就不用输入评价内容.评价内容为neutral/bad的时候需要输入评价内容
    @request result(String): (required)评价结果。可选值:good(好评),neutral(中评),bad(差评)
    @request role(String): (required)评价者角色。可选值:seller(卖家),buyer(买家)
    @request tid(Number): (required)交易ID
    """
    REQUEST = {
        'anony': {'type': topstruct.Boolean, 'is_required': False},
        'content': {'type': topstruct.String, 'is_required': False},
        'result': {'type': topstruct.String, 'is_required': True},
        'role': {'type': topstruct.String, 'is_required': True},
        'tid': {'type': topstruct.Number, 'is_required': True}
    }

    RESPONSE = {
        'trade_rate': {'type': topstruct.TradeRate, 'is_list': False}
    }

    API = 'taobao.traderate.list.add'


class TraderatesGetRequest(TOPRequest):
    """ 搜索评价信息，只能获取距今180天内的评价记录

    @response has_next(Boolean): 当使用use_has_next时返回信息，如果还有下一页则返回true
    @response total_results(Number): 搜索到的评价总数
    @response trade_rates(TradeRate): 评价列表。返回的TradeRate包含的具体信息为入参fields请求的字段信息

    @request end_date(Date): (optional)评价结束时间。如果只输入结束时间，那么全部返回所有评价数据。
    @request fields(FieldList): (required)需返回的字段列表。可选值：TradeRate 结构中的所有字段，多个字段之间用“,”分隔
    @request page_no(Number): (optional)页码。取值范围:大于零的整数; 默认值:1
    @request page_size(Number): (optional)每页获取条数。默认值40，最小值1，最大值150。相同的查询时间段条件下，最大只能获取总共1500条评价记录。
    @request rate_type(String): (required)评价类型。可选值:get(得到),give(给出)
    @request result(String): (optional)评价结果。可选值:good(好评),neutral(中评),bad(差评)
    @request role(String): (required)评价者角色即评价的发起方。可选值:seller(卖家),buyer(买家)。 当 give buyer 以买家身份给卖家的评价； 当 get seller 以买家身份得到卖家给的评价； 当 give seller 以卖家身份给买家的评价； 当 get buyer 以卖家身份得到买家给的评价。
    @request start_date(Date): (optional)评价开始时。如果只输入开始时间，那么能返回开始时间之后的评价数据。
    @request tid(Number): (optional)交易订单id，可以是父订单id号，也可以是子订单id号
    @request use_has_next(Boolean): (optional)是否启用has_next的分页方式，如果指定true,则返回的结果中不包含总记录数，但是会新增一个是否存在下一页的的字段，通过此种方式获取评价信息，效率在原有的基础上有80%的提升。
    """
    REQUEST = {
        'end_date': {'type': topstruct.Date, 'is_required': False},
        'fields': {'type': topstruct.FieldList, 'is_required': True, 'optional': topstruct.Set({'item_title', 'tid', 'oid', 'valid_score', 'result', 'role', 'rated_nick', 'nick', 'reply', 'created', 'content', 'item_price'})},
        'page_no': {'type': topstruct.Number, 'is_required': False},
        'page_size': {'type': topstruct.Number, 'is_required': False},
        'rate_type': {'type': topstruct.String, 'is_required': True},
        'result': {'type': topstruct.String, 'is_required': False},
        'role': {'type': topstruct.String, 'is_required': True},
        'start_date': {'type': topstruct.Date, 'is_required': False},
        'tid': {'type': topstruct.Number, 'is_required': False},
        'use_has_next': {'type': topstruct.Boolean, 'is_required': False}
    }

    RESPONSE = {
        'has_next': {'type': topstruct.Boolean, 'is_list': False},
        'total_results': {'type': topstruct.Number, 'is_list': False},
        'trade_rates': {'type': topstruct.TradeRate, 'is_list': False}
    }

    API = 'taobao.traderates.get'


class AreasGetRequest(TOPRequest):
    """ 查询标准地址区域代码信息 参考：http://www.stats.gov.cn/tjbz/xzqhdm/t20100623_402652267.htm

    @response areas(Area): 地址区域信息列表.返回的Area包含的具体信息为入参fields请求的字段信息.

    @request fields(FieldList): (required)需返回的字段列表.可选值:Area 结构中的所有字段;多个字段之间用","分隔.如:id,type,name,parent_id,zip.
    """
    REQUEST = {
        'fields': {'type': topstruct.FieldList, 'is_required': True, 'optional': topstruct.Set({'name', 'type', 'parent_id', 'id', 'zip'})}
    }

    RESPONSE = {
        'areas': {'type': topstruct.Area, 'is_list': False}
    }

    API = 'taobao.areas.get'


class DeliveryTemplateAddRequest(TOPRequest):
    """ 新增运费模板

    @response delivery_template(DeliveryTemplate): 模板对象

    @request assumer(Number): (required)可选值：0,1 <br>  说明<br>0:表示买家承担服务费;<br>1:表示卖家承担服务费
    @request name(String): (required)运费模板的名称，长度不能超过50个字节
    @request template_add_fees(String): (required)增费：输入0.00-999.99（最多包含两位小数）<br/><font color=blue>增费可以为0</font><br/><font color=red>输入的格式分号个数和template_types数量一致，逗号个数必须与template_dests以分号隔开之后一一对应的数量一致</font>
    @request template_add_standards(String): (required)增费标准：当valuation(记价方式)为0时输入1-9999范围内的整数<br><font color=blue>增费标准目前只能为1</font>
        <br><font color=red>输入的格式分号个数和template_types数量一致，逗号个数必须与template_dests以分号隔开之后一一对应的数量一致</font>
    @request template_dests(String): (required)邮费子项涉及的地区.结构: value1;value2;value3,value4
        <br>如:1,110000;1,110000;1,310000;1,320000,330000。 aredId解释(1=全国,110000=北京,310000=上海,320000=江苏,330000=浙江)
        如果template_types设置为post;ems;exmpress;cod则表示为平邮(post)指定默认地区(全国)和北京地区的运费;其他的类似以分号区分一一对应
        <br/>可以用taobao.areas.get接口获取.或者参考：http://www.stats.gov.cn/tjbz/xzqhdm/t20080215_402462675.htm
        <br/><font color=red>每个运费方式设置的设涉及地区中必须包含全国地区（areaId=1）表示默认运费,可以只设置默认运费</font>
        <br><font color=blue>注意:为多个地区指定指定不同（首费标准、首费、增费标准、增费一项不一样就算不同）的运费以逗号","区分，
        template_start_standards(首费标准)、template_start_fees(首费)、
        template_add_standards(增费标准)、
        template_add_fees(增费)必须与template_types分号数量相同。如果为需要为多个地区指定相同运费则地区之间用“|”隔开即可。</font>
    @request template_start_fees(String): (required)首费：输入0.01-999.99（最多包含两位小数）
        <br/><font color=blue> 首费不能为0</font><br><font color=red>输入的格式分号个数和template_types数量一致，逗号个数必须与template_dests以分号隔开之后一一对应的数量一致</font>
    @request template_start_standards(String): (required)首费标准：当valuation(记价方式)为0时输入1-9999范围内的整数<br><font color=blue>首费标准目前只能为1</br>
        <br><font color=red>输入的格式分号个数和template_types数量一致，逗号个数必须与template_dests以分号隔开之后一一对应的数量一致</font>
    @request template_types(String): (required)运费方式:平邮 (post),快递公司(express),EMS (ems),货到付款(cod)结构:value1;value2;value3;value4
        如: post;express;ems;cod
        <br/><font color=red>
        注意:在添加多个运费方式时,字符串中使用 ";" 分号区分
        。template_dests(指定地区)
        template_start_standards(首费标准)、template_start_fees(首费)、template_add_standards(增费标准)、template_add_fees(增费)必须与template_types的分号数量相同. </font>
        <br>
        <font color=blue>普通用户：post,ems,express三种运费方式必须填写一个，不能填写cod。
        货到付款用户：如果填写了cod运费方式，则post,ems,express三种运费方式也必须填写一个，如果没有填写cod则填写的运费方式中必须存在express</font>
    @request valuation(Number): (required)可选值：0<br>说明：<br>0:表示按宝贝件数计算运费
    """
    REQUEST = {
        'assumer': {'type': topstruct.Number, 'is_required': True},
        'name': {'type': topstruct.String, 'is_required': True},
        'template_add_fees': {'type': topstruct.String, 'is_required': True},
        'template_add_standards': {'type': topstruct.String, 'is_required': True},
        'template_dests': {'type': topstruct.String, 'is_required': True},
        'template_start_fees': {'type': topstruct.String, 'is_required': True},
        'template_start_standards': {'type': topstruct.String, 'is_required': True},
        'template_types': {'type': topstruct.String, 'is_required': True},
        'valuation': {'type': topstruct.Number, 'is_required': True}
    }

    RESPONSE = {
        'delivery_template': {'type': topstruct.DeliveryTemplate, 'is_list': False}
    }

    API = 'taobao.delivery.template.add'


class DeliveryTemplateDeleteRequest(TOPRequest):
    """ 根据用户指定的模板ID删除指定的模板

    @response complete(Boolean): 表示删除成功还是失败

    @request template_id(Number): (required)运费模板ID
    """
    REQUEST = {
        'template_id': {'type': topstruct.Number, 'is_required': True}
    }

    RESPONSE = {
        'complete': {'type': topstruct.Boolean, 'is_list': False}
    }

    API = 'taobao.delivery.template.delete'


class DeliveryTemplateGetRequest(TOPRequest):
    """ 获取用户指定运费模板信息

    @response delivery_templates(DeliveryTemplate): 运费模板列表
    @response total_results(Number): 获得到符合条件的结果总数

    @request fields(FieldList): (required)需返回的字段列表。
        可选值:DeliveryTemplate结构体中的所有字段以及定义的四个常量;各字段之间用","隔开
        <br/>
        DeliveryTemplate结构:
        template_id：查询模板ID template_name:查询模板名称 assumer：查询服务承担放
        valuation:查询计价规则 supports:查询增值服务列表 created:查询模板创建时间 modified:查询修改时间；
        <br/>
        常量:<br/>
        query_cod:查询货到付款运费信息；
        query_post:查询平邮运费信息；
        query_express:查询快递公司运费信息；
        query_ems:查询EMS运费信息
        <br/>
        <font color=red>不能有空格</font>
    @request template_ids(FieldList): (required)需要查询的运费模板ID列表
    @request user_nick(String): (optional)在没有登录的情况下根据淘宝用户昵称查询指定的模板
    """
    REQUEST = {
        'fields': {'type': topstruct.FieldList, 'is_required': True, 'optional': topstruct.Set({'supports', 'valuation', 'query_post', 'query_express', 'assumer', 'template_id', 'query_ems', 'created', 'query_cod', 'name', 'fee_list', 'modified'})},
        'template_ids': {'type': topstruct.FieldList, 'is_required': True},
        'user_nick': {'type': topstruct.String, 'is_required': False}
    }

    RESPONSE = {
        'delivery_templates': {'type': topstruct.DeliveryTemplate, 'is_list': False},
        'total_results': {'type': topstruct.Number, 'is_list': False}
    }

    API = 'taobao.delivery.template.get'


class DeliveryTemplateUpdateRequest(TOPRequest):
    """ 修改运费模板

    @response complete(Boolean): 表示修改是否成功

    @request assumer(Number): (optional)可选值：0,1 <br>  说明<br>0:表示买家承担服务费;<br>1:表示卖家承担服务费
    @request name(String): (optional)模板名称，长度不能大于50个字节
    @request template_add_fees(String): (required)增费：输入0.00-999.99（最多包含两位小数）<br/><font color=blue>增费可以为0</font><br/><font color=red>输入的格式分号个数和template_types数量一致，逗号个数必须与template_dests以分号隔开之后一一对应的数量一致</font>
    @request template_add_standards(String): (required)增费标准：当valuation(记价方式)为0时输入1-9999范围内的整数<br><font color=blue>增费标准目前只能为1</font>
        <br><font color=red>输入的格式分号个数和template_types数量一致，逗号个数必须与template_dests以分号隔开之后一一对应的数量一致</font>
    @request template_dests(String): (required)邮费子项涉及的地区.结构: value1;value2;value3,value4
        <br>如:1,110000;1,110000;1,310000;1,320000,330000。 aredId解释(1=全国,110000=北京,310000=上海,320000=江苏,330000=浙江)
        如果template_types设置为post;ems;exmpress;cod则表示为平邮(post)指定默认地区(全国)和北京地区的运费;其他的类似以分号区分一一对应
        <br/>可以用taobao.areas.get接口获取.或者参考：http://www.stats.gov.cn/tjbz/xzqhdm/t20080215_402462675.htm
        <br/><font color=red>每个运费方式设置的设涉及地区中必须包含全国地区（areaId=1）表示默认运费,可以只设置默认运费</font>
        <br><font color=blue>注意:为多个地区指定指定不同（首费标准、首费、增费标准、增费一项不一样就算不同）的运费以逗号","区分，
        template_start_standards(首费标准)、template_start_fees(首费)、
        template_add_standards(增费标准)、
        template_add_fees(增费)必须与template_types分号数量相同。如果为需要为多个地区指定相同运费则地区之间用“|”隔开即可。</font>
    @request template_id(Number): (required)需要修改的模板对应的模板ID
    @request template_start_fees(String): (required)首费：输入0.01-999.99（最多包含两位小数）
        <br/><font color=blue> 首费不能为0</font><br><font color=red>输入的格式分号个数和template_types数量一致，逗号个数必须与template_dests以分号隔开之后一一对应的数量一致</font>
    @request template_start_standards(String): (required)首费标准：当valuation(记价方式)为0时输入1-9999范围内的整数<br><font color=blue>首费标准目前只能为1</br>
        <br><font color=red>输入的格式分号个数和template_types数量一致，逗号个数必须与template_dests以分号隔开之后一一对应的数量一致</font>
    @request template_types(String): (required)运费方式:平邮 (post),快递公司(express),EMS (ems),货到付款(cod)结构:value1;value2;value3;value4
        如: post;express;ems;cod
        <br/><font color=red>
        注意:在添加多个运费方式时,字符串中使用 ";" 分号区分。template_dests(指定地区) template_start_standards(首费标准)、template_start_fees(首费)、template_add_standards(增费标准)、template_add_fees(增费)必须与template_types的分号数量相同.
        </font>
        <br/>
        <font color=blue>
        普通用户：post,ems,express三种运费方式必须填写一个，不能填写cod。
        货到付款用户：如果填写了cod运费方式，则post,ems,express三种运费方式也必须填写一个，如果没有填写cod则填写的运费方式中必须存在express</font>
    """
    REQUEST = {
        'assumer': {'type': topstruct.Number, 'is_required': False},
        'name': {'type': topstruct.String, 'is_required': False},
        'template_add_fees': {'type': topstruct.String, 'is_required': True},
        'template_add_standards': {'type': topstruct.String, 'is_required': True},
        'template_dests': {'type': topstruct.String, 'is_required': True},
        'template_id': {'type': topstruct.Number, 'is_required': True},
        'template_start_fees': {'type': topstruct.String, 'is_required': True},
        'template_start_standards': {'type': topstruct.String, 'is_required': True},
        'template_types': {'type': topstruct.String, 'is_required': True}
    }

    RESPONSE = {
        'complete': {'type': topstruct.Boolean, 'is_list': False}
    }

    API = 'taobao.delivery.template.update'


class DeliveryTemplatesGetRequest(TOPRequest):
    """ 根据用户ID获取用户下所有模板

    @response delivery_templates(DeliveryTemplate): 运费模板列表
    @response total_results(Number): 获得到符合条件的结果总数

    @request fields(FieldList): (required)需返回的字段列表。
        可选值:DeliveryTemplate结构体中的所有字段以及定义的四个常量;各字段之间用","隔开
        <br/>
        DeliveryTemplate结构:
        template_id：查询模板ID template_name:查询模板名称 assumer：查询服务承担放
        valuation:查询计价规则 supports:查询增值服务列表 created:查询模板创建时间 modified:查询修改时间；
        <br/>
        常量:<br/>
        query_cod:查询货到付款运费信息；
        query_post:查询平邮运费信息；
        query_express:查询快递公司运费信息；
        query_ems:查询EMS运费信息
        <br/>
        <font color=red>不能有空格</font>
    """
    REQUEST = {
        'fields': {'type': topstruct.FieldList, 'is_required': True, 'optional': topstruct.Set({'supports', 'valuation', 'query_post', 'query_express', 'assumer', 'template_id', 'query_ems', 'created', 'query_cod', 'name', 'fee_list', 'modified'})}
    }

    RESPONSE = {
        'delivery_templates': {'type': topstruct.DeliveryTemplate, 'is_list': False},
        'total_results': {'type': topstruct.Number, 'is_list': False}
    }

    API = 'taobao.delivery.templates.get'


class LogisticsAddressAddRequest(TOPRequest):
    """ 通过此接口新增卖家地址库,卖家最多可添加5条地址库,新增第一条卖家地址，将会自动设为默认地址库

    @response address_result(AddressResult): 只返回修改日期modify_date

    @request addr(String): (required)详细街道地址，不需要重复填写省/市/区
    @request cancel_def(Boolean): (optional)默认退货地址。<br>
        <font color='red'>选择此项(true)，将当前地址设为默认退货地址，撤消原默认退货地址</font>
    @request city(String): (required)所在市
    @request contact_name(String): (required)联系人姓名 <font color='red'>长度不可超过20个字节</font>
    @request country(String): (optional)区、县
        <br><font color='red'>如果所在地区是海外的可以为空，否则为必参</font>
    @request get_def(Boolean): (optional)默认取货地址。<br>
        <font color='red'>选择此项(true)，将当前地址设为默认取货地址，撤消原默认取货地址</font>
    @request memo(String): (optional)备注,<br><font color='red'>备注不能超过256字节</font>
    @request mobile_phone(String): (special)手机号码，手机与电话必需有一个
        <br><font color='red'>手机号码不能超过20位</font>
    @request phone(String): (special)电话号码,手机与电话必需有一个
    @request province(String): (required)所在省
    @request seller_company(String): (optional)公司名称,<br><font color="red">公司名称长能不能超过20字节</font>
    @request zip_code(String): (optional)地区邮政编码
        <br><font color='red'>如果所在地区是海外的可以为空，否则为必参</font>
    """
    REQUEST = {
        'addr': {'type': topstruct.String, 'is_required': True},
        'cancel_def': {'type': topstruct.Boolean, 'is_required': False},
        'city': {'type': topstruct.String, 'is_required': True},
        'contact_name': {'type': topstruct.String, 'is_required': True},
        'country': {'type': topstruct.String, 'is_required': False},
        'get_def': {'type': topstruct.Boolean, 'is_required': False},
        'memo': {'type': topstruct.String, 'is_required': False},
        'mobile_phone': {'type': topstruct.String, 'is_required': False},
        'phone': {'type': topstruct.String, 'is_required': False},
        'province': {'type': topstruct.String, 'is_required': True},
        'seller_company': {'type': topstruct.String, 'is_required': False},
        'zip_code': {'type': topstruct.String, 'is_required': False}
    }

    RESPONSE = {
        'address_result': {'type': topstruct.AddressResult, 'is_list': False}
    }

    API = 'taobao.logistics.address.add'


class LogisticsAddressModifyRequest(TOPRequest):
    """ 卖家地址库修改

    @response address_result(AddressResult): 只返回修改时间modify_date

    @request addr(String): (required)详细街道地址，不需要重复填写省/市/区
    @request cancel_def(Boolean): (optional)默认退货地址。<br>
        <font color='red'>选择此项(true)，将当前地址设为默认退货地址，撤消原默认退货地址</font>
    @request city(String): (required)所在市
    @request contact_id(Number): (required)地址库ID
    @request contact_name(String): (required)联系人姓名
        <font color='red'>长度不可超过20个字节</font>
    @request country(String): (optional)区、县
        <br><font color='red'>如果所在地区是海外的可以为空，否则为必参</font>
    @request get_def(Boolean): (optional)默认取货地址。<br>
        <font color='red'>选择此项(true)，将当前地址设为默认取货地址，撤消原默认取货地址</font>
    @request memo(String): (optional)备注,<br><font color='red'>备注不能超过256字节</font>
    @request mobile_phone(String): (special)手机号码，手机与电话必需有一个 <br><font color='red'>手机号码不能超过20位</font>
    @request phone(String): (special)电话号码,手机与电话必需有一个
    @request province(String): (required)所在省
    @request seller_company(String): (optional)公司名称,
        <br><font color='red'>公司名称长能不能超过20字节</font>
    @request zip_code(String): (optional)地区邮政编码
        <br><font color='red'>如果所在地区是海外的可以为空，否则为必参</font>
    """
    REQUEST = {
        'addr': {'type': topstruct.String, 'is_required': True},
        'cancel_def': {'type': topstruct.Boolean, 'is_required': False},
        'city': {'type': topstruct.String, 'is_required': True},
        'contact_id': {'type': topstruct.Number, 'is_required': True},
        'contact_name': {'type': topstruct.String, 'is_required': True},
        'country': {'type': topstruct.String, 'is_required': False},
        'get_def': {'type': topstruct.Boolean, 'is_required': False},
        'memo': {'type': topstruct.String, 'is_required': False},
        'mobile_phone': {'type': topstruct.String, 'is_required': False},
        'phone': {'type': topstruct.String, 'is_required': False},
        'province': {'type': topstruct.String, 'is_required': True},
        'seller_company': {'type': topstruct.String, 'is_required': False},
        'zip_code': {'type': topstruct.String, 'is_required': False}
    }

    RESPONSE = {
        'address_result': {'type': topstruct.AddressResult, 'is_list': False}
    }

    API = 'taobao.logistics.address.modify'


class LogisticsAddressRemoveRequest(TOPRequest):
    """ 用此接口删除卖家地址库

    @response address_result(AddressResult): 只返回修改日期modify_date

    @request contact_id(Number): (required)地址库ID
    """
    REQUEST = {
        'contact_id': {'type': topstruct.Number, 'is_required': True}
    }

    RESPONSE = {
        'address_result': {'type': topstruct.AddressResult, 'is_list': False}
    }

    API = 'taobao.logistics.address.remove'


class LogisticsAddressSearchRequest(TOPRequest):
    """ 通过此接口查询卖家地址库，

    @response addresses(AddressResult): 一组地址库数据，

    @request rdef(String): (optional)可选，参数列表如下：<br><font color='red'>
        no_def:查询非默认地址<br>
        get_def:查询默认取货地址<br>
        cancel_def:查询默认退货地址<br>
        缺省此参数时，查询所有当前用户的地址库
        </font>
    """
    REQUEST = {
        'rdef': {'type': topstruct.String, 'is_required': False}
    }

    RESPONSE = {
        'addresses': {'type': topstruct.AddressResult, 'is_list': False}
    }

    API = 'taobao.logistics.address.search'


class LogisticsCompaniesGetRequest(TOPRequest):
    """ 查询淘宝网合作的物流公司信息，用于发货接口。

    @response logistics_companies(LogisticsCompany): 物流公司信息。返回的LogisticCompany包含的具体信息为入参fields请求的字段信息。

    @request fields(FieldList): (required)需返回的字段列表。可选值:LogisticsCompany 结构中的所有字段;多个字段间用","逗号隔开.
        如:id,code,name,reg_mail_no
        <br><font color='red'>说明：</font>
        <br>id：物流公司ID
        <br>code：物流公司code
        <br>name：物流公司名称
        <br>reg_mail_no：物流公司对应的运单规则
    @request is_recommended(Boolean): (optional)是否查询推荐物流公司.可选值:true,false.如果不提供此参数,将会返回所有支持电话联系的物流公司.
    @request order_mode(String): (optional)推荐物流公司的下单方式.可选值:offline(电话联系/自己联系),online(在线下单),all(即电话联系又在线下单). 此参数仅仅用于is_recommended 为ture时。就是说对于推荐物流公司才可用.如果不选择此参数将会返回推荐物流中支持电话联系的物流公司.
    """
    REQUEST = {
        'fields': {'type': topstruct.FieldList, 'is_required': True, 'optional': topstruct.Set({'reg_mail_no', 'name', 'code', 'id'})},
        'is_recommended': {'type': topstruct.Boolean, 'is_required': False},
        'order_mode': {'type': topstruct.String, 'is_required': False}
    }

    RESPONSE = {
        'logistics_companies': {'type': topstruct.LogisticsCompany, 'is_list': False}
    }

    API = 'taobao.logistics.companies.get'


class LogisticsDummySendRequest(TOPRequest):
    """ 用户调用该接口可实现无需物流（虚拟）发货,使用该接口发货，交易订单状态会直接变成卖家已发货

    @response shipping(Shipping): 返回发货是否成功is_success

    @request feature(String): (optional)feature参数格式<br>
        范例: mobileCode=tid1:手机串号1,手机串号2|tid2:手机串号3;machineCode=tid3:3C机器号A,3C机器号B<br>
        mobileCode无忧购的KEY,machineCode为3C的KEY,多个key之间用”;”分隔<br>
        “tid1:手机串号1,手机串号2|tid2:手机串号3”为mobileCode对应的value。
        "|"不同商品间的分隔符。<br>
        例A商品和B商品都属于无忧购商品，之间就用"|"分开。<br>
        TID就是商品代表的子订单号，对应taobao.trade.fullinfo.get 接口获得的oid字段。(通过OID可以唯一定位到当前商品上)<br>
        ":"TID和具体传入参数间的分隔符。冒号前表示TID,之后代表该商品的参数属性。<br>
        "," 属性间分隔符。（对应商品数量，当存在一个商品的数量超过1个时，用逗号分开）。<br>
        具体:当订单中A商品的数量为2个，其中手机串号分别为"12345","67890"。<br>
        参数格式：mobileCode=TIDA:12345,67890。
        TIDA对应了A宝贝，冒号后用逗号分隔的"12345","67890".说明本订单A宝贝的数量为2，值分别为"12345","67890"。<br>
        当存在"|"时，就说明订单中存在多个无忧购的商品，商品间用"|"分隔了开来。|"之后的内容含义同上。
    @request tid(Number): (required)淘宝交易ID
    """
    REQUEST = {
        'feature': {'type': topstruct.String, 'is_required': False},
        'tid': {'type': topstruct.Number, 'is_required': True}
    }

    RESPONSE = {
        'shipping': {'type': topstruct.Shipping, 'is_list': False}
    }

    API = 'taobao.logistics.dummy.send'


class LogisticsOfflineSendRequest(TOPRequest):
    """ 用户调用该接口可实现自己联系发货（线下物流），使用该接口发货，交易订单状态会直接变成卖家已发货。不支持货到付款、在线下单类型的订单。

    @response shipping(Shipping): 返回发货是否成功is_success

    @request cancel_id(Number): (optional)卖家联系人地址库ID，可以通过taobao.logistics.address.search接口查询到地址库ID。<br><font color='red'>如果为空，取的卖家的默认退货地址</font><br>
    @request company_code(String): (required)物流公司代码.如"POST"就代表中国邮政,"ZJS"就代表宅急送.调用 taobao.logistics.companies.get 获取。非淘宝官方物流合作公司，填写“其他”。
    @request feature(String): (optional)feature参数格式<br>
        范例: mobileCode=tid1:手机串号1,手机串号2|tid2:手机串号3;machineCode=tid3:3C机器号A,3C机器号B<br>
        mobileCode无忧购的KEY,machineCode为3C的KEY,多个key之间用”;”分隔<br>
        “tid1:手机串号1,手机串号2|tid2:手机串号3”为mobileCode对应的value。
        "|"不同商品间的分隔符。<br>
        例A商品和B商品都属于无忧购商品，之间就用"|"分开。<br>
        TID就是商品代表的子订单号，对应taobao.trade.fullinfo.get 接口获得的oid字段。(通过OID可以唯一定位到当前商品上)<br>
        ":"TID和具体传入参数间的分隔符。冒号前表示TID,之后代表该商品的参数属性。<br>
        "," 属性间分隔符。（对应商品数量，当存在一个商品的数量超过1个时，用逗号分开）。<br>
        具体:当订单中A商品的数量为2个，其中手机串号分别为"12345","67890"。<br>
        参数格式：mobileCode=TIDA:12345,67890。
        TIDA对应了A宝贝，冒号后用逗号分隔的"12345","67890".说明本订单A宝贝的数量为2，值分别为"12345","67890"。<br>
        当存在"|"时，就说明订单中存在多个无忧购的商品，商品间用"|"分隔了开来。|"之后的内容含义同上。
    @request out_sid(String): (required)运单号.具体一个物流公司的真实运单号码。淘宝官方物流会校验，请谨慎传入；若company_code中传入的代码非淘宝官方物流合作公司，此处运单号不校验。
    @request sender_id(Number): (optional)卖家联系人地址库ID，可以通过taobao.logistics.address.search接口查询到地址库ID。<font color='red'>如果为空，取的卖家的默认取货地址</font>
    @request tid(Number): (required)淘宝交易ID
    """
    REQUEST = {
        'cancel_id': {'type': topstruct.Number, 'is_required': False},
        'company_code': {'type': topstruct.String, 'is_required': True},
        'feature': {'type': topstruct.String, 'is_required': False},
        'out_sid': {'type': topstruct.String, 'is_required': True},
        'sender_id': {'type': topstruct.Number, 'is_required': False},
        'tid': {'type': topstruct.Number, 'is_required': True}
    }

    RESPONSE = {
        'shipping': {'type': topstruct.Shipping, 'is_list': False}
    }

    API = 'taobao.logistics.offline.send'


class LogisticsOnlineCancelRequest(TOPRequest):
    """ 调此接口取消发货的订单，重新选择物流公司发货。前提是物流公司未揽收货物。对未发货和已经被物流公司揽收的物流订单，是不能取消的。

    @response is_success(Boolean): 成功与失败
    @response modify_time(Date): 修改时间
    @response recreated_order_id(Number): 重新创建物流订单id

    @request tid(Number): (required)淘宝交易ID
    """
    REQUEST = {
        'tid': {'type': topstruct.Number, 'is_required': True}
    }

    RESPONSE = {
        'is_success': {'type': topstruct.Boolean, 'is_list': False},
        'modify_time': {'type': topstruct.Date, 'is_list': False},
        'recreated_order_id': {'type': topstruct.Number, 'is_list': False}
    }

    API = 'taobao.logistics.online.cancel'


class LogisticsOnlineConfirmRequest(TOPRequest):
    """ 确认发货的目的是让交易流程继承走下去，确认发货后交易状态会由【买家已付款】变为【卖家已发货】，然后买家才可以确认收货，货款打入卖家账号。货到付款的订单除外

    @response shipping(Shipping): 只返回is_success：是否成功。

    @request out_sid(String): (required)运单号.具体一个物流公司的真实运单号码。淘宝官方物流会校验，请谨慎传入；若company_code中传入的代码非淘宝官方物流合作公司，此处运单号不校验。<br>
    @request tid(Number): (required)淘宝交易ID
    """
    REQUEST = {
        'out_sid': {'type': topstruct.String, 'is_required': True},
        'tid': {'type': topstruct.Number, 'is_required': True}
    }

    RESPONSE = {
        'shipping': {'type': topstruct.Shipping, 'is_list': False}
    }

    API = 'taobao.logistics.online.confirm'


class LogisticsOnlineSendRequest(TOPRequest):
    """ 用户调用该接口可实现在线订单发货（支持货到付款）
        调用该接口实现在线下单发货，有两种情况：<br>
        <font color='red'>如果不输入运单号的情况：交易状态不会改变，需要调用taobao.logistics.online.confirm确认发货后交易状态才会变成卖家已发货。<br>
        如果输入运单号的情况发货：交易订单状态会直接变成卖家已发货 。</font>

    @response shipping(Shipping): 返回发货是否成功is_success

    @request cancel_id(Number): (optional)卖家联系人地址库ID，可以通过taobao.logistics.address.search接口查询到地址库ID。<br><font color='red'>如果为空，取的卖家的默认退货地址</font><br>
    @request company_code(String): (required)物流公司代码.如"POST"就代表中国邮政,"ZJS"就代表宅急送.调用 taobao.logistics.companies.get 获取。
        <br><font color='red'>如果是货到付款订单，选择的物流公司必须支持货到付款发货方式</font>
    @request feature(String): (optional)feature参数格式<br>
        范例: mobileCode=tid1:手机串号1,手机串号2|tid2:手机串号3;machineCode=tid3:3C机器号A,3C机器号B<br>
        mobileCode无忧购的KEY,machineCode为3C的KEY,多个key之间用”;”分隔<br>
        “tid1:手机串号1,手机串号2|tid2:手机串号3”为mobileCode对应的value。
        "|"不同商品间的分隔符。<br>
        例A商品和B商品都属于无忧购商品，之间就用"|"分开。<br>
        TID就是商品代表的子订单号，对应taobao.trade.fullinfo.get 接口获得的oid字段。(通过OID可以唯一定位到当前商品上)<br>
        ":"TID和具体传入参数间的分隔符。冒号前表示TID,之后代表该商品的参数属性。<br>
        "," 属性间分隔符。（对应商品数量，当存在一个商品的数量超过1个时，用逗号分开）。<br>
        具体:当订单中A商品的数量为2个，其中手机串号分别为"12345","67890"。<br>
        参数格式：mobileCode=TIDA:12345,67890。
        TIDA对应了A宝贝，冒号后用逗号分隔的"12345","67890".说明本订单A宝贝的数量为2，值分别为"12345","67890"。<br>
        当存在"|"时，就说明订单中存在多个无忧购的商品，商品间用"|"分隔了开来。|"之后的内容含义同上。
    @request out_sid(String): (optional)运单号.具体一个物流公司的真实运单号码。淘宝官方物流会校验，请谨慎传入；
    @request sender_id(Number): (optional)卖家联系人地址库ID，可以通过taobao.logistics.address.search接口查询到地址库ID。<font color='red'>如果为空，取的卖家的默认取货地址</font>
    @request tid(Number): (required)淘宝交易ID
    """
    REQUEST = {
        'cancel_id': {'type': topstruct.Number, 'is_required': False},
        'company_code': {'type': topstruct.String, 'is_required': True},
        'feature': {'type': topstruct.String, 'is_required': False},
        'out_sid': {'type': topstruct.String, 'is_required': False},
        'sender_id': {'type': topstruct.Number, 'is_required': False},
        'tid': {'type': topstruct.Number, 'is_required': True}
    }

    RESPONSE = {
        'shipping': {'type': topstruct.Shipping, 'is_list': False}
    }

    API = 'taobao.logistics.online.send'


class LogisticsOrdersDetailGetRequest(TOPRequest):
    """ 查询物流订单的详细信息，涉及用户隐私字段。（注：该API主要是提供给卖家查询物流订单使用，买家查询物流订单，建议使用taobao.logistics.trace.search）

    @response shippings(Shipping): 获取的物流订单详情列表.返回的Shipping包含的具体信息为入参fields请求的字段信息.
    @response total_results(Number): 搜索到的物流订单列表总数

    @request buyer_nick(String): (optional)买家昵称
    @request end_created(Date): (optional)创建时间结束.格式:yyyy-MM-dd HH:mm:ss
    @request fields(FieldList): (required)需返回的字段列表.可选值:Shipping 物流数据结构中所有字段.fileds中可以指定返回以上任意一个或者多个字段,以","分隔.
    @request freight_payer(String): (optional)谁承担运费.可选值:buyer(买家),seller(卖家).如:buyer
    @request page_no(Number): (optional)页码.该字段没传 或 值<1 ,则默认page_no为1
    @request page_size(Number): (optional)每页条数.该字段没传 或 值<1 ，则默认page_size为40
    @request receiver_name(String): (optional)收货人姓名
    @request seller_confirm(String): (optional)卖家是否发货.可选值:yes(是),no(否).如:yes.
    @request start_created(Date): (optional)创建时间开始.格式:yyyy-MM-dd HH:mm:ss
    @request status(String): (optional)物流状态.可查看数据结构 Shipping 中的status字段.
    @request tid(Number): (optional)交易ID.如果加入tid参数的话,不用传其他的参数,但是仅会返回一条物流订单信息.
    @request type(String): (optional)物流方式.可选值:post(平邮),express(快递),ems(EMS).如:post
    """
    REQUEST = {
        'buyer_nick': {'type': topstruct.String, 'is_required': False},
        'end_created': {'type': topstruct.Date, 'is_required': False},
        'fields': {'type': topstruct.FieldList, 'is_required': True, 'optional': topstruct.Set({'buyer_nick', 'delivery_end', 'location', 'item_title', 'is_success', 'receiver_mobile', 'is_quick_cod_order', 'receiver_phone', 'out_sid', 'company_name', 'seller_nick', 'order_code', 'created', 'status', 'delivery_start', 'freight_payer', 'receiver_name', 'tid', 'type', 'modified', 'seller_confirm'})},
        'freight_payer': {'type': topstruct.String, 'is_required': False},
        'page_no': {'type': topstruct.Number, 'is_required': False},
        'page_size': {'type': topstruct.Number, 'is_required': False},
        'receiver_name': {'type': topstruct.String, 'is_required': False},
        'seller_confirm': {'type': topstruct.String, 'is_required': False},
        'start_created': {'type': topstruct.Date, 'is_required': False},
        'status': {'type': topstruct.String, 'is_required': False},
        'tid': {'type': topstruct.Number, 'is_required': False},
        'type': {'type': topstruct.String, 'is_required': False}
    }

    RESPONSE = {
        'shippings': {'type': topstruct.Shipping, 'is_list': False},
        'total_results': {'type': topstruct.Number, 'is_list': False}
    }

    API = 'taobao.logistics.orders.detail.get'


class LogisticsOrdersGetRequest(TOPRequest):
    """ 批量查询物流订单。（注：该API主要是提供给卖家查询物流订单使用，买家查询物流订单，建议使用taobao.logistics.trace.search）

    @response shippings(Shipping): 获取的物流订单详情列表
        返回的Shipping包含的具体信息为入参fields请求的字段信息
    @response total_results(Number): 搜索到的物流订单列表总数

    @request buyer_nick(String): (optional)买家昵称
    @request end_created(Date): (optional)创建时间结束
    @request fields(FieldList): (required)需返回的字段列表.可选值:Shipping 物流数据结构中的以下字段:
        tid,seller_nick,buyer_nick,delivery_start, delivery_end,out_sid,item_title,receiver_name, created,modified,status,type,freight_payer,seller_confirm,company_name；多个字段之间用","分隔。如tid,seller_nick,buyer_nick,delivery_start。
    @request freight_payer(String): (optional)谁承担运费.可选值:buyer(买家),seller(卖家).如:buyer
    @request page_no(Number): (optional)页码.该字段没传 或 值<1 ,则默认page_no为1
    @request page_size(Number): (optional)每页条数.该字段没传 或 值<1 ,则默认page_size为40
    @request receiver_name(String): (optional)收货人姓名
    @request seller_confirm(String): (optional)卖家是否发货.可选值:yes(是),no(否).如:yes
    @request start_created(Date): (optional)创建时间开始
    @request status(String): (optional)物流状态.查看数据结构 Shipping 中的status字段.
    @request tid(Number): (optional)交易ID.如果加入tid参数的话,不用传其他的参数,但是仅会返回一条物流订单信息.
    @request type(String): (optional)物流方式.可选值:post(平邮),express(快递),ems(EMS).如:post
    """
    REQUEST = {
        'buyer_nick': {'type': topstruct.String, 'is_required': False},
        'end_created': {'type': topstruct.Date, 'is_required': False},
        'fields': {'type': topstruct.FieldList, 'is_required': True, 'optional': topstruct.Set({'buyer_nick', 'delivery_end', 'item_title', 'tid', 'seller_nick', 'out_sid', '"分隔。如tid', 'created', 'status', 'delivery_start', 'freight_payer', 'receiver_name', 'company_name；多个字段之间用"', 'type', 'modified', 'seller_confirm'})},
        'freight_payer': {'type': topstruct.String, 'is_required': False},
        'page_no': {'type': topstruct.Number, 'is_required': False},
        'page_size': {'type': topstruct.Number, 'is_required': False},
        'receiver_name': {'type': topstruct.String, 'is_required': False},
        'seller_confirm': {'type': topstruct.String, 'is_required': False},
        'start_created': {'type': topstruct.Date, 'is_required': False},
        'status': {'type': topstruct.String, 'is_required': False},
        'tid': {'type': topstruct.Number, 'is_required': False},
        'type': {'type': topstruct.String, 'is_required': False}
    }

    RESPONSE = {
        'shippings': {'type': topstruct.Shipping, 'is_list': False},
        'total_results': {'type': topstruct.Number, 'is_list': False}
    }

    API = 'taobao.logistics.orders.get'


class LogisticsOrderstorePushRequest(TOPRequest):
    """ 卖家使用自己的物流公司发货，可以通过本接口将订单的仓内信息推送到淘宝，淘宝保存这些仓内信息，并可在页面展示这些仓内信息。

    @response shipping(Shipping): 返回结果是否成功is_success

    @request occure_time(Date): (required)流转状态发生时间
    @request operate_detail(String): (required)仓内操作描述
    @request operator_contact(String): (optional)快递业务员联系方式
    @request operator_name(String): (optional)快递业务员名称
    @request trade_id(Number): (required)淘宝订单交易号
    """
    REQUEST = {
        'occure_time': {'type': topstruct.Date, 'is_required': True},
        'operate_detail': {'type': topstruct.String, 'is_required': True},
        'operator_contact': {'type': topstruct.String, 'is_required': False},
        'operator_name': {'type': topstruct.String, 'is_required': False},
        'trade_id': {'type': topstruct.Number, 'is_required': True}
    }

    RESPONSE = {
        'shipping': {'type': topstruct.Shipping, 'is_list': False}
    }

    API = 'taobao.logistics.orderstore.push'


class LogisticsOrdertracePushRequest(TOPRequest):
    """ 卖家使用自己的物流公司发货，可以通过本接口将订单的流转信息推送到淘宝，淘宝保存这些流转信息，并可在页面展示这些流转信息。

    @response shipping(Shipping): 返回结果是否成功is_success

    @request company_name(String): (required)物流公司名称
    @request current_city(String): (optional)流转节点的当前城市
    @request facility_name(String): (optional)网点名称
    @request mail_no(String): (required)快递单号。各个快递公司的运单号格式不同。
    @request next_city(String): (optional)流转节点的下一个城市
    @request node_description(String): (optional)描述当前节点的操作，操作是“揽收”、“派送”或“签收”。
    @request occure_time(Date): (required)流转节点发生时间
    @request operate_detail(String): (required)流转节点的详细地址及操作描述
    @request operator_contact(String): (optional)快递业务员联系方式，手机号码或电话。
    @request operator_name(String): (optional)快递业务员名称
    """
    REQUEST = {
        'company_name': {'type': topstruct.String, 'is_required': True},
        'current_city': {'type': topstruct.String, 'is_required': False},
        'facility_name': {'type': topstruct.String, 'is_required': False},
        'mail_no': {'type': topstruct.String, 'is_required': True},
        'next_city': {'type': topstruct.String, 'is_required': False},
        'node_description': {'type': topstruct.String, 'is_required': False},
        'occure_time': {'type': topstruct.Date, 'is_required': True},
        'operate_detail': {'type': topstruct.String, 'is_required': True},
        'operator_contact': {'type': topstruct.String, 'is_required': False},
        'operator_name': {'type': topstruct.String, 'is_required': False}
    }

    RESPONSE = {
        'shipping': {'type': topstruct.Shipping, 'is_list': False}
    }

    API = 'taobao.logistics.ordertrace.push'


class LogisticsPartnersGetRequest(TOPRequest):
    """ 查询物流公司信息（可以查询目的地可不可达情况）

    @response logistics_partners(LogisticsPartner): 物流公司信息。

    @request goods_value(String): (optional)货物价格.只有当选择货到付款此参数才会有效
    @request is_need_carriage(Boolean): (optional)是否需要揽收资费信息，默认false。在此值为false时，返回内容中将无carriage。在未设置source_id或target_id的情况下，无法查询揽收资费信息。自己联系无揽收资费记录。
    @request service_type(String): (required)服务类型，根据此参数可查出提供相应服务类型的物流公司信息(物流公司状态正常)，可选值：cod(货到付款)、online(在线下单)、 offline(自己联系)、limit(限时物流)。然后再根据source_id,target_id,goods_value这三个条件来过滤物流公司. 目前输入自己联系服务类型将会返回空，因为自己联系并没有具体的服务信息，所以不会有记录。
    @request source_id(String): (optional)物流公司揽货地地区码（必须是区、县一级的）.参考:http://www.stats.gov.cn/tjbz/xzqhdm/t20100623_402652267.htm  或者调用 taobao.areas.get 获取
    @request target_id(String): (optional)物流公司派送地地区码（必须是区、县一级的）.参考:http://www.stats.gov.cn/tjbz/xzqhdm/t20100623_402652267.htm  或者调用 taobao.areas.get 获取
    """
    REQUEST = {
        'goods_value': {'type': topstruct.String, 'is_required': False},
        'is_need_carriage': {'type': topstruct.Boolean, 'is_required': False},
        'service_type': {'type': topstruct.String, 'is_required': True},
        'source_id': {'type': topstruct.String, 'is_required': False},
        'target_id': {'type': topstruct.String, 'is_required': False}
    }

    RESPONSE = {
        'logistics_partners': {'type': topstruct.LogisticsPartner, 'is_list': False}
    }

    API = 'taobao.logistics.partners.get'


class LogisticsTraceSearchRequest(TOPRequest):
    """ 用户根据淘宝交易号查询物流流转信息，如2010-8-10 15：23：00到达杭州集散地

    @response company_name(String): 物流公司名称
    @response out_sid(String): 运单号
    @response status(String): 订单的物流状态
        * 等候发送给物流公司
        *已提交给物流公司,等待物流公司接单
        *已经确认消息接收，等待物流公司接单
        *物流公司已接单
        *物流公司不接单
        *物流公司揽收失败
        *物流公司揽收成功
        *签收失败
        *对方已签收
        *对方拒绝签收
    @response tid(Number): 交易号
    @response trace_list(TransitStepInfo): 流转信息列表

    @request seller_nick(String): (required)卖家昵称
    @request tid(Number): (required)淘宝交易号，请勿传非淘宝交易号
    """
    REQUEST = {
        'seller_nick': {'type': topstruct.String, 'is_required': True},
        'tid': {'type': topstruct.Number, 'is_required': True}
    }

    RESPONSE = {
        'company_name': {'type': topstruct.String, 'is_list': False},
        'out_sid': {'type': topstruct.String, 'is_list': False},
        'status': {'type': topstruct.String, 'is_list': False},
        'tid': {'type': topstruct.Number, 'is_list': False},
        'trace_list': {'type': topstruct.TransitStepInfo, 'is_list': False}
    }

    API = 'taobao.logistics.trace.search'


class TopatsDeliverySendRequest(TOPRequest):
    """ 使用指南：http://open.taobao.com/dev/index.php/ATS%E4%BD%BF%E7%94%A8%E6%8C%87%E5%8D%97
        1.提供异步批量物流发货功能 2.一次最多发货40个订单 3.提交任务会进行初步任务校验，如果成功会返回任务号和创建时间，如果失败就报错 4.可以接收淘宝发出的任务完成消息，也可以过一段时间来取结果。获取结果接口为taobao.topats.result.get
        5.此api执行完成发送的通知消息格式为{"task":{"task_id":123456,"created":"2010-8-19"}}

    @response task(Task): 创建任务信息。里面只包含task_id和created

    @request company_codes(String): (optional)每个tid所对应的物流公司代码。可以不传，表示所有的物流公司都为"其他"，但是只要有一个订单需要指定物流公司，所有的订单都需要指定物流公司,每个类型之间用";"连接。排列要和tid顺序一致，不需要指定物流公司的订单，该位置上放上一个空字符串""。可以不传，传了长度和位置要和tid保持一致。
        每个company_code表示物流公司代码.如"POST"就代表中国邮政,"ZJS"就代表宅急送.调用 taobao.logisticcompanies.get 获取。如传入的代码非淘宝官方物流合作公司，默认是“其他”物流的方式，在淘宝不显示物流具体进度，故传入需谨慎。如果orderType为delivery_needed，则必传
    @request memos(String): (optional)每个tid所对应的卖家备注。可以不传，表示所有的发货订单都不需要卖家备注，但是只要有一个订单需要指定卖家备注，所有的订单都需要指定卖家备注,每个卖家备注之间用";"连接。排列要和tid顺序一致，不需要指定卖家备注的订单，该位置上放上一个空字符串""。可以不传，传了长度和位置要和tid保持一致。卖家备注.最大长度为250个字符。如果orderType为delivery_needed，则必传
    @request order_types(String): (optional)每个tid所对应的物流发货类型。可以不传，表示所有的发货类型都为"delivery_needed"，但是只要有一个订单需要指定发货类型，所有的订单都需要指定发货类型,每个类型之间用";"连接。排列要和tid顺序一致，不需要指定发货类型的订单，该位置上放上一个空字符串""。可以不传，传了长度和位置要和tid保持一致。 每个类型可选( delivery_needed(物流订单发货),virtual_goods(虚拟物品发货). ) 注:选择virtual_goods类型进行发货的话下面的参数可以不需填写。如果选择delivery_needed 则下面的参数必须要填写
    @request out_sids(String): (optional)每个tid所对应的物流公司运单号。可以不传，表示所有的物流订单都没有订单号，但是只要有一个订单需要有订单号，所有的订单都需要指定订单号,每个订单号之间用";"连接。排列要和tid顺序一致，不需要指定订单号的订单，该位置上放上一个空字符串""。可以不传，传了长度和位置要和tid保持一致。
        具体一个物流公司的真实运单号码。淘宝官方物流会校验，请谨慎传入；若company_codes中传入的代码非淘宝官方物流合作公司，此处运单号不校验。如果orderType为delivery_needed，则必传
    @request seller_address(String): (optional)卖家地址(详细地址).如:XXX街道XXX门牌,省市区不需要提供。如果orderType为delivery_needed，则必传
    @request seller_area_id(Number): (optional)卖家所在地国家公布的标准地区码.参考:http://www.stats.gov.cn/tjbz/xzqhdm/t20080215_402462675.htm 或者调用 taobao.areas.get 获取。如果orderType为delivery_needed，则必传
    @request seller_mobile(String): (optional)卖家手机号码
    @request seller_name(String): (optional)卖家姓名。如果orderType为delivery_needed，则必传
    @request seller_phone(String): (optional)卖家固定电话.包含区号,电话,分机号,中间用 " – "; 卖家固定电话和卖家手机号码,必须填写一个.
    @request seller_zip(String): (optional)卖家邮编。如果orderType为delivery_needed，则必传
    @request tids(String): (required)批量发货的订单id列表，每个订单id必需是合法的数字类型的tid，每个tid之间以";"分隔，至少要指定一个tid，最多不超过40个tid
    """
    REQUEST = {
        'company_codes': {'type': topstruct.String, 'is_required': False},
        'memos': {'type': topstruct.String, 'is_required': False},
        'order_types': {'type': topstruct.String, 'is_required': False},
        'out_sids': {'type': topstruct.String, 'is_required': False},
        'seller_address': {'type': topstruct.String, 'is_required': False},
        'seller_area_id': {'type': topstruct.Number, 'is_required': False},
        'seller_mobile': {'type': topstruct.String, 'is_required': False},
        'seller_name': {'type': topstruct.String, 'is_required': False},
        'seller_phone': {'type': topstruct.String, 'is_required': False},
        'seller_zip': {'type': topstruct.String, 'is_required': False},
        'tids': {'type': topstruct.String, 'is_required': True}
    }

    RESPONSE = {
        'task': {'type': topstruct.Task, 'is_list': False}
    }

    API = 'taobao.topats.delivery.send'


class SellercatsListAddRequest(TOPRequest):
    """ 此API添加卖家店铺内自定义类目
        父类目parent_cid值等于0：表示此类目为店铺下的一级类目，值不等于0：表示此类目有父类目
        注：因为缓存的关系,添加的新类目需8个小时后才可以在淘宝页面上正常显示，但是不影响在该类目下商品发布

    @response seller_cat(SellerCat): 返回seller_cat数据结构中的：cid,created

    @request name(String): (required)卖家自定义类目名称。不超过20个字符
    @request parent_cid(Number): (optional)父类目编号，如果类目为店铺下的一级类目：值等于0，如果类目为子类目，调用获取taobao.sellercats.list.get父类目编号
    @request pict_url(String): (optional)链接图片URL地址。(绝对地址，格式：http://host/image_path)
    @request sort_order(Number): (optional)该类目在页面上的排序位置,取值范围:大于零的整数
    """
    REQUEST = {
        'name': {'type': topstruct.String, 'is_required': True},
        'parent_cid': {'type': topstruct.Number, 'is_required': False},
        'pict_url': {'type': topstruct.String, 'is_required': False},
        'sort_order': {'type': topstruct.Number, 'is_required': False}
    }

    RESPONSE = {
        'seller_cat': {'type': topstruct.SellerCat, 'is_list': False}
    }

    API = 'taobao.sellercats.list.add'


class SellercatsListGetRequest(TOPRequest):
    """ 此API获取当前卖家店铺在淘宝前端被展示的浏览导航类目（面向买家）

    @response seller_cats(SellerCat): 卖家自定义类目

    @request nick(String): (required)卖家昵称
    """
    REQUEST = {
        'nick': {'type': topstruct.String, 'is_required': True}
    }

    RESPONSE = {
        'seller_cats': {'type': topstruct.SellerCat, 'is_list': False}
    }

    API = 'taobao.sellercats.list.get'


class SellercatsListUpdateRequest(TOPRequest):
    """ 此API更新卖家店铺内自定义类目
        注：因为缓存的关系，添加的新类目需8个小时后才可以在淘宝页面上正常显示，但是不影响在该类目下商品发布

    @response seller_cat(SellerCat): 返回sellercat数据结构中的：cid,modified

    @request cid(Number): (required)卖家自定义类目编号
    @request name(String): (optional)卖家自定义类目名称。不超过20个字符
    @request pict_url(String): (optional)链接图片URL地址
    @request sort_order(Number): (optional)该类目在页面上的排序位置,取值范围:大于零的整数
    """
    REQUEST = {
        'cid': {'type': topstruct.Number, 'is_required': True},
        'name': {'type': topstruct.String, 'is_required': False},
        'pict_url': {'type': topstruct.String, 'is_required': False},
        'sort_order': {'type': topstruct.Number, 'is_required': False}
    }

    RESPONSE = {
        'seller_cat': {'type': topstruct.SellerCat, 'is_list': False}
    }

    API = 'taobao.sellercats.list.update'


class ShopGetRequest(TOPRequest):
    """ 获取卖家店铺的基本信息

    @response shop(Shop): 店铺信息

    @request fields(FieldList): (required)需返回的字段列表。可选值：Shop 结构中的所有字段；多个字段之间用逗号(,)分隔
    @request nick(String): (required)卖家昵称
    """
    REQUEST = {
        'fields': {'type': topstruct.FieldList, 'is_required': True, 'optional': topstruct.Set({'pic_path', 'desc', 'sid', 'nick', 'bulletin', 'all_count', 'title', 'created', 'cid', 'remain_count', 'shop_score', 'modified', 'used_count'})},
        'nick': {'type': topstruct.String, 'is_required': True}
    }

    RESPONSE = {
        'shop': {'type': topstruct.Shop, 'is_list': False}
    }

    API = 'taobao.shop.get'


class ShopRemainshowcaseGetRequest(TOPRequest):
    """ 获取卖家店铺剩余橱窗数量，已用橱窗数量，总橱窗数量（对于B卖家，后两个参数返回-1）

    @response shop(Shop): 支持返回剩余橱窗数量，已用橱窗数量，总橱窗数量
    """
    REQUEST = {}

    RESPONSE = {
        'shop': {'type': topstruct.Shop, 'is_list': False}
    }

    API = 'taobao.shop.remainshowcase.get'


class ShopUpdateRequest(TOPRequest):
    """ 目前只支持标题、公告和描述的更新

    @response shop(Shop): 店铺信息

    @request bulletin(String): (special)店铺公告。不超过1024个字符
    @request desc(String): (special)店铺描述。10～2000个字符以内
    @request title(String): (special)店铺标题。不超过30个字符；过滤敏感词，如淘咖啡、阿里巴巴等。title, bulletin和desc至少必须传一个
    """
    REQUEST = {
        'bulletin': {'type': topstruct.String, 'is_required': False},
        'desc': {'type': topstruct.String, 'is_required': False},
        'title': {'type': topstruct.String, 'is_required': False}
    }

    RESPONSE = {
        'shop': {'type': topstruct.Shop, 'is_list': False}
    }

    API = 'taobao.shop.update'


class FenxiaoCooperationGetRequest(TOPRequest):
    """ 获取供应商的合作关系信息

    @response cooperations(Cooperation): 合作分销关系
    @response total_results(Number): 结果记录数

    @request end_date(Date): (optional)合作结束时间yyyy-MM-dd
    @request page_no(Number): (optional)页码（大于0的整数，默认1）
    @request page_size(Number): (optional)每页记录数（默认20，最大50）
    @request start_date(Date): (optional)合作开始时间yyyy-MM-dd
    @request status(String): (optional)合作状态： NORMAL(合作中)、 ENDING(终止中) 、END (终止)
    @request trade_type(String): (optional)分销方式：AGENT(代销) 、DEALER（经销）
    """
    REQUEST = {
        'end_date': {'type': topstruct.Date, 'is_required': False},
        'page_no': {'type': topstruct.Number, 'is_required': False},
        'page_size': {'type': topstruct.Number, 'is_required': False},
        'start_date': {'type': topstruct.Date, 'is_required': False},
        'status': {'type': topstruct.String, 'is_required': False},
        'trade_type': {'type': topstruct.String, 'is_required': False}
    }

    RESPONSE = {
        'cooperations': {'type': topstruct.Cooperation, 'is_list': False},
        'total_results': {'type': topstruct.Number, 'is_list': False}
    }

    API = 'taobao.fenxiao.cooperation.get'


class FenxiaoCooperationUpdateRequest(TOPRequest):
    """ 供应商更新合作的分销商等级

    @response is_success(Boolean): 更新结果成功失败

    @request distributor_id(Number): (required)分销商ID
    @request grade_id(Number): (required)等级ID(0代表取消)
    @request trade_type(String): (optional)分销方式(新增)： AGENT(代销)、DEALER(经销)(默认为代销)
    """
    REQUEST = {
        'distributor_id': {'type': topstruct.Number, 'is_required': True},
        'grade_id': {'type': topstruct.Number, 'is_required': True},
        'trade_type': {'type': topstruct.String, 'is_required': False}
    }

    RESPONSE = {
        'is_success': {'type': topstruct.Boolean, 'is_list': False}
    }

    API = 'taobao.fenxiao.cooperation.update'


class FenxiaoDiscountAddRequest(TOPRequest):
    """ 新增等级折扣

    @response discount_id(Number): 折扣ID

    @request discount_name(String): (required)折扣名称,长度不能超过25字节
    @request discount_types(String): (required)PERCENT（按折扣优惠）、PRICE（按减价优惠），例如"PERCENT,PRICE,PERCENT"
    @request discount_values(String): (required)优惠比率或者优惠价格，例如：”8000,-2300,7000”,大小为-100000000到100000000之间（单位：分）
    @request target_ids(String): (required)会员等级的id或者分销商id，例如：”1001,2001,1002”
    @request target_types(String): (required)GRADE（按会员等级优惠）、DISTRIBUTOR（按分销商优惠），例如"GRADE,DISTRIBUTOR"
    """
    REQUEST = {
        'discount_name': {'type': topstruct.String, 'is_required': True},
        'discount_types': {'type': topstruct.String, 'is_required': True},
        'discount_values': {'type': topstruct.String, 'is_required': True},
        'target_ids': {'type': topstruct.String, 'is_required': True},
        'target_types': {'type': topstruct.String, 'is_required': True}
    }

    RESPONSE = {
        'discount_id': {'type': topstruct.Number, 'is_list': False}
    }

    API = 'taobao.fenxiao.discount.add'


class FenxiaoDiscountUpdateRequest(TOPRequest):
    """ 修改等级折扣

    @response is_success(Boolean): 成功状态

    @request detail_ids(String): (optional)详情ID，例如：”0,1002,1003”
    @request detail_statuss(String): (optional)ADD(新增)、UPDATE（更新）、DEL（删除，对应的target_type等信息填NULL），例如：”UPDATE,DEL,DEL”
    @request discount_id(Number): (optional)折扣ID
    @request discount_name(String): (optional)折扣名称，长度不能超过25字节
    @request discount_status(String): (optional)状态DEL（删除）UPDATE(更新)
    @request discount_types(String): (optional)PERCENT（按折扣优惠）、PRICE（按减价优惠），例如"PERCENT,PRICE,PERCENT"
    @request discount_values(String): (optional)优惠比率或者优惠价格，例如：”8000,-2300,7000”,大小为-100000000到100000000之间（单位：分）
    @request target_ids(String): (optional)会员等级的id或者分销商id，例如：”1001,2001,1002”
    @request target_types(String): (optional)GRADE（按会员等级优惠）、DISTRIBUTOR（按分销商优惠），例如"GRADE,DISTRIBUTOR"
    """
    REQUEST = {
        'detail_ids': {'type': topstruct.String, 'is_required': False},
        'detail_statuss': {'type': topstruct.String, 'is_required': False},
        'discount_id': {'type': topstruct.Number, 'is_required': False},
        'discount_name': {'type': topstruct.String, 'is_required': False},
        'discount_status': {'type': topstruct.String, 'is_required': False},
        'discount_types': {'type': topstruct.String, 'is_required': False},
        'discount_values': {'type': topstruct.String, 'is_required': False},
        'target_ids': {'type': topstruct.String, 'is_required': False},
        'target_types': {'type': topstruct.String, 'is_required': False}
    }

    RESPONSE = {
        'is_success': {'type': topstruct.Boolean, 'is_list': False}
    }

    API = 'taobao.fenxiao.discount.update'


class FenxiaoDiscountsGetRequest(TOPRequest):
    """ 查询折扣信息

    @response discounts(Discount): 折扣数据结构
    @response total_results(Number): 记录数

    @request discount_id(Number): (optional)折扣ID
    @request ext_fields(String): (optional)指定查询额外的信息，可选值：DETAIL（查询折扣详情），多个可选值用逗号分割。（只允许指定折扣ID情况下使用）
    """
    REQUEST = {
        'discount_id': {'type': topstruct.Number, 'is_required': False},
        'ext_fields': {'type': topstruct.String, 'is_required': False}
    }

    RESPONSE = {
        'discounts': {'type': topstruct.Discount, 'is_list': False},
        'total_results': {'type': topstruct.Number, 'is_list': False}
    }

    API = 'taobao.fenxiao.discounts.get'


class FenxiaoDistributorItemsGetRequest(TOPRequest):
    """ 供应商查询分销商商品下载记录。

    @response records(FenxiaoItemRecord): 下载记录对象
    @response total_results(Number): 查询结果记录数

    @request distributor_id(Number): (special)分销商ID 。
    @request end_modified(Date): (optional)设置结束时间,空为不设置。
    @request page_no(Number): (optional)页码（大于0的整数，默认1）
    @request page_size(Number): (optional)每页记录数（默认20，最大50）
    @request product_id(Number): (special)产品ID
    @request start_modified(Date): (optional)设置开始时间。空为不设置。
    """
    REQUEST = {
        'distributor_id': {'type': topstruct.Number, 'is_required': False},
        'end_modified': {'type': topstruct.Date, 'is_required': False},
        'page_no': {'type': topstruct.Number, 'is_required': False},
        'page_size': {'type': topstruct.Number, 'is_required': False},
        'product_id': {'type': topstruct.Number, 'is_required': False},
        'start_modified': {'type': topstruct.Date, 'is_required': False}
    }

    RESPONSE = {
        'records': {'type': topstruct.FenxiaoItemRecord, 'is_list': False},
        'total_results': {'type': topstruct.Number, 'is_list': False}
    }

    API = 'taobao.fenxiao.distributor.items.get'


class FenxiaoDistributorsGetRequest(TOPRequest):
    """ 查询和当前登录供应商有合作关系的分销商的信息

    @response distributors(Distributor): 分销商详细信息

    @request nicks(String): (required)分销商用户名列表。多个之间以“,”分隔;最多支持50个分销商用户名。
    """
    REQUEST = {
        'nicks': {'type': topstruct.String, 'is_required': True}
    }

    RESPONSE = {
        'distributors': {'type': topstruct.Distributor, 'is_list': False}
    }

    API = 'taobao.fenxiao.distributors.get'


class FenxiaoGradesGetRequest(TOPRequest):
    """ 根据供应商ID，查询他的分销商等级信息

    @response fenxiao_grades(FenxiaoGrade): 分销商等级信息
    @response total_results(Number): 记录数
    """
    REQUEST = {}

    RESPONSE = {
        'fenxiao_grades': {'type': topstruct.FenxiaoGrade, 'is_list': False},
        'total_results': {'type': topstruct.Number, 'is_list': False}
    }

    API = 'taobao.fenxiao.grades.get'


class FenxiaoLoginUserGetRequest(TOPRequest):
    """ 获取用户登录信息

    @response login_user(LoginUser): 登录用户信息
    """
    REQUEST = {}

    RESPONSE = {
        'login_user': {'type': topstruct.LoginUser, 'is_list': False}
    }

    API = 'taobao.fenxiao.login.user.get'


class FenxiaoOrderCustomfieldUpdateRequest(TOPRequest):
    """ 采购单自定义字段

    @response is_success(Boolean): 操作是否成功

    @request isv_custom_key(String): (required)自定义key
    @request isv_custom_value(String): (optional)自定义的值
    @request purchase_order_id(Number): (required)采购单id
    """
    REQUEST = {
        'isv_custom_key': {'type': topstruct.String, 'is_required': True},
        'isv_custom_value': {'type': topstruct.String, 'is_required': False},
        'purchase_order_id': {'type': topstruct.Number, 'is_required': True}
    }

    RESPONSE = {
        'is_success': {'type': topstruct.Boolean, 'is_list': False}
    }

    API = 'taobao.fenxiao.order.customfield.update'


class FenxiaoOrderMessageAddRequest(TOPRequest):
    """ 添加采购单留言，最多20条（供应商分销商都可添加）

    @response is_success(Boolean): 是否成功

    @request message(String): (required)留言内容
    @request purchase_order_id(Number): (required)采购单id
    """
    REQUEST = {
        'message': {'type': topstruct.String, 'is_required': True},
        'purchase_order_id': {'type': topstruct.Number, 'is_required': True}
    }

    RESPONSE = {
        'is_success': {'type': topstruct.Boolean, 'is_list': False}
    }

    API = 'taobao.fenxiao.order.message.add'


class FenxiaoOrderPriceUpdateRequest(TOPRequest):
    """ 采购单价格修改接口

    @response is_success(Boolean): 操作是否成功

    @request adjust_fee(String): (optional)单位是分，多个值用","分隔。负数表示减价，正数表示加价。
        adjust_fee值的个数必须和sub_order_ids个数一样
    @request post_fee(Number): (optional)单位是分,值不能小于0,值必须在采购单可改的范围内。
        post_fee和sub_order_ids  至少有一组不能为空
    @request purchase_order_id(Number): (required)采购单id
    @request sub_order_ids(String): (optional)采购子单id
    """
    REQUEST = {
        'adjust_fee': {'type': topstruct.String, 'is_required': False},
        'post_fee': {'type': topstruct.Number, 'is_required': False},
        'purchase_order_id': {'type': topstruct.Number, 'is_required': True},
        'sub_order_ids': {'type': topstruct.String, 'is_required': False}
    }

    RESPONSE = {
        'is_success': {'type': topstruct.Boolean, 'is_list': False}
    }

    API = 'taobao.fenxiao.order.price.update'


class FenxiaoOrderRemarkUpdateRequest(TOPRequest):
    """ 供应商修改采购单备注

    @response is_success(Boolean): 操作是否成功

    @request purchase_order_id(Number): (required)采购单编号
    @request supplier_memo(String): (required)备注旗子(供应商操作)
    @request supplier_memo_flag(Number): (optional)旗子的标记，1-5之间的数字。非1-5之间，都采用1作为默认。
        1:红色
        2:黄色
        3:绿色
        4:蓝色
        5:粉红色
    """
    REQUEST = {
        'purchase_order_id': {'type': topstruct.Number, 'is_required': True},
        'supplier_memo': {'type': topstruct.String, 'is_required': True},
        'supplier_memo_flag': {'type': topstruct.Number, 'is_required': False}
    }

    RESPONSE = {
        'is_success': {'type': topstruct.Boolean, 'is_list': False}
    }

    API = 'taobao.fenxiao.order.remark.update'


class FenxiaoOrdersGetRequest(TOPRequest):
    """ 分销商或供应商均可用此接口查询采购单信息. (发货处理请调用物流API中的发货接口)

    @response purchase_orders(PurchaseOrder): 采购单及子采购单信息。返回 PurchaseOrder 包含的字段信息。
    @response total_results(Number): 搜索到的采购单记录总数

    @request end_created(Date): (optional)结束时间 格式 yyyy-MM-dd HH:mm:ss.支持到秒的查询。若不传时分秒，默认为0时0分0秒。若purchase_order_id没传，则此参数必传。
    @request fields(String): (optional)多个字段用","分隔。
        fields
        如果为空：返回所有采购单对象(purchase_orders)字段。
        如果不为空：返回指定采购单对象(purchase_orders)字段。
        例1：
        sub_purchase_orders.tc_order_id 表示只返回tc_order_id
        例2：
        sub_purchase_orders表示只返回子采购单列表
    @request page_no(Number): (optional)页码。（大于0的整数。默认为1）
    @request page_size(Number): (optional)每页条数。（每页条数不超过50条）
    @request purchase_order_id(Number): (optional)采购单编号或分销流水号，若其它参数没传，则此参数必传。
    @request start_created(Date): (optional)起始时间 格式 yyyy-MM-dd HH:mm:ss.支持到秒的查询。若不传时分秒，默认为0时0分0秒。若purchase_order_id没传，则此参数必传。
    @request status(String): (optional)交易状态，不传默认查询所有采购单。根据身份选择自身状态。可选值:<br>
        *供应商：<br>
        WAIT_SELLER_SEND_GOODS(等待发货)<br>
        WAIT_SELLER_CONFIRM_PAY(待确认收款)<br>
        WAIT_BUYER_PAY(等待付款)<br>
        WAIT_BUYER_CONFIRM_GOODS(已发货)<br>
        TRADE_REFUNDING(退款中)<br>
        TRADE_FINISHED(采购成功)<br>
        TRADE_CLOSED(已关闭)。<br>
        WAIT_SELLER_SEND_GOODS_WAIT_ACOUNT (已付款（待分账），待发货。只对代销分账支持)<br>
        WAIT_SELLER_SEND_GOODS_ACOUNTED(已付款（已分账），待发货。只对代销分账支持)<br>
        *分销商：<br>
        WAIT_BUYER_PAY(等待付款)<br>
        WAIT_BUYER_CONFIRM_GOODS(待收货确认)<br>
        TRADE_FOR_PAY(已付款)<br>
        TRADE_REFUNDING(退款中)<br>
        TRADE_FINISHED(采购成功)<br>
        TRADE_CLOSED(已关闭)。<br>
        WAIT_BUYER_CONFIRM_GOODS_WAIT_ACOUNT(已付款（待分账），已发货。只对代销分账支持)<br>
        WAIT_BUYER_CONFIRM_GOODS_ACOUNTED(已付款（已分账），已发货。只对代销分账支持)<br>
    @request time_type(String): (optional)可选值：trade_time_type(采购单按照成交时间范围查询),update_time_type(采购单按照更新时间范围查询)
    """
    REQUEST = {
        'end_created': {'type': topstruct.Date, 'is_required': False},
        'fields': {'type': topstruct.String, 'is_required': False, 'optional': topstruct.Set({'total_fee', 'sub_purchase_orders.status', 'sub_purchase_orders.refund_fee', 'end_time', 'post_fee', 'distributor_username', 'sub_purchase_orders.auction_price', 'status', 'logistics_company_name', 'supplier_from', 'modified', 'sub_purchase_orders.total_fee', 'sub_purchase_orders.item_id', 'distributor_payment', 'sub_purchase_orders.sku_id', 'sub_purchase_orders.price', 'sub_purchase_orders', 'logistics_id', 'sub_purchase_orders.old_sku_properties', 'distributor_from', 'fenxiao_id', 'sub_purchase_orders.title', 'sub_purchase_orders.item_outer_id', 'isv_custom_value', 'id', 'buyer_nick', 'shipping', 'alipay_no', 'pay_type', 'sub_purchase_orders.num', 'sub_purchase_orders.tc_order_id', 'memo', 'sub_purchase_orders.buyer_payment', 'snapshot_url', 'created', 'pay_time', 'sub_purchase_orders.sku_properties', 'sub_purchase_orders.snapshot_url', 'isv_custom_key', 'sub_purchase_orders.order_200_status', 'sub_purchase_orders.sku_outer_id', 'consign_time', 'sub_purchase_orders.distributor_payment', 'receiver', 'supplier_flag', 'supplier_username', 'sub_purchase_orders.created', 'supplier_memo', 'tc_order_id', 'sub_purchase_orders.id', 'sub_purchase_orders.fenxiao_id', 'trade_type'}), 'default': {'None'}},
        'page_no': {'type': topstruct.Number, 'is_required': False},
        'page_size': {'type': topstruct.Number, 'is_required': False},
        'purchase_order_id': {'type': topstruct.Number, 'is_required': False},
        'start_created': {'type': topstruct.Date, 'is_required': False},
        'status': {'type': topstruct.String, 'is_required': False},
        'time_type': {'type': topstruct.String, 'is_required': False}
    }

    RESPONSE = {
        'purchase_orders': {'type': topstruct.PurchaseOrder, 'is_list': False},
        'total_results': {'type': topstruct.Number, 'is_list': False}
    }

    API = 'taobao.fenxiao.orders.get'


class FenxiaoProductAddRequest(TOPRequest):
    """ 添加分销平台产品数据。业务逻辑与分销系统前台页面一致。
        * 产品图片默认为空
        * 产品发布后默认为下架状态

    @response created(Date): 产品创建时间 时间格式：yyyy-MM-dd HH:mm:ss
    @response pid(Number): 产品ID

    @request alarm_number(Number): (required)警戒库存必须是0到29999。
    @request category_id(Number): (required)所属类目id，参考Taobao.itemcats.get，不支持成人等类目，输入成人类目id保存提示类目属性错误。
    @request city(String): (required)所在地：市，例：“杭州”
    @request cost_price(String): (optional)代销采购价格，单位：元。例：“10.56”。必须在0.01元到10000000元之间。
    @request dealer_cost_price(String): (optional)经销采购价，单位：元。例：“10.56”。必须在0.01元到10000000元之间。
    @request desc(String): (required)产品描述，长度为5到25000字符。
    @request discount_id(Number): (optional)折扣ID
    @request have_guarantee(String): (required)是否有保修，可选值：false（否）、true（是），默认false。
    @request have_invoice(String): (required)是否有发票，可选值：false（否）、true（是），默认false。
    @request image(Image): (optional)产品主图，大小不超过500k，格式为gif,jpg,jpeg,png,bmp等图片
    @request input_properties(String): (optional)自定义属性。格式为pid:value;pid:value
    @request is_authz(String): (optional)添加产品时，添加入参isAuthz:yes|no
        yes:需要授权
        no:不需要授权
        默认是需要授权
    @request item_id(Number): (optional)导入的商品ID
    @request name(String): (required)产品名称，长度不超过60个字节。
    @request outer_id(String): (optional)商家编码，长度不能超过60个字节。
    @request pic_path(String): (optional)产品主图图片空间相对路径或绝对路径
    @request postage_ems(String): (optional)ems费用，单位：元。例：“10.56”。 大小为0.00元到999999元之间。
    @request postage_fast(String): (optional)快递费用，单位：元。例：“10.56”。 大小为0.01元到999999元之间。
    @request postage_id(Number): (optional)运费模板ID，参考taobao.postages.get。
    @request postage_ordinary(String): (optional)平邮费用，单位：元。例：“10.56”。 大小为0.01元到999999元之间。
    @request postage_type(String): (required)运费类型，可选值：seller（供应商承担运费）、buyer（分销商承担运费）,默认seller。
    @request productcat_id(Number): (required)产品线ID
    @request properties(String): (optional)产品属性，格式为pid:vid;pid:vid
    @request property_alias(String): (optional)属性别名，格式为：pid:vid:alias;pid:vid:alias（alias为别名）
    @request prov(String): (required)所在地：省，例：“浙江”
    @request quantity(Number): (required)产品库存必须是1到999999。
    @request retail_price_high(String): (required)最高零售价，单位：元。例：“10.56”。必须在0.01元到10000000元之间，最高零售价必须大于最低零售价。
    @request retail_price_low(String): (required)最低零售价，单位：元。例：“10.56”。必须在0.01元到10000000元之间。
    @request sku_cost_prices(String): (optional)sku的采购价。如果多个，用逗号分隔，并与其他sku信息保持相同顺序
    @request sku_dealer_cost_prices(String): (optional)sku的经销采购价。如果多个，用逗号分隔，并与其他sku信息保持相同顺序。其中每个值的单位：元。例：“10.56,12.3”。必须在0.01元到10000000元之间。
    @request sku_outer_ids(String): (optional)sku的商家编码。如果多个，用逗号分隔，并与其他sku信息保持相同顺序
    @request sku_properties(String): (optional)sku的属性。如果多个，用逗号分隔，并与其他sku信息保持相同顺序
    @request sku_quantitys(String): (optional)sku的库存。如果多个，用逗号分隔，并与其他sku信息保持相同顺序
    @request sku_standard_prices(String): (optional)sku的市场价。如果多个，用逗号分隔，并与其他sku信息保持相同顺序
    @request standard_price(String): (required)标准价格，单位：元。例：“10.56”。必须在0.01元到10000000元之间。
    @request trade_type(String): (optional)分销方式：AGENT（只做代销，默认值）、DEALER（只做经销）、ALL（代销和经销都做）
    """
    REQUEST = {
        'alarm_number': {'type': topstruct.Number, 'is_required': True},
        'category_id': {'type': topstruct.Number, 'is_required': True},
        'city': {'type': topstruct.String, 'is_required': True},
        'cost_price': {'type': topstruct.String, 'is_required': False},
        'dealer_cost_price': {'type': topstruct.String, 'is_required': False},
        'desc': {'type': topstruct.String, 'is_required': True},
        'discount_id': {'type': topstruct.Number, 'is_required': False},
        'have_guarantee': {'type': topstruct.String, 'is_required': True},
        'have_invoice': {'type': topstruct.String, 'is_required': True},
        'image': {'type': topstruct.Image, 'is_required': False},
        'input_properties': {'type': topstruct.String, 'is_required': False},
        'is_authz': {'type': topstruct.String, 'is_required': False},
        'item_id': {'type': topstruct.Number, 'is_required': False},
        'name': {'type': topstruct.String, 'is_required': True},
        'outer_id': {'type': topstruct.String, 'is_required': False},
        'pic_path': {'type': topstruct.String, 'is_required': False},
        'postage_ems': {'type': topstruct.String, 'is_required': False},
        'postage_fast': {'type': topstruct.String, 'is_required': False},
        'postage_id': {'type': topstruct.Number, 'is_required': False},
        'postage_ordinary': {'type': topstruct.String, 'is_required': False},
        'postage_type': {'type': topstruct.String, 'is_required': True},
        'productcat_id': {'type': topstruct.Number, 'is_required': True},
        'properties': {'type': topstruct.String, 'is_required': False},
        'property_alias': {'type': topstruct.String, 'is_required': False},
        'prov': {'type': topstruct.String, 'is_required': True},
        'quantity': {'type': topstruct.Number, 'is_required': True},
        'retail_price_high': {'type': topstruct.String, 'is_required': True},
        'retail_price_low': {'type': topstruct.String, 'is_required': True},
        'sku_cost_prices': {'type': topstruct.String, 'is_required': False},
        'sku_dealer_cost_prices': {'type': topstruct.String, 'is_required': False},
        'sku_outer_ids': {'type': topstruct.String, 'is_required': False},
        'sku_properties': {'type': topstruct.String, 'is_required': False},
        'sku_quantitys': {'type': topstruct.String, 'is_required': False},
        'sku_standard_prices': {'type': topstruct.String, 'is_required': False},
        'standard_price': {'type': topstruct.String, 'is_required': True},
        'trade_type': {'type': topstruct.String, 'is_required': False}
    }

    RESPONSE = {
        'created': {'type': topstruct.Date, 'is_list': False},
        'pid': {'type': topstruct.Number, 'is_list': False}
    }

    API = 'taobao.fenxiao.product.add'


class FenxiaoProductImageDeleteRequest(TOPRequest):
    """ 产品图片删除，只删除图片信息，不真正删除图片

    @response created(Date): 操作时间
    @response result(Boolean): 操作结果

    @request position(Number): (required)图片位置
    @request product_id(Number): (required)产品ID
    @request properties(String): (optional)properties表示sku图片的属性。key:value形式，key是pid，value是vid。如果position是0的话，则properties需要是必传项
    """
    REQUEST = {
        'position': {'type': topstruct.Number, 'is_required': True},
        'product_id': {'type': topstruct.Number, 'is_required': True},
        'properties': {'type': topstruct.String, 'is_required': False}
    }

    RESPONSE = {
        'created': {'type': topstruct.Date, 'is_list': False},
        'result': {'type': topstruct.Boolean, 'is_list': False}
    }

    API = 'taobao.fenxiao.product.image.delete'


class FenxiaoProductImageUploadRequest(TOPRequest):
    """ 产品主图图片空间相对路径或绝对路径添加或更新，或者是图片上传。如果指定位置的图片已存在，则覆盖原有信息。如果位置为1,自动设为主图；如果位置为0，表示属性图片

    @response created(Date): 操作时间
    @response result(Boolean): 操作是否成功

    @request image(Image): (special)产品图片
    @request pic_path(String): (special)产品主图图片空间相对路径或绝对路径
    @request position(Number): (required)图片位置，0-14之间。0：操作sku属性图片，1：主图，2-5：细节图，6-14：额外主图
    @request product_id(Number): (required)产品ID
    @request properties(String): (optional)properties表示sku图片的属性。key:value形式，key是pid，value是vid。如果position是0的话，则properties需要是必传项
    """
    REQUEST = {
        'image': {'type': topstruct.Image, 'is_required': False},
        'pic_path': {'type': topstruct.String, 'is_required': False},
        'position': {'type': topstruct.Number, 'is_required': True},
        'product_id': {'type': topstruct.Number, 'is_required': True},
        'properties': {'type': topstruct.String, 'is_required': False}
    }

    RESPONSE = {
        'created': {'type': topstruct.Date, 'is_list': False},
        'result': {'type': topstruct.Boolean, 'is_list': False}
    }

    API = 'taobao.fenxiao.product.image.upload'


class FenxiaoProductSkuAddRequest(TOPRequest):
    """ 添加产品SKU信息

    @response created(Date): 操作时间
    @response result(Boolean): 操作结果

    @request agent_cost_price(String): (special)代销采购价
    @request dealer_cost_price(String): (special)经销采购价
    @request product_id(Number): (required)产品ID
    @request properties(String): (required)sku属性
    @request quantity(Number): (optional)sku产品库存，在0到1000000之间，如果不传，则库存为0
    @request sku_number(String): (optional)商家编码
    @request standard_price(String): (required)市场价，最大值1000000000
    """
    REQUEST = {
        'agent_cost_price': {'type': topstruct.String, 'is_required': False},
        'dealer_cost_price': {'type': topstruct.String, 'is_required': False},
        'product_id': {'type': topstruct.Number, 'is_required': True},
        'properties': {'type': topstruct.String, 'is_required': True},
        'quantity': {'type': topstruct.Number, 'is_required': False},
        'sku_number': {'type': topstruct.String, 'is_required': False},
        'standard_price': {'type': topstruct.String, 'is_required': True}
    }

    RESPONSE = {
        'created': {'type': topstruct.Date, 'is_list': False},
        'result': {'type': topstruct.Boolean, 'is_list': False}
    }

    API = 'taobao.fenxiao.product.sku.add'


class FenxiaoProductSkuDeleteRequest(TOPRequest):
    """ 根据sku properties删除sku数据

    @response created(Date): 操作时间
    @response result(Boolean): 操作结果

    @request product_id(Number): (required)产品id
    @request properties(String): (required)sku属性
    """
    REQUEST = {
        'product_id': {'type': topstruct.Number, 'is_required': True},
        'properties': {'type': topstruct.String, 'is_required': True}
    }

    RESPONSE = {
        'created': {'type': topstruct.Date, 'is_list': False},
        'result': {'type': topstruct.Boolean, 'is_list': False}
    }

    API = 'taobao.fenxiao.product.sku.delete'


class FenxiaoProductSkuUpdateRequest(TOPRequest):
    """ 产品SKU信息更新

    @response created(Date): 操作时间
    @response result(Boolean): 操作结果

    @request agent_cost_price(String): (optional)代销采购价
    @request dealer_cost_price(String): (optional)经销采购价
    @request product_id(Number): (required)产品ID
    @request properties(String): (required)sku属性
    @request quantity(Number): (optional)产品SKU库存
    @request sku_number(String): (optional)商家编码
    @request standard_price(String): (optional)市场价
    """
    REQUEST = {
        'agent_cost_price': {'type': topstruct.String, 'is_required': False},
        'dealer_cost_price': {'type': topstruct.String, 'is_required': False},
        'product_id': {'type': topstruct.Number, 'is_required': True},
        'properties': {'type': topstruct.String, 'is_required': True},
        'quantity': {'type': topstruct.Number, 'is_required': False},
        'sku_number': {'type': topstruct.String, 'is_required': False},
        'standard_price': {'type': topstruct.String, 'is_required': False}
    }

    RESPONSE = {
        'created': {'type': topstruct.Date, 'is_list': False},
        'result': {'type': topstruct.Boolean, 'is_list': False}
    }

    API = 'taobao.fenxiao.product.sku.update'


class FenxiaoProductSkusGetRequest(TOPRequest):
    """ 产品sku查询

    @response skus(FenxiaoSku): sku信息
    @response total_results(Number): 记录数量

    @request product_id(Number): (required)产品ID
    """
    REQUEST = {
        'product_id': {'type': topstruct.Number, 'is_required': True}
    }

    RESPONSE = {
        'skus': {'type': topstruct.FenxiaoSku, 'is_list': False},
        'total_results': {'type': topstruct.Number, 'is_list': False}
    }

    API = 'taobao.fenxiao.product.skus.get'


class FenxiaoProductUpdateRequest(TOPRequest):
    """ 更新分销平台产品数据，不传更新数据返回失败<br>
        1. 对sku进行增、删操作时，原有的sku_ids字段会被忽略，请使用sku_properties和sku_properties_del。<br>

    @response modified(Date): 更新时间，时间格式：yyyy-MM-dd HH:mm:ss
    @response pid(Number): 产品ID

    @request alarm_number(Number): (optional)警戒库存必须是0到29999。
    @request category_id(Number): (optional)所属类目id，参考Taobao.itemcats.get，不支持成人等类目，输入成人类目id保存提示类目属性错误。
    @request city(String): (optional)所在地：市，例：“杭州”
    @request cost_price(String): (optional)代销采购价格，单位：元。例：“10.56”。必须在0.01元到10000000元之间。
    @request dealer_cost_price(String): (optional)经销采购价，单位：元。例：“10.56”。必须在0.01元到10000000元之间。
    @request desc(String): (optional)产品描述，长度为5到25000字符。
    @request discount_id(Number): (optional)折扣ID
    @request have_guarantee(String): (optional)是否有保修，可选值：false（否）、true（是），默认false。
    @request have_invoice(String): (optional)是否有发票，可选值：false（否）、true（是），默认false。
    @request image(Image): (optional)主图图片，如果pic_path参数不空，则优先使用pic_path，忽略该参数
    @request input_properties(String): (optional)自定义属性。格式为pid:value;pid:value
    @request is_authz(String): (optional)产品是否需要授权isAuthz:yes|no
        yes:需要授权
        no:不需要授权
    @request name(String): (optional)产品名称，长度不超过60个字节。
    @request outer_id(String): (optional)商家编码，长度不能超过60个字节。
    @request pic_path(String): (optional)产品主图图片空间相对路径或绝对路径
    @request pid(Number): (required)产品ID
    @request postage_ems(String): (optional)ems费用，单位：元。例：“10.56”。大小为0.01元到999999元之间。更新时必须指定运费类型为buyer，否则不更新。
    @request postage_fast(String): (optional)快递费用，单位：元。例：“10.56”。大小为0.01元到999999元之间。更新时必须指定运费类型为buyer，否则不更新。
    @request postage_id(Number): (optional)运费模板ID，参考taobao.postages.get。更新时必须指定运费类型为 buyer，否则不更新。
    @request postage_ordinary(String): (optional)平邮费用，单位：元。例：“10.56”。大小为0.01元到999999元之间。更新时必须指定运费类型为buyer，否则不更新。
    @request postage_type(String): (optional)运费类型，可选值：seller（供应商承担运费）、buyer（分销商承担运费）。
    @request properties(String): (optional)产品属性
    @request property_alias(String): (optional)属性别名
    @request prov(String): (optional)所在地：省，例：“浙江”
    @request quantity(Number): (optional)产品库存必须是1到999999。
    @request retail_price_high(String): (optional)最高零售价，单位：元。例：“10.56”。必须在0.01元到10000000元之间，最高零售价必须大于最低零售价。
    @request retail_price_low(String): (optional)最低零售价，单位：元。例：“10.56”。必须在0.01元到10000000元之间。
    @request sku_cost_prices(String): (optional)sku采购价格，单位元，例："10.50,11.00,20.50"，字段必须和上面的sku_ids或sku_properties保持一致。
    @request sku_dealer_cost_prices(String): (optional)sku的经销采购价。如果多个，用逗号分隔，并与其他sku信息保持相同顺序。其中每个值的单位：元。例：“10.56,12.3”。必须在0.01元到10000000元之间。
    @request sku_ids(String): (optional)sku id列表，例：1001,1002,1003。如果传入sku_properties将忽略此参数。
    @request sku_outer_ids(String): (optional)sku商家编码 ，单位元，例："S1000,S1002,S1003"，字段必须和上面的id或sku_properties保持一致，如果没有可以写成",,"
    @request sku_properties(String): (optional)sku属性。格式:pid:vid;pid:vid,表示一组属性如:1627207:3232483;1630696:3284570,表示一组:机身颜色:军绿色;手机套餐:一电一充。多组之间用逗号“,”区分。(属性的pid调用taobao.itemprops.get取得，属性值的vid用taobao.itempropvalues.get取得vid)
        通过此字段可新增和更新sku。若传入此值将忽略sku_ids字段。sku其他字段与此值保持一致。
    @request sku_properties_del(String): (optional)根据sku属性删除sku信息。需要按组删除属性。
    @request sku_quantitys(String): (optional)sku库存，单位元，例："10,20,30"，字段必须和sku_ids或sku_properties保持一致。
    @request sku_standard_prices(String): (optional)sku市场价，单位元，例："10.50,11.00,20.50"，字段必须和上面的sku_ids或sku_properties保持一致。
    @request standard_price(String): (optional)标准价格，单位：元。例：“10.56”。必须在0.01元到10000000元之间。
    @request status(String): (optional)发布状态，可选值：up（上架）、down（下架）、delete（删除），输入非法字符则忽略。
    """
    REQUEST = {
        'alarm_number': {'type': topstruct.Number, 'is_required': False},
        'category_id': {'type': topstruct.Number, 'is_required': False},
        'city': {'type': topstruct.String, 'is_required': False},
        'cost_price': {'type': topstruct.String, 'is_required': False},
        'dealer_cost_price': {'type': topstruct.String, 'is_required': False},
        'desc': {'type': topstruct.String, 'is_required': False},
        'discount_id': {'type': topstruct.Number, 'is_required': False},
        'have_guarantee': {'type': topstruct.String, 'is_required': False},
        'have_invoice': {'type': topstruct.String, 'is_required': False},
        'image': {'type': topstruct.Image, 'is_required': False},
        'input_properties': {'type': topstruct.String, 'is_required': False},
        'is_authz': {'type': topstruct.String, 'is_required': False},
        'name': {'type': topstruct.String, 'is_required': False},
        'outer_id': {'type': topstruct.String, 'is_required': False},
        'pic_path': {'type': topstruct.String, 'is_required': False},
        'pid': {'type': topstruct.Number, 'is_required': True},
        'postage_ems': {'type': topstruct.String, 'is_required': False},
        'postage_fast': {'type': topstruct.String, 'is_required': False},
        'postage_id': {'type': topstruct.Number, 'is_required': False},
        'postage_ordinary': {'type': topstruct.String, 'is_required': False},
        'postage_type': {'type': topstruct.String, 'is_required': False},
        'properties': {'type': topstruct.String, 'is_required': False},
        'property_alias': {'type': topstruct.String, 'is_required': False},
        'prov': {'type': topstruct.String, 'is_required': False},
        'quantity': {'type': topstruct.Number, 'is_required': False},
        'retail_price_high': {'type': topstruct.String, 'is_required': False},
        'retail_price_low': {'type': topstruct.String, 'is_required': False},
        'sku_cost_prices': {'type': topstruct.String, 'is_required': False},
        'sku_dealer_cost_prices': {'type': topstruct.String, 'is_required': False},
        'sku_ids': {'type': topstruct.String, 'is_required': False},
        'sku_outer_ids': {'type': topstruct.String, 'is_required': False},
        'sku_properties': {'type': topstruct.String, 'is_required': False},
        'sku_properties_del': {'type': topstruct.String, 'is_required': False},
        'sku_quantitys': {'type': topstruct.String, 'is_required': False},
        'sku_standard_prices': {'type': topstruct.String, 'is_required': False},
        'standard_price': {'type': topstruct.String, 'is_required': False},
        'status': {'type': topstruct.String, 'is_required': False}
    }

    RESPONSE = {
        'modified': {'type': topstruct.Date, 'is_list': False},
        'pid': {'type': topstruct.Number, 'is_list': False}
    }

    API = 'taobao.fenxiao.product.update'


class FenxiaoProductcatsGetRequest(TOPRequest):
    """ 查询供应商的所有产品线数据。根据登陆用户来查询，不需要其他入参

    @response productcats(ProductCat): 产品线列表。返回 ProductCat 包含的字段信息。
    @response total_results(Number): 查询结果记录数

    @request fields(String): (optional)返回字段列表
    """
    REQUEST = {
        'fields': {'type': topstruct.String, 'is_required': False, 'optional': topstruct.Set({'cost_percent_dealer', 'retail_low_percent', 'product_num', 'cost_percent_agent', 'retail_high_percent', 'name', 'id'})}
    }

    RESPONSE = {
        'productcats': {'type': topstruct.ProductCat, 'is_list': False},
        'total_results': {'type': topstruct.Number, 'is_list': False}
    }

    API = 'taobao.fenxiao.productcats.get'


class FenxiaoProductsGetRequest(TOPRequest):
    """ 查询供应商的产品数据。
        * 入参传入pids将优先查询，即只按这个条件查询。
        *入参传入sku_number将优先查询(没有传入pids)，即只按这个条件查询(最多显示50条)
        * 入参fields传skus将查询sku的数据，不传该参数默认不查询，返回产品的其它信息。
        * 入参fields传入images将查询多图数据，不传只返回主图数据。
        * 入参fields仅对传入pids生效（只有按ID查询时，才能查询额外的数据）
        * 查询结果按照产品发布时间倒序，即时间近的数据在前。

    @response products(FenxiaoProduct): 产品对象记录集。返回 FenxiaoProduct 包含的字段信息。
    @response total_results(Number): 查询结果记录数

    @request end_modified(Date): (optional)结束修改时间
    @request fields(FieldList): (optional)指定查询额外的信息，可选值：skus（sku数据）、images（多图），多个可选值用逗号分割。
    @request is_authz(String): (optional)查询产品列表时，查询入参“是否需要授权”
        yes:需要授权
        no:不需要授权
    @request item_ids(Number): (optional)可根据导入的商品ID列表查询，优先级次于产品ID、sku_numbers，高于其他分页查询条件。最大限制20，用逗号分割，例如：“1001,1002,1003,1004,1005”
    @request outer_id(String): (optional)商家编码
    @request page_no(Number): (optional)页码（大于0的整数，默认1）
    @request page_size(Number): (optional)每页记录数（默认20，最大50）
    @request pids(Number): (optional)产品ID列表（最大限制30），用逗号分割，例如：“1001,1002,1003,1004,1005”
    @request productcat_id(Number): (optional)产品线ID
    @request sku_number(String): (optional)sku商家编码
    @request start_modified(Date): (optional)开始修改时间
    @request status(String): (optional)产品状态，可选值：up（上架）、down（下架），不传默认查询所有
    """
    REQUEST = {
        'end_modified': {'type': topstruct.Date, 'is_required': False},
        'fields': {'type': topstruct.FieldList, 'is_required': False, 'optional': topstruct.Set({'images', 'skus'})},
        'is_authz': {'type': topstruct.String, 'is_required': False},
        'item_ids': {'type': topstruct.Number, 'is_required': False},
        'outer_id': {'type': topstruct.String, 'is_required': False},
        'page_no': {'type': topstruct.Number, 'is_required': False},
        'page_size': {'type': topstruct.Number, 'is_required': False},
        'pids': {'type': topstruct.Number, 'is_required': False},
        'productcat_id': {'type': topstruct.Number, 'is_required': False},
        'sku_number': {'type': topstruct.String, 'is_required': False},
        'start_modified': {'type': topstruct.Date, 'is_required': False},
        'status': {'type': topstruct.String, 'is_required': False}
    }

    RESPONSE = {
        'products': {'type': topstruct.FenxiaoProduct, 'is_list': False},
        'total_results': {'type': topstruct.Number, 'is_list': False}
    }

    API = 'taobao.fenxiao.products.get'


class PosterAppointedpostersGetRequest(TOPRequest):
    """ 取得最近最热门的画报。与频道有关，按点击排序

    @response appointedposters(Huabao): 画报列表

    @request appointed_type(String): (required)HOT(热门），RECOMMEND（推荐）
    @request channel_ids(Number): (required)频道ID列表
    @request re_num(Number): (optional)请求返回的记录数，默认10条，最多20条，如果请求超过20或者小于等于0，则按10条返回
    """
    REQUEST = {
        'appointed_type': {'type': topstruct.String, 'is_required': True},
        'channel_ids': {'type': topstruct.Number, 'is_required': True},
        're_num': {'type': topstruct.Number, 'is_required': False}
    }

    RESPONSE = {
        'appointedposters': {'type': topstruct.Huabao, 'is_list': False}
    }

    API = 'taobao.poster.appointedposters.get'


class PosterChannelGetRequest(TOPRequest):
    """ 根据频道ID获取频道信息

    @response channel(HuabaoChannel): 频道信息

    @request channel_id(Number): (required)根据频道ID获取频道信息
    """
    REQUEST = {
        'channel_id': {'type': topstruct.Number, 'is_required': True}
    }

    RESPONSE = {
        'channel': {'type': topstruct.HuabaoChannel, 'is_list': False}
    }

    API = 'taobao.poster.channel.get'


class PosterChannelsGetRequest(TOPRequest):
    """ 获取画报所有频道信息

    @response channels(HuabaoChannel): 返回频道列表
    """
    REQUEST = {}

    RESPONSE = {
        'channels': {'type': topstruct.HuabaoChannel, 'is_list': False}
    }

    API = 'taobao.poster.channels.get'


class PosterPostauctionsGetRequest(TOPRequest):
    """ 根据画报ID获取相关商品

    @response posterauctions(HuabaoAuctionInfo): 返回画报商品列表

    @request poster_id(Number): (required)画报ID
    """
    REQUEST = {
        'poster_id': {'type': topstruct.Number, 'is_required': True}
    }

    RESPONSE = {
        'posterauctions': {'type': topstruct.HuabaoAuctionInfo, 'is_list': False}
    }

    API = 'taobao.poster.postauctions.get'


class PosterPosterdetailGetRequest(TOPRequest):
    """ 通过画报ID取得画报信息，上一张，下一张，图片列表等信息

    @response poster(Huabao): 根据ID获取画报
    @response poster_pics(HuabaoPicture): 根据画报ID获取画报图片

    @request poster_id(Number): (required)画报id
    """
    REQUEST = {
        'poster_id': {'type': topstruct.Number, 'is_required': True}
    }

    RESPONSE = {
        'poster': {'type': topstruct.Huabao, 'is_list': False},
        'poster_pics': {'type': topstruct.HuabaoPicture, 'is_list': False}
    }

    API = 'taobao.poster.posterdetail.get'


class PosterPostersGetRequest(TOPRequest):
    """ 获取频道ID对应的画报列表

    @response posters(Huabao): 画报列表

    @request channel_id(Number): (required)频道ID
    @request page_no(Number): (optional)第几页
    @request page_size(Number): (optional)每页条数
    """
    REQUEST = {
        'channel_id': {'type': topstruct.Number, 'is_required': True},
        'page_no': {'type': topstruct.Number, 'is_required': False},
        'page_size': {'type': topstruct.Number, 'is_required': False}
    }

    RESPONSE = {
        'posters': {'type': topstruct.Huabao, 'is_list': False}
    }

    API = 'taobao.poster.posters.get'


class PosterPostersSearchRequest(TOPRequest):
    """ 根据画报关键词、发布时间、画报制作者、编辑推荐、特色推荐进行搜索，同时支持多种排序方式。此接口至少需要一个查询条件方可进行查询，如key_word，start_date，end_date，channel_ids，editor_recommend，user_nick，recommend_factor，至少有一个查询条件。

    @response posters(Huabao): 返回画报列表

    @request channel_ids(Number): (special)频道id列表
    @request editor_recommend(Number): (special)编辑推荐：editor_recommend = 1；
    @request end_date(Date): (special)结束时间
    @request key_word(String): (special)关键词出现在标题，短标题，标签中
    @request page_no(Number): (required)当前页
    @request page_size(Number): (required)每页显示画报数
        <br>注：
        <br>1.当输入的值小于10或者大于20，会按照默认值10返回
        <br>2.最大支持20条返回
    @request recommend_factor(Number): (special)服饰 频道	{
        推荐系数  2 	服饰—平铺图;
        推荐系数  5	服饰—真人秀;
        ;推荐系数  7	服饰—风格秀场;
        }
        男人 频道{
        推荐系数  8	男人频道—卖家画报;
        }
        女人 频道{
        推荐系数 6	女人频道—淘宝红人;
        推荐系数 8	女人频道—优质街拍;
        }
        亲子 频道{
        推荐系数 1	亲子频道—亲子单品；
        推荐系数 8	亲子频道—卖家画报；
        }
        美容 频道{
        推荐系数 5+关键字:护肤	美容频道—护肤内容；
        推荐系数 5+关键字:彩妆	美容频道—彩妆内容；
        推荐系数 5+关键字:美发	美容频道—扎发类内容；
        }
        居家 频道{
        推荐系数 5	居家频道—线下体验馆-爱蜂潮；
        }
    @request sort_type(Number): (optional)1："点击升序"；
        2："点击降序"；
        3："创建时间升序"；
        4："创建时间降序"；
    @request start_date(Date): (special)开始时间
    @request user_nick(String): (special)制作画报的 用户名
    """
    REQUEST = {
        'channel_ids': {'type': topstruct.Number, 'is_required': False},
        'editor_recommend': {'type': topstruct.Number, 'is_required': False},
        'end_date': {'type': topstruct.Date, 'is_required': False},
        'key_word': {'type': topstruct.String, 'is_required': False},
        'page_no': {'type': topstruct.Number, 'is_required': True},
        'page_size': {'type': topstruct.Number, 'is_required': True},
        'recommend_factor': {'type': topstruct.Number, 'is_required': False},
        'sort_type': {'type': topstruct.Number, 'is_required': False},
        'start_date': {'type': topstruct.Date, 'is_required': False},
        'user_nick': {'type': topstruct.String, 'is_required': False}
    }

    RESPONSE = {
        'posters': {'type': topstruct.Huabao, 'is_list': False}
    }

    API = 'taobao.poster.posters.search'


class WangwangEserviceAvgwaittimeGetRequest(TOPRequest):
    """ 根据客服ID和日期，获取该客服"当日接待的所有客户的平均等待时长"。  <br/>
        备注：  <br/>
        1、如果是操作者ID=被查者ID，返回被查者ID的"当日接待的所有客户的平均等待时长"。  <br/>
        2、如果操作者是组管理员，他可以查询他的组中的所有子帐号的"当日接待的所有客户的平均等待时长"。service_staff_id为所有子帐号，用 "," 隔开 <br/>
        3、如果操作者是主账户，他可以查询所有子帐号的"当日接待的所有客户的平均等待时长"。  service_staff_id为所有子帐号，用 "," 隔开<br/>
        4、被查者ID可以是多个，用 "," 隔开，id数不能超过30。  <br/>
        5、开始时间与结束时间之间的间隔不能超过7天  <br/>
        6、不能查询90天以前的数据  <br/>
        7、不能查询当天的记录

    @response waiting_time_list_on_days(WaitingTimesOnDay): 平均等待时长

    @request end_date(Date): (required)结束时间
    @request service_staff_id(String): (required)客服人员id：cntaobao+淘宝nick，例如cntaobaotest
    @request start_date(Date): (required)开始时间
    """
    REQUEST = {
        'end_date': {'type': topstruct.Date, 'is_required': True},
        'service_staff_id': {'type': topstruct.String, 'is_required': True},
        'start_date': {'type': topstruct.Date, 'is_required': True}
    }

    RESPONSE = {
        'waiting_time_list_on_days': {'type': topstruct.WaitingTimesOnDay, 'is_list': False}
    }

    API = 'taobao.wangwang.eservice.avgwaittime.get'


class WangwangEserviceChatlogGetRequest(TOPRequest):
    """ 调用前确认开通聊天记录保存到服务器的服务

    @response count(Number): 聊天记录数目。
    @response msgs(Msg): 聊天消息列表，即Msg[]，direction=0为from_id发送消息给to_id，direction=1为to_id发送消息给from_id
    @response ret(Number): 返回码：<br>
        10000:成功；<br>
        50000：时间非法，包括1)时间段超过7天,或2)起始时间距今超过30天，或3)时间格式不对；<br>
        40000：聊天用户ID不是该店铺的帐号或子帐号查询主帐号私密联系人的聊天记录；<br>
        30000：系统错误，主要是入参时间早与开通聊天记录保存到服务器的时间。包括必填参数为空等<br>

    @request end_date(String): (required)聊天消息终止时间，如2010-03-24
    @request from_id(String): (required)聊天消息被查询用户ID：cntaobao+淘宝nick，例如cntaobaotest
    @request start_date(String): (required)聊天消息起始时间，如2010-02-01
    @request to_id(String): (required)聊天消息相关方ID：cntaobao+淘宝nick，例如cntaobaotest
    """
    REQUEST = {
        'end_date': {'type': topstruct.String, 'is_required': True},
        'from_id': {'type': topstruct.String, 'is_required': True},
        'start_date': {'type': topstruct.String, 'is_required': True},
        'to_id': {'type': topstruct.String, 'is_required': True}
    }

    RESPONSE = {
        'count': {'type': topstruct.Number, 'is_list': False},
        'msgs': {'type': topstruct.Msg, 'is_list': False},
        'ret': {'type': topstruct.Number, 'is_list': False}
    }

    API = 'taobao.wangwang.eservice.chatlog.get'


class WangwangEserviceChatpeersGetRequest(TOPRequest):
    """ 获取聊天对象列表，查询时间段<=7天,只支持xml返回

    @response chatpeers(Chatpeer): 聊天对象ID列表
    @response count(Number): 成员数目。
    @response ret(Number): 返回码：
        10000:成功；
        60000：时间非法，包括1)时间段超过7天,或2)起始时间距今超过30天，或3)时间格式不对；
        50000：聊天用户ID不是该店铺的帐号；
        40000：系统错误，包括必填参数为空。

    @request charset(String): (optional)字符集
    @request chat_id(String): (required)聊天用户ID：cntaobao+淘宝nick，例如cntaobaotest
    @request end_date(String): (required)查询结束日期。如2010-03-24，与起始日期跨度不能超过7天
    @request start_date(String): (required)查询起始日期。如2010-02-01，与当前日期间隔小于1个月。
    """
    REQUEST = {
        'charset': {'type': topstruct.String, 'is_required': False},
        'chat_id': {'type': topstruct.String, 'is_required': True},
        'end_date': {'type': topstruct.String, 'is_required': True},
        'start_date': {'type': topstruct.String, 'is_required': True}
    }

    RESPONSE = {
        'chatpeers': {'type': topstruct.Chatpeer, 'is_list': False},
        'count': {'type': topstruct.Number, 'is_list': False},
        'ret': {'type': topstruct.Number, 'is_list': False}
    }

    API = 'taobao.wangwang.eservice.chatpeers.get'


class WangwangEserviceChatrecordGetRequest(TOPRequest):
    """ 该接口会返回一个聊天记录的下载地址。
        请于5分钟以后使用该链接下载(因为文件大小的不同，生成日志的时间会延长到50分钟),该链接有如下限制：<br/>
        1.该链接的有效期为3个小时，逾期作废。<br/>
        2.同一链接只能使用一次。<br/>
        用户点击地址，下载聊天记录压缩包（压缩包中含有1个文件或多个文件，查询了几个用户的聊天记录，就含有几个文本文件）<br/>
        文件格式：以不同聊天对象为单位，每段聊天记录空一行。
        <br/>
        yyyy-MM-dd HH:mm:ss NICK-a:message<br/>
        yyyy-MM-dd HH:mm:ss NICK-客服:message<br/>
        yyyy-MM-dd HH:mm:ss NICK-a:message<br/>
        <不同对象空一行>
        yyyy-MM-dd HH:mm:ss NICK-b:message<br/>
        yyyy-MM-dd HH:mm:ss NICK-b:message<br/>
        yyyy-MM-dd HH:mm:ss NICK-客服:message<br/>
        备注：<br/>
        1、如果是操作者ID=被查者ID，返回被查者ID的"聊天记录"。<br/>
        2、如果操作者是组管理员，他可以查询他的组中的所有子帐号的"聊天记录"。<br/>
        3、如果操作者是主账户，他可以查询所有子帐号的"聊天记录"。<br/>
        4、被查者ID可以是多个，用 "," 隔开，id数不能超过30。<br/>
        5、开始时间与结束时间之间的间隔不能超过7天<br/>
        6、不能查询30天以前的记录<br/>
        7、不能查询当天的数据<br/>

    @response log_file_url(String): 聊天日志文件下载url

    @request end_date(Date): (required)截止日期
    @request service_staff_id(String): (required)客服人员id：cntaobao+淘宝nick，例如cntaobaotest
    @request start_date(Date): (required)开始日期
    """
    REQUEST = {
        'end_date': {'type': topstruct.Date, 'is_required': True},
        'service_staff_id': {'type': topstruct.String, 'is_required': True},
        'start_date': {'type': topstruct.Date, 'is_required': True}
    }

    RESPONSE = {
        'log_file_url': {'type': topstruct.String, 'is_list': False}
    }

    API = 'taobao.wangwang.eservice.chatrecord.get'


class WangwangEserviceEvalsGetRequest(TOPRequest):
    """ 根据用户id查询用户对应的评价详细情况，
        主账号id可以查询店铺内子账号的评价
        组管理员可以查询组内账号的评价
        非管理员的子账号可以查自己的评价

    @response result_code(Number): 0表示成功
    @response result_count(Number): 总条数
    @response staff_eval_details(EvalDetail): 评价具体数据

    @request end_date(Date): (required)结束时间
    @request service_staff_id(String): (required)想要查询的账号列表
    @request start_date(Date): (required)开始时间
    """
    REQUEST = {
        'end_date': {'type': topstruct.Date, 'is_required': True},
        'service_staff_id': {'type': topstruct.String, 'is_required': True},
        'start_date': {'type': topstruct.Date, 'is_required': True}
    }

    RESPONSE = {
        'result_code': {'type': topstruct.Number, 'is_list': False},
        'result_count': {'type': topstruct.Number, 'is_list': False},
        'staff_eval_details': {'type': topstruct.EvalDetail, 'is_list': False}
    }

    API = 'taobao.wangwang.eservice.evals.get'


class WangwangEserviceEvaluationGetRequest(TOPRequest):
    """ 根据操作者ID，返回被查者ID指定日期内每个帐号每日的"客服评价统计"
        备注：1、如果是操作者ID=被查者ID，返回被查者ID的"客服评价统计"。
        2、如果操作者是组管理员，他可以查询他的组中的所有子帐号的"客服评价统计"。
        3、如果操作者是主账户，他可以查询所有子帐号的"客服评价统计"。
        4、被查者ID可以是多个，用 "," 隔开，id数不能超过30。
        5、开始时间与结束时间之间的间隔不能超过7天
        6、不能查询90天以前的数据
        7、不能查询当天的记录

    @response staff_eval_stat_on_days(StaffEvalStatOnDay): 客服平均统计列表

    @request end_date(Date): (required)查询结束日期
    @request service_staff_id(String): (required)客服人员id：cntaobao+淘宝nick，例如cntaobaotest
    @request start_date(Date): (required)查询开始日期
    """
    REQUEST = {
        'end_date': {'type': topstruct.Date, 'is_required': True},
        'service_staff_id': {'type': topstruct.String, 'is_required': True},
        'start_date': {'type': topstruct.Date, 'is_required': True}
    }

    RESPONSE = {
        'staff_eval_stat_on_days': {'type': topstruct.StaffEvalStatOnDay, 'is_list': False}
    }

    API = 'taobao.wangwang.eservice.evaluation.get'


class WangwangEserviceGroupmemberGetRequest(TOPRequest):
    """ 用某个组管理员账号查询，返回该组组名、和该组所有组成员ID（E客服的分流设置）。
        用旺旺主帐号查询，返回所有组的组名和该组所有组成员ID。
        返回的组成员ID可以是多个，用 "," 隔开。
        被查者ID只能传入一个。
        组成员中排名最靠前的ID是组管理员ID

    @response group_member_list(GroupMember): 组及其成员列表

    @request manager_id(String): (required)被查询用户组管理员ID：cntaobao+淘宝nick，例如cntaobaotest
    """
    REQUEST = {
        'manager_id': {'type': topstruct.String, 'is_required': True}
    }

    RESPONSE = {
        'group_member_list': {'type': topstruct.GroupMember, 'is_list': False}
    }

    API = 'taobao.wangwang.eservice.groupmember.get'


class WangwangEserviceLoginlogsGetRequest(TOPRequest):
    """ 通过用户id查询用户自己或者子账户的登录日志：
        主账号可以查询自己和店铺子账户的登录日志（查询时需要输入子账号，多个用，隔开）
        组管理员可以查询自己和组内子账号的登录日志（查询时需要输入子账号，多个用，隔开）
        非组管理员的子账户只能查询自己的登录日志

    @response count(Number): 在指定时间段登录日志的条数
    @response loginlogs(LoginLog): 登录日志具体信息
    @response user_id(String): 被查询的用户id

    @request end_date(Date): (required)查询登录日志的结束时间，必须按示例的格式，否则会返回错误
    @request service_staff_id(String): (required)需要查询登录日志的账号列表
    @request start_date(Date): (required)查询登录日志的开始日期，必须按示例的格式，否则会返回错误
    """
    REQUEST = {
        'end_date': {'type': topstruct.Date, 'is_required': True},
        'service_staff_id': {'type': topstruct.String, 'is_required': True},
        'start_date': {'type': topstruct.Date, 'is_required': True}
    }

    RESPONSE = {
        'count': {'type': topstruct.Number, 'is_list': False},
        'loginlogs': {'type': topstruct.LoginLog, 'is_list': False},
        'user_id': {'type': topstruct.String, 'is_list': False}
    }

    API = 'taobao.wangwang.eservice.loginlogs.get'


class WangwangEserviceNoreplynumGetRequest(TOPRequest):
    """ 根据操作者ID，返回被查者ID指定日期内每个帐号每日的"未回复情况"
        备注：1、如果是操作者ID=被查者ID，返回被查者ID的"未回复情况"（未回复人数、未回复的ID）。
        2、如果操作者是组管理员，他可以查询他的组中的所有子帐号的"未回复情况"。
        3、如果操作者是主账户，他可以查询所有子帐号的"未回复情况"。
        4、被查者ID可以是多个，用 "," 隔开，id数不能超过30。
        5、开始时间与结束时间之间的间隔不能超过7天
        6、不能查询90天以前的数据
        7、不能查询当天的记录

    @response non_reply_stat_on_days(NonReplyStatOnDay): 未回复统计列表

    @request end_date(Date): (required)结束日期
    @request service_staff_id(String): (required)客服人员id：cntaobao+淘宝nick，例如cntaobaotest
    @request start_date(Date): (required)开始日期
    """
    REQUEST = {
        'end_date': {'type': topstruct.Date, 'is_required': True},
        'service_staff_id': {'type': topstruct.String, 'is_required': True},
        'start_date': {'type': topstruct.Date, 'is_required': True}
    }

    RESPONSE = {
        'non_reply_stat_on_days': {'type': topstruct.NonReplyStatOnDay, 'is_list': False}
    }

    API = 'taobao.wangwang.eservice.noreplynum.get'


class WangwangEserviceOnlinetimeGetRequest(TOPRequest):
    """ 描述：根据客服ID和日期，获取该客服"当日在线时长"。
        备注：1、如果是操作者ID=被查者ID，返回被查者ID的"当日在线时长"。
        2、如果操作者是组管理员，他可以查询他的组中的所有子帐号的"当日在线时长"。
        3、如果操作者是主账户，他可以查询所有子帐号的"当日在线时长"。
        4、被查者ID可以是多个，用 "," 隔开，id数不能超过30。
        5、日累计在线时长定义：当日该用户累计的旺旺在线时长
        6、开始时间与结束时间之间的间隔不能超过7天
        7、不能查询90天以前的数据
        8、不能查询当天的记录

    @response online_times_list_on_days(OnlineTimesOnDay): 客服在线时长（按天统计，排列）

    @request end_date(Date): (required)结束日期
    @request service_staff_id(String): (required)客服人员id：cntaobao+淘宝nick，例如cntaobaotest
    @request start_date(Date): (required)开始日期
    """
    REQUEST = {
        'end_date': {'type': topstruct.Date, 'is_required': True},
        'service_staff_id': {'type': topstruct.String, 'is_required': True},
        'start_date': {'type': topstruct.Date, 'is_required': True}
    }

    RESPONSE = {
        'online_times_list_on_days': {'type': topstruct.OnlineTimesOnDay, 'is_list': False}
    }

    API = 'taobao.wangwang.eservice.onlinetime.get'


class WangwangEserviceReceivenumGetRequest(TOPRequest):
    """ 根据操作者ID，返回被查者ID指定时间段内每个帐号的"已接待人数"<br/>
        备注：<br/>
        1、如果是操作者ID=被查者ID，返回被查者ID的"已接待人数"。<br/>
        2、如果操作者是组管理员，他可以查询他的组中的所有子帐号的"已接待人数"。<br/>
        3、如果操作者是主账户，他可以查询所有子帐号的"已接待人数"。<br/>
        （注意：这里说的是授权是主帐号，可以查询所有子帐号的数据，具体要查询哪些子账号的数据，需要在service_staff_id具体指定，而不是service_staff_id直接输入主帐号）<br/>
        4、被查者ID可以是多个，用 "," 隔开，id数不能超过30。<br/>
        5、规则：某客服在1天内和同一个客户交流了多次，已回复人数算1。<br/>
        6、"已接待人数"定义：买家、卖家彼此发过至少1条消息 ，不论谁先发都可以。<br/>
        7、被查者ID可以是多个，用 "," 隔开，id数不能超过30。<br/>
        8、开始时间与结束时间之间的间隔不能超过7天<br/>
        9、不能查询90天以前的数据<br/>
        10、不能查询当天的记录<br/>
        11、查询日期精确到日<br/>

    @response reply_stat_list_on_days(ReplyStatOnDay): 客服回复列表，按天统计，排列

    @request end_date(Date): (required)查询接待人数的结束日期 时间精确到日 时分秒可以直接传00:00:00
    @request service_staff_id(String): (required)客服人员id：cntaobao+淘宝nick，例如cntaobaotest
    @request start_date(Date): (required)查询接待人数的开始日期 时间精确到日 时分秒可直接传 00:00:00
    """
    REQUEST = {
        'end_date': {'type': topstruct.Date, 'is_required': True},
        'service_staff_id': {'type': topstruct.String, 'is_required': True},
        'start_date': {'type': topstruct.Date, 'is_required': True}
    }

    RESPONSE = {
        'reply_stat_list_on_days': {'type': topstruct.ReplyStatOnDay, 'is_list': False}
    }

    API = 'taobao.wangwang.eservice.receivenum.get'


class WangwangEserviceStreamweigthsGetRequest(TOPRequest):
    """ 获取当前登录用户自己的店铺内的分流权重设置

    @response result_code(Number): 0表示返回正确
    @response result_count(Number): 返回数据条数
    @response staff_stream_weights(StreamWeight): 分流权重数据
    @response total_weight(Number): 返回数据的总权重，返回数据为空的时候没有这个数字
    """
    REQUEST = {}

    RESPONSE = {
        'result_code': {'type': topstruct.Number, 'is_list': False},
        'result_count': {'type': topstruct.Number, 'is_list': False},
        'staff_stream_weights': {'type': topstruct.StreamWeight, 'is_list': False},
        'total_weight': {'type': topstruct.Number, 'is_list': False}
    }

    API = 'taobao.wangwang.eservice.streamweigths.get'


class TaobaokeCaturlGetRequest(TOPRequest):
    """ 淘宝客类目推广URL

    @response taobaoke_item(TaobaokeItem): 只返回taobaoke_cat_click_url

    @request cid(Number): (required)类目id.注意：这里的类目id是淘宝后台发布商品的类目id.
    @request nick(String): (special)推广者的淘宝会员昵称.注：这里指的是淘宝的登录会员名
    @request outer_code(String): (optional)自定义输入串.格式:英文和数字组成;长度不能大于12个字符,区分不同的推广渠道,如:bbs,表示bbs为推广渠道;blog,表示blog为推广渠道.
    @request pid(Number): (special)淘客用户的pid,用于生成点击串.nick和pid都传入的话,以pid为准
    @request q(String): (optional)关键词
    """
    REQUEST = {
        'cid': {'type': topstruct.Number, 'is_required': True},
        'nick': {'type': topstruct.String, 'is_required': False},
        'outer_code': {'type': topstruct.String, 'is_required': False},
        'pid': {'type': topstruct.Number, 'is_required': False},
        'q': {'type': topstruct.String, 'is_required': False}
    }

    RESPONSE = {
        'taobaoke_item': {'type': topstruct.TaobaokeItem, 'is_list': False}
    }

    API = 'taobao.taobaoke.caturl.get'


class TaobaokeItemsConvertRequest(TOPRequest):
    """ 淘宝客商品转换

    @response taobaoke_items(TaobaokeItem): 淘宝客商品对象列表
    @response total_results(Number): 返回的结果总数

    @request fields(FieldList): (required)需返回的字段列表.可选值:num_iid,title,nick,pic_url,price,click_url,commission,ommission_rate,commission_num,commission_volume,shop_click_url,seller_credit_score,item_location,volume
        ;字段之间用","分隔.
    @request is_mobile(Boolean): (optional)标识一个应用是否来在无线或者手机应用,如果是true则会使用其他规则加密点击串.如果不穿值,则默认是false.
    @request nick(String): (special)推广者的淘宝会员昵称.注：指的是淘宝的会员登录名
    @request num_iids(Number): (required)淘宝客商品数字id串.最大输入40个.格式如:"value1,value2,value3" 用" , "号分隔商品数字id
    @request outer_code(String): (optional)自定义输入串.格式:英文和数字组成;长度不能大于12个字符,区分不同的推广渠道,如:bbs,表示bbs为推广渠道;blog,表示blog为推广渠道.
    @request pid(Number): (special)淘客用户的pid,用于生成点击串.nick和pid都传入的话,以pid为准
    """
    REQUEST = {
        'fields': {'type': topstruct.FieldList, 'is_required': True, 'optional': topstruct.Set({'ommission_rate', 'num_iid', 'commission', 'seller_credit_score', 'shop_click_url', 'title', 'volume', 'commission_volume', 'nick', 'commission_num', 'price', 'pic_url', 'click_url', 'item_location'})},
        'is_mobile': {'type': topstruct.Boolean, 'is_required': False},
        'nick': {'type': topstruct.String, 'is_required': False},
        'num_iids': {'type': topstruct.Number, 'is_required': True},
        'outer_code': {'type': topstruct.String, 'is_required': False},
        'pid': {'type': topstruct.Number, 'is_required': False}
    }

    RESPONSE = {
        'taobaoke_items': {'type': topstruct.TaobaokeItem, 'is_list': False},
        'total_results': {'type': topstruct.Number, 'is_list': False}
    }

    API = 'taobao.taobaoke.items.convert'


class TaobaokeItemsDetailGetRequest(TOPRequest):
    """ 查询淘宝客推广商品详细信息

    @response taobaoke_item_details(TaobaokeItemDetail): 淘宝客商品对象列表
    @response total_results(Number): 搜索到符合条件的结果总数

    @request fields(FieldList): (required)需返回的字段列表.可选值:TaobaokeItemDetail淘宝客商品结构体中的所有字段;字段之间用","分隔。item_detail需要设置到Item模型下的字段,如设置:num_iid,detail_url等; 只设置item_detail,则不返回的Item下的所有信息.注：item结构中的skus、videos、props_name不返回
    @request nick(String): (special)淘宝用户昵称，注：指的是淘宝的会员登录名.如果昵称错误,那么客户就收不到佣金.每个淘宝昵称都对应于一个pid，在这里输入要结算佣金的淘宝昵称，当推广的商品成功后，佣金会打入此输入的淘宝昵称的账户。具体的信息可以登入阿里妈妈的网站查看.
    @request num_iids(Number): (required)淘宝客商品数字id串.最大输入10个.格式如:"value1,value2,value3" 用" , "号分隔商品id.
    @request outer_code(String): (optional)自定义输入串.格式:英文和数字组成;长度不能大于12个字符,区分不同的推广渠道,如:bbs,表示bbs为推广渠道;blog,表示blog为推广渠道.
    @request pid(Number): (special)淘客用户的pid,用于生成点击串.nick和pid都传入的话,以pid为准
    """
    REQUEST = {
        'fields': {'type': topstruct.FieldList, 'is_required': True, 'optional': topstruct.Set({'seller_credit_score', 'click_url', 'shop_click_url', 'item'})},
        'nick': {'type': topstruct.String, 'is_required': False},
        'num_iids': {'type': topstruct.Number, 'is_required': True},
        'outer_code': {'type': topstruct.String, 'is_required': False},
        'pid': {'type': topstruct.Number, 'is_required': False}
    }

    RESPONSE = {
        'taobaoke_item_details': {'type': topstruct.TaobaokeItemDetail, 'is_list': False},
        'total_results': {'type': topstruct.Number, 'is_list': False}
    }

    API = 'taobao.taobaoke.items.detail.get'


class TaobaokeItemsGetRequest(TOPRequest):
    """ 查询淘宝客推广商品,不能通过设置cid=0来查询

    @response taobaoke_items(TaobaokeItem): 淘宝客商品对象列表.不返回taobaoke_cat_click_url和keyword_click_url两个字段。
    @response total_results(Number): 搜索到符合条件的结果总数

    @request area(String): (optional)商品所在地
    @request auto_send(String): (optional)是否自动发货
    @request cash_coupon(String): (optional)是否支持抵价券，设置为true表示该商品支持抵价券，设置为false或不设置表示不判断这个属性
    @request cash_ondelivery(String): (optional)是否支持货到付款，设置为true表示该商品是支持货到付款，设置为false或不设置表示不判断这个属性
    @request cid(Number): (special)商品所属分类id
    @request end_commissionNum(String): (optional)最高累计推广佣金选项
    @request end_commissionRate(String): (optional)最高佣金比率选项，如：2345表示23.45%。注：要起始佣金比率和最高佣金比率一起设置才有效。
    @request end_credit(String): (optional)可选值和start_credit一样.start_credit的值一定要小于或等于end_credit的值。注：end_credit与start_credit一起使用才生效
    @request end_price(String): (optional)最高价格
    @request end_totalnum(String): (optional)累计推广量范围结束
    @request fields(FieldList): (required)需返回的字段列表.可选值:num_iid,title,nick,pic_url,price,click_url,commission,commission_rate,commission_num,commission_volume,shop_click_url,seller_credit_score,item_location,volume
        ;字段之间用","分隔
    @request guarantee(String): (optional)是否查询消保卖家
    @request is_mobile(Boolean): (optional)标识一个应用是否来在无线或者手机应用,如果是true则会使用其他规则加密点击串.如果不穿值,则默认是false.
    @request keyword(String): (special)商品标题中包含的关键字. 注意:查询时keyword,cid至少选择其中一个参数
    @request mall_item(String): (optional)是否商城的商品，设置为true表示该商品是属于淘宝商城的商品，设置为false或不设置表示不判断这个属性
    @request nick(String): (special)淘宝用户昵称，注：指的是淘宝的会员登录名.如果昵称错误,那么客户就收不到佣金.每个淘宝昵称都对应于一个pid，在这里输入要结算佣金的淘宝昵称，当推广的商品成功后，佣金会打入此输入的淘宝昵称的账户。具体的信息可以登入阿里妈妈的网站查看.
        <font color="red">注意nick和pid至少需要传递一个,如果2个都传了,将以pid为准</font>
    @request onemonth_repair(String): (optional)是否30天维修，设置为true表示该商品是支持30天维修，设置为false或不设置表示不判断这个属性
    @request outer_code(String): (optional)自定义输入串.格式:英文和数字组成;长度不能大于12个字符,区分不同的推广渠道,如:bbs,表示bbs为推广渠道;blog,表示blog为推广渠道.
    @request overseas_item(String): (optional)是否海外商品，设置为true表示该商品是属于海外商品，默认为false
    @request page_no(Number): (optional)结果页数.1~99
    @request page_size(Number): (optional)每页返回结果数.最大每页40
    @request pid(String): (special)用户的pid,必须是mm_xxxx_0_0这种格式中间的"xxxx".
        <font color="red">注意nick和pid至少需要传递一个,如果2个都传了,将以pid为准,且pid的最大长度是20</font>
    @request real_describe(String): (optional)是否如实描述(即:先行赔付)商品，设置为true表示该商品是如实描述的商品，设置为false或不设置表示不判断这个属性
    @request sevendays_return(String): (optional)是否支持7天退换，设置为true表示该商品支持7天退换，设置为false或不设置表示不判断这个属性
    @request sort(String): (optional)默认排序:default
        price_desc(价格从高到低)
        price_asc(价格从低到高)
        credit_desc(信用等级从高到低)
        commissionRate_desc(佣金比率从高到低)
        commissionRate_asc(佣金比率从低到高)
        commissionNum_desc(成交量成高到低)
        commissionNum_asc(成交量从低到高)
        commissionVolume_desc(总支出佣金从高到低)
        commissionVolume_asc(总支出佣金从低到高)
        delistTime_desc(商品下架时间从高到低)
        delistTime_asc(商品下架时间从低到高)
    @request start_commissionNum(String): (optional)起始累计推广量佣金.注：返回的数据是30天内累计推广量，具该字段要与最高累计推广量一起使用才生效
    @request start_commissionRate(String): (optional)起始佣金比率选项，如：1234表示12.34%
    @request start_credit(String): (optional)卖家信用:
        1heart(一心)
        2heart (两心)
        3heart(三心)
        4heart(四心)
        5heart(五心)
        1diamond(一钻)
        2diamond(两钻)
        3diamond(三钻)
        4diamond(四钻)
        5diamond(五钻)
        1crown(一冠)
        2crown(两冠)
        3crown(三冠)
        4crown(四冠)
        5crown(五冠)
        1goldencrown(一黄冠)
        2goldencrown(二黄冠)
        3goldencrown(三黄冠)
        4goldencrown(四黄冠)
        5goldencrown(五黄冠)
    @request start_price(String): (optional)起始价格.传入价格参数时,需注意起始价格和最高价格必须一起传入,并且 start_price <= end_price
    @request start_totalnum(String): (optional)累计推广量范围开始
    @request vip_card(String): (optional)是否支持VIP卡，设置为true表示该商品支持VIP卡，设置为false或不设置表示不判断这个属性
    """
    REQUEST = {
        'area': {'type': topstruct.String, 'is_required': False},
        'auto_send': {'type': topstruct.String, 'is_required': False},
        'cash_coupon': {'type': topstruct.String, 'is_required': False},
        'cash_ondelivery': {'type': topstruct.String, 'is_required': False},
        'cid': {'type': topstruct.Number, 'is_required': False},
        'end_commissionNum': {'type': topstruct.String, 'is_required': False},
        'end_commissionRate': {'type': topstruct.String, 'is_required': False},
        'end_credit': {'type': topstruct.String, 'is_required': False},
        'end_price': {'type': topstruct.String, 'is_required': False},
        'end_totalnum': {'type': topstruct.String, 'is_required': False},
        'fields': {'type': topstruct.FieldList, 'is_required': True, 'optional': topstruct.Set({'seller_credit_score', 'num_iid', 'commission', 'commission_rate', 'shop_click_url', 'title', 'volume', 'commission_volume', 'nick', 'commission_num', 'price', 'pic_url', 'click_url', 'item_location'})},
        'guarantee': {'type': topstruct.String, 'is_required': False},
        'is_mobile': {'type': topstruct.Boolean, 'is_required': False},
        'keyword': {'type': topstruct.String, 'is_required': False},
        'mall_item': {'type': topstruct.String, 'is_required': False},
        'nick': {'type': topstruct.String, 'is_required': False},
        'onemonth_repair': {'type': topstruct.String, 'is_required': False},
        'outer_code': {'type': topstruct.String, 'is_required': False},
        'overseas_item': {'type': topstruct.String, 'is_required': False},
        'page_no': {'type': topstruct.Number, 'is_required': False},
        'page_size': {'type': topstruct.Number, 'is_required': False},
        'pid': {'type': topstruct.String, 'is_required': False},
        'real_describe': {'type': topstruct.String, 'is_required': False},
        'sevendays_return': {'type': topstruct.String, 'is_required': False},
        'sort': {'type': topstruct.String, 'is_required': False},
        'start_commissionNum': {'type': topstruct.String, 'is_required': False},
        'start_commissionRate': {'type': topstruct.String, 'is_required': False},
        'start_credit': {'type': topstruct.String, 'is_required': False},
        'start_price': {'type': topstruct.String, 'is_required': False},
        'start_totalnum': {'type': topstruct.String, 'is_required': False},
        'vip_card': {'type': topstruct.String, 'is_required': False}
    }

    RESPONSE = {
        'taobaoke_items': {'type': topstruct.TaobaokeItem, 'is_list': False},
        'total_results': {'type': topstruct.Number, 'is_list': False}
    }

    API = 'taobao.taobaoke.items.get'


class TaobaokeListurlGetRequest(TOPRequest):
    """ 淘宝客关键词搜索URL

    @response taobaoke_item(TaobaokeItem): 只返回keyword_click_url

    @request nick(String): (special)推广者的淘宝会员昵称.注：这里指的是淘宝的登录会员名
    @request outer_code(String): (optional)自定义输入串.格式:英文和数字组成;长度不能大于12个字符,区分不同的推广渠道,如:bbs,表示bbs为推广渠道;blog,表示blog为推广渠道.
    @request pid(Number): (special)淘客用户的pid,用于生成点击串.nick和pid都传入的话,以pid为准
    @request q(String): (required)关键词
    """
    REQUEST = {
        'nick': {'type': topstruct.String, 'is_required': False},
        'outer_code': {'type': topstruct.String, 'is_required': False},
        'pid': {'type': topstruct.Number, 'is_required': False},
        'q': {'type': topstruct.String, 'is_required': True}
    }

    RESPONSE = {
        'taobaoke_item': {'type': topstruct.TaobaokeItem, 'is_list': False}
    }

    API = 'taobao.taobaoke.listurl.get'


class TaobaokeReportGetRequest(TOPRequest):
    """ 淘宝客报表查询

    @response taobaoke_report(TaobaokeReport): 淘宝客报表

    @request date(String): (required)需要查询报表的日期，有效的日期为最近3个月内的某一天，格式为:yyyyMMdd,如20090520.
    @request fields(FieldList): (required)需返回的字段列表.可选值:TaobaokeReportMember淘宝客报表成员结构体中的所有字段;字段之间用","分隔.
    @request page_no(Number): (optional)当前页数.只能获取1-499页数据.
    @request page_size(Number): (optional)每页返回结果数,默认是40条.最大每页100
    """
    REQUEST = {
        'date': {'type': topstruct.String, 'is_required': True},
        'fields': {'type': topstruct.FieldList, 'is_required': True, 'optional': topstruct.Set({'real_pay_fee', 'item_title', 'iid', 'num_iid', 'commission', 'app_key', 'outer_code', 'item_num', 'commission_rate', 'category_name', 'seller_nick', 'pay_price', 'pay_time', 'trade_id', 'category_id', 'shop_title'})},
        'page_no': {'type': topstruct.Number, 'is_required': False},
        'page_size': {'type': topstruct.Number, 'is_required': False}
    }

    RESPONSE = {
        'taobaoke_report': {'type': topstruct.TaobaokeReport, 'is_list': False}
    }

    API = 'taobao.taobaoke.report.get'


class TaobaokeShopsConvertRequest(TOPRequest):
    """ 淘宝客店铺转换

    @response taobaoke_shops(TaobaokeShop): 淘宝客店铺对象列表,不能返回shop_type,seller_credit,auction_coun,
        total_auction

    @request fields(FieldList): (required)需返回的字段列表.可选值:TaobaokeShop淘宝客商品结构体中的user_id,shop_title,click_url,commission_rate;字段之间用","分隔.
    @request nick(String): (special)推广者的淘宝会员昵称.注：这里指的是淘宝的登录会员名
    @request outer_code(String): (optional)自定义输入串.格式:英文和数字组成;长度不能大于12个字符,区分不同的推广渠道,如:bbs,表示bbs为推广渠道;blog,表示blog为推广渠道.
    @request pid(Number): (special)淘客用户的pid,用于生成点击串.nick和pid都传入的话,以pid为准<br>
        <red>注：填写pid只需要填写pid中的数字，例如：pid为mm_1234567_0_0入参的时候填写1234567</red>
    @request sids(Number): (required)店铺id串.最大输入10个.格式如:"value1,value2,value3" 用" , "号分隔店铺id.
    """
    REQUEST = {
        'fields': {'type': topstruct.FieldList, 'is_required': True, 'optional': topstruct.Set({'user_id', 'click_url', 'commission_rate', 'shop_title'})},
        'nick': {'type': topstruct.String, 'is_required': False},
        'outer_code': {'type': topstruct.String, 'is_required': False},
        'pid': {'type': topstruct.Number, 'is_required': False},
        'sids': {'type': topstruct.Number, 'is_required': True}
    }

    RESPONSE = {
        'taobaoke_shops': {'type': topstruct.TaobaokeShop, 'is_list': False}
    }

    API = 'taobao.taobaoke.shops.convert'


class TaobaokeShopsGetRequest(TOPRequest):
    """ 提供对参加了淘客推广的店铺的搜索

    @response taobaoke_shops(TaobaokeShop): 搜索结果列表
    @response total_results(Number): 符合条件的店铺总数

    @request cid(Number): (special)前台类目id
    @request end_auctioncount(String): (optional)店铺商品数查询结束值
    @request end_commissionrate(String): (optional)店铺佣金比例查询结束值
    @request end_credit(String): (optional)店铺掌柜信用等级查询结束
        店铺的信用等级总共为20级 1-5:1heart-5heart;6-10:1diamond-5diamond;11-15:1crown-5crown;16-20:1goldencrown-5goldencrown
    @request end_totalaction(String): (optional)店铺累计推广数查询结束值
    @request fields(FieldList): (required)需要返回的字段，目前包括如下字段 user_id click_url shop_title commission_rate seller_credit shop_type auction_count total_auction
    @request keyword(String): (special)店铺主题关键字查询
    @request nick(String): (special)淘宝用户昵称，注：指的是淘宝的会员登录名.如果昵称错误,那么客户就收不到佣金.每个淘宝昵称都对应于一个pid，在这里输入要结算佣金的淘宝昵称，当推广的商品成功后，佣金会打入此输入的淘宝昵称的账户。具体的信息可以登入阿里妈妈的网站查看
    @request only_mall(Boolean): (optional)是否只显示商城店铺
    @request outer_code(String): (optional)自定义输入串.格式:英文和数字组成;长度不能大于12个字符,区分不同的推广渠道,如:bbs,表示bbs为推广渠道;blog,表示blog为推广渠道.
    @request page_no(Number): (optional)页码.结果页1~99
    @request page_size(Number): (optional)每页条数.最大每页40
    @request pid(Number): (special)淘客用户的pid,用于生成点击串.nick和pid都传入的话,以pid为准
    @request start_auctioncount(String): (optional)店铺宝贝数查询开始值
    @request start_commissionrate(String): (optional)店铺佣金比例查询开始值，注意佣金比例是x10000的整数.50表示0.5%
    @request start_credit(String): (optional)店铺掌柜信用等级起始
        店铺的信用等级总共为20级 1-5:1heart-5heart;6-10:1diamond-5diamond;11-15:1crown-5crown;16-20:1goldencrown-5goldencrown
    @request start_totalaction(String): (optional)店铺累计推广量开始值
    """
    REQUEST = {
        'cid': {'type': topstruct.Number, 'is_required': False},
        'end_auctioncount': {'type': topstruct.String, 'is_required': False},
        'end_commissionrate': {'type': topstruct.String, 'is_required': False},
        'end_credit': {'type': topstruct.String, 'is_required': False},
        'end_totalaction': {'type': topstruct.String, 'is_required': False},
        'fields': {'type': topstruct.FieldList, 'is_required': True, 'optional': topstruct.Set({'shop_type', 'user_id', 'commission_rate', 'auction_count', 'seller_credit', 'total_auction', 'click_url', 'shop_title'})},
        'keyword': {'type': topstruct.String, 'is_required': False},
        'nick': {'type': topstruct.String, 'is_required': False},
        'only_mall': {'type': topstruct.Boolean, 'is_required': False},
        'outer_code': {'type': topstruct.String, 'is_required': False},
        'page_no': {'type': topstruct.Number, 'is_required': False},
        'page_size': {'type': topstruct.Number, 'is_required': False},
        'pid': {'type': topstruct.Number, 'is_required': False},
        'start_auctioncount': {'type': topstruct.String, 'is_required': False},
        'start_commissionrate': {'type': topstruct.String, 'is_required': False},
        'start_credit': {'type': topstruct.String, 'is_required': False},
        'start_totalaction': {'type': topstruct.String, 'is_required': False}
    }

    RESPONSE = {
        'taobaoke_shops': {'type': topstruct.TaobaokeShop, 'is_list': False},
        'total_results': {'type': topstruct.Number, 'is_list': False}
    }

    API = 'taobao.taobaoke.shops.get'


class TaobaokeToolRelationRequest(TOPRequest):
    """ 判断用户pid是否是appkey关联的注册用户

    @response tools_user(Boolean): 返回true或false表示是否关联用户

    @request pubid(Number): (required)用户的pubid 用来判断这个pubid是否是appkey关联的开发者的注册用户
    """
    REQUEST = {
        'pubid': {'type': topstruct.Number, 'is_required': True}
    }

    RESPONSE = {
        'tools_user': {'type': topstruct.Boolean, 'is_list': False}
    }

    API = 'taobao.taobaoke.tool.relation'


class CometDiscardinfoGetRequest(TOPRequest):
    """ 获取一个appkey的哪些用户丢失了消息

    @response discard_info_list(DiscardInfo): 丢弃消息的列表

    @request end(Date): (optional)指定截止日志，如果不传则为服务端当前时间
    @request nick(String): (optional)用户nick
    @request start(Date): (required)指定从那个时间开始找丢弃的消息
    @request types(String): (optional)指定多个消息类型
    @request user_id(Number): (optional)指定查看那个用户的丢弃消息
    """
    REQUEST = {
        'end': {'type': topstruct.Date, 'is_required': False},
        'nick': {'type': topstruct.String, 'is_required': False},
        'start': {'type': topstruct.Date, 'is_required': True},
        'types': {'type': topstruct.String, 'is_required': False},
        'user_id': {'type': topstruct.Number, 'is_required': False}
    }

    RESPONSE = {
        'discard_info_list': {'type': topstruct.DiscardInfo, 'is_list': False}
    }

    API = 'taobao.comet.discardinfo.get'


class IncrementCustomerPermitRequest(TOPRequest):
    """ 提供app为自己的用户开通增量消息服务功能

    @response app_customer(AppCustomer): 当订阅成功后，返回的订阅情况。具体内容见AppCustomer数据结构。

    @request status(String): (optional)表示与topics相对应的消息状态。各个消息主题间用";"分隔，各个状态间用","分隔，消息主题必须和topics一致。如果为all时，表示开通应用订阅的所有的消息。
        如果不填写,会默认开通应用所订阅的所有消息。
    @request topics(String): (optional)应用为用户开通的主动通知的消息主题（或消息类别），该主题必须是应用订阅的主题。如果应用未订阅该主题，则系统会自动过滤掉该主题。各个主题间用";"分隔。
        如果不填写，会默认开通应用所订阅的所有消息。
    @request type(String): (optional)用户需要开通的功能。值可为get,notify和syn分别表示增量api取消息，主动发送消息和同步数据功能。这三个值可任意无序组合。应用在为用户开通相应功能前需先订阅相应的功能；get和notify在主动通知界面中订阅，syn在mysql数据同步步界面中订阅。
        当重复开通时，只会在已经开通的功能上，开通新的功能，不会覆盖旧的开通。例如：在开通get功能后，再次开通notify功能的结果是开通了get和notify功能；而不会只开通notify功能。
        在开通时，type里面的参数会根据应用订阅的类型进行相应的过虑。如应用只订阅主动通知，则默认值过滤后为get,notify，如果应用只订阅数据同步服务，默认值过滤后为syn。
    """
    REQUEST = {
        'status': {'type': topstruct.String, 'is_required': False},
        'topics': {'type': topstruct.String, 'is_required': False},
        'type': {'type': topstruct.String, 'is_required': False}
    }

    RESPONSE = {
        'app_customer': {'type': topstruct.AppCustomer, 'is_list': False}
    }

    API = 'taobao.increment.customer.permit'


class IncrementCustomerStopRequest(TOPRequest):
    """ 供应用关闭其用户的增量消息服务功能，这样可以节省ISV的流量。

    @response is_success(Boolean): 关闭增量消息或数据同步是否成功

    @request nick(String): (required)应用要关闭增量消息服务的用户昵称
    @request type(String): (optional)应用需要关闭用户的功能。取值可为get,notify和syn分别表示增量api取消息，主动发送消息和同步数据功能。用户关闭相应功能前,需应用已为用户经开通了相应的功能。这三个参数可无序任意组合。在关闭时，type里面的参数会根据应用订阅的类型进行相应的过虑。如应用只订阅主动通知，则默认值过滤后为get,notify，如果应用只订阅数据同步服务，默认值过滤后为syn。
    """
    REQUEST = {
        'nick': {'type': topstruct.String, 'is_required': True},
        'type': {'type': topstruct.String, 'is_required': False}
    }

    RESPONSE = {
        'is_success': {'type': topstruct.Boolean, 'is_list': False}
    }

    API = 'taobao.increment.customer.stop'


class IncrementCustomersGetRequest(TOPRequest):
    """ 提供查询应用为自身用户所开通的增量消息服务信息。

    @response app_customers(AppCustomer): 查询到的用户开通信息
    @response total_results(Number): 查询到的开通增量服务的用户数

    @request fields(FieldList): (optional)需要返回的字段。可填写的字段参见AppCustomer中的返回字段。如：nick,created,status,type,subscriptions。
    @request nicks(String): (optional)查询用户的昵称。当为空时通过分页方式查询appkey开通的所有用户,最多填入20个昵称。
    @request page_no(Number): (optional)分页查询时，查询的页码。此参数只有nicks为空时起作用。
    @request page_size(Number): (optional)分布查询时，页的大小。此参数只有当nicks为空时起作用。
    @request type(String): (optional)查询用户开通的功能。值可为get,notify和syn分别表示增量api取消息，主动发送消息和同步数据功能。这三个值不分次序。在查询时，type里面的参数会根据应用订阅的类型进行相应的过虑。如应用只订阅主动通知，则默认值过滤后为get,notify，如果应用只订阅数据同步服务，默认值过滤后为syn。
    """
    REQUEST = {
        'fields': {'type': topstruct.FieldList, 'is_required': False, 'optional': topstruct.Set({'user_id', 'type', 'subscriptions', 'nick', 'created', 'status', 'modified'})},
        'nicks': {'type': topstruct.String, 'is_required': False},
        'page_no': {'type': topstruct.Number, 'is_required': False},
        'page_size': {'type': topstruct.Number, 'is_required': False},
        'type': {'type': topstruct.String, 'is_required': False}
    }

    RESPONSE = {
        'app_customers': {'type': topstruct.AppCustomer, 'is_list': False},
        'total_results': {'type': topstruct.Number, 'is_list': False}
    }

    API = 'taobao.increment.customers.get'


class IncrementItemsGetRequest(TOPRequest):
    """ 开通主动通知业务的APP可以通过该接口获取商品变更通知信息
        <font color="red">建议获取增量消息的时间间隔是：半个小时</font>

    @response notify_items(NotifyItem): None
    @response total_results(Number): 搜索到符合条件的结果总数。

    @request end_modified(Date): (optional)消息所对应的操作时间的最大值。和start_modified搭配使用能过滤消通知消息的时间段。不传时：如果设置了start_modified，默认为与start_modified同一天的23:59:59；否则默认为调用接口当天的23:59:59。（格式：yyyy-MM-dd HH:mm:ss）<br>
        <font color="red">注意：start_modified和end_modified的日期必须在必须在同一天内，比如：start_modified设置2000-01-01 00:00:00，则end_modified必须设置为2000-01-01这个日期</font>
    @request nick(String): (optional)消息所属于的用户的昵称。设置此参数，返回的消息会根据传入nick的进行过滤。自用型AppKey的昵称默认为自己的绑定昵称，此参数无效。
    @request page_no(Number): (optional)页码。取值范围:大于零的整数; 默认值:1,即返回第一页数据。
    @request page_size(Number): (optional)每页条数。取值范围:大于零的整数;最大值:200;默认值:40。
    @request start_modified(Date): (optional)消息所对应的操作时间的最小值和end_modified搭配使用能过滤消通知消息的时间段。不传时：如果设置了end_modified，默认为与 end_modified同一天的00:00:00，否则默认为调用接口当天的00:00:00。（格式：yyyy-MM-dd HH:mm:ss）<br>
        <font color="red">注意：start_modified和end_modified的日期必须在必须在同一天内，比如：start_modified设置2000-01-01 00:00:00，则end_modified必须设置为2000-01-01这个日期</font>
    @request status(String): (optional)商品操作状态，默认查询所有状态的数据，除了默认值外每次只能查询一种状态。具体类型列表见：
        ItemAdd（新增商品）
        ItemUpshelf（上架商品，自动上架商品不能获取到增量信息）
        ItemDownshelf（下架商品）
        ItemDelete（删除商品）
        ItemUpdate（更新商品）
        ItemRecommendDelete（取消橱窗推荐商品）
        ItemRecommendAdd（橱窗推荐商品）
        ItemZeroStock（商品卖空）
        ItemPunishDelete（小二删除商品）
        ItemPunishDownshelf（小二下架商品）
        ItemPunishCc（小二CC商品）
        ItemSkuZeroStock（商品SKU卖空）
        ItemStockChanged（修改商品库存）
    """
    REQUEST = {
        'end_modified': {'type': topstruct.Date, 'is_required': False},
        'nick': {'type': topstruct.String, 'is_required': False},
        'page_no': {'type': topstruct.Number, 'is_required': False},
        'page_size': {'type': topstruct.Number, 'is_required': False},
        'start_modified': {'type': topstruct.Date, 'is_required': False},
        'status': {'type': topstruct.String, 'is_required': False}
    }

    RESPONSE = {
        'notify_items': {'type': topstruct.NotifyItem, 'is_list': False},
        'total_results': {'type': topstruct.Number, 'is_list': False}
    }

    API = 'taobao.increment.items.get'


class IncrementRefundsGetRequest(TOPRequest):
    """ 开通主动通知业务的APP可以通过该接口获取用户的退款变更通知信息
        <font color="red">建议在获取增量消息的时间间隔是：半个小时</font>

    @response notify_refunds(NotifyRefund): 获取的退款通知消息体 ，具体字段见NotifyRefund数据结构
    @response total_results(Number): 搜索到符合条件的结果总数。

    @request end_modified(Date): (optional)消息所对应的操作时间的最大值。和start_modified搭配使用能过滤消通知消息的时间段。不传时：如果设置了start_modified，默认为与start_modified同一天的23:59:59；否则默认为调用接口当天的23:59:59。（格式：yyyy-MM-dd HH:mm:ss）<br>
        <font color="red">注意：start_modified和end_modified的日期必须在必须在同一天内，比如：start_modified设置2000-01-01 00:00:00，则end_modified必须设置为2000-01-01这个日期</font>
    @request nick(String): (optional)消息所属于的用户的昵称。设置此参数，返回的消息会根据传入nick的进行过滤。自用型appKey的昵称默认为自己的绑定昵称，此参数无效。
    @request page_no(Number): (optional)页码。取值范围:大于零的整数; 默认值:1,即返回第一页数据。
    @request page_size(Number): (optional)每页条数。取值范围:大于零的整数;最大值:200;默认值:40。
    @request start_modified(Date): (optional)消息所对应的操作时间的最小值。和end_modified搭配使用能过滤消通知消息的时间段。不传时：如果设置了end_modified，默认为与 end_modified同一天的00:00:00，否则默认为调用接口当天的00:00:00。（格式：yyyy-MM-dd HH:mm:ss）<br>
        <font color="red">注意：start_modified和end_modified的日期必须在必须在同一天内，比如：start_modified设置2000-01-01 00:00:00，则end_modified必须设置为2000-01-01这个日期</font>
    @request status(String): (optional)退款操作状态，默认查询所有状态的数据，除了默认值外每次只能查询一种状态。具体字段说明请见 退款消息状态
    """
    REQUEST = {
        'end_modified': {'type': topstruct.Date, 'is_required': False},
        'nick': {'type': topstruct.String, 'is_required': False},
        'page_no': {'type': topstruct.Number, 'is_required': False},
        'page_size': {'type': topstruct.Number, 'is_required': False},
        'start_modified': {'type': topstruct.Date, 'is_required': False},
        'status': {'type': topstruct.String, 'is_required': False}
    }

    RESPONSE = {
        'notify_refunds': {'type': topstruct.NotifyRefund, 'is_list': False},
        'total_results': {'type': topstruct.Number, 'is_list': False}
    }

    API = 'taobao.increment.refunds.get'


class IncrementTradesGetRequest(TOPRequest):
    """ 开通主动通知业务的APP可以通过该接口获取用户的交易和评价变更通知信息
        <font color="red">建议在获取增量消息的时间间隔是：半个小时</font>

    @response notify_trades(NotifyTrade): 获取的交易通知消息体 ，具体字段见NotifyTrade数据结构
    @response total_results(Number): 搜索到符合条件的结果总数。

    @request end_modified(Date): (optional)消息所对应的操作时间的最大值。和start_modified搭配使用能过滤消通知消息的时间段。不传时：如果设置了start_modified，默认为与start_modified同一天的23:59:59；否则默认为调用接口当天的23:59:59。（格式：yyyy-MM-dd HH:mm:ss）<br>
        <font color="red">注意：start_modified和end_modified的日期必须在必须在同一天内，比如：start_modified设置2000-01-01 00:00:00，则end_modified必须设置为2000-01-01这个日期</font>
    @request nick(String): (optional)消息所属于的用户的昵称。设置此参数，返回的消息会根据传入nick的进行过滤。自用型appKey的昵称默认为自己的绑定昵称，此参数无效。
    @request page_no(Number): (optional)页码。取值范围:大于零的整数; 默认值:1,即返回第一页数据。
    @request page_size(Number): (optional)每页条数。取值范围:大于零的整数;最大值:200;默认值:40。
    @request start_modified(Date): (optional)消息所对应的操作时间的最小值。和end_modified搭配使用能过滤消通知消息的时间段。不传时：如果设置了end_modified，默认为与end_modified同一天的00:00:00，否则默认为调用接口当天的00:00:00。（格式：yyyy-MM-dd HH:mm:ss）<br>
        <font color="red">注意：start_modified和end_modified的日期必须在必须在同一天内，比如：start_modified设置2000-01-01 00:00:00，则end_modified必须设置为2000-01-01这个日期</font>
    @request status(String): (optional)交易或评价的状态，默认查询所有状态的数据，除了默认值外每次只能查询一种状态。除了交易超时提醒消息没有type分类以外，交易的其他消息都有type分类。
        可选值
        TradeCreate（创建交易）
        TradeModifyFee（修改交易费用）
        TradeCloseAndModifyDetailOrder（关闭或修改子订单）
        TradeClose（关闭交易）
        TradeBuyerPay（买家付款）
        TradeSellerShip（卖家发货）
        TradeDelayConfirmPay（延长收货时间）
        TradePartlyRefund（子订单退款成功）
        TradePartlyConfirmPay（子订单打款成功）
        TradeSuccess（交易成功）
        TradeTimeoutRemind（交易超时提醒）
        TradeRated（交易评价变更）
        TradeMemoModified（交易备注修改）
        TradeLogisticsAddressChanged（修改交易收货地址）
        TradeChanged（修改订单信息（SKU等））
    @request type(String): (optional)交易所属的类型，默认查询所有类型的数据，除了默认值外每次只能查询一种类型。交易超时提醒类型的消息没有消息类型，固定返回“timeout”。
        可选值：
        ec（直冲）
        guarantee_trade（一口价、拍卖）
        auto_delivery（自动发货）
        cod（货到付款）
        independent_shop_trade（旺店标准版交易）
        independent_simple_trade（旺店入门版交易）
        shopex_trade（ShopEX版)
        netcn_trade（淘宝与万网合作版网）
        travel（旅游产品交易）
        fenxiao（分销平台交易）
        game_equipment（网游虚拟交易）
    """
    REQUEST = {
        'end_modified': {'type': topstruct.Date, 'is_required': False},
        'nick': {'type': topstruct.String, 'is_required': False},
        'page_no': {'type': topstruct.Number, 'is_required': False},
        'page_size': {'type': topstruct.Number, 'is_required': False},
        'start_modified': {'type': topstruct.Date, 'is_required': False},
        'status': {'type': topstruct.String, 'is_required': False},
        'type': {'type': topstruct.String, 'is_required': False}
    }

    RESPONSE = {
        'notify_trades': {'type': topstruct.NotifyTrade, 'is_list': False},
        'total_results': {'type': topstruct.Number, 'is_list': False}
    }

    API = 'taobao.increment.trades.get'


class KfcKeywordSearchRequest(TOPRequest):
    """ 对输入的文本信息进行禁忌关键词匹配，返回匹配的结果

    @response kfc_search_result(KfcSearchResult): KFC关键词匹配返回的结果信息

    @request apply(String): (optional)应用点，分为一级应用点、二级应用点。其中一级应用点通常是指某一个系统或产品，比如淘宝的商品应用（taobao_auction）；二级应用点，是指一级应用点下的具体的分类，比如商品标题(title)、商品描述(content)。不同的二级应用可以设置不同关键词。
        这里的apply参数是由一级应用点与二级应用点合起来的字符（一级应用点+"."+二级应用点），如taobao_auction.title。
        通常apply参数是不需要传递的。如有特殊需求（比如特殊的过滤需求，需要自己维护一套自己词库），需传递此参数。
    @request content(String): (required)需要过滤的文本信息
    @request nick(String): (optional)发布信息的淘宝会员名，可以不传
    """
    REQUEST = {
        'apply': {'type': topstruct.String, 'is_required': False},
        'content': {'type': topstruct.String, 'is_required': True},
        'nick': {'type': topstruct.String, 'is_required': False}
    }

    RESPONSE = {
        'kfc_search_result': {'type': topstruct.KfcSearchResult, 'is_list': False}
    }

    API = 'taobao.kfc.keyword.search'


class TimeGetRequest(TOPRequest):
    """ 获取淘宝系统当前时间

    @response time(Date): 淘宝系统当前时间。格式:yyyy-MM-dd HH:mm:ss
    """
    REQUEST = {}

    RESPONSE = {
        'time': {'type': topstruct.Date, 'is_list': False}
    }

    API = 'taobao.time.get'


class TopatsResultGetRequest(TOPRequest):
    """ 使用指南：http://open.taobao.com/doc/detail.htm?id=30
        1.此接口用于获取异步任务处理的结果，传入的task_id必需属于当前的appKey才可以
        2.此接口只返回执行完成的任务结果，未执行完的返回结果里面不包含任务结果，只有任务id，执行状态
        3.执行完成的每个task的子任务结果内容与单个任务的结果结构一致。如：taobao.topats.trades.fullinfo.get返回的子任务结果就会是Trade的结构体。

    @response task(Task): 返回任务处理信息

    @request task_id(Number): (required)任务id号，创建任务时返回的task_id
    """
    REQUEST = {
        'task_id': {'type': topstruct.Number, 'is_required': True}
    }

    RESPONSE = {
        'task': {'type': topstruct.Task, 'is_list': False}
    }

    API = 'taobao.topats.result.get'


class TopatsTaskDeleteRequest(TOPRequest):
    """ 可用于取消已经创建的ATS任务。</br>
        条件限制：1)一次只可以取消一个任务</br>
        2）只能取消自己创建的任务</br>

    @response is_success(Boolean): 表示操作是否成功，是为true，否为false。

    @request task_id(Number): (required)需要取消的任务ID
    """
    REQUEST = {
        'task_id': {'type': topstruct.Number, 'is_required': True}
    }

    RESPONSE = {
        'is_success': {'type': topstruct.Boolean, 'is_list': False}
    }

    API = 'taobao.topats.task.delete'


class TopatsTasksGetRequest(TOPRequest):
    """ 用于获取指定时间段内的定时API任务信息。</br>
        条件：1）必须是本APPKEY创建的任务。</br>
        2)起始时间不能早于3天前的当前时刻。</br>
        3）结束时间不能晚于一天以后的当前时刻。</br>

    @response tasks(Task): 符合查询条件内的定时任务的结果集

    @request end_time(Date): (required)要查询的已经创建的定时任务的结束时间(这里的时间是指执行时间)。
    @request start_time(Date): (required)要查询的已创建过的定时任务的开始时间(这里的时间是指执行时间)。
    """
    REQUEST = {
        'end_time': {'type': topstruct.Date, 'is_required': True},
        'start_time': {'type': topstruct.Date, 'is_required': True}
    }

    RESPONSE = {
        'tasks': {'type': topstruct.Task, 'is_list': False}
    }

    API = 'taobao.topats.tasks.get'


class WlbInventoryDetailGetRequest(TOPRequest):
    """ 查询库存详情，通过商品ID获取发送请求的卖家的库存详情

    @response inventory_list(WlbInventory): 库存详情列表
    @response item_id(Number): 商品ID

    @request inventory_type_list(String): (optional)库存类型列表，值包括：
        VENDIBLE--可销售库存
        FREEZE--冻结库存
        ONWAY--在途库存
        DEFECT--残次品库存
        ENGINE_DAMAGE--机损
        BOX_DAMAGE--箱损
    @request item_id(Number): (required)商品ID
    @request store_code(String): (optional)仓库编码
    """
    REQUEST = {
        'inventory_type_list': {'type': topstruct.String, 'is_required': False},
        'item_id': {'type': topstruct.Number, 'is_required': True},
        'store_code': {'type': topstruct.String, 'is_required': False}
    }

    RESPONSE = {
        'inventory_list': {'type': topstruct.WlbInventory, 'is_list': False},
        'item_id': {'type': topstruct.Number, 'is_list': False}
    }

    API = 'taobao.wlb.inventory.detail.get'


class WlbInventorySyncRequest(TOPRequest):
    """ 将库存同步至IC

    @response gmt_modified(Date): 修改时间

    @request item_id(Number): (required)商品ID
    @request item_type(String): (required)外部实体类型.存如下值
        IC_ITEM --表示IC商品;
        IC_SKU --表示IC最小单位商品;
        WLB_ITEM  --表示WLB商品.
        若值不在范围内，则按WLB_ITEM处理
    @request quantity(Number): (required)库存数量
    """
    REQUEST = {
        'item_id': {'type': topstruct.Number, 'is_required': True},
        'item_type': {'type': topstruct.String, 'is_required': True},
        'quantity': {'type': topstruct.Number, 'is_required': True}
    }

    RESPONSE = {
        'gmt_modified': {'type': topstruct.Date, 'is_list': False}
    }

    API = 'taobao.wlb.inventory.sync'


class WlbInventorylogQueryRequest(TOPRequest):
    """ 通过商品ID等几个条件来分页查询库存变更记录

    @response inventory_log_list(WlbItemInventoryLog): 库存变更记录列表
    @response total_count(Number): 记录数

    @request gmt_end(Date): (optional)结束修改时间,小于等于该时间
    @request gmt_start(Date): (optional)起始修改时间,大于等于该时间
    @request item_id(Number): (optional)商品ID
    @request op_type(String): (optional)库存操作作类型(可以为空)
        CHU_KU 1-出库
        RU_KU 2-入库
        FREEZE 3-冻结
        THAW 4-解冻
        CHECK_FREEZE 5-冻结确认
        CHANGE_KU 6-库存类型变更
        若值不在范围内，则按CHU_KU处理
    @request op_user_id(Number): (optional)可指定授权的用户来查询
    @request order_code(String): (optional)单号
    @request page_no(Number): (optional)当前页
    @request page_size(Number): (optional)分页记录个数
    @request store_code(String): (optional)仓库编码
    """
    REQUEST = {
        'gmt_end': {'type': topstruct.Date, 'is_required': False},
        'gmt_start': {'type': topstruct.Date, 'is_required': False},
        'item_id': {'type': topstruct.Number, 'is_required': False},
        'op_type': {'type': topstruct.String, 'is_required': False},
        'op_user_id': {'type': topstruct.Number, 'is_required': False},
        'order_code': {'type': topstruct.String, 'is_required': False},
        'page_no': {'type': topstruct.Number, 'is_required': False},
        'page_size': {'type': topstruct.Number, 'is_required': False},
        'store_code': {'type': topstruct.String, 'is_required': False}
    }

    RESPONSE = {
        'inventory_log_list': {'type': topstruct.WlbItemInventoryLog, 'is_list': False},
        'total_count': {'type': topstruct.Number, 'is_list': False}
    }

    API = 'taobao.wlb.inventorylog.query'


class WlbItemAddRequest(TOPRequest):
    """ 添加物流宝商品，支持物流宝子商品和属性添加

    @response item_id(Number): 新增的商品

    @request color(String): (optional)商品颜色
    @request goods_cat(String): (optional)货类
    @request height(Number): (optional)商品高度，单位毫米
    @request is_dangerous(Boolean): (optional)是否危险品
    @request is_friable(Boolean): (optional)是否易碎品
    @request is_sku(String): (required)是否sku
    @request item_code(String): (required)商品编码
    @request length(Number): (optional)商品长度，单位毫米
    @request name(String): (required)商品名称
    @request package_material(String): (optional)商品包装材料类型
    @request price(Number): (optional)商品价格，单位：分
    @request pricing_cat(String): (optional)计价货类
    @request pro_name_list(FieldList): (optional)属性名列表,目前支持的属性：
        毛重:GWeight
        净重:Nweight
        皮重: Tweight
        自定义属性：
        paramkey1
        paramkey2
        paramkey3
        paramkey4
    @request pro_value_list(FieldList): (optional)属性值列表：
        10,8
    @request remark(String): (optional)商品备注
    @request support_batch(Boolean): (optional)是否支持批次
    @request title(String): (optional)商品标题
    @request type(String): (optional)NORMAL--普通商品
        COMBINE--组合商品
        DISTRIBUTION--分销
    @request volume(Number): (optional)商品体积，单位立方厘米
    @request weight(Number): (optional)商品重量，单位G
    @request width(Number): (optional)商品宽度，单位毫米
    """
    REQUEST = {
        'color': {'type': topstruct.String, 'is_required': False},
        'goods_cat': {'type': topstruct.String, 'is_required': False},
        'height': {'type': topstruct.Number, 'is_required': False},
        'is_dangerous': {'type': topstruct.Boolean, 'is_required': False},
        'is_friable': {'type': topstruct.Boolean, 'is_required': False},
        'is_sku': {'type': topstruct.String, 'is_required': True},
        'item_code': {'type': topstruct.String, 'is_required': True},
        'length': {'type': topstruct.Number, 'is_required': False},
        'name': {'type': topstruct.String, 'is_required': True},
        'package_material': {'type': topstruct.String, 'is_required': False},
        'price': {'type': topstruct.Number, 'is_required': False},
        'pricing_cat': {'type': topstruct.String, 'is_required': False},
        'pro_name_list': {'type': topstruct.FieldList, 'is_required': False},
        'pro_value_list': {'type': topstruct.FieldList, 'is_required': False},
        'remark': {'type': topstruct.String, 'is_required': False},
        'support_batch': {'type': topstruct.Boolean, 'is_required': False},
        'title': {'type': topstruct.String, 'is_required': False},
        'type': {'type': topstruct.String, 'is_required': False},
        'volume': {'type': topstruct.Number, 'is_required': False},
        'weight': {'type': topstruct.Number, 'is_required': False},
        'width': {'type': topstruct.Number, 'is_required': False}
    }

    RESPONSE = {
        'item_id': {'type': topstruct.Number, 'is_list': False}
    }

    API = 'taobao.wlb.item.add'


class WlbItemAuthorizationAddRequest(TOPRequest):
    """ 添加商品的授权规则：添加规则之后代销商可以增加商品代销关系

    @response rule_id_list(Number): 授权规则ID列表

    @request auth_type(Number): (required)授权类型：1=全量授权，0=部分授权
        当部分授权时，需要指定授权数量quantity
    @request authorize_end_time(Date): (required)授权结束时间
    @request authorize_start_time(Date): (required)授权开始时间
    @request consign_user_nick(String): (required)被授权人用户id
    @request item_id_list(String): (required)商品id列表，以英文逗号,分隔，最多可放入50个商品ID。
    @request name(String): (required)规则名称
    @request quantity(Number): (optional)授权数量
    @request rule_code(String): (required)授权规则：目前只有GRANT_FIX，按照数量授权
    """
    REQUEST = {
        'auth_type': {'type': topstruct.Number, 'is_required': True},
        'authorize_end_time': {'type': topstruct.Date, 'is_required': True},
        'authorize_start_time': {'type': topstruct.Date, 'is_required': True},
        'consign_user_nick': {'type': topstruct.String, 'is_required': True},
        'item_id_list': {'type': topstruct.String, 'is_required': True},
        'name': {'type': topstruct.String, 'is_required': True},
        'quantity': {'type': topstruct.Number, 'is_required': False},
        'rule_code': {'type': topstruct.String, 'is_required': True}
    }

    RESPONSE = {
        'rule_id_list': {'type': topstruct.Number, 'is_list': False}
    }

    API = 'taobao.wlb.item.authorization.add'


class WlbItemAuthorizationDeleteRequest(TOPRequest):
    """ 删除授权关系.若有建立代销关系，会将其代销关系冻结即将状态置为失效(代销关系)。

    @response gmt_modified(Date): 修改时间

    @request authorize_id(Number): (required)授权关系ID
    """
    REQUEST = {
        'authorize_id': {'type': topstruct.Number, 'is_required': True}
    }

    RESPONSE = {
        'gmt_modified': {'type': topstruct.Date, 'is_list': False}
    }

    API = 'taobao.wlb.item.authorization.delete'


class WlbItemAuthorizationQueryRequest(TOPRequest):
    """ 查询授权关系,可由货主或被授权人查询。

    @response authorization_list(WlbAuthorization): 授权关系列表
    @response total_count(Number): 结果总数

    @request item_id(Number): (optional)授权商品ID
    @request name(String): (optional)授权名称
    @request page_no(Number): (optional)当前页
    @request page_size(Number): (optional)分页记录个数，如果用户输入的记录数大于50，则一页显示50条记录
    @request rule_code(String): (optional)授权编码
    @request status(String): (optional)状态： 只能输入如下值,范围外的默认按VALID处理;不选则查询所有;
        VALID -- 1 有效； INVALIDATION -- 2 失效
    @request type(String): (optional)类型：可由不同角色来查询，默认值OWNER,
        OWNER -- 授权人,
        ON_COMMISSION -- 被授权人
    """
    REQUEST = {
        'item_id': {'type': topstruct.Number, 'is_required': False},
        'name': {'type': topstruct.String, 'is_required': False},
        'page_no': {'type': topstruct.Number, 'is_required': False},
        'page_size': {'type': topstruct.Number, 'is_required': False},
        'rule_code': {'type': topstruct.String, 'is_required': False},
        'status': {'type': topstruct.String, 'is_required': False},
        'type': {'type': topstruct.String, 'is_required': False}
    }

    RESPONSE = {
        'authorization_list': {'type': topstruct.WlbAuthorization, 'is_list': False},
        'total_count': {'type': topstruct.Number, 'is_list': False}
    }

    API = 'taobao.wlb.item.authorization.query'


class WlbItemBatchQueryRequest(TOPRequest):
    """ 根据用户id，item id list和store code来查询商品库存信息和批次信息

    @response item_inventory_batch_list(WlbItemBatchInventory): 商品库存及批次信息查询结果
    @response total_count(Number): 返回结果记录的数量

    @request item_ids(String): (required)需要查询的商品ID列表，以字符串表示，ID间以;隔开
    @request page_no(Number): (optional)分页查询参数，指定查询页数，默认为1
    @request page_size(Number): (optional)分页查询参数，每页查询数量，默认20，最大值50,大于50时按照50条查询
    @request store_code(String): (optional)仓库编号
    """
    REQUEST = {
        'item_ids': {'type': topstruct.String, 'is_required': True},
        'page_no': {'type': topstruct.Number, 'is_required': False},
        'page_size': {'type': topstruct.Number, 'is_required': False},
        'store_code': {'type': topstruct.String, 'is_required': False}
    }

    RESPONSE = {
        'item_inventory_batch_list': {'type': topstruct.WlbItemBatchInventory, 'is_list': False},
        'total_count': {'type': topstruct.Number, 'is_list': False}
    }

    API = 'taobao.wlb.item.batch.query'


class WlbItemCombinationCreateRequest(TOPRequest):
    """ 创建商品组合关系

    @response gmt_create(Date): 组合关系创建时间

    @request dest_item_list(FieldList): (required)组合商品的id列表
    @request item_id(Number): (required)要建立组合关系的商品id
    @request proportion_list(FieldList): (optional)组成组合商品的比例列表，描述组合商品的组合比例，默认为1,1,1
    """
    REQUEST = {
        'dest_item_list': {'type': topstruct.FieldList, 'is_required': True},
        'item_id': {'type': topstruct.Number, 'is_required': True},
        'proportion_list': {'type': topstruct.FieldList, 'is_required': False}
    }

    RESPONSE = {
        'gmt_create': {'type': topstruct.Date, 'is_list': False}
    }

    API = 'taobao.wlb.item.combination.create'


class WlbItemCombinationDeleteRequest(TOPRequest):
    """ 删除商品组合关系

    @response gmt_modified(Date): 修改时间

    @request dest_item_list(FieldList): (required)组合商品的id列表
    @request item_id(Number): (required)组合关系的商品id
    """
    REQUEST = {
        'dest_item_list': {'type': topstruct.FieldList, 'is_required': True},
        'item_id': {'type': topstruct.Number, 'is_required': True}
    }

    RESPONSE = {
        'gmt_modified': {'type': topstruct.Date, 'is_list': False}
    }

    API = 'taobao.wlb.item.combination.delete'


class WlbItemCombinationGetRequest(TOPRequest):
    """ 根据商品id查询商品组合关系

    @response item_id_list(Number): 组合子商品id列表

    @request item_id(Number): (required)要查询的组合商品id
    """
    REQUEST = {
        'item_id': {'type': topstruct.Number, 'is_required': True}
    }

    RESPONSE = {
        'item_id_list': {'type': topstruct.Number, 'is_list': False}
    }

    API = 'taobao.wlb.item.combination.get'


class WlbItemConsignmentCreateRequest(TOPRequest):
    """ 代销商创建商品代销关系：货主创建授权规则，获得授权规则后方可创建商品代销关系。

    @response consignment_id(Number): 代销关系唯一标识

    @request item_id(Number): (required)商品id
    @request number(Number): (required)代销数量
    @request owner_item_id(Number): (required)货主商品id
    @request owner_user_id(Number): (required)货主id
    @request rule_id(Number): (required)通过taobao.wlb.item.authorization.add接口创建后得到的rule_id，规则中设定了代销商可以代销的商品数量
    """
    REQUEST = {
        'item_id': {'type': topstruct.Number, 'is_required': True},
        'number': {'type': topstruct.Number, 'is_required': True},
        'owner_item_id': {'type': topstruct.Number, 'is_required': True},
        'owner_user_id': {'type': topstruct.Number, 'is_required': True},
        'rule_id': {'type': topstruct.Number, 'is_required': True}
    }

    RESPONSE = {
        'consignment_id': {'type': topstruct.Number, 'is_list': False}
    }

    API = 'taobao.wlb.item.consignment.create'


class WlbItemConsignmentDeleteRequest(TOPRequest):
    """ 删除商品的代销关系

    @response gmt_modified(Date): 修改时间

    @request ic_item_id(Number): (required)代销商前台宝贝ID
    @request owner_item_id(Number): (required)货主的物流宝商品ID
    @request rule_id(Number): (required)授权关系id
    """
    REQUEST = {
        'ic_item_id': {'type': topstruct.Number, 'is_required': True},
        'owner_item_id': {'type': topstruct.Number, 'is_required': True},
        'rule_id': {'type': topstruct.Number, 'is_required': True}
    }

    RESPONSE = {
        'gmt_modified': {'type': topstruct.Date, 'is_list': False}
    }

    API = 'taobao.wlb.item.consignment.delete'


class WlbItemConsignmentPageGetRequest(TOPRequest):
    """ 代销商角度分页查询物流宝商品的代销关系

    @response total_count(Number): 条件查询结果总数
    @response wlb_consign_ments(WlbConsignMent): 代销关系列表

    @request ic_item_id(Number): (optional)代销商宝贝id
    @request owner_item_id(Number): (optional)供应商商品id
    @request owner_user_nick(String): (optional)供应商用户昵称
    """
    REQUEST = {
        'ic_item_id': {'type': topstruct.Number, 'is_required': False},
        'owner_item_id': {'type': topstruct.Number, 'is_required': False},
        'owner_user_nick': {'type': topstruct.String, 'is_required': False}
    }

    RESPONSE = {
        'total_count': {'type': topstruct.Number, 'is_list': False},
        'wlb_consign_ments': {'type': topstruct.WlbConsignMent, 'is_list': False}
    }

    API = 'taobao.wlb.item.consignment.page.get'


class WlbItemDeleteRequest(TOPRequest):
    """ 通过ItemId,UserId来删除单个商品

    @response gmt_modified(Date): 修改时间

    @request item_id(Number): (required)商品ID
    @request user_nick(String): (required)商品所有人淘宝nick
    """
    REQUEST = {
        'item_id': {'type': topstruct.Number, 'is_required': True},
        'user_nick': {'type': topstruct.String, 'is_required': True}
    }

    RESPONSE = {
        'gmt_modified': {'type': topstruct.Date, 'is_list': False}
    }

    API = 'taobao.wlb.item.delete'


class WlbItemGetRequest(TOPRequest):
    """ 根据商品ID获取商品信息,除了获取商品信息外还可获取商品属性信息和库存信息。

    @response item(WlbItem): 商品信息

    @request item_id(Number): (required)商品ID
    """
    REQUEST = {
        'item_id': {'type': topstruct.Number, 'is_required': True}
    }

    RESPONSE = {
        'item': {'type': topstruct.WlbItem, 'is_list': False}
    }

    API = 'taobao.wlb.item.get'


class WlbItemMapGetRequest(TOPRequest):
    """ 根据物流宝商品ID查询商品映射关系

    @response out_entity_item_list(OutEntityItem): 外部商品实体列表

    @request item_id(Number): (required)要查询映射关系的物流宝商品id
    """
    REQUEST = {
        'item_id': {'type': topstruct.Number, 'is_required': True}
    }

    RESPONSE = {
        'out_entity_item_list': {'type': topstruct.OutEntityItem, 'is_list': False}
    }

    API = 'taobao.wlb.item.map.get'


class WlbItemMapGetByExtentityRequest(TOPRequest):
    """ 根据外部实体类型和实体id查询映射的物流宝商品id

    @response item_id(Number): 物流宝商品id

    @request ext_entity_id(Number): (required)外部实体类型对应的商品id
    @request ext_entity_type(String): (required)外部实体类型： IC_ITEM--ic商品 IC_SKU--ic销售单元
    """
    REQUEST = {
        'ext_entity_id': {'type': topstruct.Number, 'is_required': True},
        'ext_entity_type': {'type': topstruct.String, 'is_required': True}
    }

    RESPONSE = {
        'item_id': {'type': topstruct.Number, 'is_list': False}
    }

    API = 'taobao.wlb.item.map.get.by.extentity'


class WlbItemQueryRequest(TOPRequest):
    """ 根据状态、卖家、SKU等信息查询商品列表

    @response item_list(WlbItem): 商品信息列表
    @response total_count(Number): 结果总数

    @request is_sku(String): (optional)是否是最小库存单元，只有最小库存单元的商品才可以有库存,值只能给"true","false"来表示;
        若值不在范围内，则按true处理
    @request item_code(String): (optional)商家编码
    @request item_type(String): (optional)ITEM类型(只允许输入以下英文或空)
        NORMAL  0:普通商品;
        COMBINE  1:是否是组合商品
        DISTRIBUTION  2:是否是分销商品(货主是别人)
        若值不在范围内，则按NORMAL处理
    @request name(String): (optional)商品名称
    @request page_no(Number): (optional)当前页
    @request page_size(Number): (optional)分页记录个数，如果用户输入的记录数大于50，则一页显示50条记录
    @request parent_id(Number): (optional)父ID,只有is_sku=1时才能有父ID，商品也可以没有付商品
    @request status(String): (optional)只能输入以下值或空：
        ITEM_STATUS_VALID -- 1 表示 有效；
        ITEM_STATUS_LOCK  -- 2 表示锁住。
        若值不在范围内，按ITEM_STATUS_VALID处理
    @request title(String): (optional)商品前台销售名字
    """
    REQUEST = {
        'is_sku': {'type': topstruct.String, 'is_required': False},
        'item_code': {'type': topstruct.String, 'is_required': False},
        'item_type': {'type': topstruct.String, 'is_required': False},
        'name': {'type': topstruct.String, 'is_required': False},
        'page_no': {'type': topstruct.Number, 'is_required': False},
        'page_size': {'type': topstruct.Number, 'is_required': False},
        'parent_id': {'type': topstruct.Number, 'is_required': False},
        'status': {'type': topstruct.String, 'is_required': False},
        'title': {'type': topstruct.String, 'is_required': False}
    }

    RESPONSE = {
        'item_list': {'type': topstruct.WlbItem, 'is_list': False},
        'total_count': {'type': topstruct.Number, 'is_list': False}
    }

    API = 'taobao.wlb.item.query'


class WlbItemSynchronizeRequest(TOPRequest):
    """ 同步仓储商品与前台商品，建立仓储商品与前台商品的关系,并更新IC中的信息到仓储商品Item中

    @response gmt_modified(Date): 修改时间

    @request ext_entity_id(Number): (required)外部实体ID
    @request ext_entity_type(String): (required)外部实体类型.存如下值
        IC_ITEM   --表示IC商品
        IC_SKU    --表示IC最小单位商品
        若输入其他值，则按IC_ITEM处理
    @request item_id(Number): (required)商品ID
    @request user_nick(String): (required)商品所有人淘宝nick
    """
    REQUEST = {
        'ext_entity_id': {'type': topstruct.Number, 'is_required': True},
        'ext_entity_type': {'type': topstruct.String, 'is_required': True},
        'item_id': {'type': topstruct.Number, 'is_required': True},
        'user_nick': {'type': topstruct.String, 'is_required': True}
    }

    RESPONSE = {
        'gmt_modified': {'type': topstruct.Date, 'is_list': False}
    }

    API = 'taobao.wlb.item.synchronize'


class WlbItemSynchronizeDeleteRequest(TOPRequest):
    """ 通过物流宝商品ID和IC商品ID删除映射关系。

    @response gmt_modified(Date): 修改时间

    @request ext_entity_id(Number): (required)外部实体ID
    @request ext_entity_type(String): (required)外部实体类型.存如下值 IC_ITEM --表示IC商品; IC_SKU --表示IC最小单位商品;若输入其他值，则按IC_ITEM处理
    @request item_id(Number): (required)物流宝商品ID
    """
    REQUEST = {
        'ext_entity_id': {'type': topstruct.Number, 'is_required': True},
        'ext_entity_type': {'type': topstruct.String, 'is_required': True},
        'item_id': {'type': topstruct.Number, 'is_required': True}
    }

    RESPONSE = {
        'gmt_modified': {'type': topstruct.Date, 'is_list': False}
    }

    API = 'taobao.wlb.item.synchronize.delete'


class WlbItemUpdateRequest(TOPRequest):
    """ 修改物流宝商品信息

    @response gmt_modified(Date): 修改时间

    @request color(String): (optional)商品颜色
    @request delete_property_key_list(FieldList): (optional)需要删除的商品属性key列表
    @request goods_cat(String): (optional)商品货类
    @request height(Number): (optional)商品高度，单位厘米
    @request id(Number): (required)要修改的商品id
    @request is_dangerous(Boolean): (optional)是否危险品
    @request is_friable(Boolean): (optional)是否易碎品
    @request length(Number): (optional)商品长度，单位厘米
    @request name(String): (optional)要修改的商品名称
    @request package_material(String): (optional)商品包装材料类型
    @request pricing_cat(String): (optional)商品计价货类
    @request remark(String): (optional)要修改的商品备注
    @request title(String): (optional)要修改的商品标题
    @request update_property_key_list(FieldList): (optional)需要修改的商品属性值的列表，如果属性不存在，则新增属性
    @request update_property_value_list(FieldList): (optional)需要修改的属性值的列表
    @request volume(Number): (optional)商品体积，单位立方厘米
    @request weight(Number): (optional)商品重量，单位G
    @request width(Number): (optional)商品宽度，单位厘米
    """
    REQUEST = {
        'color': {'type': topstruct.String, 'is_required': False},
        'delete_property_key_list': {'type': topstruct.FieldList, 'is_required': False},
        'goods_cat': {'type': topstruct.String, 'is_required': False},
        'height': {'type': topstruct.Number, 'is_required': False},
        'id': {'type': topstruct.Number, 'is_required': True},
        'is_dangerous': {'type': topstruct.Boolean, 'is_required': False},
        'is_friable': {'type': topstruct.Boolean, 'is_required': False},
        'length': {'type': topstruct.Number, 'is_required': False},
        'name': {'type': topstruct.String, 'is_required': False},
        'package_material': {'type': topstruct.String, 'is_required': False},
        'pricing_cat': {'type': topstruct.String, 'is_required': False},
        'remark': {'type': topstruct.String, 'is_required': False},
        'title': {'type': topstruct.String, 'is_required': False},
        'update_property_key_list': {'type': topstruct.FieldList, 'is_required': False},
        'update_property_value_list': {'type': topstruct.FieldList, 'is_required': False},
        'volume': {'type': topstruct.Number, 'is_required': False},
        'weight': {'type': topstruct.Number, 'is_required': False},
        'width': {'type': topstruct.Number, 'is_required': False}
    }

    RESPONSE = {
        'gmt_modified': {'type': topstruct.Date, 'is_list': False}
    }

    API = 'taobao.wlb.item.update'


class WlbNotifyMessageConfirmRequest(TOPRequest):
    """ 确认物流宝可执行消息

    @response gmt_modified(Date): 物流宝消息确认时间

    @request message_id(Number): (required)物流宝通知消息的id，通过taobao.wlb.notify.message.page.get接口得到的WlbMessage数据结构中的id字段
    """
    REQUEST = {
        'message_id': {'type': topstruct.Number, 'is_required': True}
    }

    RESPONSE = {
        'gmt_modified': {'type': topstruct.Date, 'is_list': False}
    }

    API = 'taobao.wlb.notify.message.confirm'


class WlbNotifyMessagePageGetRequest(TOPRequest):
    """ 物流宝提供的消息通知查询接口，消息内容包括;出入库单不一致消息，取消订单成功消息，盘点单消息

    @response total_count(Number): 条件查询结果总数量
    @response wlb_messages(WlbMessage): 消息结果列表

    @request end_date(Date): (optional)查询条件：记录截至时间
    @request msg_code(String): (optional)通知消息编码：
        STOCK_IN_NOT_CONSISTENT---入库单不一致
        CANCEL_ORDER_SUCCESS---取消订单成功
        INVENTORY_CHECK---盘点
        CANCEL_ORDER_FAILURE---取消订单失败
        ORDER_REJECT--wms拒单
        ORDER_CONFIRMED--订单处理成功
    @request page_no(Number): (optional)分页查询页数
    @request page_size(Number): (optional)分页查询的每页页数
    @request start_date(Date): (optional)查询条件：记录开始时间
    @request status(String): (optional)消息状态：
        不需要确认：NO_NEED_CONFIRM
        已确认：CONFIRMED
        待确认：TO_BE_CONFIRM
    """
    REQUEST = {
        'end_date': {'type': topstruct.Date, 'is_required': False},
        'msg_code': {'type': topstruct.String, 'is_required': False},
        'page_no': {'type': topstruct.Number, 'is_required': False},
        'page_size': {'type': topstruct.Number, 'is_required': False},
        'start_date': {'type': topstruct.Date, 'is_required': False},
        'status': {'type': topstruct.String, 'is_required': False}
    }

    RESPONSE = {
        'total_count': {'type': topstruct.Number, 'is_list': False},
        'wlb_messages': {'type': topstruct.WlbMessage, 'is_list': False}
    }

    API = 'taobao.wlb.notify.message.page.get'


class WlbOrderCancelRequest(TOPRequest):
    """ 取消物流宝订单

    @response error_code_list(String): 错误编码列表
    @response modify_time(Date): 修改时间，只有在取消成功的情况下，才可以做

    @request wlb_order_code(String): (required)物流宝订单编号
    """
    REQUEST = {
        'wlb_order_code': {'type': topstruct.String, 'is_required': True}
    }

    RESPONSE = {
        'error_code_list': {'type': topstruct.String, 'is_list': False},
        'modify_time': {'type': topstruct.Date, 'is_list': False}
    }

    API = 'taobao.wlb.order.cancel'


class WlbOrderConsignRequest(TOPRequest):
    """ 如果erp导入淘宝交易订单到物流宝，当物流宝订单已发货的时候，erp需要调用该接口来通知物流订单和淘宝交易订单已发货

    @response modify_time(Date): 修改时间

    @request wlb_order_code(String): (required)物流宝订单编号
    """
    REQUEST = {
        'wlb_order_code': {'type': topstruct.String, 'is_required': True}
    }

    RESPONSE = {
        'modify_time': {'type': topstruct.Date, 'is_list': False}
    }

    API = 'taobao.wlb.order.consign'


class WlbOrderCreateRequest(TOPRequest):
    """ 创建物流宝订单，由外部ISV或者ERP，Elink，淘宝交易产生

    @response create_time(Date): 订单创建时间
    @response order_code(String): 物流宝订单创建成功后，返回物流宝的订单编号；如果订单创建失败，该字段为空。

    @request alipay_no(String): (optional)支付宝交易号
    @request attributes(String): (optional)该字段暂时保留
    @request buyer_nick(String): (optional)买家呢称
    @request expect_end_time(Date): (optional)期望结束时间，在入库单会使用到
    @request expect_start_time(Date): (optional)计划开始送达时间  在入库单中可能会使用
    @request invoince_info(String): (optional){"invoince_info": [{"bill_type":"发票类型，必选", "bill_title":"发票抬头，必选", "bill_amount":"发票金额(单位是分)，必选","bill_content":"发票内容，可选"}]}
    @request is_finished(Boolean): (required)该物流宝订单是否已完成，如果完成则设置为true，如果为false，则需要等待继续创建订单商品信息。
    @request order_code(String): (optional)物流宝订单编号，该接口约定每次最多只能传50条order_item_list，如果一个物流宝订单超过50条商品的时候，需要批量来调用该接口，第一次调用的时候，wlb_order_code为空，如果第一次创建成功，该接口返回wlb_order_code，其后继续再该订单上添加商品条目，需要带上wlb_order_code，out_biz_code，order_item_list,is_finished四个字段。
    @request order_flag(String): (optional)用字符串格式来表示订单标记列表：比如COD^PRESELL^SPLIT^LIMIT 等，中间用“^”来隔开 ---------------------------------------- 订单标记list（所有字母全部大写）： 1: COD –货到付款 2: LIMIT-限时配送 3: PRESELL-预售 5:COMPLAIN-已投诉 7:SPLIT-拆单， 8:EXCHANGE-换货， 9:VISIT-上门 ， 10: MODIFYTRANSPORT-是否可改配送方式，
        : 是否可改配送方式  默认可更改
        11 CONSIGN 物流宝代理发货,自动更改发货状态
        12: SELLER_AFFORD 是否卖家承担运费 默认是，即没 13: SYNC_RETURN_BILL，同时退回发票
    @request order_item_list(String): (required)订单商品列表： {"order_item_list":[{"trade_code":"可选,淘宝交易订单，并且不是赠品，必须要传订单来源编号"," sub_trade_code ":"可选,淘宝子交易号","item_id":"必须,商品Id","item_code":"必须,商家编码","item_name":"可选,物流宝商品名称","item_quantity":"必选,计划数量","item_price":"必选,物品价格,单位为分","owner_user_nick
        ":"可选,货主nick 代销模式下会存在","flag":"判断是否为赠品0 不是1是","remarks":"可选,备注","batch_remark":"可选，批次描述信息会把这个信息带给WMS，但不会跟物流宝库存相关联"，"inventory_type":"库存类型1 可销售库存 101 类型用来定义残次品 201 冻结类型库存 301 在途库存","picture_url":"图片Url","distributor_user_nick": "分销商NICK","ext_order_item_code":"可选，外部商品的商家编码"]} ======================================== 如果订单中的商品条目数大于50条的时候，我们会校验，不能创建成功，需要你按照50个一批的数量传，需要分批调用该接口，第二次传的时候，需要带上wlb_order_code和is_finished和order_item_list三个字段是必传的，is_finished为true表示传输完毕，为false表示还没完全传完。
    @request order_sub_type(String): (required)订单子类型：
        （1）OTHER： 其他
        （2）TAOBAO_TRADE： 淘宝交易
        （3）OTHER_TRADE：其他交易
        （4）ALLCOATE： 调拨
        （5）PURCHASE:采购
    @request order_type(String): (required)订单类型:
        （1）NORMAL_OUT ：正常出库
        （2）NORMAL_IN：正常入库
        （3）RETURN_IN：退货入库
        （4）EXCHANGE_OUT：换货出库
    @request out_biz_code(String): (required)外部订单业务ID，该编号在isv中是唯一编号， 用来控制并发，去重用
    @request package_count(Number): (optional)包裹件数，入库单和出库单中会用到
    @request payable_amount(Number): (optional)应收金额，cod订单必选
    @request prev_order_code(String): (optional)源订单编号
    @request receiver_info(String): (optional)发收方发货方信息必须传 手机和电话必选其一
        收货方信息
        邮编^^^省^^^市^^^区^^^具体地址^^^收件方名称^^^手机^^^电话
        如果某一个字段的数据为空时，必须传NA
    @request remark(String): (optional)备注
    @request schedule_end(String): (optional)投递时间范围要求,格式'15:20'用分号隔开
    @request schedule_start(String): (optional)投递时间范围要求,格式'13:20'用分号隔开
    @request schedule_type(String): (optional)投递时延要求:
        （1）INSTANT_ARRIVED： 当日达
        （2）TOMMORROY_MORNING_ARRIVED：次晨达
        （3）TOMMORROY_ARRIVED：次日达
        （4）工作日：WORK_DAY
        （5）节假日：WEEKED_DAY
    @request sender_info(String): (optional)发货方信息，发收方发货方信息必须传 手机和电话必选其一
        邮编^^^省^^^市^^^区^^^具体地址^^^收件方名称^^^手机^^^电话
        如果某一个字段的数据为空时，必须传NA
    @request service_fee(Number): (optional)cod服务费，只有cod订单的时候，才需要这个字段
    @request store_code(String): (required)仓库编码
    @request tms_info(String): (optional)出库单中可能会用到
        运输公司名称^^^运输公司联系人^^^运输公司运单号^^^运输公司电话^^^运输公司联系人身份证号
        ========================================
        如果某一个字段的数据为空时，必须传NA
    @request tms_order_code(String): (optional)运单编号，退货单时可能会使用
    @request tms_service_code(String): (optional)物流公司编码
    @request total_amount(Number): (optional)总金额
    """
    REQUEST = {
        'alipay_no': {'type': topstruct.String, 'is_required': False},
        'attributes': {'type': topstruct.String, 'is_required': False},
        'buyer_nick': {'type': topstruct.String, 'is_required': False},
        'expect_end_time': {'type': topstruct.Date, 'is_required': False},
        'expect_start_time': {'type': topstruct.Date, 'is_required': False},
        'invoince_info': {'type': topstruct.String, 'is_required': False},
        'is_finished': {'type': topstruct.Boolean, 'is_required': True},
        'order_code': {'type': topstruct.String, 'is_required': False},
        'order_flag': {'type': topstruct.String, 'is_required': False},
        'order_item_list': {'type': topstruct.String, 'is_required': True},
        'order_sub_type': {'type': topstruct.String, 'is_required': True},
        'order_type': {'type': topstruct.String, 'is_required': True},
        'out_biz_code': {'type': topstruct.String, 'is_required': True},
        'package_count': {'type': topstruct.Number, 'is_required': False},
        'payable_amount': {'type': topstruct.Number, 'is_required': False},
        'prev_order_code': {'type': topstruct.String, 'is_required': False},
        'receiver_info': {'type': topstruct.String, 'is_required': False},
        'remark': {'type': topstruct.String, 'is_required': False},
        'schedule_end': {'type': topstruct.String, 'is_required': False},
        'schedule_start': {'type': topstruct.String, 'is_required': False},
        'schedule_type': {'type': topstruct.String, 'is_required': False},
        'sender_info': {'type': topstruct.String, 'is_required': False},
        'service_fee': {'type': topstruct.Number, 'is_required': False},
        'store_code': {'type': topstruct.String, 'is_required': True},
        'tms_info': {'type': topstruct.String, 'is_required': False},
        'tms_order_code': {'type': topstruct.String, 'is_required': False},
        'tms_service_code': {'type': topstruct.String, 'is_required': False},
        'total_amount': {'type': topstruct.Number, 'is_required': False}
    }

    RESPONSE = {
        'create_time': {'type': topstruct.Date, 'is_list': False},
        'order_code': {'type': topstruct.String, 'is_list': False}
    }

    API = 'taobao.wlb.order.create'


class WlbOrderPageGetRequest(TOPRequest):
    """ 分页查询物流宝订单

    @response order_list(WlbOrder): 分页查询返回结果
    @response total_count(Number): 总条数

    @request end_time(Date): (optional)查询截止时间
    @request order_code(String): (optional)物流订单编号
    @request order_status(Number): (optional)订单状态
    @request order_sub_type(String): (optional)订单子类型：
        （1）OTHER： 其他
        （2）TAOBAO_TRADE： 淘宝交易
        （3）OTHER_TRADE：其他交易
        （4）ALLCOATE： 调拨
        （5）CHECK:  盘点单
        （6）PURCHASE: 采购单
    @request order_type(String): (optional)订单类型:
        （1）NORMAL_OUT ：正常出库
        （2）NORMAL_IN：正常入库
        （3）RETURN_IN：退货入库
        （4）EXCHANGE_OUT：换货出库
    @request page_no(Number): (optional)分页的第几页
    @request page_size(Number): (optional)每页多少条
    @request start_time(Date): (optional)查询开始时间
    """
    REQUEST = {
        'end_time': {'type': topstruct.Date, 'is_required': False},
        'order_code': {'type': topstruct.String, 'is_required': False},
        'order_status': {'type': topstruct.Number, 'is_required': False},
        'order_sub_type': {'type': topstruct.String, 'is_required': False},
        'order_type': {'type': topstruct.String, 'is_required': False},
        'page_no': {'type': topstruct.Number, 'is_required': False},
        'page_size': {'type': topstruct.Number, 'is_required': False},
        'start_time': {'type': topstruct.Date, 'is_required': False}
    }

    RESPONSE = {
        'order_list': {'type': topstruct.WlbOrder, 'is_list': False},
        'total_count': {'type': topstruct.Number, 'is_list': False}
    }

    API = 'taobao.wlb.order.page.get'


class WlbOrderScheduleRuleAddRequest(TOPRequest):
    """ 为订单的自动流转设置订单调度规则。规则设定之后，可以根据发货地区，精确路由订单至指定仓库处理。

    @response schedule_rule_id(Number): 新增成功的订单调度规则id

    @request backup_store_id(Number): (optional)备用发货仓库服务id（通过taobao.wlb.subscription.query接口获得service_id）
    @request default_store_id(Number): (required)发货仓库服务id（通过taobao.wlb.subscription.query接口获得service_id）
    @request option(FieldList): (optional)发货规则的额外规则设置：
        REMARK_STOP--有订单留言不自动下发
        COD_STOP--货到付款订单不自动下发
        CHECK_WAREHOUSE_DELIVER--检查仓库的配送范围
    @request prov_area_ids(String): (required)国家地区标准编码列表
    """
    REQUEST = {
        'backup_store_id': {'type': topstruct.Number, 'is_required': False},
        'default_store_id': {'type': topstruct.Number, 'is_required': True},
        'option': {'type': topstruct.FieldList, 'is_required': False},
        'prov_area_ids': {'type': topstruct.String, 'is_required': True}
    }

    RESPONSE = {
        'schedule_rule_id': {'type': topstruct.Number, 'is_list': False}
    }

    API = 'taobao.wlb.order.schedule.rule.add'


class WlbOrderScheduleRuleUpdateRequest(TOPRequest):
    """ 修改物流宝订单调度规则

    @response gmt_modified(Date): 修改时间

    @request backup_store_id(Number): (optional)备用发货仓库id
    @request default_store_id(Number): (optional)默认发货仓库id
    @request option(FieldList): (optional)订单调度规则的额外规则设置： REMARK_STOP--有订单留言不自动下发 COD_STOP--货到付款订单不自动下发 CHECK_WAREHOUSE_DELIVER--检查仓库的配送范围
    @request prov_area_ids(String): (optional)国家地区标准编码列表
    @request schedule_rule_id(Number): (required)要修改的订单调度规则明细id
    """
    REQUEST = {
        'backup_store_id': {'type': topstruct.Number, 'is_required': False},
        'default_store_id': {'type': topstruct.Number, 'is_required': False},
        'option': {'type': topstruct.FieldList, 'is_required': False},
        'prov_area_ids': {'type': topstruct.String, 'is_required': False},
        'schedule_rule_id': {'type': topstruct.Number, 'is_required': True}
    }

    RESPONSE = {
        'gmt_modified': {'type': topstruct.Date, 'is_list': False}
    }

    API = 'taobao.wlb.order.schedule.rule.update'


class WlbOrderitemPageGetRequest(TOPRequest):
    """ 分页查询物流宝订单商品详情

    @response order_item_list(WlbOrderItem): 物流宝订单商品列表
    @response total_count(Number): 总数量

    @request order_code(String): (required)物流宝订单编码
    @request page_no(Number): (optional)分页查询参数，指定查询页数，默认为1
    @request page_size(Number): (optional)分页查询参数，每页查询数量，默认20，最大值50,大于50时按照50条查询
    """
    REQUEST = {
        'order_code': {'type': topstruct.String, 'is_required': True},
        'page_no': {'type': topstruct.Number, 'is_required': False},
        'page_size': {'type': topstruct.Number, 'is_required': False}
    }

    RESPONSE = {
        'order_item_list': {'type': topstruct.WlbOrderItem, 'is_list': False},
        'total_count': {'type': topstruct.Number, 'is_list': False}
    }

    API = 'taobao.wlb.orderitem.page.get'


class WlbOrderscheduleruleDeleteRequest(TOPRequest):
    """ 删除单个订单调度规则

    @response gmt_modified(Date): 修改时间

    @request id(Number): (required)订单调度规则ID
    @request user_nick(String): (required)商品userNick
    """
    REQUEST = {
        'id': {'type': topstruct.Number, 'is_required': True},
        'user_nick': {'type': topstruct.String, 'is_required': True}
    }

    RESPONSE = {
        'gmt_modified': {'type': topstruct.Date, 'is_list': False}
    }

    API = 'taobao.wlb.orderschedulerule.delete'


class WlbOrderscheduleruleQueryRequest(TOPRequest):
    """ 查询某个卖家的所有订单调度规则，提供分页查询。

    @response order_schedule_rule_list(WlbOrderScheduleRule): 订单调度规则列表
    @response total_count(Number): 结果总数

    @request page_no(Number): (optional)当前页
    @request page_size(Number): (optional)分页记录个数，如果用户输入的记录数大于50，则一页显示50条记录
    """
    REQUEST = {
        'page_no': {'type': topstruct.Number, 'is_required': False},
        'page_size': {'type': topstruct.Number, 'is_required': False}
    }

    RESPONSE = {
        'order_schedule_rule_list': {'type': topstruct.WlbOrderScheduleRule, 'is_list': False},
        'total_count': {'type': topstruct.Number, 'is_list': False}
    }

    API = 'taobao.wlb.orderschedulerule.query'


class WlbOrderstatusGetRequest(TOPRequest):
    """ 根据物流宝订单号查询物流宝订单至目前为止的流转状态列表

    @response wlb_order_status(WlbProcessStatus): 订单流转信息状态列表

    @request order_code(String): (required)物流宝订单编码
    """
    REQUEST = {
        'order_code': {'type': topstruct.String, 'is_required': True}
    }

    RESPONSE = {
        'wlb_order_status': {'type': topstruct.WlbProcessStatus, 'is_list': False}
    }

    API = 'taobao.wlb.orderstatus.get'


class WlbOutInventoryChangeNotifyRequest(TOPRequest):
    """ 拥有自有仓的企业物流用户通过该接口把自有仓的库存通知到物流宝，由物流宝维护该库存，控制前台显示库存的准确性。

    @response gmt_modified(Date): 库存变化通知成功时间

    @request change_count(Number): (required)库存变化数量
    @request item_id(Number): (required)物流宝商品id或前台宝贝id（由type类型决定）
    @request op_type(String): (required)OUT--出库
        IN--入库
    @request order_source_code(String): (optional)订单号，如果source为TAOBAO_TRADE,order_source_code必须为淘宝交易号
    @request out_biz_code(String): (required)库存变化唯一标识，用于去重，一个外部唯一编码唯一标识一次库存变化。
    @request result_count(Number): (required)本次库存变化后库存余额
    @request source(String): (required)（1）OTHER： 其他
        （2）TAOBAO_TRADE： 淘宝交易
        （3）OTHER_TRADE：其他交易
        （4）ALLCOATE： 调拨
        （5）CHECK:盘点
        （6）PURCHASE:采购
    @request store_code(String): (optional)目前非必须，系统会选择默认值
    @request type(String): (required)WLB_ITEM--物流宝商品
        IC_ITEM--淘宝商品
        IC_SKU--淘宝sku
    """
    REQUEST = {
        'change_count': {'type': topstruct.Number, 'is_required': True},
        'item_id': {'type': topstruct.Number, 'is_required': True},
        'op_type': {'type': topstruct.String, 'is_required': True},
        'order_source_code': {'type': topstruct.String, 'is_required': False},
        'out_biz_code': {'type': topstruct.String, 'is_required': True},
        'result_count': {'type': topstruct.Number, 'is_required': True},
        'source': {'type': topstruct.String, 'is_required': True},
        'store_code': {'type': topstruct.String, 'is_required': False},
        'type': {'type': topstruct.String, 'is_required': True}
    }

    RESPONSE = {
        'gmt_modified': {'type': topstruct.Date, 'is_list': False}
    }

    API = 'taobao.wlb.out.inventory.change.notify'


class WlbReplenishStatisticsRequest(TOPRequest):
    """ 查询BI的统计的补货统计数据

    @response replenish_list(WlbReplenish): 补货统计列表
    @response total_count(Number): 查询记录总数

    @request item_code(String): (optional)商品编码
    @request name(String): (optional)商品名称
    @request page_no(Number): (optional)分页参数，默认第一页
    @request page_size(Number): (optional)分页每页页数，默认20，最大50
    @request store_code(String): (optional)仓库编码
    """
    REQUEST = {
        'item_code': {'type': topstruct.String, 'is_required': False},
        'name': {'type': topstruct.String, 'is_required': False},
        'page_no': {'type': topstruct.Number, 'is_required': False},
        'page_size': {'type': topstruct.Number, 'is_required': False},
        'store_code': {'type': topstruct.String, 'is_required': False}
    }

    RESPONSE = {
        'replenish_list': {'type': topstruct.WlbReplenish, 'is_list': False},
        'total_count': {'type': topstruct.Number, 'is_list': False}
    }

    API = 'taobao.wlb.replenish.statistics'


class WlbSubscriptionQueryRequest(TOPRequest):
    """ 查询商家定购的所有服务,可通过入参状态来筛选

    @response seller_subscription_list(WlbSellerSubscription): 卖家定购的服务列表
    @response total_count(Number): 结果总数

    @request page_no(Number): (optional)当前页
    @request page_size(Number): (optional)分页记录个数，如果用户输入的记录数大于50，则一页显示50条记录
    @request status(String): (optional)状态
        AUDITING 1-待审核;
        CANCEL 2-撤销 ;
        CHECKED 3-审核通过 ;
        FAILED 4-审核未通过 ;
        SYNCHRONIZING 5-同步中;
        只允许输入上面指定的值，且可以为空，为空时查询所有状态。若输错了，则按AUDITING处理。
    """
    REQUEST = {
        'page_no': {'type': topstruct.Number, 'is_required': False},
        'page_size': {'type': topstruct.Number, 'is_required': False},
        'status': {'type': topstruct.String, 'is_required': False}
    }

    RESPONSE = {
        'seller_subscription_list': {'type': topstruct.WlbSellerSubscription, 'is_list': False},
        'total_count': {'type': topstruct.Number, 'is_list': False}
    }

    API = 'taobao.wlb.subscription.query'


class WlbTmsorderQueryRequest(TOPRequest):
    """ 通过物流订单编号分页查询物流信息

    @response tms_order_list(WlbTmsOrder): 物流订单运单信息列表
    @response total_count(Number): 结果总数

    @request order_code(String): (required)物流订单编号
    @request page_no(Number): (optional)当前页
    @request page_size(Number): (optional)分页记录个数，如果用户输入的记录数大于50，则一页显示50条记录
    """
    REQUEST = {
        'order_code': {'type': topstruct.String, 'is_required': True},
        'page_no': {'type': topstruct.Number, 'is_required': False},
        'page_size': {'type': topstruct.Number, 'is_required': False}
    }

    RESPONSE = {
        'tms_order_list': {'type': topstruct.WlbTmsOrder, 'is_list': False},
        'total_count': {'type': topstruct.Number, 'is_list': False}
    }

    API = 'taobao.wlb.tmsorder.query'


class WlbTradeorderGetRequest(TOPRequest):
    """ 根据交易类型和交易id查询物流宝订单详情

    @response wlb_order_list(WlbOrder): 物流宝订单列表信息

    @request trade_id(String): (required)指定交易类型的交易号
    @request trade_type(String): (required)交易类型:
        TAOBAO--淘宝交易
        PAIPAI--拍拍交易
        YOUA--有啊交易
    """
    REQUEST = {
        'trade_id': {'type': topstruct.String, 'is_required': True},
        'trade_type': {'type': topstruct.String, 'is_required': True}
    }

    RESPONSE = {
        'wlb_order_list': {'type': topstruct.WlbOrder, 'is_list': False}
    }

    API = 'taobao.wlb.tradeorder.get'


class WlbWlborderGetRequest(TOPRequest):
    """ 根据物流宝订单编号查询物流宝订单概要信息

    @response wlb_order(WlbOrder): 物流宝订单详情

    @request wlb_order_code(String): (required)物流宝订单编码
    """
    REQUEST = {
        'wlb_order_code': {'type': topstruct.String, 'is_required': True}
    }

    RESPONSE = {
        'wlb_order': {'type': topstruct.WlbOrder, 'is_list': False}
    }

    API = 'taobao.wlb.wlborder.get'


class MarketingPromotionKfcRequest(TOPRequest):
    """ 活动名称与描述违禁词检查

    @response is_success(Boolean): 是否成功

    @request promotion_desc(String): (required)活动描述
    @request promotion_title(String): (required)活动名称
    """
    REQUEST = {
        'promotion_desc': {'type': topstruct.String, 'is_required': True},
        'promotion_title': {'type': topstruct.String, 'is_required': True}
    }

    RESPONSE = {
        'is_success': {'type': topstruct.Boolean, 'is_list': False}
    }

    API = 'taobao.marketing.promotion.kfc'


class MarketingPromotionsGetRequest(TOPRequest):
    """ 根据商品ID查询卖家使用该第三方工具对商品设置的所有优惠策略

    @response promotions(Promotion): 商品对应的所有优惠列表
    @response total_results(Number): 结果总数

    @request fields(FieldList): (required)需返回的优惠策略结构字段列表。可选值为Promotion中所有字段，如：promotion_id, promotion_title, item_id, status, tag_id等等
    @request num_iid(String): (required)商品数字ID。根据该ID查询商品下通过第三方工具设置的所有优惠策略
    @request status(String): (optional)优惠策略状态。可选值：ACTIVE(有效)，UNACTIVE(无效)，若不传或者传入其他值，则默认查询全部
    @request tag_id(Number): (optional)标签ID
    """
    REQUEST = {
        'fields': {'type': topstruct.FieldList, 'is_required': True, 'optional': topstruct.Set({'promotion_desc', 'end_date', 'start_date', 'discount_type', 'promotion_title', 'decrease_num', 'discount_value', 'status', 'promotion_id', 'tag_id', 'num_iid'})},
        'num_iid': {'type': topstruct.String, 'is_required': True},
        'status': {'type': topstruct.String, 'is_required': False},
        'tag_id': {'type': topstruct.Number, 'is_required': False}
    }

    RESPONSE = {
        'promotions': {'type': topstruct.Promotion, 'is_list': False},
        'total_results': {'type': topstruct.Number, 'is_list': False}
    }

    API = 'taobao.marketing.promotions.get'


class MarketingTagsGetRequest(TOPRequest):
    """ 查询人群标签，返回卖家创建的全部人群标签（有效的）

    @response user_tags(UserTag): 标签列表

    @request fields(FieldList): (required)需要的返回字段，可选值为UserTag中所有字段
    """
    REQUEST = {
        'fields': {'type': topstruct.FieldList, 'is_required': True, 'optional': topstruct.Set({'description', 'tag_name', 'tag_id', 'create_date'})}
    }

    RESPONSE = {
        'user_tags': {'type': topstruct.UserTag, 'is_list': False}
    }

    API = 'taobao.marketing.tags.get'


class PromotionActivityGetRequest(TOPRequest):
    """ 查询某个卖家的店铺优惠券领取活动
        返回，优惠券领取活动ID，优惠券ID，总领用量，每人限领量，已领取数量
        领取活动状态，优惠券领取链接
        最多50个优惠券

    @response activitys(Activity): 活动列表

    @request activity_id(Number): (optional)活动的id
    """
    REQUEST = {
        'activity_id': {'type': topstruct.Number, 'is_required': False}
    }

    RESPONSE = {
        'activitys': {'type': topstruct.Activity, 'is_list': False}
    }

    API = 'taobao.promotion.activity.get'


class PromotionCouponBuyerSearchRequest(TOPRequest):
    """ 通过接口获得买家当前所有优惠券信息

    @response buyer_coupon_details(BuyerCouponDetail): 返回的优惠券信息
    @response total_results(Number): 查询结果是总数

    @request end_time(Date): (optional)查询有效期晚于查询日期的所有优惠券
    @request page_no(Number): (optional)第几页
    @request page_size(Number): (optional)每页条数
    @request seller_nick(String): (optional)店铺的名称，就是卖家的昵称
    @request status(String): (required)unused：未使用，using：使用中,used,已经使用，overdue：已经过期，transfered：已经转发
    """
    REQUEST = {
        'end_time': {'type': topstruct.Date, 'is_required': False},
        'page_no': {'type': topstruct.Number, 'is_required': False},
        'page_size': {'type': topstruct.Number, 'is_required': False},
        'seller_nick': {'type': topstruct.String, 'is_required': False},
        'status': {'type': topstruct.String, 'is_required': True}
    }

    RESPONSE = {
        'buyer_coupon_details': {'type': topstruct.BuyerCouponDetail, 'is_list': False},
        'total_results': {'type': topstruct.Number, 'is_list': False}
    }

    API = 'taobao.promotion.coupon.buyer.search'


class PromotionCoupondetailGetRequest(TOPRequest):
    """ 通过接口可以查询某个店铺优惠券的买家详细信息返回的信息，买家昵称， 使用渠道，使用状态，总数量

    @response coupon_details(CouponDetail): 优惠券详细信息
    @response total_results(Number): 查询数量总数

    @request buyer_nick(String): (optional)买家昵称
    @request coupon_id(Number): (required)优惠券的id
    @request page_no(Number): (optional)查询的页号，结果集是分页返回的，每页20条
    @request page_size(Number): (optional)每页行数
    @request state(String): (optional)优惠券使用情况unused：代表未使用using：代表使用中used：代表已使用。必须是unused，using，used
    """
    REQUEST = {
        'buyer_nick': {'type': topstruct.String, 'is_required': False},
        'coupon_id': {'type': topstruct.Number, 'is_required': True},
        'page_no': {'type': topstruct.Number, 'is_required': False},
        'page_size': {'type': topstruct.Number, 'is_required': False},
        'state': {'type': topstruct.String, 'is_required': False}
    }

    RESPONSE = {
        'coupon_details': {'type': topstruct.CouponDetail, 'is_list': False},
        'total_results': {'type': topstruct.Number, 'is_list': False}
    }

    API = 'taobao.promotion.coupondetail.get'


class PromotionCouponsGetRequest(TOPRequest):
    """ 查询卖家已经创建的优惠券，接口返回信息：优惠券ID，面值，创建时间，有效期，使用条件，使用渠道，创建渠道，优惠券总数量

    @response coupons(Coupon): 优惠券列表
    @response total_results(Number): 查询的总数量

    @request coupon_id(Number): (optional)优惠券的id，唯一标识这个优惠券
    @request denominations(Number): (optional)优惠券的面额，必须是3，5，10，20，50,100
    @request end_time(Date): (optional)优惠券的截止日期
    @request page_no(Number): (optional)查询的页号，结果集是分页返回的，每页20条
    @request page_size(Number): (optional)每页条数
    """
    REQUEST = {
        'coupon_id': {'type': topstruct.Number, 'is_required': False},
        'denominations': {'type': topstruct.Number, 'is_required': False},
        'end_time': {'type': topstruct.Date, 'is_required': False},
        'page_no': {'type': topstruct.Number, 'is_required': False},
        'page_size': {'type': topstruct.Number, 'is_required': False}
    }

    RESPONSE = {
        'coupons': {'type': topstruct.Coupon, 'is_list': False},
        'total_results': {'type': topstruct.Number, 'is_list': False}
    }

    API = 'taobao.promotion.coupons.get'


class PromotionLimitdiscountDetailGetRequest(TOPRequest):
    """ 限时打折详情查询。查询出指定限时打折的对应商品记录信息。

    @response item_discount_detail_list(LimitDiscountDetail): 限时打折对应的商品详情列表。

    @request limit_discount_id(Number): (required)限时打折ID。这个针对查询唯一限时打折情况。
    """
    REQUEST = {
        'limit_discount_id': {'type': topstruct.Number, 'is_required': True}
    }

    RESPONSE = {
        'item_discount_detail_list': {'type': topstruct.LimitDiscountDetail, 'is_list': False}
    }

    API = 'taobao.promotion.limitdiscount.detail.get'


class PromotionLimitdiscountGetRequest(TOPRequest):
    """ 分页查询某个卖家的限时打折信息。每页20条数据，按照结束时间降序排列。也可指定某一个限时打折id查询唯一的限时打折信息。

    @response limit_discount_list(LimitDiscount): 限时打折列表。
    @response total_count(Number): 满足该查询条件的限时打折总数量。

    @request end_time(Date): (optional)限时打折结束时间。输入的时间会被截取，年月日有效，时分秒忽略。
    @request limit_discount_id(Number): (optional)限时打折ID。这个针对查询唯一限时打折情况。若此字段不为空，则说明操作为单条限时打折记录查询，其他字段忽略。若想分页按条件查询，这个字段置为空。
    @request page_number(Number): (optional)分页页号。默认1。当页数大于最大页数时，结果为最大页数的数据。
    @request start_time(Date): (optional)限时打折开始时间。输入的时间会被截取，年月日有效，时分秒忽略。
    @request status(String): (optional)限时打折活动状态。ALL:全部状态;OVER:已结束;DOING:进行中;PROPARE:未开始(只支持大写)。当limit_discount_id为空时，为空时，默认为全部的状态。
    """
    REQUEST = {
        'end_time': {'type': topstruct.Date, 'is_required': False},
        'limit_discount_id': {'type': topstruct.Number, 'is_required': False},
        'page_number': {'type': topstruct.Number, 'is_required': False},
        'start_time': {'type': topstruct.Date, 'is_required': False},
        'status': {'type': topstruct.String, 'is_required': False}
    }

    RESPONSE = {
        'limit_discount_list': {'type': topstruct.LimitDiscount, 'is_list': False},
        'total_count': {'type': topstruct.Number, 'is_list': False}
    }

    API = 'taobao.promotion.limitdiscount.get'


class PromotionMealGetRequest(TOPRequest):
    """ 搭配套餐查询。每个卖家最多创建50个搭配套餐，所以查询不会分页，会将所有的满足状态的搭配套餐全部查出。该接口不会校验商品的下架或库存为0，查询结果的状态表明搭配套餐在数据库中的状态，商品的状态请isv自己验证。在卖家后台页面点击查看会触发数据库状态的修改。

    @response meal_list(Meal): 搭配套餐列表。

    @request meal_id(Number): (optional)搭配套餐id
    @request status(String): (optional)套餐状态。有效：VALID;失效：INVALID(有效套餐为可使用的套餐,无效套餐为套餐中有商品下架或库存为0时)。默认时两种情况都会查询。
    """
    REQUEST = {
        'meal_id': {'type': topstruct.Number, 'is_required': False},
        'status': {'type': topstruct.String, 'is_required': False}
    }

    RESPONSE = {
        'meal_list': {'type': topstruct.Meal, 'is_list': False}
    }

    API = 'taobao.promotion.meal.get'


class UmpActivitiesGetRequest(TOPRequest):
    """ 查询活动列表

    @response contents(String): 营销活动内容，可以通过ump sdk来进行处理
    @response total_count(Number): 记录总数

    @request page_no(Number): (required)分页的页码
    @request page_size(Number): (required)每页的最大条数
    @request tool_id(Number): (required)工具id
    """
    REQUEST = {
        'page_no': {'type': topstruct.Number, 'is_required': True},
        'page_size': {'type': topstruct.Number, 'is_required': True},
        'tool_id': {'type': topstruct.Number, 'is_required': True}
    }

    RESPONSE = {
        'contents': {'type': topstruct.String, 'is_list': False},
        'total_count': {'type': topstruct.Number, 'is_list': False}
    }

    API = 'taobao.ump.activities.get'


class UmpActivitiesListGetRequest(TOPRequest):
    """ 按照营销活动id的列表ids，查询对应的营销活动列表。

    @response activities(String): 营销活动列表！

    @request ids(Number): (required)营销活动id列表。
    """
    REQUEST = {
        'ids': {'type': topstruct.Number, 'is_required': True}
    }

    RESPONSE = {
        'activities': {'type': topstruct.String, 'is_list': False}
    }

    API = 'taobao.ump.activities.list.get'


class UmpActivityAddRequest(TOPRequest):
    """ 新增优惠活动。设置优惠活动的基本信息，比如活动时间，活动针对的对象（可以是满足某些条件的买家）

    @response act_id(Number): 活动id

    @request content(String): (required)活动内容，通过ump sdk里面的MarkeitngTool来生成
    @request tool_id(Number): (required)工具id
    """
    REQUEST = {
        'content': {'type': topstruct.String, 'is_required': True},
        'tool_id': {'type': topstruct.Number, 'is_required': True}
    }

    RESPONSE = {
        'act_id': {'type': topstruct.Number, 'is_list': False}
    }

    API = 'taobao.ump.activity.add'


class UmpActivityDeleteRequest(TOPRequest):
    """ 删除营销活动。对应的活动详情等将会被全部删除。

    @response is_success(Boolean): 调用是否成功

    @request act_id(Number): (required)活动id
    """
    REQUEST = {
        'act_id': {'type': topstruct.Number, 'is_required': True}
    }

    RESPONSE = {
        'is_success': {'type': topstruct.Boolean, 'is_list': False}
    }

    API = 'taobao.ump.activity.delete'


class UmpActivityGetRequest(TOPRequest):
    """ 查询营销活动

    @response content(String): 营销活动的内容，可以通过ump sdk中的marketingTool来完成对该内容的处理

    @request act_id(Number): (required)活动id
    """
    REQUEST = {
        'act_id': {'type': topstruct.Number, 'is_required': True}
    }

    RESPONSE = {
        'content': {'type': topstruct.String, 'is_list': False}
    }

    API = 'taobao.ump.activity.get'


class UmpActivityUpdateRequest(TOPRequest):
    """ 修改营销活动

    @response is_success(Boolean): 调用是否成功

    @request act_id(Number): (required)活动id
    @request content(String): (required)营销活动内容，json格式，通过ump sdk 的marketingTool来生成
    """
    REQUEST = {
        'act_id': {'type': topstruct.Number, 'is_required': True},
        'content': {'type': topstruct.String, 'is_required': True}
    }

    RESPONSE = {
        'is_success': {'type': topstruct.Boolean, 'is_list': False}
    }

    API = 'taobao.ump.activity.update'


class UmpChannelGetRequest(TOPRequest):
    """ 功能：获取渠道信息。
        说明：
        1、给出channel_keys时，返回所查询的渠道信息；
        2、channel_keys为空时，返回所有已维护的渠道信息。

    @response channels(ChannelInfo): 渠道信息。

    @request channel_keys(String): (optional)渠道代码以逗号(半角)隔开，若channel_keys为空，则返回所有已维护的渠道信息。
    """
    REQUEST = {
        'channel_keys': {'type': topstruct.String, 'is_required': False}
    }

    RESPONSE = {
        'channels': {'type': topstruct.ChannelInfo, 'is_list': False}
    }

    API = 'taobao.ump.channel.get'


class UmpChannelRemoveRequest(TOPRequest):
    """ 功能：删除渠道信息。
        说明：
        1、referers不为空，则从当前渠道中按照给定的referers删除对应的referer；若所有referer都被清空，渠道信息也将被删除。
        2、referers为空时，删除渠道信息及所有关联的referer。

    @response effect_referer_number(Number): 本次操作所影响到的referer个数。

    @request channel_key(String): (required)标示某个渠道的代码（由新增渠道时添加）。
    @request referers(String): (optional)当前渠道中，需要删除的referer地址。
        referers为空，删除当前渠道信息，同时清空当前渠道已关联的所有referer。
    """
    REQUEST = {
        'channel_key': {'type': topstruct.String, 'is_required': True},
        'referers': {'type': topstruct.String, 'is_required': False}
    }

    RESPONSE = {
        'effect_referer_number': {'type': topstruct.Number, 'is_list': False}
    }

    API = 'taobao.ump.channel.remove'


class UmpDetailAddRequest(TOPRequest):
    """ 增加活动详情。活动详情里面包括活动的范围（店铺，商品），活动的参数（比如具体的折扣），参与类型（全部，部分，部分不参加）等信息。当参与类型为部分或部分不参加的时候需要和taobao.ump.range.add来配合使用。

    @response detail_id(Number): 活动详情的id

    @request act_id(Number): (required)增加工具详情
    @request content(String): (required)活动详情内容，json格式，可以通过ump sdk中的MarketingTool来进行处理
    """
    REQUEST = {
        'act_id': {'type': topstruct.Number, 'is_required': True},
        'content': {'type': topstruct.String, 'is_required': True}
    }

    RESPONSE = {
        'detail_id': {'type': topstruct.Number, 'is_list': False}
    }

    API = 'taobao.ump.detail.add'


class UmpDetailDeleteRequest(TOPRequest):
    """ 删除活动详情

    @response is_success(Boolean): 是否成功

    @request detail_id(Number): (required)活动详情id
    """
    REQUEST = {
        'detail_id': {'type': topstruct.Number, 'is_required': True}
    }

    RESPONSE = {
        'is_success': {'type': topstruct.Boolean, 'is_list': False}
    }

    API = 'taobao.ump.detail.delete'


class UmpDetailGetRequest(TOPRequest):
    """ 查询活动详情

    @response content(String): 活动详情信息，可以通过ump sdk中的MarketingTool来进行处理

    @request detail_id(Number): (required)活动详情的id
    """
    REQUEST = {
        'detail_id': {'type': topstruct.Number, 'is_required': True}
    }

    RESPONSE = {
        'content': {'type': topstruct.String, 'is_list': False}
    }

    API = 'taobao.ump.detail.get'


class UmpDetailListAddRequest(TOPRequest):
    """ 批量添加营销活动。替代单条添加营销详情的的API。此接口适用针对某个营销活动的多档设置，会按顺序插入detail。若在整个事务过程中出现断点，会将已插入完成的detail_id返回，注意记录这些id，并将其删除，会对交易过程中的优惠产生影响。

    @response detail_id_list(Number): 返回对应的营销详情的id列表！若有某一条插入失败，会将插入成功的detail_id放到errorMessage里面返回，此时errorMessage里面会包含格式为(id1,id2,id3)的插入成功id列表。这些ids会对交易产生影响，通过截取此信息，将对应detail删除！

    @request act_id(Number): (required)营销活动id。
    @request details(String): (required)营销详情的列表。此列表由detail的json字符串组成。最多插入为10个。
    """
    REQUEST = {
        'act_id': {'type': topstruct.Number, 'is_required': True},
        'details': {'type': topstruct.String, 'is_required': True}
    }

    RESPONSE = {
        'detail_id_list': {'type': topstruct.Number, 'is_list': False}
    }

    API = 'taobao.ump.detail.list.add'


class UmpDetailUpdateRequest(TOPRequest):
    """ 更新活动详情

    @response is_success(Boolean): 调用是否成功

    @request content(String): (required)活动详情内容，可以通过ump sdk中的MarketingTool来生成这个内容
    @request detail_id(Number): (required)活动详情id
    """
    REQUEST = {
        'content': {'type': topstruct.String, 'is_required': True},
        'detail_id': {'type': topstruct.Number, 'is_required': True}
    }

    RESPONSE = {
        'is_success': {'type': topstruct.Boolean, 'is_list': False}
    }

    API = 'taobao.ump.detail.update'


class UmpDetailsGetRequest(TOPRequest):
    """ 分页查询优惠详情列表

    @response contents(String): 活动详情的信息
    @response total_count(Number): 记录总数

    @request act_id(Number): (required)营销活动id
    @request page_no(Number): (required)分页的页码
    @request page_size(Number): (required)每页的最大条数
    """
    REQUEST = {
        'act_id': {'type': topstruct.Number, 'is_required': True},
        'page_no': {'type': topstruct.Number, 'is_required': True},
        'page_size': {'type': topstruct.Number, 'is_required': True}
    }

    RESPONSE = {
        'contents': {'type': topstruct.String, 'is_list': False},
        'total_count': {'type': topstruct.Number, 'is_list': False}
    }

    API = 'taobao.ump.details.get'


class UmpMbbGetbycodeRequest(TOPRequest):
    """ 根据营销积木块代码获取积木块。接口返回该代码最新版本的积木块。如果要查询某个非最新版本的积木块，可以使用积木块id查询接口。

    @response mbb(String): 营销积木块的内容，通过ump sdk来进行处理

    @request code(String): (required)营销积木块code
    """
    REQUEST = {
        'code': {'type': topstruct.String, 'is_required': True}
    }

    RESPONSE = {
        'mbb': {'type': topstruct.String, 'is_list': False}
    }

    API = 'taobao.ump.mbb.getbycode'


class UmpMbbGetbyidRequest(TOPRequest):
    """ 根据积木块id获取营销积木块。

    @response mbb(String): 营销积木块定义信息，可以通过ump sdk里面的MBB.fromJson来处理

    @request id(Number): (required)积木块的id
    """
    REQUEST = {
        'id': {'type': topstruct.Number, 'is_required': True}
    }

    RESPONSE = {
        'mbb': {'type': topstruct.String, 'is_list': False}
    }

    API = 'taobao.ump.mbb.getbyid'


class UmpMbbsGetRequest(TOPRequest):
    """ 获取营销积木块列表，可以根据类型获取，也可以将该字段设为空，获取所有的

    @response mbbs(String): 营销积木块内容列表，内容为json格式的，可以通过ump sdk里面的MBB.fromJson来处理

    @request type(String): (optional)积木块类型。如果该字段为空表示查出所有类型的
        现在有且仅有如下几种：resource,condition,action,target
    """
    REQUEST = {
        'type': {'type': topstruct.String, 'is_required': False}
    }

    RESPONSE = {
        'mbbs': {'type': topstruct.String, 'is_list': False}
    }

    API = 'taobao.ump.mbbs.get'


class UmpMbbsListGetRequest(TOPRequest):
    """ 通过营销积木id列表来获取营销积木块列表。

    @response mbbs(String): 营销积木块内容列表，内容为json格式的，可以通过ump sdk里面的MBB.fromJson来处理

    @request ids(Number): (required)营销积木块id组成的字符串。
    """
    REQUEST = {
        'ids': {'type': topstruct.Number, 'is_required': True}
    }

    RESPONSE = {
        'mbbs': {'type': topstruct.String, 'is_list': False}
    }

    API = 'taobao.ump.mbbs.list.get'


class UmpRangeAddRequest(TOPRequest):
    """ 指定某项活动中，某个商家的某些类型物品（指定商品，指定类目或者别的）参加或者不参加活动。当活动详情的参与类型为部分或者部分不参加的时候，需要指定具体哪部分参加或者不参加，使用本接口完成操作。比如部分商品满就送，这里的range用来指定具体哪些商品参加满就送活动。

    @response is_success(Boolean): 是否成功

    @request act_id(Number): (required)活动id
    @request ids(String): (required)id列表，当范围类型为商品时，该id为商品id；当范围类型为类目时，该id为类目id.多个id用逗号隔开，一次不超过50个
    @request type(Number): (required)范围的类型，比如是全店，商品，类目
        见：MarketingConstants.PARTICIPATE_TYPE_*
    """
    REQUEST = {
        'act_id': {'type': topstruct.Number, 'is_required': True},
        'ids': {'type': topstruct.String, 'is_required': True},
        'type': {'type': topstruct.Number, 'is_required': True}
    }

    RESPONSE = {
        'is_success': {'type': topstruct.Boolean, 'is_list': False}
    }

    API = 'taobao.ump.range.add'


class UmpRangeDeleteRequest(TOPRequest):
    """ 去指先前指定在某项活动中，某些类型的物品参加或者不参加活动的设置

    @response is_success(Boolean): 调用是否成功

    @request act_id(Number): (required)活动id
    @request ids(String): (required)id列表，当范围类型为商品时，该id为商品id；当范围类型为类目时，该id为类目id
    @request type(Number): (required)范围的类型，比如是全店，商品，类目见：MarketingConstants.PARTICIPATE_TYPE_*
    """
    REQUEST = {
        'act_id': {'type': topstruct.Number, 'is_required': True},
        'ids': {'type': topstruct.String, 'is_required': True},
        'type': {'type': topstruct.Number, 'is_required': True}
    }

    RESPONSE = {
        'is_success': {'type': topstruct.Boolean, 'is_list': False}
    }

    API = 'taobao.ump.range.delete'


class UmpRangeGetRequest(TOPRequest):
    """ 查询某个卖家所有参加或者不参加某项活动的物品

    @response ranges(Range): 营销范围类列表！

    @request act_id(Number): (required)活动id
    """
    REQUEST = {
        'act_id': {'type': topstruct.Number, 'is_required': True}
    }

    RESPONSE = {
        'ranges': {'type': topstruct.Range, 'is_list': False}
    }

    API = 'taobao.ump.range.get'


class UmpToolAddRequest(TOPRequest):
    """ 新增优惠工具。通过ump sdk来完成将积木块拼装成为工具的操作，再使用本接口上传优惠工具。

    @response tool_id(Number): 工具id

    @request content(String): (required)工具内容，由sdk里面的MarketingTool生成的json字符串
    """
    REQUEST = {
        'content': {'type': topstruct.String, 'is_required': True}
    }

    RESPONSE = {
        'tool_id': {'type': topstruct.Number, 'is_list': False}
    }

    API = 'taobao.ump.tool.add'


class UmpToolDeleteRequest(TOPRequest):
    """ 删除营销工具。当工具正在被使用的时候，是不能被删除的。

    @response is_success(Boolean): 是否成功

    @request tool_id(Number): (required)营销工具id
    """
    REQUEST = {
        'tool_id': {'type': topstruct.Number, 'is_required': True}
    }

    RESPONSE = {
        'is_success': {'type': topstruct.Boolean, 'is_list': False}
    }

    API = 'taobao.ump.tool.delete'


class UmpToolGetRequest(TOPRequest):
    """ 根据工具id获取一个工具对象

    @response content(String): 工具信息内容，格式为json，可以通过提供给的sdk里面的MarketingBuilder来处理这个内容

    @request tool_id(Number): (required)工具的id
    """
    REQUEST = {
        'tool_id': {'type': topstruct.Number, 'is_required': True}
    }

    RESPONSE = {
        'content': {'type': topstruct.String, 'is_list': False}
    }

    API = 'taobao.ump.tool.get'


class UmpToolUpdateRequest(TOPRequest):
    """ 修改工具

    @response tool_id(Number): 更新后生成的新的工具id

    @request content(String): (required)工具的内容，由sdk的marketingBuilder生成
    @request tool_id(Number): (required)工具id
    """
    REQUEST = {
        'content': {'type': topstruct.String, 'is_required': True},
        'tool_id': {'type': topstruct.Number, 'is_required': True}
    }

    RESPONSE = {
        'tool_id': {'type': topstruct.Number, 'is_list': False}
    }

    API = 'taobao.ump.tool.update'


class UmpToolsGetRequest(TOPRequest):
    """ 查询工具列表

    @response tools(String): 工具列表，单个内容为json格式，需要通过ump的sdk提供的MarketingBuilder来进行处理

    @request tool_code(String): (optional)工具编码
    """
    REQUEST = {
        'tool_code': {'type': topstruct.String, 'is_required': False}
    }

    RESPONSE = {
        'tools': {'type': topstruct.String, 'is_list': False}
    }

    API = 'taobao.ump.tools.get'


class TaohuaAudioreaderAlbumGetRequest(TOPRequest):
    """ 根据商品ID获取有声读物专辑信息

    @response audioreader_album(TaohuaAudioReaderAlbum): 有声读物专辑

    @request item_id(Number): (required)有声读物商品ID
    """
    REQUEST = {
        'item_id': {'type': topstruct.Number, 'is_required': True}
    }

    RESPONSE = {
        'audioreader_album': {'type': topstruct.TaohuaAudioReaderAlbum, 'is_list': False}
    }

    API = 'taobao.taohua.audioreader.album.get'


class TaohuaAudioreaderMyalbumsGetRequest(TOPRequest):
    """ 根据用户ID获取其购买的有声书库专辑列表

    @response my_audioreader_albums(TaohuaAudioReaderMyAlbum): 我的有声书库专辑列表
    @response total_count(Number): 我的有声书库专辑数

    @request page_no(Number): (optional)当前页码
    @request page_size(Number): (optional)每页个数
    """
    REQUEST = {
        'page_no': {'type': topstruct.Number, 'is_required': False},
        'page_size': {'type': topstruct.Number, 'is_required': False}
    }

    RESPONSE = {
        'my_audioreader_albums': {'type': topstruct.TaohuaAudioReaderMyAlbum, 'is_list': False},
        'total_count': {'type': topstruct.Number, 'is_list': False}
    }

    API = 'taobao.taohua.audioreader.myalbums.get'


class TaohuaAudioreaderMytracksGetRequest(TOPRequest):
    """ 根据用户ID、专辑ID和购买专辑的序列ID获取我的有声书库单曲列表

    @response my_audioreader_tracks(TaohuaAudioReaderTrack): 我的有声书库单曲列表
    @response total_count(Number): 我的有声书库单曲数

    @request page_no(Number): (optional)当前页码
    @request page_size(Number): (optional)每页个数
    @request serial_id(Number): (required)购买专辑的序列ID
    """
    REQUEST = {
        'page_no': {'type': topstruct.Number, 'is_required': False},
        'page_size': {'type': topstruct.Number, 'is_required': False},
        'serial_id': {'type': topstruct.Number, 'is_required': True}
    }

    RESPONSE = {
        'my_audioreader_tracks': {'type': topstruct.TaohuaAudioReaderTrack, 'is_list': False},
        'total_count': {'type': topstruct.Number, 'is_list': False}
    }

    API = 'taobao.taohua.audioreader.mytracks.get'


class TaohuaAudioreaderRecommendGetRequest(TOPRequest):
    """ 获取花匠推荐的有声读物专辑列表，分为最近更新和热门两种

    @response audioreader_summaries(TaohuaAudioReaderAlbumSummary): 有声读物专辑摘要列表
    @response total_count(Number): 符合条件的专辑总数

    @request item_type(String): (required)推荐专辑的类型，有两个可选项，recent:最近更新，hot:热门
    @request page_no(Number): (optional)当前页码
    @request page_size(Number): (optional)每页个数
    """
    REQUEST = {
        'item_type': {'type': topstruct.String, 'is_required': True},
        'page_no': {'type': topstruct.Number, 'is_required': False},
        'page_size': {'type': topstruct.Number, 'is_required': False}
    }

    RESPONSE = {
        'audioreader_summaries': {'type': topstruct.TaohuaAudioReaderAlbumSummary, 'is_list': False},
        'total_count': {'type': topstruct.Number, 'is_list': False}
    }

    API = 'taobao.taohua.audioreader.recommend.get'


class TaohuaAudioreaderSearchRequest(TOPRequest):
    """ 根据条件搜索有声读物专辑

    @response audioreader_search_results(TaohuaAudioReaderAlbumSummary): 有声读物专辑摘要列表
    @response total_count(Number): 搜索返回的专辑总数

    @request cid(Number): (optional)类目id
    @request free(Boolean): (optional)是否免费，如果为true则表示只搜索免费的商品
    @request keyword(String): (optional)查询关键字,超过60个字符则自动截断为60个字符. 允许为空
    @request page_no(Number): (optional)当前页码
    @request page_size(Number): (optional)每页个数
    @request sort(String): (optional)排序值: 1. 评分排序：ratescoredesc, 2. 价格升序：priceasc, 3. 价格降序：pricedesc, 4. 最新发布：shelvesdate, 5. 最多浏览：viewcount, 6. 销量升序：saleasc, 7. 销量降序：saledesc, 8. 最受欢迎：favoritedesc, 9. 默认排序：default
    """
    REQUEST = {
        'cid': {'type': topstruct.Number, 'is_required': False},
        'free': {'type': topstruct.Boolean, 'is_required': False},
        'keyword': {'type': topstruct.String, 'is_required': False},
        'page_no': {'type': topstruct.Number, 'is_required': False},
        'page_size': {'type': topstruct.Number, 'is_required': False},
        'sort': {'type': topstruct.String, 'is_required': False}
    }

    RESPONSE = {
        'audioreader_search_results': {'type': topstruct.TaohuaAudioReaderAlbumSummary, 'is_list': False},
        'total_count': {'type': topstruct.Number, 'is_list': False}
    }

    API = 'taobao.taohua.audioreader.search'


class TaohuaAudioreaderTrackAuditionurlGetRequest(TOPRequest):
    """ 获取有声读物单曲试听地址

    @response url(String): 有声读物单曲试听地址

    @request item_id(Number): (required)单曲商品ID
    """
    REQUEST = {
        'item_id': {'type': topstruct.Number, 'is_required': True}
    }

    RESPONSE = {
        'url': {'type': topstruct.String, 'is_list': False}
    }

    API = 'taobao.taohua.audioreader.track.auditionurl.get'


class TaohuaAudioreaderTrackDownloadurlGetRequest(TOPRequest):
    """ 获取有声读物单曲下载地址

    @response url(String): 有声读物单曲下载地址

    @request item_id(Number): (required)单曲商品ID
    """
    REQUEST = {
        'item_id': {'type': topstruct.Number, 'is_required': True}
    }

    RESPONSE = {
        'url': {'type': topstruct.String, 'is_list': False}
    }

    API = 'taobao.taohua.audioreader.track.downloadurl.get'


class TaohuaAudioreaderTracksGetRequest(TOPRequest):
    """ 根据有声读物专辑商品ID获取单曲信息

    @response audioreader_tracks(TaohuaAudioReaderTrack): 有声读物单曲列表
    @response total_count(Number): 专辑内的单曲总数

    @request item_id(Number): (required)有声读物专辑ID
    @request page_no(Number): (optional)当前页码
    @request page_size(Number): (optional)每页个数
    """
    REQUEST = {
        'item_id': {'type': topstruct.Number, 'is_required': True},
        'page_no': {'type': topstruct.Number, 'is_required': False},
        'page_size': {'type': topstruct.Number, 'is_required': False}
    }

    RESPONSE = {
        'audioreader_tracks': {'type': topstruct.TaohuaAudioReaderTrack, 'is_list': False},
        'total_count': {'type': topstruct.Number, 'is_list': False}
    }

    API = 'taobao.taohua.audioreader.tracks.get'


class TaohuaBoughtitemIsRequest(TOPRequest):
    """ 判断用户是否购买过该商品

    @response is_bought(Boolean): 返回结果，true代表该商品已经被购买过，false代表该商品还没有被购买过

    @request item_id(Number): (required)商品ID
    """
    REQUEST = {
        'item_id': {'type': topstruct.Number, 'is_required': True}
    }

    RESPONSE = {
        'is_bought': {'type': topstruct.Boolean, 'is_list': False}
    }

    API = 'taobao.taohua.boughtitem.is'


class TaohuaChildcatesGetRequest(TOPRequest):
    """ 通过类目ID获取它的类目列表

    @response taohua_categories(TaohuaCategory): 淘花类目数据结构
    @response total_cates(Number): 总类目数

    @request cate_id(Number): (optional)通过类目ID获取它的子类目列表
    """
    REQUEST = {
        'cate_id': {'type': topstruct.Number, 'is_required': False}
    }

    RESPONSE = {
        'taohua_categories': {'type': topstruct.TaohuaCategory, 'is_list': False},
        'total_cates': {'type': topstruct.Number, 'is_list': False}
    }

    API = 'taobao.taohua.childcates.get'


class TaohuaDirectoryGetRequest(TOPRequest):
    """ 根据文档商品的ID获取文档目录

    @response tree_vo(TaohuaRootDirectory): 淘花文档目录

    @request item_id(Number): (required)文档商品ID
    """
    REQUEST = {
        'item_id': {'type': topstruct.Number, 'is_required': True}
    }

    RESPONSE = {
        'tree_vo': {'type': topstruct.TaohuaRootDirectory, 'is_list': False}
    }

    API = 'taobao.taohua.directory.get'


class TaohuaItemLikeRequest(TOPRequest):
    """ 用户调本接口后，对应的商品喜欢值加1

    @response like_result(String): 成功返回success

    @request item_id(Number): (required)商品ID
    """
    REQUEST = {
        'item_id': {'type': topstruct.Number, 'is_required': True}
    }

    RESPONSE = {
        'like_result': {'type': topstruct.String, 'is_list': False}
    }

    API = 'taobao.taohua.item.like'


class TaohuaItemcommentAddRequest(TOPRequest):
    """ 对指定商品发表评论

    @response add_comment_result(String): 发表评论成功标志

    @request comment(String): (required)对商品的评论内容
    @request item_id(Number): (required)商品ID
    """
    REQUEST = {
        'comment': {'type': topstruct.String, 'is_required': True},
        'item_id': {'type': topstruct.Number, 'is_required': True}
    }

    RESPONSE = {
        'add_comment_result': {'type': topstruct.String, 'is_list': False}
    }

    API = 'taobao.taohua.itemcomment.add'


class TaohuaItemcommentsGetRequest(TOPRequest):
    """ 获取淘花指定商品的评论列表

    @response taohua_comments_result(TaohuaItemCommentResult): 淘花商品评论

    @request item_id(Number): (required)指定商品的ID
    @request page_no(Number): (optional)页码。
        取值范围：大于零的整数
        默认值：1 即返回第一页数据
    @request page_size(Number): (optional)每页记录数
        取值范围：大于零的整数
        默认值：10 即每页返回10条数据
    """
    REQUEST = {
        'item_id': {'type': topstruct.Number, 'is_required': True},
        'page_no': {'type': topstruct.Number, 'is_required': False},
        'page_size': {'type': topstruct.Number, 'is_required': False}
    }

    RESPONSE = {
        'taohua_comments_result': {'type': topstruct.TaohuaItemCommentResult, 'is_list': False}
    }

    API = 'taobao.taohua.itemcomments.get'


class TaohuaItemdetailGetRequest(TOPRequest):
    """ 商品详情接口

    @response taohua_item_detail(TaohuaItem): 淘花商品数据结构

    @request item_id(Number): (required)商品ID
    """
    REQUEST = {
        'item_id': {'type': topstruct.Number, 'is_required': True}
    }

    RESPONSE = {
        'taohua_item_detail': {'type': topstruct.TaohuaItem, 'is_list': False}
    }

    API = 'taobao.taohua.itemdetail.get'


class TaohuaItempayurlGetRequest(TOPRequest):
    """ 获取商品支付链接API

    @response url(String): 支付URL

    @request item_id(Number): (required)商品ID
    """
    REQUEST = {
        'item_id': {'type': topstruct.Number, 'is_required': True}
    }

    RESPONSE = {
        'url': {'type': topstruct.String, 'is_list': False}
    }

    API = 'taobao.taohua.itempayurl.get'


class TaohuaItemresurlGetRequest(TOPRequest):
    """ 获取商品资源下载链接。
        URL调用示例：
        http://gw.api.taobao.com/router/rest?timestamp=1982-07-27 06:06:06&method=taobao.taohua.itemresurl.get&app_key=2005&session=XXXXX&sign=ERITJKEIJKJHKKKKKKKHJEREEEEEEEEEEE&item_id=3365&position=3652

    @response url(String): 下载链接地址.

    @request file_type(String): (required)商品资源的下载文件类型，可选值：1、pdf，2、epub，3、src。
        dpf代表下载pdf类型的文件，epub代表下载epub类型的文件，src代表下载源文件
    @request item_id(Number): (required)商品ID
    @request position(String): (optional)因为下载地址涉及到断点续传的功能，所以需要客户端高速服务器端，应该从哪个byte开始返回文件流，那么这个字段作用就是用于告诉服务端从指定位置读取文件流
    """
    REQUEST = {
        'file_type': {'type': topstruct.String, 'is_required': True},
        'item_id': {'type': topstruct.Number, 'is_required': True},
        'position': {'type': topstruct.String, 'is_required': False}
    }

    RESPONSE = {
        'url': {'type': topstruct.String, 'is_list': False}
    }

    API = 'taobao.taohua.itemresurl.get'


class TaohuaItemsSearchRequest(TOPRequest):
    """ 商品搜索列表接口

    @response search_items_result(TaohuaSearchItems): 商品搜索列表数据结构

    @request begin_size(String): (optional)文件最小size,单位byte。
    @request cid(Number): (optional)类目id
    @request end_size(String): (optional)文件最大size,单位byte。
    @request file_type(String): (optional)按照文件类型来搜索
    @request free(Boolean): (optional)是否免费，如果为true则表示只搜索免费的商品。
    @request keywords(String): (optional)查询关键字,超过60好字符则自动截断为60个字符.  默认允许为null
    @request page_no(Number): (optional)分页搜索商品信息，page_no代表的是第几页
    @request page_size(Number): (optional)分页搜索商品信息，page_size代表：每页显示多少条数据。  目前最少5条，最多30条数据。
    @request sort(String): (optional)排序值:
        1. 评分排序：ratescoredesc,
        2. 价格升序: priceasc,
        3. 价格降序: pricedesc,
        4. 时间排序: shelvesdate,
        5. 浏览排序：viewcount,
        6. 销量升序：saleasc,
        7. 默认排序：default,
    """
    REQUEST = {
        'begin_size': {'type': topstruct.String, 'is_required': False},
        'cid': {'type': topstruct.Number, 'is_required': False},
        'end_size': {'type': topstruct.String, 'is_required': False},
        'file_type': {'type': topstruct.String, 'is_required': False},
        'free': {'type': topstruct.Boolean, 'is_required': False},
        'keywords': {'type': topstruct.String, 'is_required': False},
        'page_no': {'type': topstruct.Number, 'is_required': False},
        'page_size': {'type': topstruct.Number, 'is_required': False},
        'sort': {'type': topstruct.String, 'is_required': False}
    }

    RESPONSE = {
        'search_items_result': {'type': topstruct.TaohuaSearchItems, 'is_list': False}
    }

    API = 'taobao.taohua.items.search'


class TaohuaLatestupdateinfoGetRequest(TOPRequest):
    """ 获取最新更新信息

    @response taohua_update_info(TaohuaUpdateInfo): 更新信息版本号
    """
    REQUEST = {}

    RESPONSE = {
        'taohua_update_info': {'type': topstruct.TaohuaUpdateInfo, 'is_list': False}
    }

    API = 'taobao.taohua.latestupdateinfo.get'


class TaohuaOrdersGetRequest(TOPRequest):
    """ 查询买家订单列表

    @response taohua_order_result(TaohuaOrders): 淘花订单列表数据结构对象

    @request end_date(String): (optional)默认为当前时间， 日期格式精确到天数
    @request page_no(Number): (optional)分页获取订单列表信息，page_no代表的是第几页
    @request page_size(Number): (optional)分页获取订单列表信息，page_size代表每页显示多少条。  注意：每页显示条数。最小5条，最多30条，凡是超出范围的条数，都会被默认为10条。
    @request start_date(String): (optional)系统默认为：当前时间-90天。  日期精确到日
    @request trade_status(String): (optional)查询的交易状态：
        1.	全部 all
        2.	等待买家付款 wait_pay
        3.	交易成功 trade_suc
        4.	交易关闭 trade_close
    """
    REQUEST = {
        'end_date': {'type': topstruct.String, 'is_required': False},
        'page_no': {'type': topstruct.Number, 'is_required': False},
        'page_size': {'type': topstruct.Number, 'is_required': False},
        'start_date': {'type': topstruct.String, 'is_required': False},
        'trade_status': {'type': topstruct.String, 'is_required': False}
    }

    RESPONSE = {
        'taohua_order_result': {'type': topstruct.TaohuaOrders, 'is_list': False}
    }

    API = 'taobao.taohua.orders.get'


class TaohuaPreviewurlGetRequest(TOPRequest):
    """ 获取商品预览链接

    @response url(String): 预览链接

    @request file_type(String): (required)用来区分要预览的文档类型,目前支持两种
        pre_epub 预览epub文档
        pre_pdf  预览pdf文档
    @request item_id(Number): (required)商品ID
    @request position(String): (required)文件位置
    """
    REQUEST = {
        'file_type': {'type': topstruct.String, 'is_required': True},
        'item_id': {'type': topstruct.Number, 'is_required': True},
        'position': {'type': topstruct.String, 'is_required': True}
    }

    RESPONSE = {
        'url': {'type': topstruct.String, 'is_list': False}
    }

    API = 'taobao.taohua.previewurl.get'


class TaohuaStaffrecitemsGetRequest(TOPRequest):
    """ 获取小二推荐的商品

    @response taohua_items(TaohuaItem): 淘花商品数据结构列表
    @response total_items(Number): 总商品数量

    @request item_type(String): (required)推荐的商品类型:
        1. free:获取推荐的免费商品
        2. charges:获取推荐的收费商品
    @request page_no(Number): (optional)当前页数，大于0的整数，默认值1，代表第一页
    @request page_size(Number): (optional)每页显示最大条数，要求：大于0的整数。默认为5，代表每页显示5条
    """
    REQUEST = {
        'item_type': {'type': topstruct.String, 'is_required': True},
        'page_no': {'type': topstruct.Number, 'is_required': False},
        'page_size': {'type': topstruct.Number, 'is_required': False}
    }

    RESPONSE = {
        'taohua_items': {'type': topstruct.TaohuaItem, 'is_list': False},
        'total_items': {'type': topstruct.Number, 'is_list': False}
    }

    API = 'taobao.taohua.staffrecitems.get'


class HotelAddRequest(TOPRequest):
    """ 此接口用于新增一个酒店，酒店的发布者是当前会话的用户。
        该接口发出的是一个酒店申请，需要淘宝小二审核。

    @response hotel(Hotel): 酒店结构

    @request address(String): (required)酒店地址。长度不能超过120
    @request city(Number): (required)城市编码。参见：http://kezhan.trip.taobao.com/area.html，domestic为false时默认为0
    @request country(String): (required)domestic为true时，固定China；
        domestic为false时，必须传定义的海外国家编码值。参见：http://kezhan.trip.taobao.com/countrys.html
    @request decorate_time(String): (optional)装修年份。长度不能超过4。
    @request desc(String): (required)酒店介绍。不超过25000个汉字
    @request district(Number): (optional)区域（县级市）编码。参见：http://kezhan.trip.taobao.com/area.html
    @request domestic(Boolean): (required)是否国内酒店。可选值：true，false
    @request level(String): (required)酒店级别。可选值：A,B,C,D,E,F。代表客栈公寓、经济连锁、二星级/以下、三星级/舒适、四星级/高档、五星级/豪华
    @request name(String): (required)酒店名称。不能超过60
    @request opening_time(String): (optional)开业年份。长度不能超过4。
    @request orientation(String): (required)酒店定位。可选值：T,B。代表旅游度假、商务出行
    @request pic(Image): (required)酒店图片。最大长度:500K。支持的文件类型：gif,jpg,png
    @request province(Number): (required)省份编码。参见：http://kezhan.trip.taobao.com/area.html，domestic为false时默认为0
    @request rooms(Number): (optional)房间数。长度不能超过4。
    @request service(String): (optional)交通距离与设施服务。JSON格式。cityCenterDistance、railwayDistance、airportDistance分别代表距离市中心、距离火车站、距离机场公里数，为不超过3位正整数，默认-1代表无数据。
        其他key值true代表有此服务，false代表没有。
        parking：停车场，airportShuttle：机场接送，rentCar：租车，meetingRoom：会议室，businessCenter：商务中心，swimmingPool：游泳池，fitnessClub：健身中心，laundry：洗衣服务，morningCall：叫早服务，bankCard：接受银行卡，creditCard：接受信用卡，chineseRestaurant：中餐厅，westernRestaurant：西餐厅，cafe：咖啡厅，bar：酒吧，ktv：KTV。
    @request site_param(String): (optional)接入卖家数据主键
    @request storeys(Number): (optional)楼层数。长度不能超过4。
    @request tel(String): (optional)酒店电话。格式：国家代码（最长6位）#区号（最长4位）#电话（最长20位）。国家代码提示：中国大陆0086、香港00852、澳门00853、台湾00886
    """
    REQUEST = {
        'address': {'type': topstruct.String, 'is_required': True},
        'city': {'type': topstruct.Number, 'is_required': True},
        'country': {'type': topstruct.String, 'is_required': True},
        'decorate_time': {'type': topstruct.String, 'is_required': False},
        'desc': {'type': topstruct.String, 'is_required': True},
        'district': {'type': topstruct.Number, 'is_required': False},
        'domestic': {'type': topstruct.Boolean, 'is_required': True},
        'level': {'type': topstruct.String, 'is_required': True},
        'name': {'type': topstruct.String, 'is_required': True},
        'opening_time': {'type': topstruct.String, 'is_required': False},
        'orientation': {'type': topstruct.String, 'is_required': True},
        'pic': {'type': topstruct.Image, 'is_required': True},
        'province': {'type': topstruct.Number, 'is_required': True},
        'rooms': {'type': topstruct.Number, 'is_required': False},
        'service': {'type': topstruct.String, 'is_required': False},
        'site_param': {'type': topstruct.String, 'is_required': False},
        'storeys': {'type': topstruct.Number, 'is_required': False},
        'tel': {'type': topstruct.String, 'is_required': False}
    }

    RESPONSE = {
        'hotel': {'type': topstruct.Hotel, 'is_list': False}
    }

    API = 'taobao.hotel.add'


class HotelGetRequest(TOPRequest):
    """ 此接口用于查询一个酒店，根据传入的酒店hid查询酒店信息。

    @response hotel(Hotel): 酒店结构

    @request hid(Number): (required)要查询的酒店id。必须为数字
    @request need_room_type(Boolean): (optional)是否需要返回该酒店的房型列表。可选值：true，false。
    """
    REQUEST = {
        'hid': {'type': topstruct.Number, 'is_required': True},
        'need_room_type': {'type': topstruct.Boolean, 'is_required': False}
    }

    RESPONSE = {
        'hotel': {'type': topstruct.Hotel, 'is_list': False}
    }

    API = 'taobao.hotel.get'


class HotelImageUploadRequest(TOPRequest):
    """ 酒店图片上传

    @response hotel_image(HotelImage): 酒店图片

    @request hid(Number): (required)酒店id
    @request pic(Image): (required)上传的图片
    """
    REQUEST = {
        'hid': {'type': topstruct.Number, 'is_required': True},
        'pic': {'type': topstruct.Image, 'is_required': True}
    }

    RESPONSE = {
        'hotel_image': {'type': topstruct.HotelImage, 'is_list': False}
    }

    API = 'taobao.hotel.image.upload'


class HotelNameGetRequest(TOPRequest):
    """ 此接口用于查询一个酒店，根据传入的酒店名称/别名查询酒店信息。

    @response hotel(Hotel): 酒店结构

    @request city(Number): (optional)城市编码。参见：http://kezhan.trip.taobao.com/area.html。
        domestic为true时，province,city,district不能同时为空或为0
    @request country(String): (optional)domestic为true时，固定China；
        domestic为false时，必须传定义的海外国家编码值，是必填项。参见：http://kezhan.trip.taobao.com/countrys.html
    @request district(Number): (optional)区域（县级市）编码。参见：http://kezhan.trip.taobao.com/area.html。
        domestic为true时，province,city,district不能同时为空或为0
    @request domestic(Boolean): (required)是否国内酒店。可选值：true，false
    @request name(String): (required)酒店全部名称/别名。不能超过60字节
    @request province(Number): (optional)省份编码。参见：http://kezhan.trip.taobao.com/area.html。
        domestic为true时，province,city,district不能同时为空或为0
    """
    REQUEST = {
        'city': {'type': topstruct.Number, 'is_required': False},
        'country': {'type': topstruct.String, 'is_required': False},
        'district': {'type': topstruct.Number, 'is_required': False},
        'domestic': {'type': topstruct.Boolean, 'is_required': True},
        'name': {'type': topstruct.String, 'is_required': True},
        'province': {'type': topstruct.Number, 'is_required': False}
    }

    RESPONSE = {
        'hotel': {'type': topstruct.Hotel, 'is_list': False}
    }

    API = 'taobao.hotel.name.get'


class HotelOrderBookingFeedbackRequest(TOPRequest):
    """ 下单结果回传

    @response is_success(Boolean): 接口调用是否成功

    @request failed_reason(String): (optional)失败原因,当result为failed时,此项为必填，最长200个字符
    @request message_id(String): (required)指令消息中的messageid,最长128字符
    @request oid(Number): (optional)酒店订单id
    @request out_oid(String): (required)合作方订单号,最长250个字符
    @request refund_code(String): (optional)在合作方退订时可能要用到的标识码，最长250个字符
    @request result(String): (required)预订结果
        S:成功
        F:失败
    @request session_id(Number): (required)指令消息中的session_id
    """
    REQUEST = {
        'failed_reason': {'type': topstruct.String, 'is_required': False},
        'message_id': {'type': topstruct.String, 'is_required': True},
        'oid': {'type': topstruct.Number, 'is_required': False},
        'out_oid': {'type': topstruct.String, 'is_required': True},
        'refund_code': {'type': topstruct.String, 'is_required': False},
        'result': {'type': topstruct.String, 'is_required': True},
        'session_id': {'type': topstruct.Number, 'is_required': True}
    }

    RESPONSE = {
        'is_success': {'type': topstruct.Boolean, 'is_list': False}
    }

    API = 'taobao.hotel.order.booking.feedback'


class HotelOrderGetRequest(TOPRequest):
    """ 此接口用于查询一个酒店订单，根据传入的订单号查询订单信息。

    @response hotel_order(HotelOrder): 订单结构，是否返回入住人列表根据参数决定

    @request need_guest(Boolean): (optional)是否需要返回该订单的入住人列表。可选值：true，false。
    @request need_message(Boolean): (optional)是否显示买家留言，可选值true、false
    @request oid(Number): (special)酒店订单oid，必须为数字。oid，tid必须传一项，同时传递的情况下，作为查询条件的优先级由高到低依次为oid，tid。
    @request tid(Number): (special)淘宝订单tid，必须为数字。oid，tid必须传一项，同时传递的情况下，作为查询条件的优先级由高到低依次为oid，tid。
    """
    REQUEST = {
        'need_guest': {'type': topstruct.Boolean, 'is_required': False},
        'need_message': {'type': topstruct.Boolean, 'is_required': False},
        'oid': {'type': topstruct.Number, 'is_required': False},
        'tid': {'type': topstruct.Number, 'is_required': False}
    }

    RESPONSE = {
        'hotel_order': {'type': topstruct.HotelOrder, 'is_list': False}
    }

    API = 'taobao.hotel.order.get'


class HotelOrderPayFeedbackRequest(TOPRequest):
    """ 支付确认结果回传

    @response is_success(Boolean): 接口调用是否成功

    @request failed_reason(String): (optional)失败原因,当result为failed时,此项为必填，最长200个字符
    @request message_id(String): (required)指令消息中的messageid,最长128字符
    @request oid(Number): (optional)酒店订单id
    @request out_oid(String): (required)合作方订单号,最长250个字符
    @request result(String): (required)预订结果
        S:成功
        F:失败
    @request session_id(Number): (required)指令消息中的session_id
    """
    REQUEST = {
        'failed_reason': {'type': topstruct.String, 'is_required': False},
        'message_id': {'type': topstruct.String, 'is_required': True},
        'oid': {'type': topstruct.Number, 'is_required': False},
        'out_oid': {'type': topstruct.String, 'is_required': True},
        'result': {'type': topstruct.String, 'is_required': True},
        'session_id': {'type': topstruct.Number, 'is_required': True}
    }

    RESPONSE = {
        'is_success': {'type': topstruct.Boolean, 'is_list': False}
    }

    API = 'taobao.hotel.order.pay.feedback'


class HotelOrderRefundFeedbackRequest(TOPRequest):
    """ 退订处理结果回传

    @response is_success(Boolean): 接口调用是否成功

    @request failed_reason(String): (optional)失败原因,当result为F时,此项为必填,最长200个字符
    @request message_id(String): (required)指令消息中的messageid,最长128字符
    @request oid(Number): (optional)合作方订单号,最长250个字符
    @request out_oid(String): (required)合作方订单号,最长250个字符
    @request result(String): (required)预订结果
        S:成功
        F:失败
    @request session_id(Number): (required)指令消息中的session_id
    """
    REQUEST = {
        'failed_reason': {'type': topstruct.String, 'is_required': False},
        'message_id': {'type': topstruct.String, 'is_required': True},
        'oid': {'type': topstruct.Number, 'is_required': False},
        'out_oid': {'type': topstruct.String, 'is_required': True},
        'result': {'type': topstruct.String, 'is_required': True},
        'session_id': {'type': topstruct.Number, 'is_required': True}
    }

    RESPONSE = {
        'is_success': {'type': topstruct.Boolean, 'is_list': False}
    }

    API = 'taobao.hotel.order.refund.feedback'


class HotelOrdersSearchRequest(TOPRequest):
    """ 此接口用于查询多个酒店订单，根据传入的查询条件查询订单信息。

    @response hotel_orders(HotelOrder): 多个订单结构，是否返回入住人列表根据参数决定
    @response total_results(Number): 符合条件的结果总数

    @request checkin_date_end(Date): (optional)入住时间查询结束时间，格式为：yyyy-MM-dd。不能早于checkin_date_start，间隔不能大于30
    @request checkin_date_start(Date): (optional)入住时间查询起始时间，格式为：yyyy-MM-dd
    @request checkout_date_end(Date): (optional)离店时间查询结束时间，格式为：yyyy-MM-dd。不能早于checkout_date_start，间隔不能大于30
    @request checkout_date_start(Date): (optional)离店时间查询起始时间，格式为：yyyy-MM-dd
    @request created_end(Date): (optional)订单创建时间查询结束时间，格式为：yyyy-MM-dd。不能早于created_start，间隔不能大于30
    @request created_start(Date): (optional)订单创建时间查询起始时间，格式为：yyyy-MM-dd
    @request gids(String): (optional)商品gid列表，多个gid用英文逗号隔开，一次不超过5个
    @request hids(String): (optional)酒店hid列表，多个hid用英文逗号隔开，一次不超过5个
    @request need_guest(Boolean): (optional)是否需要返回该订单的入住人列表。可选值：true，false。
    @request need_message(Boolean): (optional)是否显示买家留言，可选值true、false
    @request oids(String): (optional)酒店订单oids列表，多个oid用英文逗号隔开，一次不超过20个。oids，tids，hids，rids，gids，（checkin_date_start，checkin_date_end），（checkout_date_start，checkout_date_end），（created_start，created_end）必须传入一项，括号表示需同时存在才做为查询条件。
        oids，tids，hids，rids，gids同时出现时，优先级按此顺序由高到低只取一项。其他同时出现时，并列使用。
    @request page_no(Number): (optional)分页页码。取值范围，大于零的整数，默认值1，即返回第一页的数据。页面大小为20
    @request rids(String): (optional)房型rid列表，多个rid用英文逗号隔开，一次不超过5个
    @request status(String): (optional)订单状态。A：等待买家付款。B：买家已付款待卖家发货。C：卖家已发货待买家确认。D：交易成功。E：交易关闭
    @request tids(String): (optional)淘宝订单tid列表，多个tid用英文逗号隔开，一次不超过20个。
    """
    REQUEST = {
        'checkin_date_end': {'type': topstruct.Date, 'is_required': False},
        'checkin_date_start': {'type': topstruct.Date, 'is_required': False},
        'checkout_date_end': {'type': topstruct.Date, 'is_required': False},
        'checkout_date_start': {'type': topstruct.Date, 'is_required': False},
        'created_end': {'type': topstruct.Date, 'is_required': False},
        'created_start': {'type': topstruct.Date, 'is_required': False},
        'gids': {'type': topstruct.String, 'is_required': False},
        'hids': {'type': topstruct.String, 'is_required': False},
        'need_guest': {'type': topstruct.Boolean, 'is_required': False},
        'need_message': {'type': topstruct.Boolean, 'is_required': False},
        'oids': {'type': topstruct.String, 'is_required': False},
        'page_no': {'type': topstruct.Number, 'is_required': False},
        'rids': {'type': topstruct.String, 'is_required': False},
        'status': {'type': topstruct.String, 'is_required': False},
        'tids': {'type': topstruct.String, 'is_required': False}
    }

    RESPONSE = {
        'hotel_orders': {'type': topstruct.HotelOrder, 'is_list': False},
        'total_results': {'type': topstruct.Number, 'is_list': False}
    }

    API = 'taobao.hotel.orders.search'


class HotelRoomAddRequest(TOPRequest):
    """ 此接口用于发布一个集市酒店商品，商品的发布者是当前会话的用户。如果该酒店、该房型、该用户所对应的商品在淘宝集市酒店系统中已经存在，则会返回错误提示。

    @response room(Room): 商品结构

    @request area(String): (optional)面积。可选值：A,B,C,D。分别代表：
        A：15平米以下，B：16－30平米，C：31－50平米，D：50平米以上
    @request bbn(String): (optional)宽带服务。A,B,C,D。分别代表：
        A：无宽带，B：免费宽带，C：收费宽带，D：部分收费宽带
    @request bed_type(String): (required)床型。可选值：A,B,C,D,E,F,G,H,I。分别代表：A：单人床，B：大床，C：双床，D：双床/大床，E：子母床，F：上下床，G：圆形床，H：多床，I：其他床型
    @request breakfast(String): (required)早餐。A,B,C,D,E。分别代表：
        A：无早，B：单早，C：双早，D：三早，E：多早
    @request deposit(Number): (optional)订金。0～99999900的正整数。在payment_type为订金时必须输入，存储的单位是分。不能带角分。
    @request desc(String): (required)商品描述。不能超过25000个汉字（50000个字符）。
    @request fee(Number): (optional)手续费。0～99999900的正整数。在payment_type为手续费或手续费/间夜时必须输入，存储的单位是分。不能带角分。
    @request guide(String): (required)购买须知。不能超过4000个汉字（8000个字符）。
    @request hid(Number): (required)酒店id。必须为数字。
    @request payment_type(String): (required)支付类型。可选值：A,B,C,D。分别代表：
        A：全额支付，B：手续费，C：订金，D：手续费/间夜
    @request pic(Image): (optional)酒店商品图片。类型:JPG,GIF;最大长度:500K。支持的文件类型：gif,jpg,jpeg,png。发布的时候只能发布一张图片。如需再发图片，需要调用商品图片上传接口，1个商品最多5张图片。
    @request pic_path(String): (optional)商品主图需要关联的图片空间的相对url。这个url所对应的图片必须要属于当前用户。pic_path和image只需要传入一个,如果两个都传，默认选择pic_path
    @request rid(Number): (required)房型id。必须为数字。
    @request room_quotas(String): (required)房态信息。可以传今天开始90天内的房态信息。日期必须连续。JSON格式传递。
        date：代表房态日期，格式为YYYY-MM-DD，
        price：代表当天房价，0～99999999，存储的单位是分，
        num：代表当天可售间数，0～999。
        如：
        [{"date":2011-01-28,"price":10000, "num":10},{"date":2011-01-29,"price":12000,"num":10}]
    @request service(String): (optional)设施服务。JSON格式。
        value值true有此服务，false没有。
        bar：吧台，catv：有线电视，ddd：国内长途电话，idd：国际长途电话，toilet：独立卫生间，pubtoliet：公共卫生间。
        如：
        {"bar":false,"catv":false,"ddd":false,"idd":false,"pubtoilet":false,"toilet":false}
    @request site_param(String): (optional)接入卖家数据主键
    @request size(String): (optional)床宽。可选值：A,B,C,D,E,F,G,H。分别代表：A：1米及以下，B：1.1米，C：1.2米，D：1.35米，E：1.5米，F：1.8米，G：2米，H：2.2米及以上
    @request storey(String): (optional)楼层。长度不超过8
    @request title(String): (required)酒店商品名称。不能超过60字节
    """
    REQUEST = {
        'area': {'type': topstruct.String, 'is_required': False},
        'bbn': {'type': topstruct.String, 'is_required': False},
        'bed_type': {'type': topstruct.String, 'is_required': True},
        'breakfast': {'type': topstruct.String, 'is_required': True},
        'deposit': {'type': topstruct.Number, 'is_required': False},
        'desc': {'type': topstruct.String, 'is_required': True},
        'fee': {'type': topstruct.Number, 'is_required': False},
        'guide': {'type': topstruct.String, 'is_required': True},
        'hid': {'type': topstruct.Number, 'is_required': True},
        'payment_type': {'type': topstruct.String, 'is_required': True},
        'pic': {'type': topstruct.Image, 'is_required': False},
        'pic_path': {'type': topstruct.String, 'is_required': False},
        'rid': {'type': topstruct.Number, 'is_required': True},
        'room_quotas': {'type': topstruct.String, 'is_required': True},
        'service': {'type': topstruct.String, 'is_required': False},
        'site_param': {'type': topstruct.String, 'is_required': False},
        'size': {'type': topstruct.String, 'is_required': False},
        'storey': {'type': topstruct.String, 'is_required': False},
        'title': {'type': topstruct.String, 'is_required': True}
    }

    RESPONSE = {
        'room': {'type': topstruct.Room, 'is_list': False}
    }

    API = 'taobao.hotel.room.add'


class HotelRoomGetRequest(TOPRequest):
    """ 此接口用于查询一个商品，根据传入的gid查询商品信息。卖家只能查询自己的商品。

    @response room(Room): 商品结构。是否返回酒店信息、房型信息、房态列表、宝贝描述根据参数决定

    @request gid(Number): (special)酒店房间商品gid。必须为数字。gid和item_id至少要传一个。
    @request item_id(Number): (special)酒店房间商品item_id。必须为数字。item_id和gid至少要传一个。
    @request need_hotel(Boolean): (optional)是否需要返回该商品的酒店信息。可选值：true，false。
    @request need_room_desc(Boolean): (optional)是否需要返回该商品的宝贝描述。可选值：true，false。
    @request need_room_quotas(Boolean): (optional)是否需要返回该商品的房态列表。可选值：true，false。
    @request need_room_type(Boolean): (optional)是否需要返回该商品的房型信息。可选值：true，false。
    """
    REQUEST = {
        'gid': {'type': topstruct.Number, 'is_required': False},
        'item_id': {'type': topstruct.Number, 'is_required': False},
        'need_hotel': {'type': topstruct.Boolean, 'is_required': False},
        'need_room_desc': {'type': topstruct.Boolean, 'is_required': False},
        'need_room_quotas': {'type': topstruct.Boolean, 'is_required': False},
        'need_room_type': {'type': topstruct.Boolean, 'is_required': False}
    }

    RESPONSE = {
        'room': {'type': topstruct.Room, 'is_list': False}
    }

    API = 'taobao.hotel.room.get'


class HotelRoomImgDeleteRequest(TOPRequest):
    """ 此接口用于为商品删除商品图片。

    @response room_image(RoomImage): 商品图片结构

    @request gid(Number): (required)酒店房间商品gid。必须为数字。
    @request position(Number): (required)图片序号，可选值：1，2，3，4，5。
        如果原图片个数小于等于1，则报错，不能删除图片。
        如果原图片个数小于待删除的图片序号，则报错，图片序号错误。
    """
    REQUEST = {
        'gid': {'type': topstruct.Number, 'is_required': True},
        'position': {'type': topstruct.Number, 'is_required': True}
    }

    RESPONSE = {
        'room_image': {'type': topstruct.RoomImage, 'is_list': False}
    }

    API = 'taobao.hotel.room.img.delete'


class HotelRoomImgUploadRequest(TOPRequest):
    """ 此接口用于为商品上传商品图片。

    @response room_image(RoomImage): 商品图片结构

    @request gid(Number): (required)酒店房间商品gid。必须为数字。
    @request pic(Image): (required)酒店商品图片。类型:JPG,GIF;最大长度:500K。支持的文件类型：gif,jpg,jpeg,png。
        如果原图片少于5张，若没传序号或序号大于原图片个数，则在原图片最后添加，否则按序号插入到原图片中去，自动后移。
        如果原图片大于5张，若没传序号，则替换最后一张图片，否则在序号位置插入，图片向后移，最后一张被删除。
    @request position(Number): (optional)图片序号，可选值：1，2，3，4，5
    """
    REQUEST = {
        'gid': {'type': topstruct.Number, 'is_required': True},
        'pic': {'type': topstruct.Image, 'is_required': True},
        'position': {'type': topstruct.Number, 'is_required': False}
    }

    RESPONSE = {
        'room_image': {'type': topstruct.RoomImage, 'is_list': False}
    }

    API = 'taobao.hotel.room.img.upload'


class HotelRoomQuotasQueryFeedbackRequest(TOPRequest):
    """ 接入方房态查询结果返回

    @response is_success(Boolean): 接口调用是否成功

    @request avaliable_room_count(Number): (required)选中日期范围内的最大可用房量
    @request checkin_date(Date): (required)入住酒店的日期
    @request checkout_date(Date): (required)离开酒店的日期
    @request failed_reason(String): (optional)失败原因,当result为F时,此项为必填,最长200个字符
    @request message_id(String): (required)指令消息中的messageid,最长128字符
    @request result(String): (required)预订结果
        S:成功
        F:失败
    @request room_quotas(String): (optional)从入住时期到离店日期的每日一间房价与预定房量,JSON格式传递。 date：代表房态日期，格式为YYYY-MM-DD， price：代表当天房价，0～99999900，存储的单位是分，货币单位为人民币，num：代表当天剩余房量，0～999，所有日期的预订间数应该一致。 如： [{"date":2011-01-28,"price":10000, "num":10},{"date":2011-01-29,"price":12000,"num":10}],最长1500个字符
    @request total_room_price(Number): (required)订单总价。0～99999999的正整数。货币单位为人民币。
    """
    REQUEST = {
        'avaliable_room_count': {'type': topstruct.Number, 'is_required': True},
        'checkin_date': {'type': topstruct.Date, 'is_required': True},
        'checkout_date': {'type': topstruct.Date, 'is_required': True},
        'failed_reason': {'type': topstruct.String, 'is_required': False},
        'message_id': {'type': topstruct.String, 'is_required': True},
        'result': {'type': topstruct.String, 'is_required': True},
        'room_quotas': {'type': topstruct.String, 'is_required': False},
        'total_room_price': {'type': topstruct.Number, 'is_required': True}
    }

    RESPONSE = {
        'is_success': {'type': topstruct.Boolean, 'is_list': False}
    }

    API = 'taobao.hotel.room.quotas.query.feedback'


class HotelRoomUpdateRequest(TOPRequest):
    """ 此接口用于更新一个集市酒店商品，根据传入的gid更新商品信息，该商品必须为对应的发布者才能执行更新操作。如果对应的商品在淘宝集市酒店系统中不存在，则会返回错误提示。

    @response room(Room): 商品结构

    @request area(String): (optional)面积。可选值：A,B,C,D。分别代表：
        A：15平米以下，B：16－30平米，C：31－50平米，D：50平米以上
    @request bbn(String): (optional)宽带服务。A,B,C,D。分别代表：
        A：无宽带，B：免费宽带，C：收费宽带，D：部分收费宽带
    @request bed_type(String): (optional)床型。可选值：A,B,C,D,E,F,G,H,I。分别代表：A：单人床，B：大床，C：双床，D：双床/大床，E：子母床，F：上下床，G：圆形床，H：多床，I：其他床型
    @request breakfast(String): (optional)早餐。A,B,C,D,E。分别代表：
        A：无早，B：单早，C：双早，D：三早，E：多早
    @request deposit(Number): (optional)订金。0～99999900的正整数。在payment_type为订金时必须输入，存储的单位是分。不能带角分。
    @request desc(String): (optional)商品描述。不能超过25000个汉字（50000个字符）。
    @request fee(Number): (optional)手续费。0～99999900的正整数。在payment_type为手续费或手续费/间夜时必须输入，存储的单位是分。不能带角分。
    @request gid(Number): (required)酒店房间商品gid。必须为数字。
    @request guide(String): (optional)购买须知。不能超过4000个汉字（8000个字符）。
    @request payment_type(String): (optional)支付类型。可选值：A,B,C,D。分别代表：
        A：全额支付，B：手续费，C：订金，D：手续费/间夜
    @request pic(Image): (optional)酒店商品图片。类型:JPG,GIF;最大长度:500K。支持的文件类型：gif,jpg,jpeg,png。更新的时候只能更新一张图片，此图片覆盖原有所有图片。如果不传则使用原有所有图片。
        如需再发图片，需要调用商品图片上传接口，1个商品最多5张图片。
    @request pic_path(String): (optional)商品主图需要关联的图片空间的相对url。这个url所对应的图片必须要属于当前用户。pic_path和image只需要传入一个,如果两个都传，默认选择pic_path
    @request room_quotas(String): (optional)房态信息。可以传今天开始90天内的房态信息。日期必须连续。JSON格式传递。
        date：代表房态日期，格式为YYYY-MM-DD，
        price：代表当天房价，0～99999999，存储的单位是分,
        num：代表当天可售间数，0～999。
        如：
        [{"date":2011-01-28,"price":10000, "num":10},{"date":2011-01-29,"price":12000,"num":10}]
    @request service(String): (optional)设施服务。JSON格式。
        value值true有此服务，false没有。
        bar：吧台，catv：有线电视，ddd：国内长途电话，idd：国际长途电话，toilet：独立卫生间，pubtoliet：公共卫生间。
        如：
        {"bar":false,"catv":false,"ddd":false,"idd":false,"pubtoilet":false,"toilet":false}
    @request size(String): (optional)床宽。可选值：A,B,C,D,E,F,G,H。分别代表：A：1米及以下，B：1.1米，C：1.2米，D：1.35米，E：1.5米，F：1.8米，G：2米，H：2.2米及以上
    @request status(Number): (optional)状态。可选值1，2，3。1：上架。2：下架。3：删除。传入相应状态代表去执行相应的操作。
    @request storey(String): (optional)楼层。长度不超过8
    @request title(String): (optional)酒店商品名称。不能超过60字节
    """
    REQUEST = {
        'area': {'type': topstruct.String, 'is_required': False},
        'bbn': {'type': topstruct.String, 'is_required': False},
        'bed_type': {'type': topstruct.String, 'is_required': False},
        'breakfast': {'type': topstruct.String, 'is_required': False},
        'deposit': {'type': topstruct.Number, 'is_required': False},
        'desc': {'type': topstruct.String, 'is_required': False},
        'fee': {'type': topstruct.Number, 'is_required': False},
        'gid': {'type': topstruct.Number, 'is_required': True},
        'guide': {'type': topstruct.String, 'is_required': False},
        'payment_type': {'type': topstruct.String, 'is_required': False},
        'pic': {'type': topstruct.Image, 'is_required': False},
        'pic_path': {'type': topstruct.String, 'is_required': False},
        'room_quotas': {'type': topstruct.String, 'is_required': False},
        'service': {'type': topstruct.String, 'is_required': False},
        'size': {'type': topstruct.String, 'is_required': False},
        'status': {'type': topstruct.Number, 'is_required': False},
        'storey': {'type': topstruct.String, 'is_required': False},
        'title': {'type': topstruct.String, 'is_required': False}
    }

    RESPONSE = {
        'room': {'type': topstruct.Room, 'is_list': False}
    }

    API = 'taobao.hotel.room.update'


class HotelRoomsSearchRequest(TOPRequest):
    """ 此接口用于查询多个酒店商品，根据传入的参数查询商品信息。卖家只能查询自己的商品。

    @response rooms(Room): 多个商品结构。是否返回酒店信息、房型信息、房态列表、宝贝描述根据参数决定
    @response total_results(Number): 符合条件的结果总数

    @request gids(String): (special)酒店房间商品gid列表，多个gid用英文逗号隔开，一次不超过20个。gids，item_ids , hids，rids四项必须传一项，同时传递的情况下，作为查询条件的优先级由高到低依次为gids，item_ids , hids，rids。
    @request hids(String): (special)酒店hid列表，多个hid用英文逗号隔开，一次不超过5个。gids，item_ids , hids，rids四项必须传一项，同时传递的情况下，作为查询条件的优先级由高到低依次为gids，item_ids , hids，rids。
    @request item_ids(String): (special)酒店房间商品item_id列表，多个item_id用英文逗号隔开，一次不超过20个。gids，item_ids , hids，rids四项必须传一项，同时传递的情况下，作为查询条件的优先级由高到低依次为gids，item_ids , hids，rids。
    @request need_hotel(Boolean): (optional)是否需要返回该商品的酒店信息。可选值：true，false。
    @request need_room_desc(Boolean): (optional)是否需要返回该商品的宝贝描述。可选值：true，false。
    @request need_room_quotas(Boolean): (optional)是否需要返回该商品的房态列表。可选值：true，false。
    @request need_room_type(Boolean): (optional)是否需要返回该商品的房型信息。可选值：true，false。
    @request page_no(Number): (optional)分页页码。取值范围，大于零的整数，默认值1，即返回第一页的数据。页面大小为20
    @request rids(String): (special)房型rid列表，多个rid用英文逗号隔开，一次不超过20个。gids，item_ids , hids，rids四项必须传一项，同时传递的情况下，作为查询条件的优先级由高到低依次为gids，item_ids , hids，rids。
    """
    REQUEST = {
        'gids': {'type': topstruct.String, 'is_required': False},
        'hids': {'type': topstruct.String, 'is_required': False},
        'item_ids': {'type': topstruct.String, 'is_required': False},
        'need_hotel': {'type': topstruct.Boolean, 'is_required': False},
        'need_room_desc': {'type': topstruct.Boolean, 'is_required': False},
        'need_room_quotas': {'type': topstruct.Boolean, 'is_required': False},
        'need_room_type': {'type': topstruct.Boolean, 'is_required': False},
        'page_no': {'type': topstruct.Number, 'is_required': False},
        'rids': {'type': topstruct.String, 'is_required': False}
    }

    RESPONSE = {
        'rooms': {'type': topstruct.Room, 'is_list': False},
        'total_results': {'type': topstruct.Number, 'is_list': False}
    }

    API = 'taobao.hotel.rooms.search'


class HotelRoomsUpdateRequest(TOPRequest):
    """ 此接口用于更新多个集市酒店商品房态信息，根据传入的gids更新商品信息，该商品必须为对应的发布者才能执行更新操作。如果对应的商品在淘宝集市酒店系统中不存在，则会返回错误提示。是全量更新，非增量，会把之前的房态进行覆盖。

    @response gids(String): 成功的gid list

    @request gid_room_quota_map(String): (required)多商品房态信息。json encode。每个商品房态参考单商品更新中的room_quota字段。反序列化后入：array(( 'gid'=>1, 'roomQuota'=>array(('date'=>'2011-01-29', 'price'=>100, 'num'=>1),('date'=>'2011-01-30', 'price'=>100, 'num'=>1)),( 'gid'=>2, 'roomQuota'=>array(('date'=>'2011-01-29', 'price'=>100, 'num'=>1),('date'=>'2011-01-30', 'price'=>100, 'num'=>1)))
    """
    REQUEST = {
        'gid_room_quota_map': {'type': topstruct.String, 'is_required': True}
    }

    RESPONSE = {
        'gids': {'type': topstruct.String, 'is_list': False}
    }

    API = 'taobao.hotel.rooms.update'


class HotelSoldHotelsIncrementGetRequest(TOPRequest):
    """ 1. 此接口用于查询该会话用户作为酒店发布者发布的酒店被审核通过的增量酒店信息。
        2. 只能查询时间跨度为一天的增量酒店记录：start_modified：2011-7-1 16:00:00 end_modified： 2011-7-2 15:59:59（注意不能写成16:00:00）
        3. 返回数据结果为发布酒店时间的倒序

    @response has_next(Boolean): 是否存在下一页
    @response hotels(Hotel): 多个酒店结构
    @response total_results(Number): 符合条件的结果总数

    @request end_modified(Date): (required)查询修改结束时间，必须大于修改开始时间（修改时间跨度不能大于1天）。格式：yyyy-MM-dd HH:mm:ss
    @request page_no(Number): (optional)分页页码。取值范围，大于零的整数，默认值1，即返回第一页的数据
    @request page_size(Number): (optional)页面大小，取值范围1-100，默认大小20
    @request start_modified(Date): (required)查询修改开始时间（修改时间跨度不能大于1天）。格式：yyyy-MM-dd HH:mm:ss
    @request use_has_next(Boolean): (optional)是否使用has_next的分页方式，如果指定true，则返回的结果中不包含总记录数，但是会新增一个是否存在下一页的字段，效率比总记录数高
    """
    REQUEST = {
        'end_modified': {'type': topstruct.Date, 'is_required': True},
        'page_no': {'type': topstruct.Number, 'is_required': False},
        'page_size': {'type': topstruct.Number, 'is_required': False},
        'start_modified': {'type': topstruct.Date, 'is_required': True},
        'use_has_next': {'type': topstruct.Boolean, 'is_required': False}
    }

    RESPONSE = {
        'has_next': {'type': topstruct.Boolean, 'is_list': False},
        'hotels': {'type': topstruct.Hotel, 'is_list': False},
        'total_results': {'type': topstruct.Number, 'is_list': False}
    }

    API = 'taobao.hotel.sold.hotels.increment.get'


class HotelSoldOrdersIncrementGetRequest(TOPRequest):
    """ 1. 搜索当前会话用户作为卖家已卖出的增量交易数据
        2. 只能查询时间跨度为一天的增量交易记录：start_modified：2011-7-1 16:00:00 end_modified： 2011-7-2 15:59:59（注意不能写成16:00:00）
        3. 返回数据结果为创建订单时间的倒序

    @response has_next(Boolean): 是否存在下一页
    @response hotel_orders(HotelOrder): 多个订单结构，是否返回入住人列表根据参数决定
    @response total_results(Number): 搜索到的交易信息总数

    @request end_modified(Date): (required)查询修改结束时间，必须大于修改开始时间（修改时间跨度不能大于1天）。格式：yyyy-MM-dd HH:mm:ss。
    @request need_guest(Boolean): (optional)是否需要返回该订单的入住人列表。可选值：true，false。
    @request need_message(Boolean): (optional)是否返回买家留言，可选值true、false
    @request page_no(Number): (optional)分页页码。取值范围，大于零的整数，默认值1，即返回第一页的数据。
    @request page_size(Number): (optional)页面大小，取值范围1-100，默认大小20。
    @request start_modified(Date): (required)查询修改开始时间（修改时间跨度不能大于1天）。格式：yyyy-MM-dd HH:mm:ss
    @request status(String): (optional)交易状态，默认查询所有交易状态的数据，除了默认值外每次只能查询一种状态。可选值：A：等待买家付款。B：买家已付款待卖家发货。C：卖家已发货待买家确认。D：交易成功。E：交易关闭
    @request use_has_next(Boolean): (optional)是否使用has_next的分页方式，如果指定true，则返回的结果中不包含总记录数，但是会新增一个是否存在下一页的字段，效率比总记录数高
    """
    REQUEST = {
        'end_modified': {'type': topstruct.Date, 'is_required': True},
        'need_guest': {'type': topstruct.Boolean, 'is_required': False},
        'need_message': {'type': topstruct.Boolean, 'is_required': False},
        'page_no': {'type': topstruct.Number, 'is_required': False},
        'page_size': {'type': topstruct.Number, 'is_required': False},
        'start_modified': {'type': topstruct.Date, 'is_required': True},
        'status': {'type': topstruct.String, 'is_required': False},
        'use_has_next': {'type': topstruct.Boolean, 'is_required': False}
    }

    RESPONSE = {
        'has_next': {'type': topstruct.Boolean, 'is_list': False},
        'hotel_orders': {'type': topstruct.HotelOrder, 'is_list': False},
        'total_results': {'type': topstruct.Number, 'is_list': False}
    }

    API = 'taobao.hotel.sold.orders.increment.get'


class HotelSoldTypesIncrementGetRequest(TOPRequest):
    """ 1. 此接口用于查询该会话用户作为房型发布者发布的房型被审核通过的增量房型信息。
        2. 只能查询时间跨度为一天的增量酒店记录：start_modified：2011-7-1 16:00:00 end_modified： 2011-7-2 15:59:59（注意不能写成16:00:00）
        3. 返回数据结果为发布房型时间的倒序

    @response has_next(Boolean): 是否存在下一页
    @response room_types(RoomType): 多个房型结构
    @response total_results(Number): 符合条件的结果总数

    @request end_modified(Date): (required)查询修改结束时间，必须大于修改开始时间（修改时间跨度不能大于1天）。格式：yyyy-MM-dd HH:mm:ss
    @request page_no(Number): (optional)分页页码。取值范围，大于零的整数，默认值1，即返回第一页的数据。
    @request page_size(Number): (optional)页面大小，取值范围1-100，默认大小20。
    @request start_modified(Date): (required)查询修改开始时间（修改时间跨度不能大于1天）。格式：yyyy-MM-dd HH:mm:ss
    @request use_has_next(Boolean): (optional)是否使用has_next的分页方式，如果指定true，则返回的结果中不包含总记录数，但是会新增一个是否存在下一页的字段，效率比总记录数高
    """
    REQUEST = {
        'end_modified': {'type': topstruct.Date, 'is_required': True},
        'page_no': {'type': topstruct.Number, 'is_required': False},
        'page_size': {'type': topstruct.Number, 'is_required': False},
        'start_modified': {'type': topstruct.Date, 'is_required': True},
        'use_has_next': {'type': topstruct.Boolean, 'is_required': False}
    }

    RESPONSE = {
        'has_next': {'type': topstruct.Boolean, 'is_list': False},
        'room_types': {'type': topstruct.RoomType, 'is_list': False},
        'total_results': {'type': topstruct.Number, 'is_list': False}
    }

    API = 'taobao.hotel.sold.types.increment.get'


class HotelTypeAddRequest(TOPRequest):
    """ 此接口用于发布一个房型，房型的发布者是当前会话的用户。如果该房型在淘宝集市酒店下已经存在，则会返回错误提示。
        该接口发布的是一个新增房型申请，需要淘宝小二审核

    @response room_type(RoomType): 房型结构

    @request hid(Number): (required)酒店id。必须为数字
    @request name(String): (required)房型名称。长度不能超过30
    @request site_param(String): (optional)接入卖家数据主键
    """
    REQUEST = {
        'hid': {'type': topstruct.Number, 'is_required': True},
        'name': {'type': topstruct.String, 'is_required': True},
        'site_param': {'type': topstruct.String, 'is_required': False}
    }

    RESPONSE = {
        'room_type': {'type': topstruct.RoomType, 'is_list': False}
    }

    API = 'taobao.hotel.type.add'


class HotelTypeNameGetRequest(TOPRequest):
    """ 此接口用于查询一个房型，根据传入的酒店hid，房型名称/别名查询房型信息。

    @response room_type(RoomType): 房型结构

    @request hid(Number): (required)要查询的酒店id。必须为数字
    @request name(String): (required)房型全部名称/别名。不能超过60字节
    """
    REQUEST = {
        'hid': {'type': topstruct.Number, 'is_required': True},
        'name': {'type': topstruct.String, 'is_required': True}
    }

    RESPONSE = {
        'room_type': {'type': topstruct.RoomType, 'is_list': False}
    }

    API = 'taobao.hotel.type.name.get'


class HotelUpdateRequest(TOPRequest):
    """ 此接口用于更新一个酒店的信息，根据用户传入的hid更新酒店数据。如果该酒店在淘宝集市酒店不存在，则会返回错误提示。
        该接口发出的是一个更新酒店信息的申请，需要淘宝小二审核。

    @response hotel(Hotel): 酒店结构

    @request address(String): (optional)酒店地址。长度不能超过120
    @request city(Number): (optional)城市编码。参见：http://kezhan.trip.taobao.com/area.html，domestic为false时默认为0
    @request country(String): (optional)domestic为true时，固定China；
        domestic为false时，必须传定义的酒店。参见：http://kezhan.trip.taobao.com/countrys.html
    @request decorate_time(String): (optional)装修时间。长度不能超过4。
    @request desc(String): (optional)酒店介绍。不超过25000个汉字
    @request district(Number): (optional)区域（县级市）编码。参见：http://kezhan.trip.taobao.com/area.html
    @request domestic(Boolean): (optional)是否国内酒店。可选值：true，false
    @request hid(Number): (required)酒店id。必须为数字。
    @request level(String): (optional)酒店级别。可选值：A,B,C,D,E,F。代表客栈公寓、经济连锁、二星级/以下、三星级/舒适、四星级/高档、五星级/豪华
    @request name(String): (optional)酒店名称。不能超过60字节
    @request opening_time(String): (optional)开业时间。长度不能超过4。
    @request orientation(String): (optional)酒店定位。可选值：T,B。代表旅游度假、商务出行
    @request pic(Image): (optional)酒店图片。类型:JPG,GIF;最大长度:500K。支持的文件类型：gif,jpg,jpeg,png。
        图片没有传，则代表不更新图片，使用原来的图片
    @request province(Number): (optional)省份编码。参见：http://kezhan.trip.taobao.com/area.html，domestic为false时默认为0
    @request rooms(Number): (optional)房间数。长度不能超过4。
    @request service(String): (optional)交通距离与设施服务。JSON格式。cityCenterDistance、railwayDistance、airportDistance分别代表距离市中心、距离火车站、距离机场公里数，为不超过3位正整数，默认-1代表无数据。
        其他key值true代表有此服务，false代表没有。
        parking：停车场，airportShuttle：机场接送，rentCar：租车，meetingRoom：会议室，businessCenter：商务中心，swimmingPool：游泳池，fitnessClub：健身中心，laundry：洗衣服务，morningCall：叫早服务，bankCard：接受银行卡，creditCard：接受信用卡，chineseRestaurant：中餐厅，westernRestaurant：西餐厅，cafe：咖啡厅，bar：酒吧，ktv：KTV。
        如：
        {"airportShuttle":true,"parking":false,"fitnessClub":false,"chineseRestaurant":false,"rentCar":false,"laundry":false,"bankCard":false,"cityCenterDistance":-1,"creditCard":false,"westernRestaurant":false,"ktv":false,"railwayDistance":-1,"swimmingPool":false,"cafe":false,"businessCenter":false,"morningCall":false,"bar":false,"meetingRoom":false,"airportDistance":-1}
    @request storeys(Number): (optional)楼层数。长度不能超过4。
    @request tel(String): (optional)酒店电话。格式：国家代码（最长6位）#区号（最长4位）#电话（最长20位）。国家代码提示：中国大陆0086、香港00852、澳门00853、台湾00886
    """
    REQUEST = {
        'address': {'type': topstruct.String, 'is_required': False},
        'city': {'type': topstruct.Number, 'is_required': False},
        'country': {'type': topstruct.String, 'is_required': False},
        'decorate_time': {'type': topstruct.String, 'is_required': False},
        'desc': {'type': topstruct.String, 'is_required': False},
        'district': {'type': topstruct.Number, 'is_required': False},
        'domestic': {'type': topstruct.Boolean, 'is_required': False},
        'hid': {'type': topstruct.Number, 'is_required': True},
        'level': {'type': topstruct.String, 'is_required': False},
        'name': {'type': topstruct.String, 'is_required': False},
        'opening_time': {'type': topstruct.String, 'is_required': False},
        'orientation': {'type': topstruct.String, 'is_required': False},
        'pic': {'type': topstruct.Image, 'is_required': False},
        'province': {'type': topstruct.Number, 'is_required': False},
        'rooms': {'type': topstruct.Number, 'is_required': False},
        'service': {'type': topstruct.String, 'is_required': False},
        'storeys': {'type': topstruct.Number, 'is_required': False},
        'tel': {'type': topstruct.String, 'is_required': False}
    }

    RESPONSE = {
        'hotel': {'type': topstruct.Hotel, 'is_list': False}
    }

    API = 'taobao.hotel.update'


class HotelsSearchRequest(TOPRequest):
    """ 此接口用于查询多个酒店，根据传入的参数查询酒店信息。

    @response hotels(Hotel): 多个酒店结构<br></br><font color = red>不返回房型信息，需要查看房型信息，请调用taobao.hotel.get</font>
    @response total_results(Number): 符合条件的结果总数

    @request city(Number): (optional)城市编码。参见：http://kezhan.trip.taobao.com/area.html。
        domestic为true时，province,city,district不能同时为空或为0
    @request country(String): (optional)domestic为true时，固定China；
        domestic为false时，必须传定义的海外国家编码值，是必填项。参见：http://kezhan.trip.taobao.com/countrys.html
    @request district(Number): (optional)区域（县级市）编码。参见：http://kezhan.trip.taobao.com/area.html。
        domestic为true时，province,city,district不能同时为空或为0
    @request domestic(Boolean): (required)是否国内酒店。可选值：true，false
    @request name(String): (optional)酒店名称。不能超过60字节
    @request page_no(Number): (optional)分页页码。取值范围，大于零的整数，默认值1，即返回第一页的数据。页面大小为20
    @request province(Number): (optional)省份编码。参见：http://kezhan.trip.taobao.com/area.html。
        domestic为true时，province,city,district不能同时为空或为0
    """
    REQUEST = {
        'city': {'type': topstruct.Number, 'is_required': False},
        'country': {'type': topstruct.String, 'is_required': False},
        'district': {'type': topstruct.Number, 'is_required': False},
        'domestic': {'type': topstruct.Boolean, 'is_required': True},
        'name': {'type': topstruct.String, 'is_required': False},
        'page_no': {'type': topstruct.Number, 'is_required': False},
        'province': {'type': topstruct.Number, 'is_required': False}
    }

    RESPONSE = {
        'hotels': {'type': topstruct.Hotel, 'is_list': False},
        'total_results': {'type': topstruct.Number, 'is_list': False}
    }

    API = 'taobao.hotels.search'


class JuCatitemidsGetRequest(TOPRequest):
    """ 根据类目获取商品列表

    @response item_ids(Number): 返回的商品ID列表

    @request child_categoryid(Number): (optional)商品子类目ID。男装:100001,女装:100002。
    @request city(String): (optional)查询本地生活团商品时需要用city进行过滤，如果city是all的话，则查询所有城市的本地生活团商品。如果为空，则查询普通商品
    @request page_no(Number): (required)分页获取商品信息页序号，代表第几页
    @request page_size(Number): (required)每次获取商品列表的数量
    @request parent_categoryid(Number): (required)商品父类目ID。服装:100000,保险:1000000。
    @request platform_id(Number): (optional)平台ID。搜狗:1008,聚划算:1001,商城:1002,无线WAP:1007,支付宝:1003,淘宝天下:1004,嗨淘:1006
    @request terminal_type(String): (optional)IPHONE,WAP,ANDROID,SINA,163 各种终端类型
    """
    REQUEST = {
        'child_categoryid': {'type': topstruct.Number, 'is_required': False},
        'city': {'type': topstruct.String, 'is_required': False},
        'page_no': {'type': topstruct.Number, 'is_required': True},
        'page_size': {'type': topstruct.Number, 'is_required': True},
        'parent_categoryid': {'type': topstruct.Number, 'is_required': True},
        'platform_id': {'type': topstruct.Number, 'is_required': False},
        'terminal_type': {'type': topstruct.String, 'is_required': False}
    }

    RESPONSE = {
        'item_ids': {'type': topstruct.Number, 'is_list': False}
    }

    API = 'taobao.ju.catitemids.get'


class JuCitiesGetRequest(TOPRequest):
    """ 获取今日有生活服务商品的城市列表

    @response cities(String): 返回城市名称列表类似 "上海","成都"
    """
    REQUEST = {}

    RESPONSE = {
        'cities': {'type': topstruct.String, 'is_list': False}
    }

    API = 'taobao.ju.cities.get'


class JuCityitemsGetRequest(TOPRequest):
    """ 根据城市，获取对应的生活服务团商品接口

    @response item_list(ItemData): 聚划算商品对象列表

    @request city(String): (required)需要获取生活服务商品的城市名称（中文）
    @request fields(FieldList): (optional)代表需要返回的商品对象字段。可选值：ItemData商品结构体中所有字段均可返回；多个字段用","分隔。如果fields为空，或者不传该参数，就默认获得所有的字段
    @request page_no(Number): (required)分页获取商品信息页序号，代表第几页
    @request page_size(Number): (required)每次获取商品列表的数量
    """
    REQUEST = {
        'city': {'type': topstruct.String, 'is_required': True},
        'fields': {'type': topstruct.FieldList, 'is_required': False, 'optional': topstruct.Set({'activity_price', 'item_guarantee', 'item_url', 'category_id', 'item_desc', 'shop_position_list', 'seller_credit', 'long_name', 'pic_wide_url', 'short_name', 'is_lock', 'pic_url', 'item_status', 'current_stock', 'exist_hold_stock', 'pay_postage', 'group_id', 'platform_id', 'online_start_time', 'pic_url_from_ic', 'seller_id', 'child_category', 'city', 'online_end_time', 'sold_count', 'shop_type', 'seller_nick', 'discount', 'parent_category', 'original_price', 'item_id'}), 'default': {'None'}},
        'page_no': {'type': topstruct.Number, 'is_required': True},
        'page_size': {'type': topstruct.Number, 'is_required': True}
    }

    RESPONSE = {
        'item_list': {'type': topstruct.ItemData, 'is_list': False}
    }

    API = 'taobao.ju.cityitems.get'


class JuItemidsGetRequest(TOPRequest):
    """ 根据终端类型和平台ID，分页获取聚划算商品id列表

    @response item_ids(Number): 返回的商品ID列表

    @request page_no(Number): (required)分页获取商品信息页序号，代表第几页
    @request page_size(Number): (required)每次获取商品列表的数量
    @request platform_id(Number): (optional)平台ID。搜狗:1008,聚划算:1001,商城:1002,无线WAP:1007,支付宝:1003,淘宝天下:1004,嗨淘:1006
    @request terminal_type(String): (optional)IPHONE,WAP,ANDROID,SINA,163 各种终端类型
    """
    REQUEST = {
        'page_no': {'type': topstruct.Number, 'is_required': True},
        'page_size': {'type': topstruct.Number, 'is_required': True},
        'platform_id': {'type': topstruct.Number, 'is_required': False},
        'terminal_type': {'type': topstruct.String, 'is_required': False}
    }

    RESPONSE = {
        'item_ids': {'type': topstruct.Number, 'is_list': False}
    }

    API = 'taobao.ju.itemids.get'


class JuItemsGetRequest(TOPRequest):
    """ 根据商品id列表获取商品列表，目前一次最多返回6条。传入的参数id列表超过6条也只返回前6条的商品

    @response item_list(ItemData): 聚划算商品对象列表

    @request fields(FieldList): (optional)代表需要返回的商品对象字段。可选值：ItemData商品结构体中所有字段均可返回；多个字段用","分隔。如果fields为空，或者不传该参数，就默认获得所有的字段
    @request ids(FieldList): (required)商品ID列表。id列表超过6条也只返回前6条的商品
    """
    REQUEST = {
        'fields': {'type': topstruct.FieldList, 'is_required': False, 'optional': topstruct.Set({'activity_price', 'item_guarantee', 'item_url', 'category_id', 'item_desc', 'shop_position_list', 'seller_credit', 'long_name', 'pic_wide_url', 'short_name', 'is_lock', 'pic_url', 'item_status', 'current_stock', 'exist_hold_stock', 'pay_postage', 'group_id', 'platform_id', 'online_start_time', 'pic_url_from_ic', 'seller_id', 'child_category', 'city', 'online_end_time', 'sold_count', 'shop_type', 'seller_nick', 'discount', 'parent_category', 'original_price', 'item_id'}), 'default': {'None'}},
        'ids': {'type': topstruct.FieldList, 'is_required': True}
    }

    RESPONSE = {
        'item_list': {'type': topstruct.ItemData, 'is_list': False}
    }

    API = 'taobao.ju.items.get'


class JuTodayitemsGetRequest(TOPRequest):
    """ 根据终端类型，随机分配一个聚划算今天的商品列表

    @response item_list(ItemData): 聚划算商品对象列表

    @request fields(FieldList): (optional)代表需要返回的商品对象字段。可选值：ItemData商品结构体中所有字段均可返回；多个字段用","分隔。如果fields为空，或者不传该参数，就默认获得所有的字段
    @request terminal_type(String): (required)IPHONE,WAP,ANDROID,SINA,163 各种终端类型
    @request uuid(String): (required)终端的唯一标识，web可以用cookie，手机使用手机号码等，确保唯一性即可，用于分配商品组
    """
    REQUEST = {
        'fields': {'type': topstruct.FieldList, 'is_required': False, 'optional': topstruct.Set({'activity_price', 'item_guarantee', 'item_url', 'category_id', 'item_desc', 'shop_position_list', 'seller_credit', 'long_name', 'pic_wide_url', 'short_name', 'is_lock', 'pic_url', 'item_status', 'current_stock', 'exist_hold_stock', 'pay_postage', 'group_id', 'platform_id', 'online_start_time', 'pic_url_from_ic', 'seller_id', 'child_category', 'city', 'online_end_time', 'sold_count', 'shop_type', 'seller_nick', 'discount', 'parent_category', 'original_price', 'item_id'}), 'default': {'None'}},
        'terminal_type': {'type': topstruct.String, 'is_required': True},
        'uuid': {'type': topstruct.String, 'is_required': True}
    }

    RESPONSE = {
        'item_list': {'type': topstruct.ItemData, 'is_list': False}
    }

    API = 'taobao.ju.todayitems.get'


class CrmGradeGetRequest(TOPRequest):
    """ 卖家查询等级规则，包括普通会员、高级会员、VIP会员、至尊VIP会员四个等级的信息

    @response grade_promotions(GradePromotion): 等级信息集合
    """
    REQUEST = {}

    RESPONSE = {
        'grade_promotions': {'type': topstruct.GradePromotion, 'is_list': False}
    }

    API = 'taobao.crm.grade.get'


class CrmGroupAddRequest(TOPRequest):
    """ 卖家创建一个新的分组，接口返回一个创建成功的分组的id

    @response group_id(Number): 新增分组的id
    @response is_success(Boolean): 添加分组是否成功

    @request group_name(String): (required)分组名称，每个卖家最多可以拥有100个分组
    """
    REQUEST = {
        'group_name': {'type': topstruct.String, 'is_required': True}
    }

    RESPONSE = {
        'group_id': {'type': topstruct.Number, 'is_list': False},
        'is_success': {'type': topstruct.Boolean, 'is_list': False}
    }

    API = 'taobao.crm.group.add'


class CrmGroupAppendRequest(TOPRequest):
    """ 将某分组下的所有会员添加到另一个分组,注：1.该操作为异步任务，建议先调用taobao.crm.grouptask.check 确保涉及分组上没有任务；2.若分组下某会员分组数超最大限额，则该会员不会被添加到新分组，同时不影响其余会员添加分组，接口调用依然返回成功。

    @response is_success(Boolean): 异步任务请求成功，添加任务是否完成通过taobao.crm.grouptask.check检测

    @request from_group_id(Number): (required)添加的来源分组
    @request to_group_id(Number): (required)添加的目标分组
    """
    REQUEST = {
        'from_group_id': {'type': topstruct.Number, 'is_required': True},
        'to_group_id': {'type': topstruct.Number, 'is_required': True}
    }

    RESPONSE = {
        'is_success': {'type': topstruct.Boolean, 'is_list': False}
    }

    API = 'taobao.crm.group.append'


class CrmGroupDeleteRequest(TOPRequest):
    """ 将该分组下的所有会员移除出该组，同时删除该分组。注：删除分组为异步任务，必须先调用taobao.crm.grouptask.check 确保涉及属性上没有任务。

    @response is_success(Boolean): 异步任务请求成功，是否执行完毕需要通过taobao.crm.grouptask.check检测

    @request group_id(Number): (required)要删除的分组id
    """
    REQUEST = {
        'group_id': {'type': topstruct.Number, 'is_required': True}
    }

    RESPONSE = {
        'is_success': {'type': topstruct.Boolean, 'is_list': False}
    }

    API = 'taobao.crm.group.delete'


class CrmGroupMoveRequest(TOPRequest):
    """ 将一个分组下的所有会员移动到另一个分组，会员从原分组中删除
        注：移动属性为异步任务建议先调用taobao.crm.grouptask.check 确保涉及属性上没有任务。

    @response is_success(Boolean): 异步任务请求成功，是否执行完毕需要通过taobao.crm.grouptask.check检测

    @request from_group_id(Number): (required)需要移动的分组
    @request to_group_id(Number): (required)目的分组
    """
    REQUEST = {
        'from_group_id': {'type': topstruct.Number, 'is_required': True},
        'to_group_id': {'type': topstruct.Number, 'is_required': True}
    }

    RESPONSE = {
        'is_success': {'type': topstruct.Boolean, 'is_list': False}
    }

    API = 'taobao.crm.group.move'


class CrmGroupUpdateRequest(TOPRequest):
    """ 修改一个已经存在的分组，接口返回分组的修改是否成功

    @response is_success(Boolean): 分组修改是否成功

    @request group_id(Number): (required)分组的id
    @request new_group_name(String): (required)新的分组名，分组名称不能包含|或者：
    """
    REQUEST = {
        'group_id': {'type': topstruct.Number, 'is_required': True},
        'new_group_name': {'type': topstruct.String, 'is_required': True}
    }

    RESPONSE = {
        'is_success': {'type': topstruct.Boolean, 'is_list': False}
    }

    API = 'taobao.crm.group.update'


class CrmGroupsGetRequest(TOPRequest):
    """ 查询卖家的分组，返回查询到的分组列表，分页返回分组

    @response groups(Group): 查询到的当前卖家的当前页的会员
    @response total_result(Number): 记录总数

    @request current_page(Number): (required)显示第几页的分组，如果输入的页码大于总共的页码数，例如总共10页，但是current_page的值为11，则返回空白页，最小页码为1
    @request page_size(Number): (optional)每页显示的记录数，其最大值不能超过100条，最小值为1，默认20条
    """
    REQUEST = {
        'current_page': {'type': topstruct.Number, 'is_required': True},
        'page_size': {'type': topstruct.Number, 'is_required': False}
    }

    RESPONSE = {
        'groups': {'type': topstruct.Group, 'is_list': False},
        'total_result': {'type': topstruct.Number, 'is_list': False}
    }

    API = 'taobao.crm.groups.get'


class CrmGrouptaskCheckRequest(TOPRequest):
    """ 检查一个分组上是否有异步任务,异步任务包括1.将一个分组下的所有用户添加到另外一个分组2.将一个分组下的所有用户移动到另外一个分组3.删除某个分组
        若分组上有任务则该属性不能被操作。

    @response is_finished(Boolean): 异步任务是否完成，true表示完成

    @request group_id(Number): (required)分组id
    """
    REQUEST = {
        'group_id': {'type': topstruct.Number, 'is_required': True}
    }

    RESPONSE = {
        'is_finished': {'type': topstruct.Boolean, 'is_list': False}
    }

    API = 'taobao.crm.grouptask.check'


class CrmMemberinfoUpdateRequest(TOPRequest):
    """ 编辑会员的基本资料，接口返回会员信息修改是否成功

    @response is_success(Boolean): 会员信息修改是否成功

    @request buyer_nick(String): (required)买家昵称
    @request city(String): (optional)城市
    @request grade(Number): (optional)会员等级，1：普通客户，2：高级会员，3：高级会员 ，4：至尊vip
        只有正常会员才给予升级，对于status 为delete或者blacklist的会员 升级无效
    @request province(String): (optional)北京=1,天津=2,河北省=3,山西省=4,内蒙古自治区=5,辽宁省=6,吉林省=7,黑龙江省=8,上海=9,江苏省=10,浙江省=11,安徽省=12,福建省=13,江西省=14,山东省=15,河南省=16,湖北省=17,湖南省=18, 广东省=19,广西壮族自治区=20,海南省=21,重庆=22,四川省=23,贵州省=24,云南省=25,西藏自治区=26,陕西省=27,甘肃省=28,青海省=29,宁夏回族自治区=30,新疆维吾尔自治区=31,台湾省=32,香港特别行政区=33,澳门特别行政区=34,海外=35，约定36为清除Province设置
    @request status(String): (required)用于描述会员的状态，normal表示正常，blacklist表示黑名单，delete表示删除会员(只有潜在未交易成功的会员才能删除)
    """
    REQUEST = {
        'buyer_nick': {'type': topstruct.String, 'is_required': True},
        'city': {'type': topstruct.String, 'is_required': False},
        'grade': {'type': topstruct.Number, 'is_required': False},
        'province': {'type': topstruct.String, 'is_required': False},
        'status': {'type': topstruct.String, 'is_required': True}
    }

    RESPONSE = {
        'is_success': {'type': topstruct.Boolean, 'is_list': False}
    }

    API = 'taobao.crm.memberinfo.update'


class CrmMembersGetRequest(TOPRequest):
    """ 查询卖家的会员，进行基本的查询，返回符合条件的会员列表

    @response members(BasicMember): 根据一定条件查询到卖家的会员
    @response total_result(Number): 记录总数

    @request buyer_nick(String): (optional)买家的昵称
    @request current_page(Number): (required)显示第几页的会员，如果输入的页码大于总共的页码数，例如总共10页，但是current_page的值为11，则返回空白页，最小页数为1
    @request grade(Number): (optional)会员等级，0：返回所有会员1：普通客户，2：高级会员，3：VIP会员， 4：至尊VIP会员
        (如果要查交易关闭的会员  请选择taobao.crm.members.search接口的 relation_source=2)
    @request max_last_trade_time(Date): (optional)最迟上次交易时间
    @request max_trade_amount(Price): (optional)最大交易额，单位为元
    @request max_trade_count(Number): (optional)最大交易量
    @request min_last_trade_time(Date): (optional)最早上次交易时间
    @request min_trade_amount(Price): (optional)最小交易额,单位为元
    @request min_trade_count(Number): (optional)最小交易量
    @request page_size(Number): (optional)表示每页显示的会员数量,page_size的最大值不能超过100条,最小值不能低于1，
    """
    REQUEST = {
        'buyer_nick': {'type': topstruct.String, 'is_required': False},
        'current_page': {'type': topstruct.Number, 'is_required': True},
        'grade': {'type': topstruct.Number, 'is_required': False},
        'max_last_trade_time': {'type': topstruct.Date, 'is_required': False},
        'max_trade_amount': {'type': topstruct.Price, 'is_required': False},
        'max_trade_count': {'type': topstruct.Number, 'is_required': False},
        'min_last_trade_time': {'type': topstruct.Date, 'is_required': False},
        'min_trade_amount': {'type': topstruct.Price, 'is_required': False},
        'min_trade_count': {'type': topstruct.Number, 'is_required': False},
        'page_size': {'type': topstruct.Number, 'is_required': False}
    }

    RESPONSE = {
        'members': {'type': topstruct.BasicMember, 'is_list': False},
        'total_result': {'type': topstruct.Number, 'is_list': False}
    }

    API = 'taobao.crm.members.get'


class CrmMembersGroupBatchaddRequest(TOPRequest):
    """ 为一批会员添加分组，接口返回添加是否成功,如至少有一个会员的分组添加成功，接口就返回成功，否则返回失败，如果当前会员已经拥有当前分组，则直接跳过

    @response is_success(Boolean): 添加操作是否成功

    @request buyer_ids(Number): (required)会员的id（一次最多传入10个）
    @request group_ids(Number): (required)分组id
    """
    REQUEST = {
        'buyer_ids': {'type': topstruct.Number, 'is_required': True},
        'group_ids': {'type': topstruct.Number, 'is_required': True}
    }

    RESPONSE = {
        'is_success': {'type': topstruct.Boolean, 'is_list': False}
    }

    API = 'taobao.crm.members.group.batchadd'


class CrmMembersGroupsBatchdeleteRequest(TOPRequest):
    """ 批量删除多个会员的公共分组，接口返回删除是否成功，该接口只删除多个会员的公共分组，不是公共分组的，不进行删除。如果入参只输入一个会员，则表示删除该会员的某些分组。

    @response is_success(Boolean): 删除是否成功

    @request buyer_ids(Number): (required)买家的Id集合
    @request group_ids(Number): (required)会员需要删除的分组
    """
    REQUEST = {
        'buyer_ids': {'type': topstruct.Number, 'is_required': True},
        'group_ids': {'type': topstruct.Number, 'is_required': True}
    }

    RESPONSE = {
        'is_success': {'type': topstruct.Boolean, 'is_list': False}
    }

    API = 'taobao.crm.members.groups.batchdelete'


class CrmMembersIncrementGetRequest(TOPRequest):
    """ 增量获取会员列表，接口返回符合查询条件的所有会员。任何状态更改都会返回

    @response members(BasicMember): 返回当前页的会员列表
    @response total_result(Number): 记录的总条数

    @request current_page(Number): (required)显示第几页的会员，如果输入的页码大于总共的页码数，例如总共10页，但是current_page的值为11，则返回空白页，最小页数为1
    @request end_modify(Date): (optional)对应买家 最后一次 确认收货或者关闭交易的时间，如果不填写此字段，默认为当前时间
    @request grade(Number): (optional)会员等级，1：普通客户，2：高级会员，3：VIP会员， 4：至尊VIP会员
    @request page_size(Number): (optional)每页显示的会员数，page_size的值不能超过100，最小值要大于1
    @request start_modify(Date): (optional)对应买家 最后一次 确认收货或者关闭交易的时间
    """
    REQUEST = {
        'current_page': {'type': topstruct.Number, 'is_required': True},
        'end_modify': {'type': topstruct.Date, 'is_required': False},
        'grade': {'type': topstruct.Number, 'is_required': False},
        'page_size': {'type': topstruct.Number, 'is_required': False},
        'start_modify': {'type': topstruct.Date, 'is_required': False}
    }

    RESPONSE = {
        'members': {'type': topstruct.BasicMember, 'is_list': False},
        'total_result': {'type': topstruct.Number, 'is_list': False}
    }

    API = 'taobao.crm.members.increment.get'


class CrmMembersSearchRequest(TOPRequest):
    """ 会员列表的高级查询，接口返回符合条件的会员列表.<br>
        注：建议获取09年以后的数据，09年之前的数据不是很完整

    @response members(CrmMember): 根据一定条件查询的卖家会员
    @response total_result(Number): 记录的总条数

    @request buyer_nick(String): (optional)买家昵称
    @request city(String): (optional)城市
    @request current_page(Number): (required)显示第几页的会员，如果输入的页码大于总共的页码数，例如总共10页，但是current_page的值为11，则返回空白页，最小页数为1
    @request grade(Number): (optional)会员等级，1：普通客户，2：高级会员，3：VIP会员, 4：至尊VIP会员
        注：grade=0通过relation_source=2查询
    @request group_id(Number): (optional)分组id
    @request max_avg_price(Price): (optional)最大平均客单价，单位为元
    @request max_close_trade_num(Number): (optional)最大交易关闭笔数
    @request max_item_num(Number): (optional)最大交易宝贝件数
    @request max_last_trade_time(Date): (optional)最迟上次交易时间
    @request max_trade_amount(Price): (optional)最大交易额，单位为元
    @request max_trade_count(Number): (optional)最大交易量
    @request min_avg_price(Price): (optional)最少平均客单价，单位为元
    @request min_close_trade_num(Number): (optional)最小交易关闭的笔数
    @request min_item_num(Number): (optional)最小交易宝贝件数
    @request min_last_trade_time(Date): (optional)最早上次交易时间
    @request min_trade_amount(Price): (optional)最小交易额，单位为元
    @request min_trade_count(Number): (optional)最小交易量
    @request order(String): (optional)指定按哪个字段排序，目前可排序的字段为：relation，trade_count，trade_amount，avg_price，lastest_time
    @request page_size(Number): (optional)每页显示的会员数量，page_size的最大值不能超过100，最小值不能小于1
    @request province(Number): (optional)北京=1,天津=2,河北省=3,山西省=4,内蒙古自治区=5,辽宁省=6,吉林省=7,黑龙江省=8,上海=9,江苏省=10,浙江省=11,安徽省=12,福建省=13,江西省=14,山东省=15,河南省=16,湖北省=17,湖南省=18, 广东省=19,广西壮族自治区=20,海南省=21,重庆=22,四川省=23,贵州省=24,云南省=25,西藏自治区26,陕西省=27,甘肃省=28,青海省=29,宁夏回族自治区=30,新疆维吾尔自治区=31,台湾省=32,香港特别行政区=33,澳门特别行政区=34,海外=35
    @request relation_source(Number): (optional)关系来源，1交易成功，2未成交(grade=0)
    @request sort(String): (optional)用于描述是按升序还是降序排列结果
    """
    REQUEST = {
        'buyer_nick': {'type': topstruct.String, 'is_required': False},
        'city': {'type': topstruct.String, 'is_required': False},
        'current_page': {'type': topstruct.Number, 'is_required': True},
        'grade': {'type': topstruct.Number, 'is_required': False},
        'group_id': {'type': topstruct.Number, 'is_required': False},
        'max_avg_price': {'type': topstruct.Price, 'is_required': False},
        'max_close_trade_num': {'type': topstruct.Number, 'is_required': False},
        'max_item_num': {'type': topstruct.Number, 'is_required': False},
        'max_last_trade_time': {'type': topstruct.Date, 'is_required': False},
        'max_trade_amount': {'type': topstruct.Price, 'is_required': False},
        'max_trade_count': {'type': topstruct.Number, 'is_required': False},
        'min_avg_price': {'type': topstruct.Price, 'is_required': False},
        'min_close_trade_num': {'type': topstruct.Number, 'is_required': False},
        'min_item_num': {'type': topstruct.Number, 'is_required': False},
        'min_last_trade_time': {'type': topstruct.Date, 'is_required': False},
        'min_trade_amount': {'type': topstruct.Price, 'is_required': False},
        'min_trade_count': {'type': topstruct.Number, 'is_required': False},
        'order': {'type': topstruct.String, 'is_required': False},
        'page_size': {'type': topstruct.Number, 'is_required': False},
        'province': {'type': topstruct.Number, 'is_required': False},
        'relation_source': {'type': topstruct.Number, 'is_required': False},
        'sort': {'type': topstruct.String, 'is_required': False}
    }

    RESPONSE = {
        'members': {'type': topstruct.CrmMember, 'is_list': False},
        'total_result': {'type': topstruct.Number, 'is_list': False}
    }

    API = 'taobao.crm.members.search'


class CrmRuleAddRequest(TOPRequest):
    """ 添加分组规则，规则可用于筛选一定条件的会员。过滤条件可以选择客户来源、会员级别 、交易笔数、交易额、上次交易时间、平均客单价、宝贝件数、省份、关闭交易数等，新建规则时必须至少选择一个以上筛选条件。如果输入的规则的筛选条件不正确则不会进行处理，可以将某些分组挂在这个规则下，对被挂在该规则下的分组，系统对现有满足规则的客户都划分到这个分组（异步任务）。每个规则可以应用到多个分组，一个用户的规则上限为5个。

    @response is_success(Boolean): 返回规则添加是否成功
    @response rule_id(Number): 新增的规则ID

    @request grade(Number): (special)会员等级，可选值为：1,2,3,4
    @request group_ids(Number): (special)规则应用分组集合，若分组上有任务，则该分组不能挂到该规则下
    @request max_avg_price(Price): (special)最大平均客单价，单位为元
    @request max_close_trade_num(Number): (special)最大交易关闭数
    @request max_item_num(Number): (special)最大宝贝件数
    @request max_last_trade_time(Date): (special)最迟交易时间
    @request max_trade_amount(Price): (special)最大交易金额，单位为元
    @request max_trade_count(Number): (special)最大交易数
    @request min_avg_price(Price): (special)最小平均客单价，单位元
    @request min_close_trade_num(Number): (special)最少交易关闭数
    @request min_item_num(Number): (special)最少宝贝件数
    @request min_last_trade_time(Date): (special)最早交易日期
        必须为早于今天的某个时间，例如今天是2011-11-11，那么必须填写2011-11-10或者早于此日期的时间
    @request min_trade_amount(Price): (special)最小交易金额,单位元。
    @request min_trade_count(Number): (special)最小交易次数
    @request province(Number): (special)北京=1,天津=2,河北省=3,山西省=4,内蒙古自治区=5,辽宁省=6,吉林省=7,黑龙江省=8,上海=9,江苏省=10,浙江省=11,安徽省=12,福建省=13,江西省=14,山东省=15,河南省=16,湖北省=17,湖南省=18, 广东省=19,广西壮族自治区=20,海南省=21,重庆=22,四川省=23,贵州省=24,云南省=25,西藏自治区26,陕西省=27,甘肃省=28,青海省=29,宁夏回族自治区=30,新疆维吾尔自治区=31,台湾省=32,香港特别行政区=33,澳门特别行政区=34,海外=35
    @request relation_source(Number): (special)客户关系来源,可选值为:1,2
    @request rule_name(String): (required)规则名称
    """
    REQUEST = {
        'grade': {'type': topstruct.Number, 'is_required': False},
        'group_ids': {'type': topstruct.Number, 'is_required': False},
        'max_avg_price': {'type': topstruct.Price, 'is_required': False},
        'max_close_trade_num': {'type': topstruct.Number, 'is_required': False},
        'max_item_num': {'type': topstruct.Number, 'is_required': False},
        'max_last_trade_time': {'type': topstruct.Date, 'is_required': False},
        'max_trade_amount': {'type': topstruct.Price, 'is_required': False},
        'max_trade_count': {'type': topstruct.Number, 'is_required': False},
        'min_avg_price': {'type': topstruct.Price, 'is_required': False},
        'min_close_trade_num': {'type': topstruct.Number, 'is_required': False},
        'min_item_num': {'type': topstruct.Number, 'is_required': False},
        'min_last_trade_time': {'type': topstruct.Date, 'is_required': False},
        'min_trade_amount': {'type': topstruct.Price, 'is_required': False},
        'min_trade_count': {'type': topstruct.Number, 'is_required': False},
        'province': {'type': topstruct.Number, 'is_required': False},
        'relation_source': {'type': topstruct.Number, 'is_required': False},
        'rule_name': {'type': topstruct.String, 'is_required': True}
    }

    RESPONSE = {
        'is_success': {'type': topstruct.Boolean, 'is_list': False},
        'rule_id': {'type': topstruct.Number, 'is_list': False}
    }

    API = 'taobao.crm.rule.add'


class CrmRuleDeleteRequest(TOPRequest):
    """ 分组规则删除

    @response is_success(Boolean): 删除是否成功

    @request rule_id(Number): (required)规则id
    """
    REQUEST = {
        'rule_id': {'type': topstruct.Number, 'is_required': True}
    }

    RESPONSE = {
        'is_success': {'type': topstruct.Boolean, 'is_list': False}
    }

    API = 'taobao.crm.rule.delete'


class CrmRuleGroupSetRequest(TOPRequest):
    """ 将规则应用或取消应用到分组上，add_groups和delete_groups，两个参数最少填写一个。

    @response is_success(Boolean): 操作是否成功

    @request add_groups(Number): (special)需要添加到规则的分组
    @request delete_groups(Number): (special)需要删除的分组
    @request rule_id(Number): (required)规则id
    """
    REQUEST = {
        'add_groups': {'type': topstruct.Number, 'is_required': False},
        'delete_groups': {'type': topstruct.Number, 'is_required': False},
        'rule_id': {'type': topstruct.Number, 'is_required': True}
    }

    RESPONSE = {
        'is_success': {'type': topstruct.Boolean, 'is_list': False}
    }

    API = 'taobao.crm.rule.group.set'


class CrmRulesGetRequest(TOPRequest):
    """ 获取现有的规则列表

    @response rule_list(RuleData): 规则列表
    @response total_result(Number): 记录的总条数

    @request current_page(Number): (required)当前显示第几页，如果current_page超过页码范围或者小于页码范围，将直接返回空白页
    @request page_size(Number): (optional)一页返回的记录的个数
    """
    REQUEST = {
        'current_page': {'type': topstruct.Number, 'is_required': True},
        'page_size': {'type': topstruct.Number, 'is_required': False}
    }

    RESPONSE = {
        'rule_list': {'type': topstruct.RuleData, 'is_list': False},
        'total_result': {'type': topstruct.Number, 'is_list': False}
    }

    API = 'taobao.crm.rules.get'


class CrmShopvipCancelRequest(TOPRequest):
    """ 此接口用于取消VIP优惠

    @response is_success(Boolean): 返回操作是否成功
    """
    REQUEST = {}

    RESPONSE = {
        'is_success': {'type': topstruct.Boolean, 'is_list': False}
    }

    API = 'taobao.crm.shopvip.cancel'


class HuabaoChannelGetRequest(TOPRequest):
    """ 更新频道Id取频道详情

    @response channel(PosterChannel): 频道信息

    @request channel_id(Number): (required)频道Id
    """
    REQUEST = {
        'channel_id': {'type': topstruct.Number, 'is_required': True}
    }

    RESPONSE = {
        'channel': {'type': topstruct.PosterChannel, 'is_list': False}
    }

    API = 'taobao.huabao.channel.get'


class HuabaoChannelsGetRequest(TOPRequest):
    """ 取画报所有频道

    @response channels(PosterChannel): 类目信息
    """
    REQUEST = {}

    RESPONSE = {
        'channels': {'type': topstruct.PosterChannel, 'is_list': False}
    }

    API = 'taobao.huabao.channels.get'


class HuabaoPosterGetRequest(TOPRequest):
    """ 根据画报Id取画报详情

    @response pics(PosterPicture): 画报图片
    @response poster(Poster): 画报信息

    @request poster_id(Number): (required)画报的Id值
    """
    REQUEST = {
        'poster_id': {'type': topstruct.Number, 'is_required': True}
    }

    RESPONSE = {
        'pics': {'type': topstruct.PosterPicture, 'is_list': False},
        'poster': {'type': topstruct.Poster, 'is_list': False}
    }

    API = 'taobao.huabao.poster.get'


class HuabaoPosterGoodsinfoGetRequest(TOPRequest):
    """ 根据画报ID获得与其相关的商品信息

    @response goodsinfolist(PosterGoodsInfo): 和画报相关的商品信息

    @request poster_id(Number): (required)画报的ID
    """
    REQUEST = {
        'poster_id': {'type': topstruct.Number, 'is_required': True}
    }

    RESPONSE = {
        'goodsinfolist': {'type': topstruct.PosterGoodsInfo, 'is_list': False}
    }

    API = 'taobao.huabao.poster.goodsinfo.get'


class HuabaoPostersGetRequest(TOPRequest):
    """ 取指定频道Id的画报列表，可以支持分页

    @response posters(Poster): 画报信息

    @request channel_id(Number): (required)频道的Id值
    @request page_no(Number): (optional)当前页，默认为1（当输入为负，零，或者超出页数范围时，取默认值）
    @request page_size(Number): (optional)查询返回的记录数
    """
    REQUEST = {
        'channel_id': {'type': topstruct.Number, 'is_required': True},
        'page_no': {'type': topstruct.Number, 'is_required': False},
        'page_size': {'type': topstruct.Number, 'is_required': False}
    }

    RESPONSE = {
        'posters': {'type': topstruct.Poster, 'is_list': False}
    }

    API = 'taobao.huabao.posters.get'


class HuabaoSpecialpostersGetRequest(TOPRequest):
    """ 取指定频道Id的指定条数推荐画报

    @response posters(Poster): 画报信息

    @request channel_ids(Number): (required)频道Id
    @request number(Number): (optional)返回的记录数，默认10条，最多20条，如果请求超过20或者小于等于10，则按10条返回 type为NEW时该参数无效,返回为指定频道的最新的一条记录
    @request type(String): (required)类型可选：HOT(热门），RECOMMEND（推荐），NEW（最新）
    """
    REQUEST = {
        'channel_ids': {'type': topstruct.Number, 'is_required': True},
        'number': {'type': topstruct.Number, 'is_required': False},
        'type': {'type': topstruct.String, 'is_required': True}
    }

    RESPONSE = {
        'posters': {'type': topstruct.Poster, 'is_list': False}
    }

    API = 'taobao.huabao.specialposters.get'


class PictureCategoryAddRequest(TOPRequest):
    """ 同一卖家最多添加500个图片分类，图片分类名称长度最大为20个字符

    @response picture_category(PictureCategory): 图片分类信息

    @request parent_id(Number): (optional)图片分类的父分类,一级分类的parent_id为0,二级分类的则为其父分类的picture_category_id
    @request picture_category_name(String): (required)图片分类名称，最大长度20字符，中英文都算一字符，不能为空
    """
    REQUEST = {
        'parent_id': {'type': topstruct.Number, 'is_required': False},
        'picture_category_name': {'type': topstruct.String, 'is_required': True}
    }

    RESPONSE = {
        'picture_category': {'type': topstruct.PictureCategory, 'is_list': False}
    }

    API = 'taobao.picture.category.add'


class PictureCategoryGetRequest(TOPRequest):
    """ 获取图片分类信息

    @response picture_categories(PictureCategory): 图片分类

    @request modified_time(Date): (optional)图片分类的修改时间点，格式:yyyy-MM-dd HH:mm:ss。查询此修改时间点之后到目前的图片分类。
    @request parent_id(Number): (optional)取二级分类时设置为对应父分类id
        取一级分类时父分类id设为0
        取全部分类的时候不设或设为-1
    @request picture_category_id(Number): (optional)图片分类ID
    @request picture_category_name(String): (optional)图片分类名，不支持模糊查询
    @request type(String): (optional)分类类型,fixed代表店铺装修分类类别，auction代表宝贝分类类别，user-define代表用户自定义分类类别
    """
    REQUEST = {
        'modified_time': {'type': topstruct.Date, 'is_required': False},
        'parent_id': {'type': topstruct.Number, 'is_required': False},
        'picture_category_id': {'type': topstruct.Number, 'is_required': False},
        'picture_category_name': {'type': topstruct.String, 'is_required': False},
        'type': {'type': topstruct.String, 'is_required': False}
    }

    RESPONSE = {
        'picture_categories': {'type': topstruct.PictureCategory, 'is_list': False}
    }

    API = 'taobao.picture.category.get'


class PictureCategoryUpdateRequest(TOPRequest):
    """ 更新图片分类的名字，或者更新图片分类的父分类（即分类移动）。只能移动2级分类到非2级分类，默认分类和1级分类不可移动。

    @response done(Boolean): 更新图片分类是否成功

    @request category_id(Number): (required)要更新的图片分类的id
    @request category_name(String): (optional)图片分类的新名字，最大长度20字符，不能为空
    @request parent_id(Number): (optional)图片分类的新父分类id
    """
    REQUEST = {
        'category_id': {'type': topstruct.Number, 'is_required': True},
        'category_name': {'type': topstruct.String, 'is_required': False},
        'parent_id': {'type': topstruct.Number, 'is_required': False}
    }

    RESPONSE = {
        'done': {'type': topstruct.Boolean, 'is_list': False}
    }

    API = 'taobao.picture.category.update'


class PictureDeleteRequest(TOPRequest):
    """ 删除图片空间图片

    @response success(Boolean): 是否删除

    @request picture_ids(String): (required)图片ID字符串,可以一个也可以一组,用英文逗号间隔,如450,120,155
    """
    REQUEST = {
        'picture_ids': {'type': topstruct.String, 'is_required': True}
    }

    RESPONSE = {
        'success': {'type': topstruct.Boolean, 'is_list': False}
    }

    API = 'taobao.picture.delete'


class PictureGetRequest(TOPRequest):
    """ 获取图片信息

    @response pictures(Picture): 图片信息列表
    @response totalResults(Number): 总的结果数

    @request deleted(String): (optional)是否删除,unfroze代表没有删除
    @request end_date(Date): (optional)查询上传结束时间点,格式:yyyy-MM-dd HH:mm:ss
    @request modified_time(Date): (optional)图片被修改的时间点，格式:yyyy-MM-dd HH:mm:ss。查询此修改时间点之后到目前的图片。
    @request order_by(String): (optional)图片查询结果排序,time:desc按上传时间从晚到早(默认), time:asc按上传时间从早到晚,sizes:desc按图片从大到小，sizes:asc按图片从小到大,默认time:desc
    @request page_no(Number): (optional)页码.传入值为1代表第一页,传入值为2代表第二页,依此类推,默认值为1
    @request page_size(Number): (optional)每页条数.每页返回最多返回100条,默认值40
    @request picture_category_id(Number): (optional)图片分类ID
    @request picture_id(Number): (optional)图片ID
    @request start_date(Date): (optional)查询上传开始时间点,格式:yyyy-MM-dd HH:mm:ss
    @request title(String): (optional)图片标题,最大长度50字符,中英文都算一字符
    """
    REQUEST = {
        'deleted': {'type': topstruct.String, 'is_required': False},
        'end_date': {'type': topstruct.Date, 'is_required': False},
        'modified_time': {'type': topstruct.Date, 'is_required': False},
        'order_by': {'type': topstruct.String, 'is_required': False},
        'page_no': {'type': topstruct.Number, 'is_required': False},
        'page_size': {'type': topstruct.Number, 'is_required': False},
        'picture_category_id': {'type': topstruct.Number, 'is_required': False},
        'picture_id': {'type': topstruct.Number, 'is_required': False},
        'start_date': {'type': topstruct.Date, 'is_required': False},
        'title': {'type': topstruct.String, 'is_required': False}
    }

    RESPONSE = {
        'pictures': {'type': topstruct.Picture, 'is_list': False},
        'totalResults': {'type': topstruct.Number, 'is_list': False}
    }

    API = 'taobao.picture.get'


class PictureIsreferencedGetRequest(TOPRequest):
    """ 查询图片是否被引用，被引用返回true，未被引用返回false

    @response is_referenced(Boolean): 图片是否被引用

    @request picture_id(Number): (required)图片id
    """
    REQUEST = {
        'picture_id': {'type': topstruct.Number, 'is_required': True}
    }

    RESPONSE = {
        'is_referenced': {'type': topstruct.Boolean, 'is_list': False}
    }

    API = 'taobao.picture.isreferenced.get'


class PictureReferencedGetRequest(TOPRequest):
    """ 查询图片被引用的详情，包括引用者，引用者名字，引用者地址

    @response references(ReferenceDetail): 引用详情列表

    @request picture_id(Number): (required)图片id
    """
    REQUEST = {
        'picture_id': {'type': topstruct.Number, 'is_required': True}
    }

    RESPONSE = {
        'references': {'type': topstruct.ReferenceDetail, 'is_list': False}
    }

    API = 'taobao.picture.referenced.get'


class PictureReplaceRequest(TOPRequest):
    """ 替换一张图片，只替换图片数据，图片名称，图片分类等保持不变。

    @response done(Boolean): 图片替换是否成功

    @request image_data(Image): (required)图片二进制文件流,不能为空,允许png、jpg、gif图片格式
    @request picture_id(Number): (required)要替换的图片的id，必须大于0
    """
    REQUEST = {
        'image_data': {'type': topstruct.Image, 'is_required': True},
        'picture_id': {'type': topstruct.Number, 'is_required': True}
    }

    RESPONSE = {
        'done': {'type': topstruct.Boolean, 'is_list': False}
    }

    API = 'taobao.picture.replace'


class PictureUpdateRequest(TOPRequest):
    """ 修改指定图片的图片名

    @response done(Boolean): 更新是否成功

    @request new_name(String): (required)新的图片名，最大长度50字符，不能为空
    @request picture_id(Number): (required)要更改名字的图片的id
    """
    REQUEST = {
        'new_name': {'type': topstruct.String, 'is_required': True},
        'picture_id': {'type': topstruct.Number, 'is_required': True}
    }

    RESPONSE = {
        'done': {'type': topstruct.Boolean, 'is_list': False}
    }

    API = 'taobao.picture.update'


class PictureUploadRequest(TOPRequest):
    """ 上传单张图片

    @response picture(Picture): 当前上传的一张图片信息

    @request image_input_title(String): (required)包括后缀名的图片标题,不能为空，如Bule.jpg,有些卖家希望图片上传后取图片文件的默认名
    @request img(Image): (required)图片二进制文件流,不能为空,允许png、jpg、gif图片格式
    @request picture_category_id(Number): (required)图片分类ID，设置具体某个分类ID或设置0上传到默认分类，只能传入一个分类
    @request title(String): (optional)图片标题,如果为空,传的图片标题就取去掉后缀名的image_input_title,超过50字符长度会截取50字符,重名会在标题末尾加"(1)";标题末尾已经有"(数字)"了，则数字加1
    """
    REQUEST = {
        'image_input_title': {'type': topstruct.String, 'is_required': True},
        'img': {'type': topstruct.Image, 'is_required': True},
        'picture_category_id': {'type': topstruct.Number, 'is_required': True},
        'title': {'type': topstruct.String, 'is_required': False}
    }

    RESPONSE = {
        'picture': {'type': topstruct.Picture, 'is_list': False}
    }

    API = 'taobao.picture.upload'


class PictureUserinfoGetRequest(TOPRequest):
    """ 查询用户的图片空间使用信息，包括：订购量，已使用容量，免费容量，总的可使用容量，订购有效期，剩余容量

    @response user_info(UserInfo): 用户使用图片空间的信息
    """
    REQUEST = {}

    RESPONSE = {
        'user_info': {'type': topstruct.UserInfo, 'is_list': False}
    }

    API = 'taobao.picture.userinfo.get'


class SellercenterRoleAddRequest(TOPRequest):
    """ 给指定的卖家创建新的子账号角色<br/>
        如果需要授权的权限点有下级权限点或上级权限点，把该权限点的父权限点和该权限点的所有子权限都一并做赋权操作，并递归处理<br/>例如：权限点列表如下<br/>
        code=sell 宝贝管理<br/>
        ---------|code=sm 店铺管理<br/>
        ---------|---------|code=sm-design 如店铺装修<br/>
        ---------|---------|---------|code=sm-tbd-visit内店装修入口<br/>
        ---------|---------|---------|code=sm-tbd-publish内店装修发布<br/>
        ---------|---------|code=phone 手机淘宝店铺<br/>
        调用改接口给code=sm-design店铺装修赋权时，同时会将下列权限点都赋予默认角色<br/>
        code=sell 宝贝管理<br/>
        ---------|code=sm 店铺管理<br/>
        ---------|---------|code=sm-design 如店铺装修<br/>
        ---------|---------|---------|code=sm-tbd-visit内店装修入口<br/>
        ---------|---------|---------|code=sm-tbd-publish内店装修发布<br/>

    @response role(Role): 子账号角色

    @request description(String): (optional)角色描述
    @request name(String): (required)角色名
    @request nick(String): (required)表示卖家昵称
    @request permission_codes(String): (optional)需要授权的权限点permission_code列表,以","分割.其code值可以通过调用taobao.sellercenter.user.permissions.get返回，其中permission.is_authorize=1的权限点可以通过本接口授权给对应角色。
    """
    REQUEST = {
        'description': {'type': topstruct.String, 'is_required': False},
        'name': {'type': topstruct.String, 'is_required': True},
        'nick': {'type': topstruct.String, 'is_required': True},
        'permission_codes': {'type': topstruct.String, 'is_required': False}
    }

    RESPONSE = {
        'role': {'type': topstruct.Role, 'is_list': False}
    }

    API = 'taobao.sellercenter.role.add'


class SellercenterRoleInfoGetRequest(TOPRequest):
    """ 获取指定角色的信息。只能查询属于自己的角色信息 (主账号或者某个主账号的子账号登陆，只能查询属于该主账号的角色信息)

    @response role(Role): 角色具体信息

    @request role_id(Number): (required)角色id
    """
    REQUEST = {
        'role_id': {'type': topstruct.Number, 'is_required': True}
    }

    RESPONSE = {
        'role': {'type': topstruct.Role, 'is_list': False}
    }

    API = 'taobao.sellercenter.role.info.get'


class SellercenterRolemembersGetRequest(TOPRequest):
    """ 获取指定卖家的角色下属员工列表，只能获取属于登陆者自己的信息。

    @response subusers(SubUserInfo): 子账号基本信息列表。具体信息为id、子账号用户名、主账号id、主账号昵称、当前状态值、是否分流

    @request role_id(Number): (required)角色id
    """
    REQUEST = {
        'role_id': {'type': topstruct.Number, 'is_required': True}
    }

    RESPONSE = {
        'subusers': {'type': topstruct.SubUserInfo, 'is_list': False}
    }

    API = 'taobao.sellercenter.rolemembers.get'


class SellercenterRolesGetRequest(TOPRequest):
    """ 获取指定卖家的角色列表，只能获取属于登陆者自己的信息。

    @response roles(Role): 卖家子账号角色列表。<br/>返回对象为 role数据对象中的role_id，role_name，description，seller_id，create_time，modified_time。不包含permissions(权限点)

    @request nick(String): (required)卖家昵称(只允许查询自己的信息：当前登陆者)
    """
    REQUEST = {
        'nick': {'type': topstruct.String, 'is_required': True}
    }

    RESPONSE = {
        'roles': {'type': topstruct.Role, 'is_list': False}
    }

    API = 'taobao.sellercenter.roles.get'


class SellercenterSubuserPermissionsRolesGetRequest(TOPRequest):
    """ 查询指定的子账号的被直接赋予的权限信息和角色信息。<br/>返回对象中包括直接赋予子账号的权限点信息、被赋予的角色以及角色的对应权限点信息。

    @response subuser_permission(SubUserPermission): 子账号被所拥有的权限

    @request nick(String): (required)子账号昵称(子账号标识)
    """
    REQUEST = {
        'nick': {'type': topstruct.String, 'is_required': True}
    }

    RESPONSE = {
        'subuser_permission': {'type': topstruct.SubUserPermission, 'is_list': False}
    }

    API = 'taobao.sellercenter.subuser.permissions.roles.get'


class SellercenterSubusersGetRequest(TOPRequest):
    """ 根据主账号nick查询该账号下所有的子账号列表，只能查询属于自己的账号信息 (主账号以及所属子账号)

    @response subusers(SubUserInfo): 子账号基本信息列表。具体信息为id、子账号用户名、主账号id、主账号昵称、当前状态值、是否分流

    @request nick(String): (required)表示卖家昵称
    """
    REQUEST = {
        'nick': {'type': topstruct.String, 'is_required': True}
    }

    RESPONSE = {
        'subusers': {'type': topstruct.SubUserInfo, 'is_list': False}
    }

    API = 'taobao.sellercenter.subusers.get'


class SellercenterUserPermissionsGetRequest(TOPRequest):
    """ 获取指定用户的权限集合，并不组装成树。如果是主账号，返回所有的权限列表；如果是子账号，返回所有已授权的权限。只能查询属于自己的账号信息 (如果是主账号，则是主账号以及所属子账号，如果是子账号则是对应主账号以及所属子账号)

    @response permissions(Permission): 权限列表

    @request nick(String): (required)用户标识
    """
    REQUEST = {
        'nick': {'type': topstruct.String, 'is_required': True}
    }

    RESPONSE = {
        'permissions': {'type': topstruct.Permission, 'is_list': False}
    }

    API = 'taobao.sellercenter.user.permissions.get'


class VasOrderSearchRequest(TOPRequest):
    """ 用于ISV查询自己名下的应用及收费项目的订单记录（已付款订单）。
        目前所有应用调用此接口的频率限制为200次/分钟，即每分钟内，所有应用调用此接口的次数加起来最多为200次。
        建议用于查询前一日的历史记录。

    @response article_biz_orders(ArticleBizOrder): 商品订单对象
    @response total_item(Number): 总记录数

    @request article_code(String): (required)应用收费代码，从合作伙伴后台（my.open.taobao.com）-收费管理-收费项目列表 能够获得该应用的收费代码
    @request biz_order_id(Number): (optional)订单号
    @request biz_type(Number): (optional)订单类型，1=新订 2=续订 3=升级 4=后台赠送 5=后台自动续订 6=订单审核后生成订购关系（暂时用不到） 空=全部
    @request end_created(Date): (optional)订单创建时间（订购时间）结束值
    @request item_code(String): (optional)收费项目代码，从合作伙伴后台（my.open.taobao.com）-收费管理-收费项目列表 能够获得收费项目代码
    @request nick(String): (optional)淘宝会员名
    @request order_id(Number): (optional)子订单号
    @request page_no(Number): (optional)页码
    @request page_size(Number): (optional)一页包含的记录数
    @request start_created(Date): (optional)订单创建时间（订购时间）起始值（当start_created和end_created都不填写时，默认返回最近90天的数据）
    """
    REQUEST = {
        'article_code': {'type': topstruct.String, 'is_required': True},
        'biz_order_id': {'type': topstruct.Number, 'is_required': False},
        'biz_type': {'type': topstruct.Number, 'is_required': False},
        'end_created': {'type': topstruct.Date, 'is_required': False},
        'item_code': {'type': topstruct.String, 'is_required': False},
        'nick': {'type': topstruct.String, 'is_required': False},
        'order_id': {'type': topstruct.Number, 'is_required': False},
        'page_no': {'type': topstruct.Number, 'is_required': False},
        'page_size': {'type': topstruct.Number, 'is_required': False},
        'start_created': {'type': topstruct.Date, 'is_required': False}
    }

    RESPONSE = {
        'article_biz_orders': {'type': topstruct.ArticleBizOrder, 'is_list': False},
        'total_item': {'type': topstruct.Number, 'is_list': False}
    }

    API = 'taobao.vas.order.search'


class VasSubscSearchRequest(TOPRequest):
    """ 用于ISV查询自己名下的应用及收费项目的订购记录

    @response article_subs(ArticleSub): 订购关系对象
    @response total_item(Number): 总记录数

    @request article_code(String): (required)应用收费代码，从合作伙伴后台（my.open.taobao.com）-收费管理-收费项目列表 能够获得该应用的收费代码
    @request autosub(Boolean): (optional)是否自动续费，true=自动续费 false=非自动续费 空=全部
    @request end_deadline(Date): (optional)到期时间结束值
    @request expire_notice(Boolean): (optional)是否到期提醒，true=到期提醒 false=非到期提醒 空=全部
    @request item_code(String): (optional)收费项目代码，从合作伙伴后台（my.open.taobao.com）-收费管理-收费项目列表 能够获得收费项目代码
    @request nick(String): (optional)淘宝会员名
    @request page_no(Number): (optional)页码
    @request page_size(Number): (optional)一页包含的记录数
    @request start_deadline(Date): (optional)到期时间起始值（当start_deadline和end_deadline都不填写时，默认返回最近90天的数据）
    @request status(Number): (optional)订购记录状态，1=有效 2=过期 空=全部
    """
    REQUEST = {
        'article_code': {'type': topstruct.String, 'is_required': True},
        'autosub': {'type': topstruct.Boolean, 'is_required': False},
        'end_deadline': {'type': topstruct.Date, 'is_required': False},
        'expire_notice': {'type': topstruct.Boolean, 'is_required': False},
        'item_code': {'type': topstruct.String, 'is_required': False},
        'nick': {'type': topstruct.String, 'is_required': False},
        'page_no': {'type': topstruct.Number, 'is_required': False},
        'page_size': {'type': topstruct.Number, 'is_required': False},
        'start_deadline': {'type': topstruct.Date, 'is_required': False},
        'status': {'type': topstruct.Number, 'is_required': False}
    }

    RESPONSE = {
        'article_subs': {'type': topstruct.ArticleSub, 'is_list': False},
        'total_item': {'type': topstruct.Number, 'is_list': False}
    }

    API = 'taobao.vas.subsc.search'


class VasSubscribeGetRequest(TOPRequest):
    """ 用于ISV根据登录进来的淘宝会员名查询该为该会员开通哪些收费项目，ISV只能查询自己名下的应用及收费项目的订购情况

    @response article_user_subscribes(ArticleUserSubscribe): 用户订购信息

    @request article_code(String): (required)应用收费代码，从合作伙伴后台（my.open.taobao.com）-收费管理-收费项目列表 能够获得该应用的收费代码
    @request nick(String): (required)淘宝会员名
    """
    REQUEST = {
        'article_code': {'type': topstruct.String, 'is_required': True},
        'nick': {'type': topstruct.String, 'is_required': True}
    }

    RESPONSE = {
        'article_user_subscribes': {'type': topstruct.ArticleUserSubscribe, 'is_list': False}
    }

    API = 'taobao.vas.subscribe.get'


class RefundGetRequest(TOPRequest):
    """ 获取单笔退款详情

    @response refund(Refund): 搜索到的交易信息列表

    @request fields(FieldList): (required)需要返回的字段。目前支持有：refund_id, alipay_no, tid, oid, buyer_nick, seller_nick, total_fee, status, created, refund_fee, good_status, has_good_return, payment, reason, desc, num_iid, title, price, num, good_return_time, company_name, sid, address, shipping_type, refund_remind_timeout
    @request refund_id(Number): (required)退款单号
    """
    REQUEST = {
        'fields': {'type': topstruct.FieldList, 'is_required': True, 'optional': topstruct.Set({'refund_remind_timeout', 'total_fee', 'tid', 'desc', 'status', 'refund_fee', 'num', 'price', 'address', 'buyer_nick', 'alipay_no', 'num_iid', 'oid', 'shipping_type', 'sid', 'payment', 'refund_id', 'created', 'company_name', 'seller_nick', 'reason', 'title', 'good_status', 'good_return_time', 'has_good_return'})},
        'refund_id': {'type': topstruct.Number, 'is_required': True}
    }

    RESPONSE = {
        'refund': {'type': topstruct.Refund, 'is_list': False}
    }

    API = 'taobao.refund.get'


class RefundMessageAddRequest(TOPRequest):
    """ 创建退款留言/凭证

    @response refund_message(RefundMessage): 退款信息。包含id和created

    @request content(String): (required)留言内容。最大长度: 400个字节
    @request image(Image): (optional)图片（凭证）。类型: JPG,GIF,PNG;最大为: 500K
    @request refund_id(Number): (required)退款编号。
    """
    REQUEST = {
        'content': {'type': topstruct.String, 'is_required': True},
        'image': {'type': topstruct.Image, 'is_required': False},
        'refund_id': {'type': topstruct.Number, 'is_required': True}
    }

    RESPONSE = {
        'refund_message': {'type': topstruct.RefundMessage, 'is_list': False}
    }

    API = 'taobao.refund.message.add'


class RefundMessagesGetRequest(TOPRequest):
    """ 单笔退款详情

    @response refund_messages(RefundMessage): 搜索到的留言凭证信息列表
    @response total_results(Number): 搜索到的留言凭证总数

    @request fields(FieldList): (required)需返回的字段列表。可选值：RefundMessage结构体中的所有字段，以半角逗号(,)分隔。
    @request page_no(Number): (optional)页码。取值范围:大于零的整数; 默认值:1
    @request page_size(Number): (optional)每页条数。取值范围:大于零的整数; 默认值:40;最大值:100
    @request refund_id(Number): (required)退款单号
    """
    REQUEST = {
        'fields': {'type': topstruct.FieldList, 'is_required': True, 'optional': topstruct.Set({'owner_nick', 'pic_urls', 'refund_id', 'created', 'message_type', 'owner_role', 'owner_id', 'content', 'id'})},
        'page_no': {'type': topstruct.Number, 'is_required': False},
        'page_size': {'type': topstruct.Number, 'is_required': False},
        'refund_id': {'type': topstruct.Number, 'is_required': True}
    }

    RESPONSE = {
        'refund_messages': {'type': topstruct.RefundMessage, 'is_list': False},
        'total_results': {'type': topstruct.Number, 'is_list': False}
    }

    API = 'taobao.refund.messages.get'


class RefundRefuseRequest(TOPRequest):
    """ 卖家拒绝单笔退款交易，要求如下：
        1. 传入的refund_id和相应的tid, oid必须匹配
        2. 如果一笔订单只有一笔子订单，则tid必须与oid相同
        3. 只有卖家才能执行拒绝退款操作
        4. 以下三种情况不能退款：卖家未发货；7天无理由退换货；网游订单

    @response refund(Refund): 拒绝退款成功后，会返回Refund数据结构中的refund_id, status, modified字段

    @request oid(Number): (required)退款记录对应的交易子订单号
    @request refund_id(Number): (required)退款单号
    @request refuse_message(String): (required)拒绝退款时的说明信息，长度2-200
    @request refuse_proof(Image): (optional)拒绝退款时的退款凭证，一般是卖家拒绝退款时使用的发货凭证，最大长度130000字节，支持的图片格式：GIF, JPG, PNG
    @request tid(Number): (required)退款记录对应的交易订单号
    """
    REQUEST = {
        'oid': {'type': topstruct.Number, 'is_required': True},
        'refund_id': {'type': topstruct.Number, 'is_required': True},
        'refuse_message': {'type': topstruct.String, 'is_required': True},
        'refuse_proof': {'type': topstruct.Image, 'is_required': False},
        'tid': {'type': topstruct.Number, 'is_required': True}
    }

    RESPONSE = {
        'refund': {'type': topstruct.Refund, 'is_list': False}
    }

    API = 'taobao.refund.refuse'


class RefundsApplyGetRequest(TOPRequest):
    """ 查询买家申请的退款列表，且查询外店的退款列表时需要指定交易类型

    @response refunds(Refund): 搜索到的退款信息列表
    @response total_results(Number): 搜索到的交易信息总数

    @request fields(FieldList): (required)需要返回的字段。目前支持有：refund_id, tid, title, buyer_nick, seller_nick, total_fee, status, created, refund_fee
    @request page_no(Number): (optional)页码。传入值为 1 代表第一页，传入值为 2 代表第二页，依此类推。默认返回的数据是从第一页开始
    @request page_size(Number): (optional)每页条数。取值范围:大于零的整数; 默认值:40;最大值:100
    @request seller_nick(String): (optional)卖家昵称
    @request status(String): (optional)退款状态，默认查询所有退款状态的数据，除了默认值外每次只能查询一种状态。
        WAIT_SELLER_AGREE(买家已经申请退款，等待卖家同意)
        WAIT_BUYER_RETURN_GOODS(卖家已经同意退款，等待买家退货)
        WAIT_SELLER_CONFIRM_GOODS(买家已经退货，等待卖家确认收货)
        SELLER_REFUSE_BUYER(卖家拒绝退款)
        CLOSED(退款关闭)
        SUCCESS(退款成功)
    @request type(String): (optional)交易类型列表，一次查询多种类型可用半角逗号分隔，默认同时查询guarantee_trade, auto_delivery的2种类型的数据。
        fixed(一口价)
        auction(拍卖)
        guarantee_trade(一口价、拍卖)
        independent_simple_trade(旺店入门版交易)
        independent_shop_trade(旺店标准版交易)
        auto_delivery(自动发货)
        ec(直冲)
        cod(货到付款)
        fenxiao(分销)
        game_equipment(游戏装备)
        shopex_trade(ShopEX交易)
        netcn_trade(万网交易)
        external_trade(统一外部交易)
    """
    REQUEST = {
        'fields': {'type': topstruct.FieldList, 'is_required': True, 'optional': topstruct.Set({'buyer_nick', 'total_fee', 'tid', 'seller_nick', 'refund_id', 'title', 'created', 'status', 'refund_fee'})},
        'page_no': {'type': topstruct.Number, 'is_required': False},
        'page_size': {'type': topstruct.Number, 'is_required': False},
        'seller_nick': {'type': topstruct.String, 'is_required': False},
        'status': {'type': topstruct.String, 'is_required': False},
        'type': {'type': topstruct.String, 'is_required': False}
    }

    RESPONSE = {
        'refunds': {'type': topstruct.Refund, 'is_list': False},
        'total_results': {'type': topstruct.Number, 'is_list': False}
    }

    API = 'taobao.refunds.apply.get'


class RefundsReceiveGetRequest(TOPRequest):
    """ 查询卖家收到的退款列表，查询外店的退款列表时需要指定交易类型

    @response refunds(Refund): 搜索到的退款信息列表
    @response total_results(Number): 搜索到的交易信息总数

    @request buyer_nick(String): (optional)买家昵称
    @request end_modified(Date): (optional)查询修改时间结束。格式: yyyy-MM-dd HH:mm:ss
    @request fields(FieldList): (required)需要返回的字段。目前支持有：refund_id, tid, title, buyer_nick, seller_nick, total_fee, status, created, refund_fee, oid, good_status, company_name, sid, payment, reason, desc, has_good_return, modified, order_status
    @request page_no(Number): (optional)页码。取值范围:大于零的整数; 默认值:1
    @request page_size(Number): (optional)每页条数。取值范围:大于零的整数; 默认值:40;最大值:100
    @request start_modified(Date): (optional)查询修改时间开始。格式: yyyy-MM-dd HH:mm:ss
    @request status(String): (optional)退款状态，默认查询所有退款状态的数据，除了默认值外每次只能查询一种状态。
        WAIT_SELLER_AGREE(买家已经申请退款，等待卖家同意)
        WAIT_BUYER_RETURN_GOODS(卖家已经同意退款，等待买家退货)
        WAIT_SELLER_CONFIRM_GOODS(买家已经退货，等待卖家确认收货)
        SELLER_REFUSE_BUYER(卖家拒绝退款)
        CLOSED(退款关闭)
        SUCCESS(退款成功)
    @request type(String): (optional)交易类型列表，一次查询多种类型可用半角逗号分隔，默认同时查询guarantee_trade, auto_delivery的2种类型的数据。
        fixed(一口价)
        auction(拍卖)
        guarantee_trade(一口价、拍卖)
        independent_simple_trade(旺店入门版交易)
        independent_shop_trade(旺店标准版交易)
        auto_delivery(自动发货)
        ec(直冲)
        cod(货到付款)
        fenxiao(分销)
        game_equipment(游戏装备)
        shopex_trade(ShopEX交易)
        netcn_trade(万网交易)
        external_trade(统一外部交易)
    """
    REQUEST = {
        'buyer_nick': {'type': topstruct.String, 'is_required': False},
        'end_modified': {'type': topstruct.Date, 'is_required': False},
        'fields': {'type': topstruct.FieldList, 'is_required': True, 'optional': topstruct.Set({'buyer_nick', 'total_fee', 'tid', 'oid', 'desc', 'sid', 'seller_nick', 'payment', 'refund_id', 'reason', 'title', 'modified', 'created', 'status', 'good_status', 'refund_fee', 'order_status', 'company_name', 'has_good_return'})},
        'page_no': {'type': topstruct.Number, 'is_required': False},
        'page_size': {'type': topstruct.Number, 'is_required': False},
        'start_modified': {'type': topstruct.Date, 'is_required': False},
        'status': {'type': topstruct.String, 'is_required': False},
        'type': {'type': topstruct.String, 'is_required': False}
    }

    RESPONSE = {
        'refunds': {'type': topstruct.Refund, 'is_list': False},
        'total_results': {'type': topstruct.Number, 'is_list': False}
    }

    API = 'taobao.refunds.receive.get'


class JianghuFanCheckRequest(TOPRequest):
    """ 判断是否是粉丝

    @response result(Check): true or false

    @request follower_id(Number): (required)粉丝的id
    @request user_id(Number): (required)达人的id值
    """
    REQUEST = {
        'follower_id': {'type': topstruct.Number, 'is_required': True},
        'user_id': {'type': topstruct.Number, 'is_required': True}
    }

    RESPONSE = {
        'result': {'type': topstruct.Check, 'is_list': False}
    }

    API = 'taobao.jianghu.fan.check'


class JianghuFanFollowRequest(TOPRequest):
    """ 用户对一个掌柜进行关注.
        关注操作失败返回对应的错误码.
        已经关注的过再调用时，返回错误信息，提示已经关注过。

    @response follow_result(Boolean): true 成功。false 失败

    @request shop_owner_id(Number): (required)掌柜的id，被关注者的id
    """
    REQUEST = {
        'shop_owner_id': {'type': topstruct.Number, 'is_required': True}
    }

    RESPONSE = {
        'follow_result': {'type': topstruct.Boolean, 'is_list': False}
    }

    API = 'taobao.jianghu.fan.follow'


class CategoryrecommendItemsGetRequest(TOPRequest):
    """ 根据类目信息推荐相关联的宝贝集

    @response favorite_items(FavoriteItem): 返回关联的商品集合

    @request category_id(Number): (required)传入叶子类目ID
    @request count(Number): (required)请求个数，建议获取20个
    @request ext(String): (optional)额外参数
    @request recommend_type(Number): (required)请求类型，1：类目下热门商品推荐。其他值当非法值处理
    """
    REQUEST = {
        'category_id': {'type': topstruct.Number, 'is_required': True},
        'count': {'type': topstruct.Number, 'is_required': True},
        'ext': {'type': topstruct.String, 'is_required': False},
        'recommend_type': {'type': topstruct.Number, 'is_required': True}
    }

    RESPONSE = {
        'favorite_items': {'type': topstruct.FavoriteItem, 'is_list': False}
    }

    API = 'taobao.categoryrecommend.items.get'


class ItemrecommendItemsGetRequest(TOPRequest):
    """ 根据推荐类型获取推荐的关联关系商品

    @response values(FavoriteItem): 返回的推荐商品列表结果集

    @request count(Number): (required)请求返回宝贝的个数，建议取20个
    @request ext(String): (optional)额外的参数信息
    @request item_id(Number): (required)商品ID
    @request recommend_type(Number): (required)查询类型标识符，可传入1-3，1：同类商品推荐，2：异类商品推荐， 3：同店商品推荐。其他值当非法值处理
    """
    REQUEST = {
        'count': {'type': topstruct.Number, 'is_required': True},
        'ext': {'type': topstruct.String, 'is_required': False},
        'item_id': {'type': topstruct.Number, 'is_required': True},
        'recommend_type': {'type': topstruct.Number, 'is_required': True}
    }

    RESPONSE = {
        'values': {'type': topstruct.FavoriteItem, 'is_list': False}
    }

    API = 'taobao.itemrecommend.items.get'


class ShoprecommendItemsGetRequest(TOPRequest):
    """ 根据店铺信息推荐相关联的宝贝集

    @response favorite_items(FavoriteItem): 返回与店铺关联的宝贝集合

    @request count(Number): (required)请求个数，建议获取10个
    @request ext(String): (optional)额外参数
    @request recommend_type(Number): (required)请求类型，1：店内热门商品推荐。其他值当非法值处理
    @request seller_id(Number): (required)传入卖家ID
    """
    REQUEST = {
        'count': {'type': topstruct.Number, 'is_required': True},
        'ext': {'type': topstruct.String, 'is_required': False},
        'recommend_type': {'type': topstruct.Number, 'is_required': True},
        'seller_id': {'type': topstruct.Number, 'is_required': True}
    }

    RESPONSE = {
        'favorite_items': {'type': topstruct.FavoriteItem, 'is_list': False}
    }

    API = 'taobao.shoprecommend.items.get'


class ShoprecommendShopsGetRequest(TOPRequest):
    """ 根据店铺信息推荐相关联的店铺集

    @response favorite_shops(FavoriteShop): 返回与店铺关联的店铺集

    @request count(Number): (required)请求个数，建议获取16个
    @request ext(String): (optional)额外参数
    @request recommend_type(Number): (required)请求类型，1：关联店铺推荐。其他值当非法值处理
    @request seller_id(Number): (required)传入卖家ID
    """
    REQUEST = {
        'count': {'type': topstruct.Number, 'is_required': True},
        'ext': {'type': topstruct.String, 'is_required': False},
        'recommend_type': {'type': topstruct.Number, 'is_required': True},
        'seller_id': {'type': topstruct.Number, 'is_required': True}
    }

    RESPONSE = {
        'favorite_shops': {'type': topstruct.FavoriteShop, 'is_list': False}
    }

    API = 'taobao.shoprecommend.shops.get'


class UserrecommendItemsGetRequest(TOPRequest):
    """ 根据用户信息推荐相关联的宝贝集。仅支持widget入口调用，需要同时校验淘宝cookie登陆情况，以及cookie和session授权的一致性。调用入口为/widget/rest。签名方法简化为Hmac-md5,hmac(secret+‘app_key' ＋app_key +'timestamp' + timestamp+secret)。timestamp为60分钟内有效
        此API为组件API，调用方式需要参照：http://open.taobao.com/doc/detail.htm?id=988，以JS-SDK调用

    @response favorite_items(FavoriteItem): 返回用户相关的关联宝贝集合

    @request count(Number): (required)请求个数，建议取20个
    @request ext(String): (optional)额外参数
    @request recommend_type(Number): (required)请求类型，1：用户购买意图。其他值当非法值处理
    """
    REQUEST = {
        'count': {'type': topstruct.Number, 'is_required': True},
        'ext': {'type': topstruct.String, 'is_required': False},
        'recommend_type': {'type': topstruct.Number, 'is_required': True}
    }

    RESPONSE = {
        'favorite_items': {'type': topstruct.FavoriteItem, 'is_list': False}
    }

    API = 'taobao.userrecommend.items.get'


class WidgetAppapiruleCheckRequest(TOPRequest):
    """ app指定api名称获取此api的http调用方法、app是否有请求权限、是否需要授权等信息。仅支持widget入口调用。调用入口为/widget。签名方法简化为Hmac-md5,hmac(secret+‘app_key' ＋app_key +'timestamp' + timestamp+secret,secret)。timestamp为60分钟内有效

    @response call_permission(String): 当前app是否可以调用次api。可以返回true，不可用返回false。
    @response http_method(String): 此api请求的http类型：get或post
    @response need_auth(String): 此api是否需要用户授权。true表示必需授权，false表示可选授权或无需授权

    @request api_name(String): (required)要判断权限的api名称，如果指定的api不存在，报错invalid method
    """
    REQUEST = {
        'api_name': {'type': topstruct.String, 'is_required': True}
    }

    RESPONSE = {
        'call_permission': {'type': topstruct.String, 'is_list': False},
        'http_method': {'type': topstruct.String, 'is_list': False},
        'need_auth': {'type': topstruct.String, 'is_list': False}
    }

    API = 'taobao.widget.appapirule.check'


class WidgetCartcountGetRequest(TOPRequest):
    """ 获取当前授权用户通过当前app加入购物车的商品记录条数。session必传且用户当前浏览器必需已经在淘宝登陆，具体判断方法可以调用taobao.widget.loginstatus.get进行判断。仅支持widget入口调用。调用入口为/widget。签名方法简化为Hmac-md5,hmac(secret+‘app_key' ＋app_key +'timestamp' + timestamp+secret, secret)。timestamp为60分钟内有效

    @response total_results(Number): 当前用户通过当前app加入购物车的商品记录条数。
    """
    REQUEST = {}

    RESPONSE = {
        'total_results': {'type': topstruct.Number, 'is_list': False}
    }

    API = 'taobao.widget.cartcount.get'


class WidgetCartitemAddRequest(TOPRequest):
    """ 当前授权用户通过当前app将指定商品加入购物车。session必传且用户当前浏览器必需已经在淘宝登陆，具体判断方法可以调用taobao.widget.loginstatus.get进行判断。具体的购物车相关业务逻辑详见taobao.cart.item.add接口的逻辑约束。仅支持widget入口调用。调用入口为/widget。签名方法为服务端签名，用户可以通过taobao.widget.itempanel.get获得相关链接内容，不支持isv自己签名请求。timestamp为60分钟内有效

    @response is_success(Boolean): 商品是否添加成功。同一个商品同一个sku添加多次购买记录不增加，单挑的购买数量增加

    @request item_id(Number): (required)要购买的商品的数字id，同Item的num_iid字段
    @request quantity(Number): (required)需要购买的数量，至少购买1件
    @request sku_id(Number): (optional)要购买的sku的id，如果是无sku的商品此字段不传，如果是有sku的商品必需指定sku_id。同sku的sku_id字段
    """
    REQUEST = {
        'item_id': {'type': topstruct.Number, 'is_required': True},
        'quantity': {'type': topstruct.Number, 'is_required': True},
        'sku_id': {'type': topstruct.Number, 'is_required': False}
    }

    RESPONSE = {
        'is_success': {'type': topstruct.Boolean, 'is_list': False}
    }

    API = 'taobao.widget.cartitem.add'


class WidgetCartitemDeleteRequest(TOPRequest):
    """ 当前授权用户删除通过当前app加入购物车的商品记录。session必传且用户当前浏览器必需已经在淘宝登陆，具体判断方法可以调用taobao.widget.loginstatus.get进行判断。具体的购物车相关业务逻辑详见taobao.cart.item.delete接口的逻辑约束。仅支持widget入口调用。调用入口为/widget。签名方法为服务端签名，用户可以通过taobao.widget.cartpanel.get获得相关删除链接内容，不支持isv自己签名请求。timestamp为60分钟内有效

    @response cart_id(Number): 被成功删除的购物车id号
    @response is_success(Boolean): 删除是否成功，true表示成功

    @request cart_id(Number): (required)要删除的购物车记录id号
    """
    REQUEST = {
        'cart_id': {'type': topstruct.Number, 'is_required': True}
    }

    RESPONSE = {
        'cart_id': {'type': topstruct.Number, 'is_list': False},
        'is_success': {'type': topstruct.Boolean, 'is_list': False}
    }

    API = 'taobao.widget.cartitem.delete'


class WidgetCartpanelGetRequest(TOPRequest):
    """ 获取当前授权用户通过当前app加入购物车的商品记录。session必传且用户当前浏览器必需已经在淘宝登陆，具体判断方法可以调用taobao.widget.loginstatus.get进行判断。仅支持widget入口调用。调用入口为/widget。签名方法简化为Hmac-md5,hmac(secret+‘app_key' ＋app_key +'timestamp' + timestamp+secret, secret)。timestamp为60分钟内有效

    @response cart_info(WidgetCartInfo): 当前用户通过当前app加入购物车的商品记录列表。
    @response total_results(Number): 当前用户通过当前app加入购物车的商品记录条数。
    """
    REQUEST = {}

    RESPONSE = {
        'cart_info': {'type': topstruct.WidgetCartInfo, 'is_list': False},
        'total_results': {'type': topstruct.Number, 'is_list': False}
    }

    API = 'taobao.widget.cartpanel.get'


class WidgetItempanelGetRequest(TOPRequest):
    """ 根据商品id获取sku选择面板需要的信息。session必传且用户当前浏览器必需已经在淘宝登陆，具体判断方法可以调用taobao.widget.loginstatus.get进行判断。会根据session生成购买链接。仅支持widget入口调用。调用入口为/widget。签名方法简化为Hmac-md5,hmac(secret+‘app_key' ＋app_key +'timestamp' + timestamp+secret, secret)。timestamp为60分钟内有效

    @response add_url(String): 服务端签名后的添加链接，isv在使用的时候前面加上“http://gw.api.taobao.com/widget?”后面加上用户选择的sku_id和购买的quantity即可生成完整的购买链接。
    @response item(WidgetItem): 取得的商品相关信息，如果不指定fields返回所有字段，如果指定了fields但是都是无效字段，返回的item结构体中字段为空

    @request fields(String): (optional)参数fields为选填参数，表示需要返回哪些字段，默认为空：表示所有字段都返回。指定item_id返回item_id; 指定title返回title; 指定click_url返回click_url(如果此商品有淘宝客会默认返回转换过的淘宝客连接，绑定用户为appkey对应的用户); 指定price返回price(商品价格，如果有多个sku返回的是sku的价格区间); 指定quantify返回quantity(商品总数); 指定pic_url返回pic_url(商品主图地址); 指定item_pics返回item_pics(商品图片列表); 指定skus返回skus和sku_props组合; 指定shop_promotion_data返回shop_promotion_data(商品所属的店铺优惠信息); 指定item_promotion_data返回item_promotion_data(商品的优惠信息); 指定seller_nick返回seller_nick(卖家昵称); 指定is_mall返回is_mall(是否商城商品，true表示是商城商品);add_url不可选一定会返回
    @request item_id(Number): (required)要查询的商品的数字id，等同于Item的num_iid
    """
    REQUEST = {
        'fields': {'type': topstruct.String, 'is_required': False, 'optional': topstruct.Set({'quantity', 'seller_nick', 'item_id', 'sku_props', 'title', 'shop_promotion_data', 'price', 'pic_url', 'click_url', 'item_pics', 'item_promotion_data', 'skus', 'is_mall'}), 'default': {'None'}},
        'item_id': {'type': topstruct.Number, 'is_required': True}
    }

    RESPONSE = {
        'add_url': {'type': topstruct.String, 'is_list': False},
        'item': {'type': topstruct.WidgetItem, 'is_list': False}
    }

    API = 'taobao.widget.itempanel.get'


class WidgetLoginstatusGetRequest(TOPRequest):
    """ 获取当前浏览器用户在淘宝登陆状态。如果传了session并且此用户已在淘宝登陆，返回nick和userId。仅支持widget入口调用。调用入口为/widget。签名方法简化为Hmac-md5,hmac(secret+‘app_key' ＋app_key +'timestamp' + timestamp+secret, secret)。timestamp为60分钟内有效

    @response is_login(Boolean): 当前浏览器用户是否已登陆。如果指定了nick，但是nick与浏览器用户不一致返回false。如果未指定nick，以浏览器用户登陆状态为准。如果指定了nick且与浏览器用户一致，以浏览器用户登陆状态为准
    @response nick(String): 淘宝用户的昵称，传了session且已登陆才返回
    @response user_id(String): 淘宝用户的数字id，传了session且已登录才返回。

    @request nick(String): (optional)指定判断当前浏览器登陆用户是否此昵称用户，并且返回是否登陆。如果用户不一致返回未登陆，如果用户一致且已登录返回已登陆
    """
    REQUEST = {
        'nick': {'type': topstruct.String, 'is_required': False}
    }

    RESPONSE = {
        'is_login': {'type': topstruct.Boolean, 'is_list': False},
        'nick': {'type': topstruct.String, 'is_list': False},
        'user_id': {'type': topstruct.String, 'is_list': False}
    }

    API = 'taobao.widget.loginstatus.get'


class TopatsUserAccountreportGetRequest(TOPRequest):
    """ 查询用户支付宝账务明细

    @response task(Task): 创建任务信息。里面只包含task_id和created

    @request charset(String): (optional)返回下载结果文件的数据格式，只支持utf-8和gbk编码，默认是utf-8
    @request end_time(Date): (required)对账单结束时间。end_time - start_time <= 1个自然月
    @request fields(FieldList): (required)需要返回的字段列表。create_time:创建时间,type：账务类型,business_type:子业务类型,balance:当时支付宝账户余额,in_amount:收入金额,out_amount:支出金额,alipay_order_no:支付宝订单号,merchant_order_no:商户订单号,self_user_id:自己的支付宝ID,opt_user_id:对方的支付宝ID,memo:账号备注
    @request start_time(Date): (required)对账单开始时间
    @request type(String): (optional)账务类型。多个类型是，用逗号分隔，不传则查询所有类型的。PAYMENT:在线支付，TRANSFER:转账，DEPOSIT:充值，WITHDRAW:提现，CHARGE:收费，PREAUTH:预授权，OTHER：其它。
    """
    REQUEST = {
        'charset': {'type': topstruct.String, 'is_required': False},
        'end_time': {'type': topstruct.Date, 'is_required': True},
        'fields': {'type': topstruct.FieldList, 'is_required': True, 'optional': topstruct.Set({'schedule', 'method', 'subtasks', 'created', 'status', 'download_url', 'check_code', 'task_id'})},
        'start_time': {'type': topstruct.Date, 'is_required': True},
        'type': {'type': topstruct.String, 'is_required': False}
    }

    RESPONSE = {
        'task': {'type': topstruct.Task, 'is_list': False}
    }

    API = 'alipay.topats.user.accountreport.get'


class UserAccountFreezeGetRequest(TOPRequest):
    """ 查询支付宝账户冻结类型的冻结金额。

    @response freeze_items(AccountFreeze): 冻结金额列表
    @response total_results(String): 冻结总条数

    @request freeze_type(String): (optional)冻结类型，多个用,分隔。不传返回所有类型的冻结金额。
        DEPOSIT_FREEZE,充值冻结
        WITHDRAW_FREEZE,提现冻结
        PAYMENT_FREEZE,支付冻结
        BAIL_FREEZE,保证金冻结
        CHARGE_FREEZE,收费冻结
        PRE_DEPOSIT_FREEZE,预存款冻结
        LOAN_FREEZE,贷款冻结
        OTHER_FREEZE,其它
    """
    REQUEST = {
        'freeze_type': {'type': topstruct.String, 'is_required': False}
    }

    RESPONSE = {
        'freeze_items': {'type': topstruct.AccountFreeze, 'is_list': False},
        'total_results': {'type': topstruct.String, 'is_list': False}
    }

    API = 'alipay.user.account.freeze.get'


class UserAccountGetRequest(TOPRequest):
    """ 查询支付宝账户余额

    @response alipay_account(AlipayAccount): 支付宝用户账户信息
    """
    REQUEST = {}

    RESPONSE = {
        'alipay_account': {'type': topstruct.AlipayAccount, 'is_list': False}
    }

    API = 'alipay.user.account.get'


class UserContractGetRequest(TOPRequest):
    """ 获取支付宝用户订购信息。在不确认用户对应用是否订购的时候，可以调用此API查询。

    @response alipay_contract(AlipayContract): 支付宝用户订购信息
    """
    REQUEST = {}

    RESPONSE = {
        'alipay_contract': {'type': topstruct.AlipayContract, 'is_list': False}
    }

    API = 'alipay.user.contract.get'


class UserTradeSearchRequest(TOPRequest):
    """ 查询支付宝账户消费明细

    @response total_pages(String): 总页数
    @response total_results(String): 总记录数
    @response trade_records(TradeRecord): 交易记录列表

    @request alipay_order_no(String): (optional)支付宝订单号，为空查询所有记录
    @request end_time(String): (required)结束时间。与开始时间间隔在七天之内
    @request merchant_order_no(String): (optional)商户订单号，为空查询所有记录
    @request order_from(String): (optional)订单来源，为空查询所有来源。淘宝(TAOBAO)，支付宝(ALIPAY)，其它(OTHER)
    @request order_status(String): (optional)订单状态，为空查询所有状态订单
    @request order_type(String): (optional)订单类型，为空查询所有类型订单。
    @request page_no(String): (required)页码。取值范围:大于零的整数; 默认值1
    @request page_size(String): (required)每页获取条数。最大值500。
    @request start_time(String): (required)开始时间，时间必须是今天范围之内。格式为yyyy-MM-dd HH:mm:ss，精确到秒
    """
    REQUEST = {
        'alipay_order_no': {'type': topstruct.String, 'is_required': False},
        'end_time': {'type': topstruct.String, 'is_required': True},
        'merchant_order_no': {'type': topstruct.String, 'is_required': False},
        'order_from': {'type': topstruct.String, 'is_required': False},
        'order_status': {'type': topstruct.String, 'is_required': False},
        'order_type': {'type': topstruct.String, 'is_required': False},
        'page_no': {'type': topstruct.String, 'is_required': True},
        'page_size': {'type': topstruct.String, 'is_required': True},
        'start_time': {'type': topstruct.String, 'is_required': True}
    }

    RESPONSE = {
        'total_pages': {'type': topstruct.String, 'is_list': False},
        'total_results': {'type': topstruct.String, 'is_list': False},
        'trade_records': {'type': topstruct.TradeRecord, 'is_list': False}
    }

    API = 'alipay.user.trade.search'

