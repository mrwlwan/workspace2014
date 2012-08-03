# coding=utf8

import datetime, re


String = str
Number = int

class Image:
    pass

class FieldList(str):
    """ 主要用于类型判定. """

class Set(set):
    """ 主要是辅助FieldList. """
    def __contains__(self, item):
        if isinstance(item, FieldList):
            return set(item.split(',')).issubset(self)
        return super().__contains__(item)


class Boolean:
    def __init__(self, arg):
        if isinstance(arg, str):
            self.__bool = not arg.lower()==false
        else:
            self.__bool = bool(arg)

    def __bool__(self):
        return self.__bool

    def __int__(self):
        return int(self.__bool)


class Price(float):
    """ 价格类型. """
    def __str__(self):
        return '%.2f' % self


class Date(datetime.datetime):
    """ 支持字符串初始化一个datetime对象. """

    def __init__(self, datetime_string):
        """ @Return: datetime object.
        @Param datetime_string: (required)str, 格式: '%Y %m %d %H:%M:%S'.
        """
        super().__init__(*re.split(r'[ :]', datetime_string))

    def __str__(self):
        return self.strftime('%Y %m %d %H:%M:%S')


class TOPDict(dict):
    """ 用于 TOP 的字典类型. """

    def __init__(self, *args, **kwargs):
        """ 传入该类的对象或者dict对象. 不调用dict的__init__, 以进行属性名限制. """
        self._befor_init(*args, **kwargs)
        self.update(*args, **kwargs)

    def _befor_init(self, *args, **kwargs):
        """ 执行 __init__ 前运行. """
        pass

    def update(self, *args, **kwargs):
        """ 更新字典属性. """
        # 子对象则直接调用dict的__init__.
        if args:
            if isinstance(args[0], self.__class__):
                dict.__init__(self, args[0])
                return
            else:
                kwargs = args[0] if isinstance(args[0], dict) else dict(args)
        for k, v in kwargs.items():
            self[k] = v

    #def __getattr__(self, field_name):
        #return self.get(field_name)

    #def __setattr__(self, field_name, field):
        #self.__setitem__(field_name, field)

    #def __hasattr__(self, field_name):
        #return field_name in self

    #def __delattr__(self, field_name):
        #del self[field_name]


class TOPObject(TOPDict):
    """ TOP Struct 的基类. """
    FIELDS = {}

    def __setitem__(self, field_name, field):
        """ 重写以进行属性限制. """
        if field_name not in self.FIELDS:
            raise Exception('无效的属性名!')
        field_type = globals().get(self.FIELDS.get(field_name).get('type'))
        is_list = globals().get(self.FIELDS.get(field_name).get('is_list'))
        value = (field_type(item) for item in field) if is_list else field_type(field)
        super().__setitem__(field_name, value)


class TOPError(TOPObject):
    """ 调用返回的错误信息. """
    FIELDS = {
        'code': {'type': 'Number', 'is_list': False},
        'msg': {'type': 'String', 'is_list': False},
        'sub_code': {'type': 'String', 'is_list': False},
        'sub_msg': {'type': 'String', 'is_list': False}
    }



class WlbItemBatch(TOPObject):
    """ 批次库存查询结果记录

    @field batch_code(String): 批次编号
    @field creator(String): 创建者
    @field defect_quantity(Number): 残次数量
    @field due_date(Date): 到期时间
    @field gmt_create(Date): 创建时间
    @field gmt_modified(Date): 最后修改时间
    @field guarantee_period(String): 保质期
    @field guarantee_unit(Number): 天（单位）
    @field id(Number): 商品批次记录id
    @field is_deleted(Boolean): 是否删除。0：正常 1：删除
    @field item_id(Number): 商品id
    @field last_modifier(String): 最后修改者
    @field produce_area(String): 产地
    @field produce_code(String): 生产编号
    @field produce_date(Date): 生产日期
    @field quantity(Number): 商品数量
    @field receive_date(Date): 接受日期
    @field remarks(String): 描述
    @field status(String): 状态。item_batch_status_open:开放 item_batch_status_lock:冻结 item_batch_status_invalid:无效
    @field store_code(String): 存储类型
    @field user_id(Number): 用户id
    @field version(Number): 版本
    """
    FIELDS = {
        'batch_code': {'type': 'String', 'is_list': False},
        'creator': {'type': 'String', 'is_list': False},
        'defect_quantity': {'type': 'Number', 'is_list': False},
        'due_date': {'type': 'Date', 'is_list': False},
        'gmt_create': {'type': 'Date', 'is_list': False},
        'gmt_modified': {'type': 'Date', 'is_list': False},
        'guarantee_period': {'type': 'String', 'is_list': False},
        'guarantee_unit': {'type': 'Number', 'is_list': False},
        'id': {'type': 'Number', 'is_list': False},
        'is_deleted': {'type': 'Boolean', 'is_list': False},
        'item_id': {'type': 'Number', 'is_list': False},
        'last_modifier': {'type': 'String', 'is_list': False},
        'produce_area': {'type': 'String', 'is_list': False},
        'produce_code': {'type': 'String', 'is_list': False},
        'produce_date': {'type': 'Date', 'is_list': False},
        'quantity': {'type': 'Number', 'is_list': False},
        'receive_date': {'type': 'Date', 'is_list': False},
        'remarks': {'type': 'String', 'is_list': False},
        'status': {'type': 'String', 'is_list': False},
        'store_code': {'type': 'String', 'is_list': False},
        'user_id': {'type': 'Number', 'is_list': False},
        'version': {'type': 'Number', 'is_list': False}
    }


class UserCredit(TOPObject):
    """ 用户信用

    @field good_num(Number): 收到的好评总条数。取值范围:大于零的整数
    @field level(Number): 信用等级（是根据score生成的），信用等级：淘宝会员在淘宝网上的信用度，分为20个级别，级别如：level = 1 时，表示一心；level = 2 时，表示二心
    @field score(Number): 信用总分（“好评”加一分，“中评”不加分，“差评”扣一分。分越高，等级越高）
    @field total_num(Number): 收到的评价总条数。取值范围:大于零的整数
    """
    FIELDS = {
        'good_num': {'type': 'Number', 'is_list': False},
        'level': {'type': 'Number', 'is_list': False},
        'score': {'type': 'Number', 'is_list': False},
        'total_num': {'type': 'Number', 'is_list': False}
    }


class Location(TOPObject):
    """ 用户地址

    @field address(String): 详细地址，最大256个字节（128个中文）
    @field city(String): 所在城市（中文名称）
    @field country(String): 国家名称
    @field district(String): 区/县（只适用于物流API）
    @field state(String): 所在省份（中文名称）
    @field zip(String): 邮政编码
    """
    FIELDS = {
        'address': {'type': 'String', 'is_list': False},
        'city': {'type': 'String', 'is_list': False},
        'country': {'type': 'String', 'is_list': False},
        'district': {'type': 'String', 'is_list': False},
        'state': {'type': 'String', 'is_list': False},
        'zip': {'type': 'String', 'is_list': False}
    }


class User(TOPObject):
    """ 用户

    @field alipay_account(String): 支付宝账户
    @field alipay_bind(String): 有无绑定。可选值:bind(绑定),notbind(未绑定)
    @field alipay_no(String): 支付宝ID
    @field auto_repost(String): 是否受限制。可选值:limited(受限制),unlimited(不受限)
    @field avatar(String): 用户头像地址
    @field birthday(Date): 生日
    @field buyer_credit(UserCredit): 买家信用
    @field consumer_protection(Boolean): 是否参加消保
    @field created(Date): 用户注册时间。格式:yyyy-MM-dd HH:mm:ss
    @field email(String): 联系人email
    @field has_more_pic(Boolean): 是否购买多图服务。可选值:true(是),false(否)
    @field has_shop(Boolean): 用户作为卖家是否开过店
    @field has_sub_stock(Boolean): 表示用户是否具备修改商品减库存逻辑的权限（一共有拍下减库存和付款减库存两种逻辑）
        值含义：
        1）true：是
        2）false：否。
    @field is_golden_seller(Boolean): 用户是否是金牌卖家
    @field is_lightning_consignment(Boolean): 是否24小时闪电发货(实物类)
    @field item_img_num(Number): 可上传商品图片数量
    @field item_img_size(Number): 单张商品图片最大容量(商品主图大小)。单位:k
    @field last_visit(Date): 最近登陆时间。格式:yyyy-MM-dd HH:mm:ss
    @field liangpin(Boolean): 是否是无名良品用户，true or  false
    @field location(Location): 用户当前居住地公开信息。如：location.city获取其中的city数据
    @field magazine_subscribe(Boolean): 是否订阅了淘宝天下杂志
    @field nick(String): 用户昵称
    @field online_gaming(Boolean): 用户是否为网游用户，属于隐私信息，需要登陆才能查看自己的。
        目前仅供taobao.user.get使用
    @field promoted_type(String): 有无实名认证。可选值:authentication(实名认证),not authentication(没有认证)
    @field prop_img_num(Number): 可上传属性图片数量
    @field prop_img_size(Number): 单张销售属性图片最大容量（非主图的商品图片和商品属性图片）。单位:k
    @field seller_credit(UserCredit): 卖家信用
    @field sex(String): 性别。可选值:m(男),f(女)
    @field sign_food_seller_promise(Boolean): 卖家是否签署食品卖家承诺协议
    @field status(String): 状态。可选值:normal(正常),inactive(未激活),delete(删除),reeze(冻结),supervise(监管)
    @field type(String): 用户类型。可选值:B(B商家),C(C商家)
    @field uid(String): 用户字符串ID
    @field user_id(Number): 用户数字ID
    @field vertical_market(String): 用户参与垂直市场类型。shoes表示鞋城垂直市场用户，3C表示3C垂直市场用户。多个类型之间用","分隔。如：一个用户既是3C用户又是鞋城用户，那么这个字段返回就是"3C,shoes"。如果用户不是垂直市场用户，此字段返回为""。
    @field vip_info(String): 用户的全站vip信息，可取值如下：c(普通会员),asso_vip(荣誉会员)，vip1,vip2,vip3,vip4,vip5,vip6(六个等级的正式vip会员)，共8种取值，其中asso_vip是由vip会员衰退而成，与主站上的vip0对应。
    """
    FIELDS = {
        'alipay_account': {'type': 'String', 'is_list': False},
        'alipay_bind': {'type': 'String', 'is_list': False},
        'alipay_no': {'type': 'String', 'is_list': False},
        'auto_repost': {'type': 'String', 'is_list': False},
        'avatar': {'type': 'String', 'is_list': False},
        'birthday': {'type': 'Date', 'is_list': False},
        'buyer_credit': {'type': 'UserCredit', 'is_list': False},
        'consumer_protection': {'type': 'Boolean', 'is_list': False},
        'created': {'type': 'Date', 'is_list': False},
        'email': {'type': 'String', 'is_list': False},
        'has_more_pic': {'type': 'Boolean', 'is_list': False},
        'has_shop': {'type': 'Boolean', 'is_list': False},
        'has_sub_stock': {'type': 'Boolean', 'is_list': False},
        'is_golden_seller': {'type': 'Boolean', 'is_list': False},
        'is_lightning_consignment': {'type': 'Boolean', 'is_list': False},
        'item_img_num': {'type': 'Number', 'is_list': False},
        'item_img_size': {'type': 'Number', 'is_list': False},
        'last_visit': {'type': 'Date', 'is_list': False},
        'liangpin': {'type': 'Boolean', 'is_list': False},
        'location': {'type': 'Location', 'is_list': False},
        'magazine_subscribe': {'type': 'Boolean', 'is_list': False},
        'nick': {'type': 'String', 'is_list': False},
        'online_gaming': {'type': 'Boolean', 'is_list': False},
        'promoted_type': {'type': 'String', 'is_list': False},
        'prop_img_num': {'type': 'Number', 'is_list': False},
        'prop_img_size': {'type': 'Number', 'is_list': False},
        'seller_credit': {'type': 'UserCredit', 'is_list': False},
        'sex': {'type': 'String', 'is_list': False},
        'sign_food_seller_promise': {'type': 'Boolean', 'is_list': False},
        'status': {'type': 'String', 'is_list': False},
        'type': {'type': 'String', 'is_list': False},
        'uid': {'type': 'String', 'is_list': False},
        'user_id': {'type': 'Number', 'is_list': False},
        'vertical_market': {'type': 'String', 'is_list': False},
        'vip_info': {'type': 'String', 'is_list': False}
    }


class UserInfo(TOPObject):
    """ 图片空间的用户信息获取，包括订购容量等

    @field available_space(String): 用户的可用容量，即订购量与免费量之和
    @field free_space(String): 图片空间的免费容量
    @field order_expiry_date(String): 图片空间的订购有效期
    @field order_space(String): 用户订购的图片空间容量
    @field remaining_space(String): 剩余的图片空间容量
    @field used_space(String): 已使用的图片空间容量
    @field water_mark(String): 用户自定义的水印参数，通过"|"分割开，如果用户没有定义则为""
        具体水印参数组合方法，用"|"分开，顺序按"是否全局设置|水印文字|是否文字水印优先|透明度|字体|字体大小|字体是否加粗|字体是否斜体|字体是否加下划线|字体颜色|旋转角度|是否带阴影|水印位置|图片水印URL|reference水印相对位置" reference取值有左上（1）/中间（3）/右下（2）,其中的null代表为空
    """
    FIELDS = {
        'available_space': {'type': 'String', 'is_list': False},
        'free_space': {'type': 'String', 'is_list': False},
        'order_expiry_date': {'type': 'String', 'is_list': False},
        'order_space': {'type': 'String', 'is_list': False},
        'remaining_space': {'type': 'String', 'is_list': False},
        'used_space': {'type': 'String', 'is_list': False},
        'water_mark': {'type': 'String', 'is_list': False}
    }


class ProductImg(TOPObject):
    """ 产品图片

    @field created(Date): 添加时间.格式:yyyy-mm-dd hh:mm:ss
    @field id(Number): 产品图片ID
    @field modified(Date): 修改时间.格式:yyyy-mm-dd hh:mm:ss
    @field position(Number): 图片序号。产品里的图片展示顺序，数据越小越靠前。要求是正整数。
    @field product_id(Number): 图片所属产品的ID
    @field url(String): 图片地址.(绝对地址,格式:http://host/image_path)
    """
    FIELDS = {
        'created': {'type': 'Date', 'is_list': False},
        'id': {'type': 'Number', 'is_list': False},
        'modified': {'type': 'Date', 'is_list': False},
        'position': {'type': 'Number', 'is_list': False},
        'product_id': {'type': 'Number', 'is_list': False},
        'url': {'type': 'String', 'is_list': False}
    }


class Product(TOPObject):
    """ 产品结构

    @field binds(String): 产品的非关键属性列表.格式:pid:vid;pid:vid.
    @field binds_str(String): 产品的非关键属性字符串列表.格式同props_str(<strong>注：</strong><font color="red">属性名称中的冒号":"被转换为："#cln#";
        分号";"被转换为："#scln#"
        </font>)
    @field cat_name(String): 商品类目名称
    @field cid(Number): 商品类目ID.必须是叶子类目ID
    @field collect_num(Number): 产品的collect次数（不提供数据，返回0)
    @field created(Date): 创建时间.格式:yyyy-mm-dd hh:mm:ss
    @field customer_props(String): 用户自定义属性,结构：pid1:value1;pid2:value2 例如：“20000:优衣库”，表示“品牌:优衣库”
    @field desc(String): 产品的描述.最大25000个字节
    @field level(Number): 产品的级别level
    @field modified(Date): 修改时间.格式:yyyy-mm-dd hh:mm:ss
    @field name(String): 产品名称
    @field outer_id(String): 外部产品ID
    @field pic_path(String): 产品对应的图片路径
    @field pic_url(String): 产品的主图片地址.(绝对地址,格式:http://host/image_path)
    @field price(Price): 产品的市场价.单位为元.精确到2位小数;如:200.07
    @field product_id(Number): 产品ID
    @field product_imgs(ProductImg, list): 产品的子图片.目前最多支持4张。fields中设置为product_imgs.id、product_imgs.url、product_imgs.position 等形式就会返回相应的字段
    @field product_prop_imgs(ProductPropImg, list): 产品的属性图片.比如说黄色对应的产品图片,绿色对应的产品图片。fields中设置为product_prop_imgs.id、
        product_prop_imgs.props、product_prop_imgs.url、product_prop_imgs.position等形式就会返回相应的字段
    @field property_alias(String): 销售属性值别名。格式为pid1:vid1:alias1;pid1:vid2:alia2。
    @field props(String): 产品的关键属性列表.格式：pid:vid;pid:vid
    @field props_str(String): 产品的关键属性字符串列表.比如:品牌:诺基亚;型号:N73(<strong>注：</strong><font color="red">属性名称中的冒号":"被转换为："#cln#";
        分号";"被转换为："#scln#"
        </font>)
    @field sale_props(String): 产品的销售属性列表.格式:pid:vid;pid:vid
    @field sale_props_str(String): 产品的销售属性字符串列表.格式同props_str(<strong>注：</strong><font color="red">属性名称中的冒号":"被转换为："#cln#";
        分号";"被转换为："#scln#"
        </font>)
    @field status(Number): 当前状态(0 商家确认 1 屏蔽 3 小二确认 2 未确认 -1 删除)
    @field tsc(String): 淘宝标准产品编码
    @field vertical_market(Number): 垂直市场,如：3（3C），4（鞋城）
    """
    FIELDS = {
        'binds': {'type': 'String', 'is_list': False},
        'binds_str': {'type': 'String', 'is_list': False},
        'cat_name': {'type': 'String', 'is_list': False},
        'cid': {'type': 'Number', 'is_list': False},
        'collect_num': {'type': 'Number', 'is_list': False},
        'created': {'type': 'Date', 'is_list': False},
        'customer_props': {'type': 'String', 'is_list': False},
        'desc': {'type': 'String', 'is_list': False},
        'level': {'type': 'Number', 'is_list': False},
        'modified': {'type': 'Date', 'is_list': False},
        'name': {'type': 'String', 'is_list': False},
        'outer_id': {'type': 'String', 'is_list': False},
        'pic_path': {'type': 'String', 'is_list': False},
        'pic_url': {'type': 'String', 'is_list': False},
        'price': {'type': 'Price', 'is_list': False},
        'product_id': {'type': 'Number', 'is_list': False},
        'product_imgs': {'type': 'ProductImg', 'is_list': True},
        'product_prop_imgs': {'type': 'ProductPropImg', 'is_list': True},
        'property_alias': {'type': 'String', 'is_list': False},
        'props': {'type': 'String', 'is_list': False},
        'props_str': {'type': 'String', 'is_list': False},
        'sale_props': {'type': 'String', 'is_list': False},
        'sale_props_str': {'type': 'String', 'is_list': False},
        'status': {'type': 'Number', 'is_list': False},
        'tsc': {'type': 'String', 'is_list': False},
        'vertical_market': {'type': 'Number', 'is_list': False}
    }


class RefundRemindTimeout(TOPObject):
    """ 退款超时结构

    @field exist_timeout(Boolean): 是否存在超时。可选值:true(是),false(否)
    @field remind_type(Number): 提醒的类型（退款详情中提示信息的类型）
    @field timeout(Date): 超时时间。格式:yyyy-MM-dd HH:mm:ss
    """
    FIELDS = {
        'exist_timeout': {'type': 'Boolean', 'is_list': False},
        'remind_type': {'type': 'Number', 'is_list': False},
        'timeout': {'type': 'Date', 'is_list': False}
    }


class ReferenceDetail(TOPObject):
    """ 图片的引用详情

    @field address(String): 引用者的地址
    @field name(String): 引用者的名字
    @field reference_type(String): 引用的类型:item,被宝贝引用；decorating，被装修引用；huabao，被画报引用；unreferenced，未被引用
    """
    FIELDS = {
        'address': {'type': 'String', 'is_list': False},
        'name': {'type': 'String', 'is_list': False},
        'reference_type': {'type': 'String', 'is_list': False}
    }


class RefundMessage(TOPObject):
    """ 留言/凭证数据结构

    @field content(String): 留言内容。最大长度: 400个字节
    @field created(Date): 留言创建时间。格式:yyyy-MM-dd HH:mm:ss
    @field id(Number): 留言编号
    @field message_type(String): 退款类型：NORMAL（普通留言），RETURN_GOODS_APPROVED（卖家留退货地址时留言）；如果为RETURN_GOODS_APPROVED，则退款留言中有卖家收货地址
    @field owner_id(Number): 留言者编号
    @field owner_nick(String): 留言者昵称
    @field owner_role(String): 留言者身份
        1代表买家，2代表卖家，3代表小二
    @field pic_urls(PicUrl, list): 凭证附件地址（图片）
    @field refund_id(Number): 退款编号。
    """
    FIELDS = {
        'content': {'type': 'String', 'is_list': False},
        'created': {'type': 'Date', 'is_list': False},
        'id': {'type': 'Number', 'is_list': False},
        'message_type': {'type': 'String', 'is_list': False},
        'owner_id': {'type': 'Number', 'is_list': False},
        'owner_nick': {'type': 'String', 'is_list': False},
        'owner_role': {'type': 'String', 'is_list': False},
        'pic_urls': {'type': 'PicUrl', 'is_list': True},
        'refund_id': {'type': 'Number', 'is_list': False}
    }


class Order(TOPObject):
    """ 订单结构

    @field adjust_fee(String): 手工调整金额.格式为:1.01;单位:元;精确到小数点后两位.
    @field buyer_nick(String): 买家昵称
    @field buyer_rate(Boolean): 买家是否已评价。可选值：true(已评价)，false(未评价)
    @field cid(Number): 交易商品对应的类目ID
    @field discount_fee(String): 订单优惠金额。精确到2位小数;单位:元。如:200.07，表示:200元7分
    @field iid(String): 商品的字符串编号(注意：iid近期即将废弃，请用num_iid参数)
    @field is_oversold(Boolean): 是否超卖
    @field is_service_order(Boolean): 是否是服务订单，是返回true，否返回false。
    @field item_meal_id(Number): 套餐ID
    @field item_meal_name(String): 套餐的值。如：M8原装电池:便携支架:M8专用座充:莫凡保护袋
    @field modified(Date): 订单修改时间，目前只有taobao.trade.ordersku.update会返回此字段。
    @field num(Number): 购买数量。取值范围:大于零的整数
    @field num_iid(Number): 商品数字ID
    @field oid(Number): 子订单编号
    @field outer_iid(String): 商家外部编码(可与商家外部系统对接)。外部商家自己定义的商品Item的id，可以通过taobao.items.custom.get获取商品的Item的信息
    @field outer_sku_id(String): 外部网店自己定义的Sku编号
    @field payment(String): 子订单实付金额。精确到2位小数，单位:元。如:200.07，表示:200元7分。计算公式如下：payment = price * num + adjust_fee - discount_fee + post_fee(邮费，单笔子订单时子订单实付金额包含邮费，多笔子订单时不包含邮费)；对于退款成功的子订单，由于主订单的优惠分摊金额，会造成该字段可能不为0.00元。建议使用退款前的实付金额减去退款单中的实际退款金额计算。
    @field pic_path(String): 商品图片的绝对路径
    @field price(String): 商品价格。精确到2位小数;单位:元。如:200.07，表示:200元7分
    @field refund_id(Number): 最近退款ID
    @field refund_status(String): 退款状态。退款状态。可选值 WAIT_SELLER_AGREE(买家已经申请退款，等待卖家同意) WAIT_BUYER_RETURN_GOODS(卖家已经同意退款，等待买家退货) WAIT_SELLER_CONFIRM_GOODS(买家已经退货，等待卖家确认收货) SELLER_REFUSE_BUYER(卖家拒绝退款) CLOSED(退款关闭) SUCCESS(退款成功)
    @field seller_nick(String): 卖家昵称
    @field seller_rate(Boolean): 卖家是否已评价。可选值：true(已评价)，false(未评价)
    @field seller_type(String): 卖家类型，可选值为：B（商城商家），C（普通卖家）
    @field sku_id(String): 商品的最小库存单位Sku的id.可以通过taobao.item.sku.get获取详细的Sku信息
    @field sku_properties_name(String): SKU的值。如：机身颜色:黑色;手机套餐:官方标配
    @field snapshot(String): 订单快照详细信息
    @field snapshot_url(String): 订单快照URL
    @field status(String): 订单状态（请关注此状态，如果为TRADE_CLOSED_BY_TAOBAO状态，则不要对此订单进行发货，切记啊！）。可选值:
        <ul>
        <li>TRADE_NO_CREATE_PAY(没有创建支付宝交易)
        <li>WAIT_BUYER_PAY(等待买家付款)
        <li>WAIT_SELLER_SEND_GOODS(等待卖家发货,即:买家已付款)
        <li>WAIT_BUYER_CONFIRM_GOODS(等待买家确认收货,即:卖家已发货)
        <li>TRADE_BUYER_SIGNED(买家已签收,货到付款专用)
        <li>TRADE_FINISHED(交易成功)
        <li>TRADE_CLOSED(付款以后用户退款成功，交易自动关闭)
        <li>TRADE_CLOSED_BY_TAOBAO(付款以前，卖家或买家主动关闭交易)
    @field timeout_action_time(Date): 订单超时到期时间。格式:yyyy-MM-dd HH:mm:ss
    @field title(String): 商品标题
    @field total_fee(String): 应付金额（商品价格 * 商品数量 + 手工调整金额 - 订单优惠金额）。精确到2位小数;单位:元。如:200.07，表示:200元7分
    """
    FIELDS = {
        'adjust_fee': {'type': 'String', 'is_list': False},
        'buyer_nick': {'type': 'String', 'is_list': False},
        'buyer_rate': {'type': 'Boolean', 'is_list': False},
        'cid': {'type': 'Number', 'is_list': False},
        'discount_fee': {'type': 'String', 'is_list': False},
        'iid': {'type': 'String', 'is_list': False},
        'is_oversold': {'type': 'Boolean', 'is_list': False},
        'is_service_order': {'type': 'Boolean', 'is_list': False},
        'item_meal_id': {'type': 'Number', 'is_list': False},
        'item_meal_name': {'type': 'String', 'is_list': False},
        'modified': {'type': 'Date', 'is_list': False},
        'num': {'type': 'Number', 'is_list': False},
        'num_iid': {'type': 'Number', 'is_list': False},
        'oid': {'type': 'Number', 'is_list': False},
        'outer_iid': {'type': 'String', 'is_list': False},
        'outer_sku_id': {'type': 'String', 'is_list': False},
        'payment': {'type': 'String', 'is_list': False},
        'pic_path': {'type': 'String', 'is_list': False},
        'price': {'type': 'String', 'is_list': False},
        'refund_id': {'type': 'Number', 'is_list': False},
        'refund_status': {'type': 'String', 'is_list': False},
        'seller_nick': {'type': 'String', 'is_list': False},
        'seller_rate': {'type': 'Boolean', 'is_list': False},
        'seller_type': {'type': 'String', 'is_list': False},
        'sku_id': {'type': 'String', 'is_list': False},
        'sku_properties_name': {'type': 'String', 'is_list': False},
        'snapshot': {'type': 'String', 'is_list': False},
        'snapshot_url': {'type': 'String', 'is_list': False},
        'status': {'type': 'String', 'is_list': False},
        'timeout_action_time': {'type': 'Date', 'is_list': False},
        'title': {'type': 'String', 'is_list': False},
        'total_fee': {'type': 'String', 'is_list': False}
    }


class Refund(TOPObject):
    """ 退款结构

    @field address(String): 卖家收货地址
    @field alipay_no(String): 支付宝交易号
    @field buyer_nick(String): 买家昵称
    @field company_name(String): 物流公司名称
    @field created(Date): 退款申请时间。格式:yyyy-MM-dd HH:mm:ss
    @field desc(String): 退款说明
    @field good_return_time(Date): 退货时间。格式:yyyy-MM-dd HH:mm:ss
    @field good_status(String): 货物状态。可选值
        BUYER_NOT_RECEIVED (买家未收到货)
        BUYER_RECEIVED (买家已收到货)
        BUYER_RETURNED_GOODS (买家已退货)
    @field has_good_return(Boolean): 买家是否需要退货。可选值:true(是),false(否)
    @field iid(String): 申请退款的商品字符串编号(注意：iid近期即将废弃，请用num_iid参数)
    @field modified(Date): 更新时间。格式:yyyy-MM-dd HH:mm:ss
    @field num(Number): 商品购买数量
    @field num_iid(Number): 申请退款的商品数字编号
    @field oid(Number): 子订单号。如果是单笔交易oid会等于tid
    @field order_status(String): 退款对应的订单交易状态。
        可选值
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
        取自"http://open.taobao.com/dev/index.php/%E4%BA%A4%E6%98%93%E7%8A%B6%E6%80%81"
    @field payment(String): 支付给卖家的金额(交易总金额-退还给买家的金额)。精确到2位小数;单位:元。如:200.07，表示:200元7分
    @field price(String): 商品价格。精确到2位小数;单位:元。如:200.07，表示:200元7分
    @field reason(String): 退款原因
    @field refund_fee(String): 退还金额(退还给买家的金额)。精确到2位小数;单位:元。如:200.07，表示:200元7分
    @field refund_id(Number): 退款单号
    @field refund_remind_timeout(RefundRemindTimeout): 退款超时结构RefundRemindTimeout
    @field seller_nick(String): 卖家昵称
    @field shipping_type(String): 物流方式.可选值:free(卖家包邮),post(平邮),express(快递),ems(EMS).
    @field sid(String): 退货运单号
    @field status(String): 退款状态。
        可选值
        WAIT_SELLER_AGREE(买家已经申请退款，等待卖家同意)
        WAIT_BUYER_RETURN_GOODS(卖家已经同意退款，等待买家退货)
        WAIT_SELLER_CONFIRM_GOODS(买家已经退货，等待卖家确认收货)
        SELLER_REFUSE_BUYER(卖家拒绝退款)
        CLOSED(退款关闭)
        SUCCESS(退款成功)
    @field tid(Number): 淘宝交易单号
    @field title(String): 商品标题
    @field total_fee(String): 交易总金额。精确到2位小数;单位:元。如:200.07，表示:200元7分
    """
    FIELDS = {
        'address': {'type': 'String', 'is_list': False},
        'alipay_no': {'type': 'String', 'is_list': False},
        'buyer_nick': {'type': 'String', 'is_list': False},
        'company_name': {'type': 'String', 'is_list': False},
        'created': {'type': 'Date', 'is_list': False},
        'desc': {'type': 'String', 'is_list': False},
        'good_return_time': {'type': 'Date', 'is_list': False},
        'good_status': {'type': 'String', 'is_list': False},
        'has_good_return': {'type': 'Boolean', 'is_list': False},
        'iid': {'type': 'String', 'is_list': False},
        'modified': {'type': 'Date', 'is_list': False},
        'num': {'type': 'Number', 'is_list': False},
        'num_iid': {'type': 'Number', 'is_list': False},
        'oid': {'type': 'Number', 'is_list': False},
        'order_status': {'type': 'String', 'is_list': False},
        'payment': {'type': 'String', 'is_list': False},
        'price': {'type': 'String', 'is_list': False},
        'reason': {'type': 'String', 'is_list': False},
        'refund_fee': {'type': 'String', 'is_list': False},
        'refund_id': {'type': 'Number', 'is_list': False},
        'refund_remind_timeout': {'type': 'RefundRemindTimeout', 'is_list': False},
        'seller_nick': {'type': 'String', 'is_list': False},
        'shipping_type': {'type': 'String', 'is_list': False},
        'sid': {'type': 'String', 'is_list': False},
        'status': {'type': 'String', 'is_list': False},
        'tid': {'type': 'Number', 'is_list': False},
        'title': {'type': 'String', 'is_list': False},
        'total_fee': {'type': 'String', 'is_list': False}
    }


class DiscardInfo(TOPObject):
    """ 用户丢失消息的数据结构

    @field end(Number): 丢弃消息的结束时间
    @field nick(String): 用户nick
    @field start(Number): 丢弃消息的开始时间
    @field subscribe_key(String): 非授权消息订阅的关键字，比如按商品编号订阅时，此值为num_iid
    @field subscribe_value(String): 非授权消息订阅的值，比如按商品编号订阅时，此值为商品的具体编号
    @field type(String): 消息类型
    @field user_id(Number): 用户id
    """
    FIELDS = {
        'end': {'type': 'Number', 'is_list': False},
        'nick': {'type': 'String', 'is_list': False},
        'start': {'type': 'Number', 'is_list': False},
        'subscribe_key': {'type': 'String', 'is_list': False},
        'subscribe_value': {'type': 'String', 'is_list': False},
        'type': {'type': 'String', 'is_list': False},
        'user_id': {'type': 'Number', 'is_list': False}
    }


class DeliveryTemplate(TOPObject):
    """ 运费模板对象

    @field assumer(Number): 可选值：0,1
        说明
        0:表示买家承担服务费;
        1:表示卖家承担服务费
    @field created(Date): 模板创建时间
    @field fee_list(TopFee, list): 运费模板中运费详细信息对象，包含默认运费和指定地区运费
    @field modified(Date): 模板修改时间
    @field name(String): 模板名称，长度不能超过25个字节
    @field supports(String): 物流服务模板支持增值服务列表，多个用分号隔开。cod:货到付款 mops：刷卡付款
    @field template_id(Number): 模块ID
    @field valuation(Number): 可选值：0
        说明：
        0:表示按宝贝件数计算运费
    """
    FIELDS = {
        'assumer': {'type': 'Number', 'is_list': False},
        'created': {'type': 'Date', 'is_list': False},
        'fee_list': {'type': 'TopFee', 'is_list': True},
        'modified': {'type': 'Date', 'is_list': False},
        'name': {'type': 'String', 'is_list': False},
        'supports': {'type': 'String', 'is_list': False},
        'template_id': {'type': 'Number', 'is_list': False},
        'valuation': {'type': 'Number', 'is_list': False}
    }


class Trade(TOPObject):
    """ 交易结构

    @field adjust_fee(String): 卖家手工调整金额，精确到2位小数，单位：元。如：200.07，表示：200元7分。来源于订单价格修改，如果有多笔子订单的时候，这个为0，单笔的话则跟[order].adjust_fee一样
    @field alipay_id(Number): 买家的支付宝id号，在UIC中有记录，买家支付宝的唯一标示，不因为买家更换Email账号而改变。
    @field alipay_no(String): 支付宝交易号，如：2009112081173831
    @field alipay_url(String): 创建交易接口成功后，返回的支付url
    @field alipay_warn_msg(String): 淘宝下单成功了,但由于某种错误支付宝订单没有创建时返回的信息。taobao.trade.add接口专用
    @field available_confirm_fee(String): 交易中剩余的确认收货金额（这个金额会随着子订单确认收货而不断减少，交易成功后会变为零）。精确到2位小数;单位:元。如:200.07，表示:200 元7分
    @field buyer_alipay_no(String): 买家支付宝账号
    @field buyer_area(String): 买家下单的地区
    @field buyer_cod_fee(String): 买家货到付款服务费。精确到2位小数;单位:元。如:12.07，表示:12元7分
    @field buyer_email(String): 买家邮件地址
    @field buyer_flag(Number): 买家备注旗帜（与淘宝网上订单的买家备注旗帜对应，只有买家才能查看该字段）
    @field buyer_memo(String): 买家备注（与淘宝网上订单的买家备注对应，只有买家才能查看该字段）
    @field buyer_message(String): 买家留言
    @field buyer_nick(String): 买家昵称
    @field buyer_obtain_point_fee(Number): 买家获得积分,返点的积分。格式:100;单位:个。返点的积分要交易成功之后才能获得。
    @field buyer_rate(Boolean): 买家是否已评价。可选值:true(已评价),false(未评价)
    @field can_rate(Boolean): 买家可以通过此字段查询是否当前交易可以评论，can_rate=true可以评价，false则不能评价。
    @field cod_fee(String): 货到付款服务费。精确到2位小数;单位:元。如:12.07，表示:12元7分。
    @field cod_status(String): 货到付款物流状态。
        初始状态 NEW_CREATED,
        接单成功 ACCEPTED_BY_COMPANY,
        接单失败 REJECTED_BY_COMPANY,
        接单超时 RECIEVE_TIMEOUT,
        揽收成功 TAKEN_IN_SUCCESS,
        揽收失败 TAKEN_IN_FAILED,
        揽收超时 RECIEVE_TIMEOUT,
        签收成功 SIGN_IN,
        签收失败 REJECTED_BY_OTHER_SIDE,
        订单等待发送给物流公司 WAITING_TO_BE_SENT,
        用户取消物流订单 CANCELED
    @field commission_fee(String): 交易佣金。精确到2位小数;单位:元。如:200.07，表示:200元7分
    @field consign_time(Date): 卖家发货时间。格式:yyyy-MM-dd HH:mm:ss
    @field created(Date): 交易创建时间。格式:yyyy-MM-dd HH:mm:ss
    @field discount_fee(String): 系统优惠金额（如打折，VIP，满就送等），精确到2位小数，单位：元。如：200.07，表示：200元7分
    @field end_time(Date): 交易结束时间。交易成功时间(更新交易状态为成功的同时更新)/确认收货时间或者交易关闭时间 。格式:yyyy-MM-dd HH:mm:ss
    @field express_agency_fee(String): 快递代收款。精确到2位小数;单位:元。如:212.07，表示:212元7分
    @field has_buyer_message(Boolean): 判断订单是否有买家留言，有买家留言返回true，否则返回false
    @field has_post_fee(Boolean): 是否包含邮费。与available_confirm_fee同时使用。可选值:true(包含),false(不包含)
    @field has_yfx(Boolean): 订单中是否包含运费险订单，如果包含运费险订单返回true，不包含运费险订单，返回false
    @field iid(String): 商品字符串编号(注意：iid近期即将废弃，请用num_iid参数)
    @field invoice_name(String): 发票抬头
    @field is_3D(Boolean): 是否是3D淘宝交易
    @field is_brand_sale(Boolean): 表示是否是品牌特卖订单，如果是返回true，如果不是返回false
    @field is_force_wlb(Boolean): 代表订单是否是强制使用物流宝发货，如果是返回true,如果不是返回false
    @field is_lgtype(Boolean): 是否需要物流宝发货的标识，如果为true，则需要可以用物流宝来发货，如果未false，则该订单不能用物流宝发货。
    @field modified(Date): 交易修改时间(用户对订单的任何修改都会更新此字段)。格式:yyyy-MM-dd HH:mm:ss
    @field num(Number): 商品购买数量。取值范围：大于零的整数
    @field num_iid(Number): 商品数字编号
    @field orders(Order, list): 订单列表
    @field pay_time(Date): 付款时间。格式:yyyy-MM-dd HH:mm:ss。订单的付款时间即为物流订单的创建时间。
    @field payment(String): 实付金额。精确到2位小数;单位:元。如:200.07，表示:200元7分
    @field pic_path(String): 商品图片绝对途径
    @field point_fee(Number): 买家使用积分。格式:100;单位:个.
    @field post_fee(String): 邮费。精确到2位小数;单位:元。如:200.07，表示:200元7分
    @field price(String): 商品价格。精确到2位小数；单位：元。如：200.07，表示：200元7分
    @field promotion(String): 交易促销详细信息
    @field promotion_details(PromotionDetail, list): 优惠详情
    @field real_point_fee(Number): 买家实际使用积分（扣除部分退款使用的积分）。格式:100;单位:个
    @field received_payment(String): 卖家实际收到的支付宝打款金额（由于子订单可以部分确认收货，这个金额会随着子订单的确认收货而不断增加，交易成功后等于买家实付款减去退款金额）。精确到2位小数;单位:元。如:200.07，表示:200元7分
    @field receiver_address(String): 收货人的详细地址
    @field receiver_city(String): 收货人的所在城市
    @field receiver_district(String): 收货人的所在地区
    @field receiver_mobile(String): 收货人的手机号码
    @field receiver_name(String): 收货人的姓名
    @field receiver_phone(String): 收货人的电话号码
    @field receiver_state(String): 收货人的所在省份
    @field receiver_zip(String): 收货人的邮编
    @field seller_alipay_no(String): 卖家支付宝账号
    @field seller_cod_fee(String): 卖家货到付款服务费。精确到2位小数;单位:元。如:12.07，表示:12元7分。卖家不承担服务费的订单：未发货的订单获取服务费为0，发货后就能获取到正确值。
    @field seller_email(String): 卖家邮件地址
    @field seller_flag(Number): 卖家备注旗帜（与淘宝网上订单的卖家备注旗帜对应，只有卖家才能查看该字段）
    @field seller_memo(String): 卖家备注（与淘宝网上订单的卖家备注对应，只有卖家才能查看该字段）
    @field seller_mobile(String): 卖家手机
    @field seller_name(String): 卖家姓名
    @field seller_nick(String): 卖家昵称
    @field seller_phone(String): 卖家电话
    @field seller_rate(Boolean): 卖家是否已评价。可选值:true(已评价),false(未评价)
    @field service_orders(ServiceOrder, list): 服务子订单列表
    @field shipping_type(String): 创建交易时的物流方式（交易完成前，物流方式有可能改变，但系统里的这个字段一直不变）。可选值：free(卖家包邮),post(平邮),express(快递),ems(EMS), virtual(虚拟发货)。
    @field snapshot(String): 交易快照详细信息
    @field snapshot_url(String): 交易快照地址
    @field status(String): 交易状态。可选值:
        * TRADE_NO_CREATE_PAY(没有创建支付宝交易)
        * WAIT_BUYER_PAY(等待买家付款)
        * WAIT_SELLER_SEND_GOODS(等待卖家发货,即:买家已付款)
        * WAIT_BUYER_CONFIRM_GOODS(等待买家确认收货,即:卖家已发货)
        * TRADE_BUYER_SIGNED(买家已签收,货到付款专用)
        * TRADE_FINISHED(交易成功)
        * TRADE_CLOSED(付款以后用户退款成功，交易自动关闭)
        * TRADE_CLOSED_BY_TAOBAO(付款以前，卖家或买家主动关闭交易)
    @field tid(Number): 交易编号 (父订单的交易编号)
    @field timeout_action_time(Date): 超时到期时间。格式:yyyy-MM-dd HH:mm:ss。业务规则：
        前提条件：只有在买家已付款，卖家已发货的情况下才有效
        如果申请了退款，那么超时会落在子订单上；比如说3笔ABC，A申请了，那么返回的是BC的列表, 主定单不存在
        如果没有申请过退款，那么超时会挂在主定单上；比如ABC，返回主定单，ABC的超时和主定单相同
    @field title(String): 交易标题，以店铺名作为此标题的值。注:taobao.trades.get接口返回的Trade中的title是商品名称
    @field total_fee(String): 商品金额（商品价格乘以数量的总金额）。精确到2位小数;单位:元。如:200.07，表示:200元7分
    @field trade_from(String): 交易来源。
        WAP(手机);HITAO(嗨淘);TOP(TOP平台);TAOBAO(普通淘宝);JHS(聚划算)
        一笔订单可能同时有以上多个标记，则以逗号分隔
    @field trade_memo(String): 交易备注。
    @field type(String): 交易类型列表，同时查询多种交易类型可用逗号分隔。默认同时查询guarantee_trade, auto_delivery, ec, cod的4种交易类型的数据
        可选值
        fixed(一口价)
        auction(拍卖)
        guarantee_trade(一口价、拍卖)
        auto_delivery(自动发货)
        independent_simple_trade(旺店入门版交易)
        independent_shop_trade(旺店标准版交易)
        ec(直冲)
        cod(货到付款)
        fenxiao(分销)
        game_equipment(游戏装备)
        shopex_trade(ShopEX交易)
        netcn_trade(万网交易)
        external_trade(统一外部交易)
    @field yfx_fee(String): 订单的运费险，单位为元
    @field yfx_id(String): 运费险订单号
    """
    FIELDS = {
        'adjust_fee': {'type': 'String', 'is_list': False},
        'alipay_id': {'type': 'Number', 'is_list': False},
        'alipay_no': {'type': 'String', 'is_list': False},
        'alipay_url': {'type': 'String', 'is_list': False},
        'alipay_warn_msg': {'type': 'String', 'is_list': False},
        'available_confirm_fee': {'type': 'String', 'is_list': False},
        'buyer_alipay_no': {'type': 'String', 'is_list': False},
        'buyer_area': {'type': 'String', 'is_list': False},
        'buyer_cod_fee': {'type': 'String', 'is_list': False},
        'buyer_email': {'type': 'String', 'is_list': False},
        'buyer_flag': {'type': 'Number', 'is_list': False},
        'buyer_memo': {'type': 'String', 'is_list': False},
        'buyer_message': {'type': 'String', 'is_list': False},
        'buyer_nick': {'type': 'String', 'is_list': False},
        'buyer_obtain_point_fee': {'type': 'Number', 'is_list': False},
        'buyer_rate': {'type': 'Boolean', 'is_list': False},
        'can_rate': {'type': 'Boolean', 'is_list': False},
        'cod_fee': {'type': 'String', 'is_list': False},
        'cod_status': {'type': 'String', 'is_list': False},
        'commission_fee': {'type': 'String', 'is_list': False},
        'consign_time': {'type': 'Date', 'is_list': False},
        'created': {'type': 'Date', 'is_list': False},
        'discount_fee': {'type': 'String', 'is_list': False},
        'end_time': {'type': 'Date', 'is_list': False},
        'express_agency_fee': {'type': 'String', 'is_list': False},
        'has_buyer_message': {'type': 'Boolean', 'is_list': False},
        'has_post_fee': {'type': 'Boolean', 'is_list': False},
        'has_yfx': {'type': 'Boolean', 'is_list': False},
        'iid': {'type': 'String', 'is_list': False},
        'invoice_name': {'type': 'String', 'is_list': False},
        'is_3D': {'type': 'Boolean', 'is_list': False},
        'is_brand_sale': {'type': 'Boolean', 'is_list': False},
        'is_force_wlb': {'type': 'Boolean', 'is_list': False},
        'is_lgtype': {'type': 'Boolean', 'is_list': False},
        'modified': {'type': 'Date', 'is_list': False},
        'num': {'type': 'Number', 'is_list': False},
        'num_iid': {'type': 'Number', 'is_list': False},
        'orders': {'type': 'Order', 'is_list': True},
        'pay_time': {'type': 'Date', 'is_list': False},
        'payment': {'type': 'String', 'is_list': False},
        'pic_path': {'type': 'String', 'is_list': False},
        'point_fee': {'type': 'Number', 'is_list': False},
        'post_fee': {'type': 'String', 'is_list': False},
        'price': {'type': 'String', 'is_list': False},
        'promotion': {'type': 'String', 'is_list': False},
        'promotion_details': {'type': 'PromotionDetail', 'is_list': True},
        'real_point_fee': {'type': 'Number', 'is_list': False},
        'received_payment': {'type': 'String', 'is_list': False},
        'receiver_address': {'type': 'String', 'is_list': False},
        'receiver_city': {'type': 'String', 'is_list': False},
        'receiver_district': {'type': 'String', 'is_list': False},
        'receiver_mobile': {'type': 'String', 'is_list': False},
        'receiver_name': {'type': 'String', 'is_list': False},
        'receiver_phone': {'type': 'String', 'is_list': False},
        'receiver_state': {'type': 'String', 'is_list': False},
        'receiver_zip': {'type': 'String', 'is_list': False},
        'seller_alipay_no': {'type': 'String', 'is_list': False},
        'seller_cod_fee': {'type': 'String', 'is_list': False},
        'seller_email': {'type': 'String', 'is_list': False},
        'seller_flag': {'type': 'Number', 'is_list': False},
        'seller_memo': {'type': 'String', 'is_list': False},
        'seller_mobile': {'type': 'String', 'is_list': False},
        'seller_name': {'type': 'String', 'is_list': False},
        'seller_nick': {'type': 'String', 'is_list': False},
        'seller_phone': {'type': 'String', 'is_list': False},
        'seller_rate': {'type': 'Boolean', 'is_list': False},
        'service_orders': {'type': 'ServiceOrder', 'is_list': True},
        'shipping_type': {'type': 'String', 'is_list': False},
        'snapshot': {'type': 'String', 'is_list': False},
        'snapshot_url': {'type': 'String', 'is_list': False},
        'status': {'type': 'String', 'is_list': False},
        'tid': {'type': 'Number', 'is_list': False},
        'timeout_action_time': {'type': 'Date', 'is_list': False},
        'title': {'type': 'String', 'is_list': False},
        'total_fee': {'type': 'String', 'is_list': False},
        'trade_from': {'type': 'String', 'is_list': False},
        'trade_memo': {'type': 'String', 'is_list': False},
        'type': {'type': 'String', 'is_list': False},
        'yfx_fee': {'type': 'String', 'is_list': False},
        'yfx_id': {'type': 'String', 'is_list': False}
    }


class TopFee(TOPObject):
    """ 运费模板中运费信息对象

    @field add_fee(String): 增费：输入0.00-999.99（最多包含两位小数） 不能为空不输入运费时必须输入0
    @field add_standard(String): 增费标准：当valuation(记价方式)为0时输入1-9999范围内的整数
    @field destination(String): 邮费子项涉及的地区,多个地区用逗号连接数量串;可以用taobao.areas.get接口获取.或者参考:http://www.stats.gov.cn/tjbz/xzqhdm/t20080215_402462675.htm 例 (110000,310000,320000,330000).就代表邮费子项涉 及(北京,上海,江苏,浙江)四个地区.填写时要注意对照地区代码值,如果填入错误地区代码,将会出现错误信息.
    @field service_type(String): 可选值：post:平邮; cod:货到付款; ems:EMS; express:快递公司
    @field start_fee(String): 首费：输入0.01-999.99（最多包含两位小数） 不能为空也不能为0
    @field start_standard(String): 首费标准：当valuation(记价方式)为0时输入1-9999范围内的整数
    """
    FIELDS = {
        'add_fee': {'type': 'String', 'is_list': False},
        'add_standard': {'type': 'String', 'is_list': False},
        'destination': {'type': 'String', 'is_list': False},
        'service_type': {'type': 'String', 'is_list': False},
        'start_fee': {'type': 'String', 'is_list': False},
        'start_standard': {'type': 'String', 'is_list': False}
    }


class Sku(TOPObject):
    """ Sku结构

    @field created(String): sku创建日期 时间格式：yyyy-MM-dd HH:mm:ss
    @field iid(String): sku所属商品id(注意：iid近期即将废弃，请用num_iid参数)
    @field modified(String): sku最后修改日期 时间格式：yyyy-MM-dd HH:mm:ss
    @field num_iid(Number): sku所属商品数字id
    @field outer_id(String): 商家设置的外部id
    @field price(String): 属于这个sku的商品的价格 取值范围:0-100000000;精确到2位小数;单位:元。如:200.07，表示:200元7分。
    @field properties(String): sku的销售属性组合字符串（颜色，大小，等等，可通过类目API获取某类目下的销售属性）,格式是p1:v1;p2:v2
    @field properties_name(String): sku所对应的销售属性的中文名字串，格式如：pid1:vid1:pid_name1:vid_name1;pid2:vid2:pid_name2:vid_name2……
    @field quantity(Number): 属于这个sku的商品的数量，
    @field sku_id(Number): sku的id
    @field status(String): sku状态。 normal:正常 ；delete:删除
    """
    FIELDS = {
        'created': {'type': 'String', 'is_list': False},
        'iid': {'type': 'String', 'is_list': False},
        'modified': {'type': 'String', 'is_list': False},
        'num_iid': {'type': 'Number', 'is_list': False},
        'outer_id': {'type': 'String', 'is_list': False},
        'price': {'type': 'String', 'is_list': False},
        'properties': {'type': 'String', 'is_list': False},
        'properties_name': {'type': 'String', 'is_list': False},
        'quantity': {'type': 'Number', 'is_list': False},
        'sku_id': {'type': 'Number', 'is_list': False},
        'status': {'type': 'String', 'is_list': False}
    }


class Video(TOPObject):
    """ 商品视频关联记录

    @field created(Date): 视频关联记录创建时间（格式：yyyy-MM-dd HH:mm:ss）
    @field id(Number): 视频关联记录的id，和商品相对应
    @field iid(String): 视频记录关联的商品的数字id(注意：iid近期即将废弃，请用num_iid参数)
    @field modified(Date): 视频关联记录修改时间（格式：yyyy-MM-dd HH:mm:ss）
    @field num_iid(Number): 视频记录所关联的商品的数字id
    @field url(String): video的url连接地址。淘秀里视频记录里面存储的url地址
    @field video_id(Number): video的id，对应于视频在淘秀的存储记录
    """
    FIELDS = {
        'created': {'type': 'Date', 'is_list': False},
        'id': {'type': 'Number', 'is_list': False},
        'iid': {'type': 'String', 'is_list': False},
        'modified': {'type': 'Date', 'is_list': False},
        'num_iid': {'type': 'Number', 'is_list': False},
        'url': {'type': 'String', 'is_list': False},
        'video_id': {'type': 'Number', 'is_list': False}
    }


class ShopScore(TOPObject):
    """ 店铺动态评分信息

    @field delivery_score(String): 发货速度评分
    @field item_score(String): 商品描述评分
    @field service_score(String): 服务态度评分
    """
    FIELDS = {
        'delivery_score': {'type': 'String', 'is_list': False},
        'item_score': {'type': 'String', 'is_list': False},
        'service_score': {'type': 'String', 'is_list': False}
    }


class SellerCat(TOPObject):
    """ 店铺内卖家自定义类目

    @field cid(Number): 卖家自定义类目编号
    @field created(Date): 创建时间。格式：yyyy-MM-dd HH:mm:ss
    @field modified(Date): 修改时间。格式：yyyy-MM-dd HH:mm:ss
    @field name(String): 卖家自定义类目名称
    @field parent_cid(Number): 父类目编号，值等于0：表示此类目为店铺下的一级类目，值不等于0：表示此类目有父类目
    @field pic_url(String): 链接图片地址
    @field sort_order(Number): 该类目在页面上的排序位置
    @field type(String): 店铺类目类型：可选值：manual_type：手动分类，new_type：新品上价， tree_type：二三级类目树 ，property_type：属性叶子类目树， brand_type：品牌推广
    """
    FIELDS = {
        'cid': {'type': 'Number', 'is_list': False},
        'created': {'type': 'Date', 'is_list': False},
        'modified': {'type': 'Date', 'is_list': False},
        'name': {'type': 'String', 'is_list': False},
        'parent_cid': {'type': 'Number', 'is_list': False},
        'pic_url': {'type': 'String', 'is_list': False},
        'sort_order': {'type': 'Number', 'is_list': False},
        'type': {'type': 'String', 'is_list': False}
    }


class PosterPicture(TOPObject):
    """ 画报图片结构

    @field created(Date): 创建时间。
    @field desc(String): 相关说明。
    @field id(String): 图片ID。
    @field modified(Date): 修改时间。
    @field poster_id(String): 画报ID。
    @field url(String): 图片地址。
    """
    FIELDS = {
        'created': {'type': 'Date', 'is_list': False},
        'desc': {'type': 'String', 'is_list': False},
        'id': {'type': 'String', 'is_list': False},
        'modified': {'type': 'Date', 'is_list': False},
        'poster_id': {'type': 'String', 'is_list': False},
        'url': {'type': 'String', 'is_list': False}
    }


class LoginLog(TOPObject):
    """ 登录日志

    @field time(String): 用户登录或退出客户端的时间
    @field type(String): 标志用户登录或退出。
        0表示登陆，1表示退出。
    """
    FIELDS = {
        'time': {'type': 'String', 'is_list': False},
        'type': {'type': 'String', 'is_list': False}
    }


class Poster(TOPObject):
    """ 画报结构

    @field channel_id(String): 画报所属频道id。
    @field cover_urls(String): 封面路径。由逗号(',')分开，最多2个
    @field created(Date): 创建时间。
    @field hits(Number): 画报的点击总数。
    @field id(String): 画报ID。
    @field modified(Date): 修改时间。
    @field short_title(String): 图片短标题。
    @field tags(String): 画报相关标签，由逗号(',')分开，最多5个。
    @field title(String): 图片标题。
    @field weight(Number): 权重。-1 至 10 。10为最高。
    """
    FIELDS = {
        'channel_id': {'type': 'String', 'is_list': False},
        'cover_urls': {'type': 'String', 'is_list': False},
        'created': {'type': 'Date', 'is_list': False},
        'hits': {'type': 'Number', 'is_list': False},
        'id': {'type': 'String', 'is_list': False},
        'modified': {'type': 'Date', 'is_list': False},
        'short_title': {'type': 'String', 'is_list': False},
        'tags': {'type': 'String', 'is_list': False},
        'title': {'type': 'String', 'is_list': False},
        'weight': {'type': 'Number', 'is_list': False}
    }


class EvalDetail(TOPObject):
    """ 评价详细

    @field eval_code(Number): 评价详细：
        1 非常满意
        2 满意
        3 一般
        4 不满意
    @field eval_recer(String): 评价接收者
    @field eval_sender(String): 评价发送者
    @field eval_time(Date): 评价时间
    @field send_time(Date): 评价发送时间
    """
    FIELDS = {
        'eval_code': {'type': 'Number', 'is_list': False},
        'eval_recer': {'type': 'String', 'is_list': False},
        'eval_sender': {'type': 'String', 'is_list': False},
        'eval_time': {'type': 'Date', 'is_list': False},
        'send_time': {'type': 'Date', 'is_list': False}
    }


class StreamWeight(TOPObject):
    """ 分流权重

    @field user(String): 账号
    @field weight(Number): 账号对应的权重
    """
    FIELDS = {
        'user': {'type': 'String', 'is_list': False},
        'weight': {'type': 'Number', 'is_list': False}
    }


class PosterChannel(TOPObject):
    """ 画报频道结构

    @field cn_name(String): 频道的中文名称。
    @field desc(String): 频道的说明。
    @field id(String): 频道ID号。
    @field name(String): 频道名称。
    @field url(String): 淘宝频道链接地址。
    @field wapurl(String): 手机画报对应频道页的链接
    """
    FIELDS = {
        'cn_name': {'type': 'String', 'is_list': False},
        'desc': {'type': 'String', 'is_list': False},
        'id': {'type': 'String', 'is_list': False},
        'name': {'type': 'String', 'is_list': False},
        'url': {'type': 'String', 'is_list': False},
        'wapurl': {'type': 'String', 'is_list': False}
    }


class TradeConfirmFee(TOPObject):
    """ 确认收货费用结构

    @field confirm_fee(Price): 确认收货的金额(不包含邮费)。精确到2位小数;单位:元。如:200.07，表示:200元7分
    @field confirm_post_fee(Price): 需确认收货的邮费，当不是最后一笔收货或者没有邮费时是0.00。精确到2位小数;单位:元。如:200.07，表示:200元7分
    @field is_last_order(Boolean): 是否是最后一笔订单（只对子订单有效，当其他子订单都是交易完成时，返回true，否则false）
    """
    FIELDS = {
        'confirm_fee': {'type': 'Price', 'is_list': False},
        'confirm_post_fee': {'type': 'Price', 'is_list': False},
        'is_last_order': {'type': 'Boolean', 'is_list': False}
    }


class ItemImg(TOPObject):
    """ ItemImg结构

    @field created(Date): 图片创建时间 时间格式：yyyy-MM-dd HH:mm:ss
    @field id(Number): 商品图片的id，和商品相对应
    @field position(Number): 图片放在第几张（多图时可设置）
    @field url(String): 图片链接地址
    """
    FIELDS = {
        'created': {'type': 'Date', 'is_list': False},
        'id': {'type': 'Number', 'is_list': False},
        'position': {'type': 'Number', 'is_list': False},
        'url': {'type': 'String', 'is_list': False}
    }


class ShopCat(TOPObject):
    """ 店铺类目

    @field cid(Number): 类目编号
    @field is_parent(Boolean): 该类目是否为父类目。即：该类目是否还有子类目
    @field name(String): 类目名称
    @field parent_cid(Number): 父类目编号，注：此类目指前台类目，值等于0：表示此类目为一级类目，值不等于0：表示此类目有父类目
    """
    FIELDS = {
        'cid': {'type': 'Number', 'is_list': False},
        'is_parent': {'type': 'Boolean', 'is_list': False},
        'name': {'type': 'String', 'is_list': False},
        'parent_cid': {'type': 'Number', 'is_list': False}
    }


class CarriageDetail(TOPObject):
    """ 物流公司资费相关信息

    @field add_fee(Number): 续费（单位：元）
    @field add_weight(Number): 续重（单位：千克）
    @field damage_payment(String): 破损赔付
    @field got_time(String): 物流公司揽收时间段
    @field initial_fee(Number): 首费（单位：元）
    @field initial_weight(Number): 首重（单位：千克）
    @field lost_payment(String): 丢单赔付
    @field way_day(String): 快件送达所需的时间(单位：天)
    """
    FIELDS = {
        'add_fee': {'type': 'Number', 'is_list': False},
        'add_weight': {'type': 'Number', 'is_list': False},
        'damage_payment': {'type': 'String', 'is_list': False},
        'got_time': {'type': 'String', 'is_list': False},
        'initial_fee': {'type': 'Number', 'is_list': False},
        'initial_weight': {'type': 'Number', 'is_list': False},
        'lost_payment': {'type': 'String', 'is_list': False},
        'way_day': {'type': 'String', 'is_list': False}
    }


class ProductPropImg(TOPObject):
    """ 产品属性图片

    @field created(Date): 添加时间.格式:yyyy-mm-dd hh:mm:ss
    @field id(Number): 产品属性图片ID
    @field modified(Date): 修改时间.格式:yyyy-mm-dd hh:mm:ss
    @field position(Number): 图片序号。产品里的图片展示顺序，数据越小越靠前。要求是正整数。
    @field product_id(Number): 图片所属产品的ID
    @field props(String): 属性串(pid:vid),目前只有颜色属性.如:颜色:红色表示为　1627207:28326
    @field url(String): 图片地址.(绝对地址,格式:http://host/image_path)
    """
    FIELDS = {
        'created': {'type': 'Date', 'is_list': False},
        'id': {'type': 'Number', 'is_list': False},
        'modified': {'type': 'Date', 'is_list': False},
        'position': {'type': 'Number', 'is_list': False},
        'product_id': {'type': 'Number', 'is_list': False},
        'props': {'type': 'String', 'is_list': False},
        'url': {'type': 'String', 'is_list': False}
    }


class NotifyRefund(TOPObject):
    """ 退款通知消息

    @field buyer_nick(String): 买家昵称
    @field modified(Date): 商品修改时间（格式：yyyy-MM-dd HH:mm:ss）
    @field nick(String): 消息所属的用户昵称
    @field oid(Number): 子订单退款交易编号
    @field refund_fee(Price): 退款金额
    @field rid(Number): 退款编号
    @field seller_nick(String): 卖家昵称
    @field status(String): 退款操作所对应的退款增量消息状态
        可选值：
        RefundSuccess（退款成功）
        RefundClosed（退款关闭）
        RefundCreated（退款创建）
        RefundSellerAgreeAgreement（卖家同意退款协议）
        RefundSellerRefuseAgreement（卖家拒绝退款协议）
        RefundBuyerModifyAgreement（买家修改退款协议）
        RefundBuyerReturnGoods（买家退货给卖家）
        RefundCreateMessage（发表留言）
        RefundBlockMessage（屏蔽留言）
        RefundTimeoutRemind（退款超时提醒）
    @field tid(Number): 父订单退款交易编号
    """
    FIELDS = {
        'buyer_nick': {'type': 'String', 'is_list': False},
        'modified': {'type': 'Date', 'is_list': False},
        'nick': {'type': 'String', 'is_list': False},
        'oid': {'type': 'Number', 'is_list': False},
        'refund_fee': {'type': 'Price', 'is_list': False},
        'rid': {'type': 'Number', 'is_list': False},
        'seller_nick': {'type': 'String', 'is_list': False},
        'status': {'type': 'String', 'is_list': False},
        'tid': {'type': 'Number', 'is_list': False}
    }


class Shop(TOPObject):
    """ 店铺信息

    @field all_count(Number): 总橱窗数量，对于C卖家返回总橱窗数，对于B卖家返回0（只有taobao.shop.remainshowcase.get可以返回）
    @field bulletin(String): 店铺公告
    @field cid(Number): 店铺所属的类目编号
    @field created(Date): 开店时间。格式：yyyy-MM-dd HH:mm:ss
    @field desc(String): 店铺描述
    @field modified(Date): 最后修改时间。格式：yyyy-MM-dd HH:mm:ss
    @field nick(String): 卖家昵称
    @field pic_path(String): 店标地址。返回相对路径，可以用"http://logo.taobao.com/shop-logo"来拼接成绝对路径
    @field remain_count(Number): 剩余橱窗数量，对于C卖家返回剩余橱窗数，对于B卖家返回-1（只有taobao.shop.remainshowcase.get可以返回）
    @field shop_score(ShopScore): 店铺动态评分信息
    @field sid(Number): 店铺编号。shop+sid.taobao.com即店铺地址，如shop123456.taobao.com
    @field title(String): 店铺标题
    @field used_count(Number): 已用的橱窗数量，对于C卖家返回已使用的橱窗数，对于B卖家返回-1（只有taobao.shop.remainshowcase.get可以返回）
    """
    FIELDS = {
        'all_count': {'type': 'Number', 'is_list': False},
        'bulletin': {'type': 'String', 'is_list': False},
        'cid': {'type': 'Number', 'is_list': False},
        'created': {'type': 'Date', 'is_list': False},
        'desc': {'type': 'String', 'is_list': False},
        'modified': {'type': 'Date', 'is_list': False},
        'nick': {'type': 'String', 'is_list': False},
        'pic_path': {'type': 'String', 'is_list': False},
        'remain_count': {'type': 'Number', 'is_list': False},
        'shop_score': {'type': 'ShopScore', 'is_list': False},
        'sid': {'type': 'Number', 'is_list': False},
        'title': {'type': 'String', 'is_list': False},
        'used_count': {'type': 'Number', 'is_list': False}
    }


class ServiceOrder(TOPObject):
    """ 商城虚拟服务子订单数据结构

    @field buyer_nick(String): 卖家昵称
    @field item_oid(Number): 服务所属的交易订单号。如果服务为一年包换，则item_oid这笔订单享受改服务的保护
    @field num(Number): 购买数量，取值范围为大于0的整数
    @field oid(Number): 虚拟服务子订单订单号
    @field payment(String): 子订单实付金额。精确到2位小数，单位:元。如:200.07，表示:200元7分。
    @field pic_path(String): 服务图片地址
    @field price(String): 服务价格，精确到小数点后两位：单位:元
    @field refund_id(Number): 最近退款的id
    @field seller_nick(String): 卖家昵称
    @field service_detail_url(String): 服务详情的URL地址
    @field service_id(Number): 服务数字id
    @field title(String): 商品名称
    @field total_fee(String): 服务子订单总费用
    """
    FIELDS = {
        'buyer_nick': {'type': 'String', 'is_list': False},
        'item_oid': {'type': 'Number', 'is_list': False},
        'num': {'type': 'Number', 'is_list': False},
        'oid': {'type': 'Number', 'is_list': False},
        'payment': {'type': 'String', 'is_list': False},
        'pic_path': {'type': 'String', 'is_list': False},
        'price': {'type': 'String', 'is_list': False},
        'refund_id': {'type': 'Number', 'is_list': False},
        'seller_nick': {'type': 'String', 'is_list': False},
        'service_detail_url': {'type': 'String', 'is_list': False},
        'service_id': {'type': 'Number', 'is_list': False},
        'title': {'type': 'String', 'is_list': False},
        'total_fee': {'type': 'String', 'is_list': False}
    }


class PropImg(TOPObject):
    """ 商品属性图片结构

    @field created(Date): 图片创建时间 时间格式：yyyy-MM-dd HH:mm:ss
    @field id(Number): 属性图片的id，和商品相对应
    @field position(Number): 图片放在第几张（多图时可设置）
    @field properties(String): 图片所对应的属性组合的字符串
    @field url(String): 图片链接地址
    """
    FIELDS = {
        'created': {'type': 'Date', 'is_list': False},
        'id': {'type': 'Number', 'is_list': False},
        'position': {'type': 'Number', 'is_list': False},
        'properties': {'type': 'String', 'is_list': False},
        'url': {'type': 'String', 'is_list': False}
    }


class NotifyTrade(TOPObject):
    """ 交易通知消息

    @field buyer_nick(String): 买家昵称
    @field modified(Date): 交易修改时间（格式：yyyy-MM-dd HH:mm:ss）
    @field nick(String): 消息所属的用户昵称
    @field oid(Number): 交易消息关联的子订单id号。多笔订单父订单操作时oid与tid一致
    @field payment(Price): 买家实付金额
    @field seller_nick(String): 卖家昵称
    @field status(String): 交易操作所对应的交易增量消息状态，对应与NotifyTrade的status字段
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
    @field tid(Number): 交易编号
    @field trade_mark(String): 交易信息中符合用户订阅的attributes标记的key1name:value1name;key2name:value2name;……标记串。必需在SubscribeMessage的attributes中订阅过的标记，并且交易上有此标记才会返回，否则此字段为空。返回值的keyname和valuename根据用户的自定义的key名称和value值别名返回。
    @field type(String): 交易类型。除了交易超时提醒消息没有类型以外，其他消息都有交易类型。
        具体分类有：
        可选值
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
    FIELDS = {
        'buyer_nick': {'type': 'String', 'is_list': False},
        'modified': {'type': 'Date', 'is_list': False},
        'nick': {'type': 'String', 'is_list': False},
        'oid': {'type': 'Number', 'is_list': False},
        'payment': {'type': 'Price', 'is_list': False},
        'seller_nick': {'type': 'String', 'is_list': False},
        'status': {'type': 'String', 'is_list': False},
        'tid': {'type': 'Number', 'is_list': False},
        'trade_mark': {'type': 'String', 'is_list': False},
        'type': {'type': 'String', 'is_list': False}
    }


class Subscription(TOPObject):
    """ 订阅类型

    @field status(String): 增量消息的状态（隶属于主题）。具体选值请见：商品消息状态、退款消息状态、交易消息状态中的说明。
    @field topic(String): 增量消息所属的主题。
        可选值
        trade（交易类型）
        item（商品类型）
        refund（退款类型）
    """
    FIELDS = {
        'status': {'type': 'String', 'is_list': False},
        'topic': {'type': 'String', 'is_list': False}
    }


class Brand(TOPObject):
    """ 品牌

    @field name(String): vid的值
    @field pid(Number): 品牌的属性id
    @field prop_name(String): 品牌的属性名
    @field vid(Number): 对应属性的 pid:vid 串中的vid
    """
    FIELDS = {
        'name': {'type': 'String', 'is_list': False},
        'pid': {'type': 'Number', 'is_list': False},
        'prop_name': {'type': 'String', 'is_list': False},
        'vid': {'type': 'Number', 'is_list': False}
    }


class ItemCat(TOPObject):
    """ 商品类目结构

    @field cid(Number): 商品所属类目ID
    @field features(Feature, list): Feature对象列表
        目前已有的属性：
        若Attr_key为 udsaleprop，attr_value为1 则允许卖家在改类目新增自定义销售属性,不然为不允许
    @field is_parent(Boolean): 该类目是否为父类目(即：该类目是否还有子类目)
    @field modified_time(Date): 增量类目：修改时间
    @field modified_type(String): 三种枚举类型：modify，add，delete（增量类目api使用）
    @field name(String): 类目名称
    @field parent_cid(Number): 父类目ID=0时，代表的是一级的类目
    @field sort_order(Number): 排列序号，表示同级类目的展现次序，如数值相等则按名称次序排列。取值范围:大于零的整数
    @field status(String): 状态。可选值:normal(正常),deleted(删除)
    """
    FIELDS = {
        'cid': {'type': 'Number', 'is_list': False},
        'features': {'type': 'Feature', 'is_list': True},
        'is_parent': {'type': 'Boolean', 'is_list': False},
        'modified_time': {'type': 'Date', 'is_list': False},
        'modified_type': {'type': 'String', 'is_list': False},
        'name': {'type': 'String', 'is_list': False},
        'parent_cid': {'type': 'Number', 'is_list': False},
        'sort_order': {'type': 'Number', 'is_list': False},
        'status': {'type': 'String', 'is_list': False}
    }


class PropValue(TOPObject):
    """ 属性值

    @field cid(Number): 类目ID
    @field is_parent(Boolean): 是否为父类目属性
    @field modified_time(Date): 修改时间（类目增量专用）
    @field modified_type(String): 三种枚举类型：modify，add，delete (增量类目专用)
    @field name(String): 属性值
    @field name_alias(String): 属性值别名
    @field pid(Number): 属性 ID
    @field prop_name(String): 属性名
    @field sort_order(Number): 排列序号。取值范围:大于零的整数
    @field status(String): 状态。可选值:normal(正常),deleted(删除)
    @field vid(Number): 属性值ID
    """
    FIELDS = {
        'cid': {'type': 'Number', 'is_list': False},
        'is_parent': {'type': 'Boolean', 'is_list': False},
        'modified_time': {'type': 'Date', 'is_list': False},
        'modified_type': {'type': 'String', 'is_list': False},
        'name': {'type': 'String', 'is_list': False},
        'name_alias': {'type': 'String', 'is_list': False},
        'pid': {'type': 'Number', 'is_list': False},
        'prop_name': {'type': 'String', 'is_list': False},
        'sort_order': {'type': 'Number', 'is_list': False},
        'status': {'type': 'String', 'is_list': False},
        'vid': {'type': 'Number', 'is_list': False}
    }


class NotifyItem(TOPObject):
    """ 商品通知消息

    @field changed_fields(String): 商品此次操作所变更的字段，以“,”分割，对应于商品Item的字段名称。目前支持title，price，num，item_img，prop_img，location，cid，approve_status， list_time几个字段的更改标记返回，其中“item_img，prop_img”会同时出现表示商品相关图片列表发生了修改
    @field iid(String): 商品编号(注意：iid近期即将废弃，请用num_iid参数)
    @field increment(Number): 商品库存的变化量，当商品库存增加时，此值为正数；当商品库存减少时，此值为负数。
    @field modified(Date): 商品修改时间（格式：yyyy-MM-dd HH:mm:ss）
    @field nick(String): 卖家昵称
    @field num(Number): 商品数量
    @field num_iid(Number): 商品数字编号
    @field price(Price): 商品价格，格式：5.00；单位：元；精确到：分
    @field sku_id(Number): 商品SKU编号
    @field sku_num(Number): 商品SKU库存
    @field status(String): 商品操作所对应的商品增量消息状态。
        可选值
        ItemAdd（新增商品）
        ItemUpshelf（上架商品）
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
    @field title(String): 商品标题,不能超过60字节
    """
    FIELDS = {
        'changed_fields': {'type': 'String', 'is_list': False},
        'iid': {'type': 'String', 'is_list': False},
        'increment': {'type': 'Number', 'is_list': False},
        'modified': {'type': 'Date', 'is_list': False},
        'nick': {'type': 'String', 'is_list': False},
        'num': {'type': 'Number', 'is_list': False},
        'num_iid': {'type': 'Number', 'is_list': False},
        'price': {'type': 'Price', 'is_list': False},
        'sku_id': {'type': 'Number', 'is_list': False},
        'sku_num': {'type': 'Number', 'is_list': False},
        'status': {'type': 'String', 'is_list': False},
        'title': {'type': 'String', 'is_list': False}
    }


class WlbItemBatchInventory(TOPObject):
    """ 商品的库存信息和批次信息

    @field item_batch(WlbItemBatch, list): 批次库存查询结果
    @field item_id(Number): 商品ID
    @field item_inventorys(WlbItemInventory, list): 商品库存查询结果
    @field total_quantity(Number): 商品在所有仓库的可销库存总数
    """
    FIELDS = {
        'item_batch': {'type': 'WlbItemBatch', 'is_list': True},
        'item_id': {'type': 'Number', 'is_list': False},
        'item_inventorys': {'type': 'WlbItemInventory', 'is_list': True},
        'total_quantity': {'type': 'Number', 'is_list': False}
    }


class Item(TOPObject):
    """ Item(商品)结构

    @field after_sale_id(Number): 售后服务ID,该字段仅在taobao.item.get接口中返回
    @field approve_status(String): 商品上传后的状态。onsale出售中，instock库中
    @field auction_point(Number): 商城返点比例，为5的倍数，最低0.5%
    @field auto_fill(String): 代充商品类型。只有少数类目下的商品可以标记上此字段，具体哪些类目可以上传可以通过taobao.itemcat.features.get获得。在代充商品的类目下，不传表示不标记商品类型（交易搜索中就不能通过标记搜到相关的交易了）。可选类型：
        time_card(点卡软件代充)
        fee_card(话费软件代充)
    @field cid(Number): 商品所属的叶子类目 id
    @field cod_postage_id(Number): 货到付款运费模板ID
    @field created(Date): Item的发布时间，目前仅供taobao.item.add和taobao.item.get可用
    @field delist_time(Date): 下架时间（格式：yyyy-MM-dd HH:mm:ss）
    @field desc(String): 商品描述, 字数要大于5个字符，小于25000个字符
    @field detail_url(String): 商品url
    @field ems_fee(Price): ems费用,格式：5.00；单位：元；精确到：分
    @field express_fee(Price): 快递费用,格式：5.00；单位：元；精确到：分
    @field freight_payer(String): 运费承担方式,seller（卖家承担），buyer(买家承担）
    @field has_discount(Boolean): 支持会员打折,true/false
    @field has_invoice(Boolean): 是否有发票,true/false
    @field has_showcase(Boolean): 橱窗推荐,true/false
    @field has_warranty(Boolean): 是否有保修,true/false
    @field increment(String): 加价幅度。如果为0，代表系统代理幅度。
        在竞拍中，为了超越上一个出价，会员需要在当前出价上增加金额，这个金额就是加价幅度。卖家在发布宝贝的时候可以自定义加价幅度，也可以让系统自动代理加价。系统自动代理加价的加价幅度随着当前出价金额的增加而增加，我们建议会员使用系统自动代理加价，并请买家在出价前看清楚加价幅度的具体金额。另外需要注意是，此功能只适用于拍卖的商品。
        以下是系统自动代理加价幅度表：
        当前价（加价幅度 ）
        1-40（ 1 ）、41-100（ 2 ）、101-200（5 ）、201-500 （10）、501-1001（15）、001-2000（25）、2001-5000（50）、5001-10000（100）
        10001以上         200
    @field inner_shop_auction_template_id(Number): 用户内店宝贝装修模板id
    @field input_pids(String): 用户自行输入的类目属性ID串。结构："pid1,pid2,pid3"，如："20000"（表示品牌） 注：通常一个类目下用户可输入的关键属性不超过1个。
    @field input_str(String): 用户自行输入的子属性名和属性值，结构:"父属性值;一级子属性名;一级子属性值;二级子属性名;自定义输入值,....",如：“耐克;耐克系列;科比系列;科比系列;2K5”，input_str需要与input_pids一一对应，注：通常一个类目下用户可输入的关键属性不超过1个。所有属性别名加起来不能超过 3999字节。
    @field is_3D(Boolean): 是否是3D淘宝的商品
    @field is_ex(Boolean): 是否在外部网店显示
    @field is_fenxiao(Number): 非分销商品：0，代销：1，经销：2
    @field is_lightning_consignment(Boolean): 是否24小时闪电发货
    @field is_prepay(Boolean): 商品是否为先行赔付
        taobao.items.search和taobao.items.vip.search专用
    @field is_taobao(Boolean): 是否在淘宝显示
    @field is_timing(Boolean): 是否定时上架商品
    @field is_virtual(Boolean): 虚拟商品的状态字段
    @field is_xinpin(Boolean): 标示商品是否为新品。
        值含义：true-是，false-否。
    @field item_imgs(ItemImg, list): 商品图片列表(包括主图)。fields中只设置item_img可以返回ItemImg结构体中所有字段，如果设置为item_img.id、item_img.url、item_img.position等形式就只会返回相应的字段
    @field list_time(Date): 上架时间（格式：yyyy-MM-dd HH:mm:ss）
    @field location(Location): 商品所在地
    @field modified(Date): 商品修改时间（格式：yyyy-MM-dd HH:mm:ss）
    @field nick(String): 卖家昵称
    @field num(Number): 商品数量
    @field num_iid(Number): 商品数字id
    @field one_station(Boolean): 是否淘1站商品
    @field outer_id(String): 商家外部编码(可与商家外部系统对接)
    @field outer_shop_auction_template_id(Number): 用户外店装修模板id
    @field pic_url(String): 商品主图片地址
    @field post_fee(Price): 平邮费用,格式：5.00；单位：元；精确到：分
    @field postage_id(Number): 宝贝所属的运费模板ID，如果没有返回则说明没有使用运费模板
    @field price(Price): 商品价格，格式：5.00；单位：元；精确到：分
    @field product_id(Number): 宝贝所属产品的id(可能为空). 该字段可以通过taobao.products.search 得到
    @field promoted_service(String): 消保类型，多个类型以,分割。可取以下值：
        2：假一赔三；4：7天无理由退换货；taobao.items.search和taobao.items.vip.search专用
    @field prop_imgs(PropImg, list): 商品属性图片列表。fields中只设置prop_img可以返回PropImg结构体中所有字段，如果设置为prop_img.id、prop_img.url、prop_img.properties、prop_img.position等形式就只会返回相应的字段
    @field property_alias(String): 属性值别名,比如颜色的自定义名称
    @field props(String): 商品属性 格式：pid:vid;pid:vid
    @field props_name(String): 商品属性名称。标识着props内容里面的pid和vid所对应的名称。格式为：pid1:vid1:pid_name1:vid_name1;pid2:vid2:pid_name2:vid_name2……(<strong>注：</strong><font color="red">属性名称中的冒号":"被转换为："#cln#";
        分号";"被转换为："#scln#"
        </font>)
    @field score(Number): 商品所属卖家的信用等级数，1表示1心，2表示2心……，只有调用商品搜索:taobao.items.get和taobao.items.search的时候才能返回
    @field second_kill(String): 秒杀商品类型。打上秒杀标记的商品，用户只能下架并不能再上架，其他任何编辑或删除操作都不能进行。如果用户想取消秒杀标记，需要联系小二进行操作。如果秒杀结束需要自由编辑请联系活动负责人（小二）去掉秒杀标记。可选类型
        web_only(只能通过web网络秒杀)
        wap_only(只能通过wap网络秒杀)
        web_and_wap(既能通过web秒杀也能通过wap秒杀)
    @field sell_promise(Boolean): 是否承诺退换货服务!
    @field seller_cids(String): 商品所属的店铺内卖家自定义类目列表
    @field skus(Sku, list): <a href="http://open.taobao.com/dev/index.php/Sku">Sku</a>列表。fields中只设置sku可以返回Sku结构体中所有字段，如果设置为sku.sku_id、sku.properties、sku.quantity等形式就只会返回相应的字段
    @field stuff_status(String): 商品新旧程度(全新:new，闲置:unused，二手：second)
    @field sub_stock(Number): 标识商品减库存的方式
        值含义：1-拍下减库存，2-付款减库存。
    @field template_id(String): 页面模板id
    @field title(String): 商品标题,不能超过60字节
    @field type(String): 商品类型(fixed:一口价;auction:拍卖)注：取消团购
    @field valid_thru(Number): 有效期,7或者14（默认是14天）
    @field videos(Video, list): 商品视频列表(目前只支持单个视频关联)。fields中只设置video可以返回Video结构体中所有字段，如果设置为video.id、video.video_id、
        video.url等形式就只会返回相应的字段
    @field violation(Boolean): 商品是否违规，违规：true , 不违规：false
    @field volume(Number): 对应搜索商品列表页的最近成交量,只有调用商品搜索:taobao.items.get和taobao.items.search的时候才能返回
    @field wap_desc(String): 不带html标签的desc文本信息，该字段只在taobao.item.get接口中返回
    @field wap_detail_url(String): 适合wap应用的商品详情url ，该字段只在taobao.item.get接口中返回
    @field ww_status(Boolean): 商品所属的商家的旺旺在线状况，
        taobao.items.search和taobao.items.vip.search专用
    """
    FIELDS = {
        'after_sale_id': {'type': 'Number', 'is_list': False},
        'approve_status': {'type': 'String', 'is_list': False},
        'auction_point': {'type': 'Number', 'is_list': False},
        'auto_fill': {'type': 'String', 'is_list': False},
        'cid': {'type': 'Number', 'is_list': False},
        'cod_postage_id': {'type': 'Number', 'is_list': False},
        'created': {'type': 'Date', 'is_list': False},
        'delist_time': {'type': 'Date', 'is_list': False},
        'desc': {'type': 'String', 'is_list': False},
        'detail_url': {'type': 'String', 'is_list': False},
        'ems_fee': {'type': 'Price', 'is_list': False},
        'express_fee': {'type': 'Price', 'is_list': False},
        'freight_payer': {'type': 'String', 'is_list': False},
        'has_discount': {'type': 'Boolean', 'is_list': False},
        'has_invoice': {'type': 'Boolean', 'is_list': False},
        'has_showcase': {'type': 'Boolean', 'is_list': False},
        'has_warranty': {'type': 'Boolean', 'is_list': False},
        'increment': {'type': 'String', 'is_list': False},
        'inner_shop_auction_template_id': {'type': 'Number', 'is_list': False},
        'input_pids': {'type': 'String', 'is_list': False},
        'input_str': {'type': 'String', 'is_list': False},
        'is_3D': {'type': 'Boolean', 'is_list': False},
        'is_ex': {'type': 'Boolean', 'is_list': False},
        'is_fenxiao': {'type': 'Number', 'is_list': False},
        'is_lightning_consignment': {'type': 'Boolean', 'is_list': False},
        'is_prepay': {'type': 'Boolean', 'is_list': False},
        'is_taobao': {'type': 'Boolean', 'is_list': False},
        'is_timing': {'type': 'Boolean', 'is_list': False},
        'is_virtual': {'type': 'Boolean', 'is_list': False},
        'is_xinpin': {'type': 'Boolean', 'is_list': False},
        'item_imgs': {'type': 'ItemImg', 'is_list': True},
        'list_time': {'type': 'Date', 'is_list': False},
        'location': {'type': 'Location', 'is_list': False},
        'modified': {'type': 'Date', 'is_list': False},
        'nick': {'type': 'String', 'is_list': False},
        'num': {'type': 'Number', 'is_list': False},
        'num_iid': {'type': 'Number', 'is_list': False},
        'one_station': {'type': 'Boolean', 'is_list': False},
        'outer_id': {'type': 'String', 'is_list': False},
        'outer_shop_auction_template_id': {'type': 'Number', 'is_list': False},
        'pic_url': {'type': 'String', 'is_list': False},
        'post_fee': {'type': 'Price', 'is_list': False},
        'postage_id': {'type': 'Number', 'is_list': False},
        'price': {'type': 'Price', 'is_list': False},
        'product_id': {'type': 'Number', 'is_list': False},
        'promoted_service': {'type': 'String', 'is_list': False},
        'prop_imgs': {'type': 'PropImg', 'is_list': True},
        'property_alias': {'type': 'String', 'is_list': False},
        'props': {'type': 'String', 'is_list': False},
        'props_name': {'type': 'String', 'is_list': False},
        'score': {'type': 'Number', 'is_list': False},
        'second_kill': {'type': 'String', 'is_list': False},
        'sell_promise': {'type': 'Boolean', 'is_list': False},
        'seller_cids': {'type': 'String', 'is_list': False},
        'skus': {'type': 'Sku', 'is_list': True},
        'stuff_status': {'type': 'String', 'is_list': False},
        'sub_stock': {'type': 'Number', 'is_list': False},
        'template_id': {'type': 'String', 'is_list': False},
        'title': {'type': 'String', 'is_list': False},
        'type': {'type': 'String', 'is_list': False},
        'valid_thru': {'type': 'Number', 'is_list': False},
        'videos': {'type': 'Video', 'is_list': True},
        'violation': {'type': 'Boolean', 'is_list': False},
        'volume': {'type': 'Number', 'is_list': False},
        'wap_desc': {'type': 'String', 'is_list': False},
        'wap_detail_url': {'type': 'String', 'is_list': False},
        'ww_status': {'type': 'Boolean', 'is_list': False}
    }


class WlbItemInventory(TOPObject):
    """ 物流宝商品库存

    @field item_id(Number): 商品id
    @field lock_quantity(Number): 锁定库存数量
    @field quantity(Number): 库存数量
    @field store_code(String): 仓库编码
    @field type(String): SELLALBE 可销售库存
        DEFECTIVE 残次
        JISHUN 机损
        XIANGSHUN 箱损
        FREEZE 冻结库存
        ONROAD 在途库存
    """
    FIELDS = {
        'item_id': {'type': 'Number', 'is_list': False},
        'lock_quantity': {'type': 'Number', 'is_list': False},
        'quantity': {'type': 'Number', 'is_list': False},
        'store_code': {'type': 'String', 'is_list': False},
        'type': {'type': 'String', 'is_list': False}
    }


class ItemCategory(TOPObject):
    """ 商品查询分类结果

    @field category_id(Number): 分类ID
    @field count(Number): 商品数量
    """
    FIELDS = {
        'category_id': {'type': 'Number', 'is_list': False},
        'count': {'type': 'Number', 'is_list': False}
    }


class Range(TOPObject):
    """ 营销工具的范围类！

    @field participate_id(Number): 营销范围参与者id。即MarketingRangeDO中的participateId。
    @field participate_type(Number): 营销范围参与者类型。MarketingRangeDO中的participateType。(1:商品;2:店铺;3:seller;4:sku;5:category;6:shopCategory)
    """
    FIELDS = {
        'participate_id': {'type': 'Number', 'is_list': False},
        'participate_type': {'type': 'Number', 'is_list': False}
    }


class SellerAuthorize(TOPObject):
    """ 授权

    @field brands(Brand, list): 品牌列表
    @field item_cats(ItemCat, list): 类目列表
    @field xinpin_item_cats(ItemCat, list): 被授权的新品类目列表
    """
    FIELDS = {
        'brands': {'type': 'Brand', 'is_list': True},
        'item_cats': {'type': 'ItemCat', 'is_list': True},
        'xinpin_item_cats': {'type': 'ItemCat', 'is_list': True}
    }


class BuyerCouponDetail(TOPObject):
    """ 买家持有优惠券信息

    @field condition(Number): 优惠券使用条件，订单满多少分才能用这个优惠券，501就是满501分能使用。注意：返回的是“分”，不是“元”
    @field coupon_number(Number): 优惠券编号
    @field denomination(Number): 优惠券的面值，返回的是“分”，不是“元”，500代表500分相当于5元
    @field end_time(Date): 优惠券有效期
    @field receiver(String): 已转送状态下，收到优惠券的淘宝昵称
    @field seller_nick(String): 卖家昵称
    @field source(String): 优惠券来源，卖家或赠送人的淘宝昵称
    @field status(String): unused：未使用，using：使用中,used,已经使用，overdue：已经过期，transfered：已经转发
    """
    FIELDS = {
        'condition': {'type': 'Number', 'is_list': False},
        'coupon_number': {'type': 'Number', 'is_list': False},
        'denomination': {'type': 'Number', 'is_list': False},
        'end_time': {'type': 'Date', 'is_list': False},
        'receiver': {'type': 'String', 'is_list': False},
        'seller_nick': {'type': 'String', 'is_list': False},
        'source': {'type': 'String', 'is_list': False},
        'status': {'type': 'String', 'is_list': False}
    }


class Msg(TOPObject):
    """ 聊天消息内容

    @field content(String): 消息内容
    @field direction(Number): direction=0为from_id发送消息给to_id，direction=1为to_id发送消息给from_id
    @field time(String): 消息日期
    """
    FIELDS = {
        'content': {'type': 'String', 'is_list': False},
        'direction': {'type': 'Number', 'is_list': False},
        'time': {'type': 'String', 'is_list': False}
    }


class ItemProp(TOPObject):
    """ 商品属性

    @field child_template(String): 子属性的模板（卖家自行输入属性时需要用到）
    @field is_allow_alias(Boolean): 是否允许别名。可选值：true（是），false（否）
    @field is_color_prop(Boolean): 是否颜色属性。可选值:true(是),false(否)
    @field is_enum_prop(Boolean): 是否是可枚举属性。可选值:true(是),false(否)
    @field is_input_prop(Boolean): 在is_enum_prop是true的前提下，是否是卖家可以自行输入的属性（注：如果is_enum_prop返回false，该参数统一返回false）。可选值:true(是),false(否)。<b>对于品牌和型号属性（包括子属性）：如果用户是C卖家，则可自定义属性；如果是B卖家，则不可自定义属性，而必须要授权的属性。</b>
    @field is_item_prop(Boolean): 是否商品属性。可选值:true(是),false(否)
    @field is_key_prop(Boolean): 是否关键属性。可选值:true(是),false(否)
    @field is_sale_prop(Boolean): 是否销售属性。可选值:true(是),false(否)
    @field modified_time(Date): 属性修改时间（增量类目专用）
    @field modified_type(String): 三种枚举类型：modify，add，delete（增量类目专用）
    @field multi(Boolean): 发布产品或商品时是否可以多选。可选值:true(是),false(否)
    @field must(Boolean): 发布产品或商品时是否为必选属性。可选值:true(是),false(否)
    @field name(String): 属性名
    @field parent_pid(Number): 上级属性ID
    @field parent_vid(Number): 上级属性值ID
    @field pid(Number): 属性 ID 例：品牌的PID=20000
    @field prop_values(PropValue, list): None
    @field sort_order(Number): 排列序号。取值范围:大于零的整排列序号。取值范围:大于零的整数
    @field status(String): 状态。可选值:normal(正常),deleted(删除)
    @field type(String): 属性值类型。可选值：input(输入)、optional（枚举）multiCheck （多选）
    """
    FIELDS = {
        'child_template': {'type': 'String', 'is_list': False},
        'is_allow_alias': {'type': 'Boolean', 'is_list': False},
        'is_color_prop': {'type': 'Boolean', 'is_list': False},
        'is_enum_prop': {'type': 'Boolean', 'is_list': False},
        'is_input_prop': {'type': 'Boolean', 'is_list': False},
        'is_item_prop': {'type': 'Boolean', 'is_list': False},
        'is_key_prop': {'type': 'Boolean', 'is_list': False},
        'is_sale_prop': {'type': 'Boolean', 'is_list': False},
        'modified_time': {'type': 'Date', 'is_list': False},
        'modified_type': {'type': 'String', 'is_list': False},
        'multi': {'type': 'Boolean', 'is_list': False},
        'must': {'type': 'Boolean', 'is_list': False},
        'name': {'type': 'String', 'is_list': False},
        'parent_pid': {'type': 'Number', 'is_list': False},
        'parent_vid': {'type': 'Number', 'is_list': False},
        'pid': {'type': 'Number', 'is_list': False},
        'prop_values': {'type': 'PropValue', 'is_list': True},
        'sort_order': {'type': 'Number', 'is_list': False},
        'status': {'type': 'String', 'is_list': False},
        'type': {'type': 'String', 'is_list': False}
    }


class Picture(TOPObject):
    """ 图片

    @field created(Date): 图片的创建时间
    @field deleted(String): 图片是否删除的标记
    @field md5(String): 图片在后台处理之后的md5值
        当md5值为32位长度的字符串时为图片搬家后的文件md5验证码
        md5值为长整数时为图片替换后的时间戳
    @field modified(Date): 图片的修改时间
    @field picture_category_id(Number): 图片分类ID
    @field picture_id(Number): 图片ID
    @field picture_path(String): 返回的是绝对路径如：http://img07.taobaocdn.com/imgextra/i7/22670458/T2dD0kXb4cXXXXXXXX_!!22670458.jpg
    @field pixel(String): 图片相素,格式:长x宽，如450x150
    @field referenced(Boolean): 图片是否被引用
    @field sizes(Number): 图片大小,bite单位
    @field status(String): 图片状态,unfroze代表没有被冻结，froze代表被冻结,pass代表排查通过
    @field title(String): 图片标题
    @field uid(Number): 卖家ID
    """
    FIELDS = {
        'created': {'type': 'Date', 'is_list': False},
        'deleted': {'type': 'String', 'is_list': False},
        'md5': {'type': 'String', 'is_list': False},
        'modified': {'type': 'Date', 'is_list': False},
        'picture_category_id': {'type': 'Number', 'is_list': False},
        'picture_id': {'type': 'Number', 'is_list': False},
        'picture_path': {'type': 'String', 'is_list': False},
        'pixel': {'type': 'String', 'is_list': False},
        'referenced': {'type': 'Boolean', 'is_list': False},
        'sizes': {'type': 'Number', 'is_list': False},
        'status': {'type': 'String', 'is_list': False},
        'title': {'type': 'String', 'is_list': False},
        'uid': {'type': 'Number', 'is_list': False}
    }


class Area(TOPObject):
    """ 地址区域结构

    @field id(Number): 标准行政区域代码.参考:http://www.stats.gov.cn/tjbz/xzqhdm/t20120105_402777427.htm
    @field name(String): 地域名称.如北京市,杭州市,西湖区,每一个area_id 都代表了一个具体的地区.
    @field parent_id(Number): 父节点区域标识.如北京市的area_id是110100,朝阳区是北京市的一个区,所以朝阳区的parent_id就是北京市的area_id.
    @field type(Number): 区域类型.area区域 1:country/国家;2:province/省/自治区/直辖市;3:city/地区(省下面的地级市);4:district/县/市(县级市)/区;abroad:海外. 比如北京市的area_type = 2,朝阳区是北京市的一个区,所以朝阳区的area_type = 4.
    @field zip(String): 具体一个地区的邮编
    """
    FIELDS = {
        'id': {'type': 'Number', 'is_list': False},
        'name': {'type': 'String', 'is_list': False},
        'parent_id': {'type': 'Number', 'is_list': False},
        'type': {'type': 'Number', 'is_list': False},
        'zip': {'type': 'String', 'is_list': False}
    }


class LogisticsCompany(TOPObject):
    """ 物流公司基础数据结构

    @field code(String): 物流公司代码
    @field id(Number): 物流公司标识
    @field name(String): 物流公司简称
    @field reg_mail_no(String): 运单号验证正则表达式
    """
    FIELDS = {
        'code': {'type': 'String', 'is_list': False},
        'id': {'type': 'Number', 'is_list': False},
        'name': {'type': 'String', 'is_list': False},
        'reg_mail_no': {'type': 'String', 'is_list': False}
    }


class Shipping(TOPObject):
    """ 物流数据结构

    @field buyer_nick(String): 买家昵称
    @field company_name(String): 物流公司名称
    @field created(Date): 运单创建时间
    @field delivery_end(Date): 预约取货结束时间
    @field delivery_start(Date): 预约取货开始时间
    @field freight_payer(String): 谁承担运费.可选值:buyer(买家承担),seller(卖家承担运费).
    @field is_quick_cod_order(Boolean): 标示为是否快捷COD订单
    @field is_success(Boolean): 返回发货是否成功。
    @field item_title(String): 货物名称
    @field location(Location): 收件人地址信息(在传输请求参数Fields字段时，必须使用“receiver_location”才能返回此字段)
    @field modified(Date): 运单修改时间
    @field order_code(String): 物流订单编号
    @field out_sid(String): 运单号.具体一个物流公司的运单号码.
    @field receiver_mobile(String): 收件人手机号码
    @field receiver_name(String): 收件人姓名
    @field receiver_phone(String): 收件人电话
    @field seller_confirm(String): 卖家是否确认发货.可选值:yes(是),no(否).
    @field seller_nick(String): 卖家昵称
    @field status(String): 物流订单状态,可选值:
        CREATED(订单已创建)
        RECREATED(订单重新创建)
        CANCELLED(订单已取消)
        CLOSED(订单关闭)
        SENDING(等候发送给物流公司)
        ACCEPTING(已发送给物流公司,等待接单)
        ACCEPTED(物流公司已接单)
        REJECTED(物流公司不接单)
        PICK_UP(物流公司揽收成功)
        PICK_UP_FAILED(物流公司揽收失败)
        LOST(物流公司丢单)
        REJECTED_BY_RECEIVER(对方拒签)
        ACCEPTED_BY_RECEIVER(对方已签收)
    @field tid(Number): 交易ID
    @field type(String): 物流方式.可选值:free(卖家包邮),post(平邮),express(快递),ems(EMS).
    """
    FIELDS = {
        'buyer_nick': {'type': 'String', 'is_list': False},
        'company_name': {'type': 'String', 'is_list': False},
        'created': {'type': 'Date', 'is_list': False},
        'delivery_end': {'type': 'Date', 'is_list': False},
        'delivery_start': {'type': 'Date', 'is_list': False},
        'freight_payer': {'type': 'String', 'is_list': False},
        'is_quick_cod_order': {'type': 'Boolean', 'is_list': False},
        'is_success': {'type': 'Boolean', 'is_list': False},
        'item_title': {'type': 'String', 'is_list': False},
        'location': {'type': 'Location', 'is_list': False},
        'modified': {'type': 'Date', 'is_list': False},
        'order_code': {'type': 'String', 'is_list': False},
        'out_sid': {'type': 'String', 'is_list': False},
        'receiver_mobile': {'type': 'String', 'is_list': False},
        'receiver_name': {'type': 'String', 'is_list': False},
        'receiver_phone': {'type': 'String', 'is_list': False},
        'seller_confirm': {'type': 'String', 'is_list': False},
        'seller_nick': {'type': 'String', 'is_list': False},
        'status': {'type': 'String', 'is_list': False},
        'tid': {'type': 'Number', 'is_list': False},
        'type': {'type': 'String', 'is_list': False}
    }


class TradeRate(TOPObject):
    """ 评价列表

    @field content(String): 评价内容,最大长度:500个汉字
    @field created(Date): 评价创建时间,格式:yyyy-MM-dd HH:mm:ss
    @field item_price(Price): 商品价格,精确到2位小数;单位:元.如:200.07，表示:200元7分
    @field item_title(String): 商品标题
    @field nick(String): 评价者昵称
    @field oid(Number): 子订单ID
    @field rated_nick(String): 被评价者昵称
    @field reply(String): 评价解释,最大长度:500个汉字
    @field result(String): 评价结果,可选值:good(好评),neutral(中评),bad(差评)
    @field role(String): 评价者角色.可选值:seller(卖家),buyer(买家)
    @field tid(Number): 交易ID
    @field valid_score(Boolean): 评价信息是否用于记分，
        可取值：true(参与记分)和false(不参与记分)
    """
    FIELDS = {
        'content': {'type': 'String', 'is_list': False},
        'created': {'type': 'Date', 'is_list': False},
        'item_price': {'type': 'Price', 'is_list': False},
        'item_title': {'type': 'String', 'is_list': False},
        'nick': {'type': 'String', 'is_list': False},
        'oid': {'type': 'Number', 'is_list': False},
        'rated_nick': {'type': 'String', 'is_list': False},
        'reply': {'type': 'String', 'is_list': False},
        'result': {'type': 'String', 'is_list': False},
        'role': {'type': 'String', 'is_list': False},
        'tid': {'type': 'Number', 'is_list': False},
        'valid_score': {'type': 'Boolean', 'is_list': False}
    }


class FenxiaoSku(TOPObject):
    """ 分销产品SKU

    @field cost_price(String): 代销采购价，单位：元
    @field dealer_cost_price(String): 经销采购价
    @field id(Number): SkuID
    @field name(String): 名称
    @field outer_id(String): 商家编码
    @field properties(String): sku的销售属性组合字符串。格式:pid:vid;pid:vid,如:1627207:3232483;1630696:3284570,表示:机身颜色:军绿色;手机套餐:一电一充。
    @field quantity(Number): 库存
    @field standard_price(String): 市场价
    """
    FIELDS = {
        'cost_price': {'type': 'String', 'is_list': False},
        'dealer_cost_price': {'type': 'String', 'is_list': False},
        'id': {'type': 'Number', 'is_list': False},
        'name': {'type': 'String', 'is_list': False},
        'outer_id': {'type': 'String', 'is_list': False},
        'properties': {'type': 'String', 'is_list': False},
        'quantity': {'type': 'Number', 'is_list': False},
        'standard_price': {'type': 'String', 'is_list': False}
    }


class TaobaokeReportMember(TOPObject):
    """ 淘宝客报表成员

    @field app_key(String): 应用授权码
    @field category_id(Number): 所购买商品的类目ID
    @field category_name(String): 所购买商品的类目名称
    @field commission(Price): 用户获得的佣金
    @field commission_rate(String): 佣金比率。比如：0.01代表1%
    @field iid(String): 商品字符串ID(注意：iid近期即将废弃，请用num_iid参数)
    @field item_num(Number): 商品成交数量
    @field item_title(String): 商品标题
    @field num_iid(Number): 商品ID
    @field outer_code(String): 推广渠道
    @field pay_price(Price): 成交价格
    @field pay_time(Date): 成交时间
    @field real_pay_fee(Price): 实际支付金额
    @field seller_nick(String): 卖家昵称
    @field shop_title(String): 店铺名称
    @field trade_id(Number): 淘宝交易号
    """
    FIELDS = {
        'app_key': {'type': 'String', 'is_list': False},
        'category_id': {'type': 'Number', 'is_list': False},
        'category_name': {'type': 'String', 'is_list': False},
        'commission': {'type': 'Price', 'is_list': False},
        'commission_rate': {'type': 'String', 'is_list': False},
        'iid': {'type': 'String', 'is_list': False},
        'item_num': {'type': 'Number', 'is_list': False},
        'item_title': {'type': 'String', 'is_list': False},
        'num_iid': {'type': 'Number', 'is_list': False},
        'outer_code': {'type': 'String', 'is_list': False},
        'pay_price': {'type': 'Price', 'is_list': False},
        'pay_time': {'type': 'Date', 'is_list': False},
        'real_pay_fee': {'type': 'Price', 'is_list': False},
        'seller_nick': {'type': 'String', 'is_list': False},
        'shop_title': {'type': 'String', 'is_list': False},
        'trade_id': {'type': 'Number', 'is_list': False}
    }


class Permission(TOPObject):
    """ 权限信息

    @field is_authorize(Number): 1 :允许授权  2：不允许授权 6：不允许授权但默认已有权限
    @field parent_code(String): 父权限code
    @field permission_code(String): 注册到权限中心的code值
    @field permission_name(String): 权限名称
    """
    FIELDS = {
        'is_authorize': {'type': 'Number', 'is_list': False},
        'parent_code': {'type': 'String', 'is_list': False},
        'permission_code': {'type': 'String', 'is_list': False},
        'permission_name': {'type': 'String', 'is_list': False}
    }


class Receiver(TOPObject):
    """ 收货人详细信息

    @field address(String): 收货人的详细地址信息
    @field city(String): 收货人的城市
    @field district(String): 区/县
    @field mobile_phone(String): 移动电话。
    @field name(String): 收货人全名。
    @field phone(String): 固定电话。
    @field state(String): 收货人所在省份
    @field zip(String): 邮政编码
    """
    FIELDS = {
        'address': {'type': 'String', 'is_list': False},
        'city': {'type': 'String', 'is_list': False},
        'district': {'type': 'String', 'is_list': False},
        'mobile_phone': {'type': 'String', 'is_list': False},
        'name': {'type': 'String', 'is_list': False},
        'phone': {'type': 'String', 'is_list': False},
        'state': {'type': 'String', 'is_list': False},
        'zip': {'type': 'String', 'is_list': False}
    }


class LoginUser(TOPObject):
    """ 登录分销用户信息

    @field create_time(Date): 入驻时间
    @field nick(String): 会员NICK
    @field user_id(Number): 分销用户ID
    @field user_type(String): 分销用户类型(1:分销商，2:供应商)
    """
    FIELDS = {
        'create_time': {'type': 'Date', 'is_list': False},
        'nick': {'type': 'String', 'is_list': False},
        'user_id': {'type': 'Number', 'is_list': False},
        'user_type': {'type': 'String', 'is_list': False}
    }


class ItemSearch(TOPObject):
    """ 商品搜索

    @field item_categories(ItemCategory, list): 商品搜索分类
    @field items(Item, list): 商品列表
    """
    FIELDS = {
        'item_categories': {'type': 'ItemCategory', 'is_list': True},
        'items': {'type': 'Item', 'is_list': True}
    }


class TaobaokeReport(TOPObject):
    """ 淘宝客报表

    @field taobaoke_report_members(TaobaokeReportMember, list): 淘宝客报表成员列表
    @field total_results(Number): 搜索到的结果的总条数
    """
    FIELDS = {
        'taobaoke_report_members': {'type': 'TaobaokeReportMember', 'is_list': True},
        'total_results': {'type': 'Number', 'is_list': False}
    }


class PurchaseOrder(TOPObject):
    """ 采购单及子采购单信息

    @field alipay_no(String): 支付宝交易号。
    @field buyer_nick(String): 买家nick，供应商查询不会返回买家昵称，分销商查询才会返回。
    @field consign_time(Date): 物流发货时间。格式:yyyy-MM-dd HH:mm:ss
    @field created(Date): 采购单创建时间。格式:yyyy-MM-dd HH:mm:ss
    @field distributor_from(String): 分销商来源网站（taobao）。
    @field distributor_payment(Price): 分销商实付金额。(精确到2位小数;单位:元。如:200.07，表示:200元7分 )
    @field distributor_username(String): 分销商在来源网站的帐号名。
    @field end_time(Date): 交易结束时间
    @field fenxiao_id(Number): 分销流水号，分销平台产生的主键
    @field id(Number): 供应商交易ID 非采购单ID，如果改发货状态 是需要该ID，ID在用户未付款前为0，付款后有具体值（发货时使用该ID）
    @field isv_custom_key(String, list): 自定义key
    @field isv_custom_value(String, list): 自定义值
    @field logistics_company_name(String): 物流公司
    @field logistics_id(String): 运单号
    @field memo(String): 采购单留言。
    @field modified(Date): 交易修改时间。格式:yyyy-MM-dd HH:mm:ss
    @field pay_time(Date): 付款时间。格式:yyyy-MM-dd HH:mm:ss
    @field pay_type(String): 支付方式：ALIPAY_SURETY（支付宝担保交易）、ALIPAY_CHAIN（分账交易）、TRANSFER（线下转账）、PREPAY（预存款）、IMMEDIATELY（即时到账）
    @field post_fee(Price): 采购单邮费。(精确到2位小数;单位:元。如:200.07，表示:200元7分 )
    @field receiver(Receiver): 买家详细的信息。
    @field shipping(String): 配送方式，FAST(快速)、EMS、ORDINARY(平邮)、SELLER(卖家包邮)
    @field snapshot_url(String): 订单快照URL
    @field status(String): 采购单交易状态。可选值：<br>
        WAIT_BUYER_PAY(等待付款)<br>
        WAIT_SELLER_SEND_GOODS(已付款，待发货）<br>
        WAIT_BUYER_CONFIRM_GOODS(已付款，已发货)<br>
        TRADE_FINISHED(交易成功)<br>
        TRADE_CLOSED(交易关闭)<br>
        WAIT_BUYER_CONFIRM_GOODS_ACOUNTED(已付款（已分账），已发货。只对代销分账支持)<br>
        WAIT_SELLER_SEND_GOODS_ACOUNTED(已付款（已分账），待发货。只对代销分账支持)
    @field sub_purchase_orders(SubPurchaseOrder, list): 子订单的详细信息列表。
    @field supplier_flag(Number): 返回供应商备注旗帜
        vlaue在1-5之间。非1-5之间，都采用1作为默认。 1:红色 2:黄色 3:绿色 4:蓝色 5:粉红色
    @field supplier_from(String): 供应商来源网站, values: taobao, alibaba
    @field supplier_memo(String): 供应商备注
    @field supplier_username(String): 供应商在来源网站的帐号名。
    @field tc_order_id(Number): 主订单ID （经销不显示）
    @field total_fee(Price): 采购单总额（不含邮费,精确到2位小数;单位:元。如:200.07，表示:200元7分 )
    @field trade_type(String): 分销方式：AGENT（代销）、DEALER（经销）
    """
    FIELDS = {
        'alipay_no': {'type': 'String', 'is_list': False},
        'buyer_nick': {'type': 'String', 'is_list': False},
        'consign_time': {'type': 'Date', 'is_list': False},
        'created': {'type': 'Date', 'is_list': False},
        'distributor_from': {'type': 'String', 'is_list': False},
        'distributor_payment': {'type': 'Price', 'is_list': False},
        'distributor_username': {'type': 'String', 'is_list': False},
        'end_time': {'type': 'Date', 'is_list': False},
        'fenxiao_id': {'type': 'Number', 'is_list': False},
        'id': {'type': 'Number', 'is_list': False},
        'isv_custom_key': {'type': 'String', 'is_list': True},
        'isv_custom_value': {'type': 'String', 'is_list': True},
        'logistics_company_name': {'type': 'String', 'is_list': False},
        'logistics_id': {'type': 'String', 'is_list': False},
        'memo': {'type': 'String', 'is_list': False},
        'modified': {'type': 'Date', 'is_list': False},
        'pay_time': {'type': 'Date', 'is_list': False},
        'pay_type': {'type': 'String', 'is_list': False},
        'post_fee': {'type': 'Price', 'is_list': False},
        'receiver': {'type': 'Receiver', 'is_list': False},
        'shipping': {'type': 'String', 'is_list': False},
        'snapshot_url': {'type': 'String', 'is_list': False},
        'status': {'type': 'String', 'is_list': False},
        'sub_purchase_orders': {'type': 'SubPurchaseOrder', 'is_list': True},
        'supplier_flag': {'type': 'Number', 'is_list': False},
        'supplier_from': {'type': 'String', 'is_list': False},
        'supplier_memo': {'type': 'String', 'is_list': False},
        'supplier_username': {'type': 'String', 'is_list': False},
        'tc_order_id': {'type': 'Number', 'is_list': False},
        'total_fee': {'type': 'Price', 'is_list': False},
        'trade_type': {'type': 'String', 'is_list': False}
    }


class FenxiaoProduct(TOPObject):
    """ 分销产品

    @field alarm_number(Number): 警戒库存
    @field category_id(String): 类目id
    @field city(String): 所在地：市
    @field cost_price(Price): 采购价格，单位：元。
    @field created(Date): 创建时间
    @field dealer_cost_price(Price): 经销采购价
    @field desc_path(String): 产品描述路径，通过http请求获取
    @field description(String): 产品描述的内容
    @field discount_id(Number): 折扣ID（新增参数）
    @field have_guarantee(Boolean): 是否有保修，可选值：false（否）、true（是）
    @field have_invoice(Boolean): 是否有发票，可选值：false（否）、true（是）
    @field input_properties(String): 自定义属性，格式为pid:value;pid:value
    @field is_authz(String): 查询产品列表时，查询入参增加is_authz:yes|no
        yes:需要授权
        no:不需要授权
    @field item_id(Number): 导入的商品ID
    @field items_count(Number): 下载人数
    @field modified(Date): 更新时间
    @field name(String): 产品名称
    @field orders_count(Number): 累计采购次数
    @field outer_id(String): 商家编码
    @field pictures(String): 产品图片路径
    @field pid(Number): 产品ID
    @field postage_ems(Price): ems费用，单位：元
    @field postage_fast(Price): 快递费用，单位：元
    @field postage_id(Number): 运费模板ID
    @field postage_ordinary(Price): 平邮费用，单位：元
    @field postage_type(String): 运费类型，可选值：seller（供应商承担运费）、buyer（分销商承担运费）
    @field productcat_id(Number): 产品线ID
    @field properties(String): 产品属性，格式为pid:vid;pid:vid
    @field property_alias(String): 属性别名，格式为pid:vid:alias;pid:vid:alias
    @field prov(String): 所在地：省
    @field quantity(Number): 产品库存
    @field retail_price_high(Price): 最高零售价，单位：分。
    @field retail_price_low(Price): 最低零售价，单位：分。
    @field skus(FenxiaoSku, list): sku列表
    @field standard_price(Price): 市场价格，单位：元。
    @field status(String): 发布状态，可选值：up（上架）、down（下架）
    @field trade_type(String): 分销方式：AGENT（只做代销，默认值）、DEALER（只做经销）、ALL（代销和经销都做）
    @field upshelf_time(Date): 铺货时间
    """
    FIELDS = {
        'alarm_number': {'type': 'Number', 'is_list': False},
        'category_id': {'type': 'String', 'is_list': False},
        'city': {'type': 'String', 'is_list': False},
        'cost_price': {'type': 'Price', 'is_list': False},
        'created': {'type': 'Date', 'is_list': False},
        'dealer_cost_price': {'type': 'Price', 'is_list': False},
        'desc_path': {'type': 'String', 'is_list': False},
        'description': {'type': 'String', 'is_list': False},
        'discount_id': {'type': 'Number', 'is_list': False},
        'have_guarantee': {'type': 'Boolean', 'is_list': False},
        'have_invoice': {'type': 'Boolean', 'is_list': False},
        'input_properties': {'type': 'String', 'is_list': False},
        'is_authz': {'type': 'String', 'is_list': False},
        'item_id': {'type': 'Number', 'is_list': False},
        'items_count': {'type': 'Number', 'is_list': False},
        'modified': {'type': 'Date', 'is_list': False},
        'name': {'type': 'String', 'is_list': False},
        'orders_count': {'type': 'Number', 'is_list': False},
        'outer_id': {'type': 'String', 'is_list': False},
        'pictures': {'type': 'String', 'is_list': False},
        'pid': {'type': 'Number', 'is_list': False},
        'postage_ems': {'type': 'Price', 'is_list': False},
        'postage_fast': {'type': 'Price', 'is_list': False},
        'postage_id': {'type': 'Number', 'is_list': False},
        'postage_ordinary': {'type': 'Price', 'is_list': False},
        'postage_type': {'type': 'String', 'is_list': False},
        'productcat_id': {'type': 'Number', 'is_list': False},
        'properties': {'type': 'String', 'is_list': False},
        'property_alias': {'type': 'String', 'is_list': False},
        'prov': {'type': 'String', 'is_list': False},
        'quantity': {'type': 'Number', 'is_list': False},
        'retail_price_high': {'type': 'Price', 'is_list': False},
        'retail_price_low': {'type': 'Price', 'is_list': False},
        'skus': {'type': 'FenxiaoSku', 'is_list': True},
        'standard_price': {'type': 'Price', 'is_list': False},
        'status': {'type': 'String', 'is_list': False},
        'trade_type': {'type': 'String', 'is_list': False},
        'upshelf_time': {'type': 'Date', 'is_list': False}
    }


class SubUserInfo(TOPObject):
    """ 子账号基本信息

    @field full_name(String): 子账号姓名
    @field is_online(Number): 是否参与分流 1不参与 2参与
    @field nick(String): 子账号用户名
    @field seller_id(Number): 子账号所属的主账号的唯一标识
    @field seller_nick(String): 主账号昵称
    @field status(Number): 子账号当前状态 1正常 -1删除  2冻结
    @field sub_id(Number): 子账号Id
    """
    FIELDS = {
        'full_name': {'type': 'String', 'is_list': False},
        'is_online': {'type': 'Number', 'is_list': False},
        'nick': {'type': 'String', 'is_list': False},
        'seller_id': {'type': 'Number', 'is_list': False},
        'seller_nick': {'type': 'String', 'is_list': False},
        'status': {'type': 'Number', 'is_list': False},
        'sub_id': {'type': 'Number', 'is_list': False}
    }


class TaobaokeItem(TOPObject):
    """ 淘宝客商品

    @field click_url(String): 推广点击url
    @field commission(Price): 淘宝客佣金
    @field commission_num(String): 累计成交量.注：返回的数据是30天内累计推广量
    @field commission_rate(String): 淘宝客佣金比率，比如：1234.00代表12.34%
    @field commission_volume(Price): 累计总支出佣金量
    @field iid(String): 淘宝客商品id(注意：iid近期即将废弃，请用num_iid参数)
    @field item_location(String): 商品所在地
    @field keyword_click_url(String): 淘宝客关键词搜索URL
    @field nick(String): 卖家昵称
    @field num_iid(Number): 淘宝客商品数字id
    @field pic_url(String): 图片url
    @field price(Price): 商品价格
    @field seller_credit_score(Number): 卖家信用等级
    @field seller_id(Number): 卖家id
    @field shop_click_url(String): 商品所在店铺的推广点击url
    @field taobaoke_cat_click_url(String): 淘宝客类目推广URL
    @field title(String): 商品title 宝贝名称
    @field volume(Number): 30天内交易量
    """
    FIELDS = {
        'click_url': {'type': 'String', 'is_list': False},
        'commission': {'type': 'Price', 'is_list': False},
        'commission_num': {'type': 'String', 'is_list': False},
        'commission_rate': {'type': 'String', 'is_list': False},
        'commission_volume': {'type': 'Price', 'is_list': False},
        'iid': {'type': 'String', 'is_list': False},
        'item_location': {'type': 'String', 'is_list': False},
        'keyword_click_url': {'type': 'String', 'is_list': False},
        'nick': {'type': 'String', 'is_list': False},
        'num_iid': {'type': 'Number', 'is_list': False},
        'pic_url': {'type': 'String', 'is_list': False},
        'price': {'type': 'Price', 'is_list': False},
        'seller_credit_score': {'type': 'Number', 'is_list': False},
        'seller_id': {'type': 'Number', 'is_list': False},
        'shop_click_url': {'type': 'String', 'is_list': False},
        'taobaoke_cat_click_url': {'type': 'String', 'is_list': False},
        'title': {'type': 'String', 'is_list': False},
        'volume': {'type': 'Number', 'is_list': False}
    }


class TaohuaAudioReaderMyAlbum(TOPObject):
    """ 我购买的有声读物专辑

    @field copyright(String): 版权所属
    @field item_id(Number): 专辑ID
    @field last_updated(String): 最后更新日期
    @field my_track_count(Number): 专辑内已购买的单曲总数
    @field pic_url(String): 专辑封面图片url
    @field serial_id(Number): 购买专辑的序列ID
    @field status(String): 专辑状态
    @field title(String): 专辑名称
    @field track_count(Number): 专辑内的单曲总数
    """
    FIELDS = {
        'copyright': {'type': 'String', 'is_list': False},
        'item_id': {'type': 'Number', 'is_list': False},
        'last_updated': {'type': 'String', 'is_list': False},
        'my_track_count': {'type': 'Number', 'is_list': False},
        'pic_url': {'type': 'String', 'is_list': False},
        'serial_id': {'type': 'Number', 'is_list': False},
        'status': {'type': 'String', 'is_list': False},
        'title': {'type': 'String', 'is_list': False},
        'track_count': {'type': 'Number', 'is_list': False}
    }


class TaobaokeShop(TOPObject):
    """ 淘宝客店铺

    @field auction_count(Number): 店铺内商品总数
    @field click_url(String): 店铺推广URL
    @field commission_rate(String): 淘宝客店铺佣金比率
    @field seller_credit(String): 店铺掌柜信用等级
    @field seller_nick(String): 卖家昵称
    @field shop_id(Number): 店铺id
    @field shop_title(String): 店铺名称
    @field shop_type(String): 店铺类型 B=商城卖家 C=普通卖家
    @field total_auction(String): 累计推广量
    @field user_id(Number): 店铺用户id
    """
    FIELDS = {
        'auction_count': {'type': 'Number', 'is_list': False},
        'click_url': {'type': 'String', 'is_list': False},
        'commission_rate': {'type': 'String', 'is_list': False},
        'seller_credit': {'type': 'String', 'is_list': False},
        'seller_nick': {'type': 'String', 'is_list': False},
        'shop_id': {'type': 'Number', 'is_list': False},
        'shop_title': {'type': 'String', 'is_list': False},
        'shop_type': {'type': 'String', 'is_list': False},
        'total_auction': {'type': 'String', 'is_list': False},
        'user_id': {'type': 'Number', 'is_list': False}
    }


class SubPurchaseOrder(TOPObject):
    """ 子采购单详细信息

    @field auction_price(Price): 代销采购单对应下游200订单的商品零售价（单位是元）
    @field buyer_payment(Price): 买家实付金额。（精确到2位小数;单位:元。如:200.07，表示:200元7分）
    @field created(Date): 创建时间。格式 yyyy-MM-dd HH:mm:ss 。
    @field distributor_payment(Price): 分销商实付金额。（精确到2位小数;单位:元。如:200.07，表示:200元7分）
    @field fenxiao_id(Number): 分销平台的子采购单主键
    @field id(Number): 子采购单id，淘宝交易主键，采购单未付款时为0.（即将废掉）
    @field item_id(Number): 分销平台上商品id
    @field item_outer_id(String): 分销平台上商品商家编码。
    @field num(Number): 商品购买数量。取值范围:大于零的整数
    @field old_sku_properties(String): 老的SKU属性值。如: 颜色:红色:别名;尺码:L:别名
    @field order_200_status(String): 代销采购单对应下游200订单状态。
        可选值：
        WAIT_SELLER_SEND_GOODS(已付款，待发货)
        WAIT_BUYER_CONFIRM_GOODS(已付款，已发货)
        TRADE_CLOSED(已退款成功)
        TRADE_REFUNDING(退款中)
        TRADE_FINISHED(交易成功)
        TRADE_CLOSED_BY_TAOBAO(交易关闭)
    @field price(Price): 单个商品价格。（精确到2位小数;单位:元。如:200.07，表示:200元7分）
    @field refund_fee(Price): 退款金额
    @field sku_id(Number): 商品的SKU id。该字段即将被废弃，所以值可能不准确，建议使用sku_outer_id，sku_properties这两个值
    @field sku_outer_id(String): SKU商家编码。
    @field sku_properties(String): SKU属性值。如: 颜色:红色:别名;尺码:L:别名
    @field snapshot_url(String): 快照地址。
    @field status(String): 交易状态。可选值：<br>
        WAIT_BUYER_PAY(等待付款)<br>
        WAIT_CONFIRM(付款信息待确认)<br>
        WAIT_CONFIRM_WAIT_SEND_GOODS(付款信息待确认，待发货)<br>
        WAIT_CONFIRM_SEND_GOODS(付款信息待确认，已发货)<br>
        WAIT_CONFIRM_GOODS_CONFIRM(付款信息待确认，已收货)<br>
        WAIT_SELLER_SEND_GOODS(已付款，待发货)<br>
        WAIT_BUYER_CONFIRM_GOODS(已付款，已发货)<br>
        CONFIRM_WAIT_SEND_GOODS(付款信息已确认，待发货)<br>
        CONFIRM_SEND_GOODS(付款信息已确认，已发货)<br>
        TRADE_REFUNDED(已退款)<br>
        TRADE_REFUNDING(退款中)<br>
        TRADE_FINISHED(交易成功)<br>
        TRADE_CLOSED(交易关闭)<br>
    @field tc_order_id(Number): TC订单ID（经销不显示）
    @field title(String): 商品标题。
    @field total_fee(Price): 分销商应付金额。（精确到2位小数;单位:元。如:200.07，表示:200元7分）
    """
    FIELDS = {
        'auction_price': {'type': 'Price', 'is_list': False},
        'buyer_payment': {'type': 'Price', 'is_list': False},
        'created': {'type': 'Date', 'is_list': False},
        'distributor_payment': {'type': 'Price', 'is_list': False},
        'fenxiao_id': {'type': 'Number', 'is_list': False},
        'id': {'type': 'Number', 'is_list': False},
        'item_id': {'type': 'Number', 'is_list': False},
        'item_outer_id': {'type': 'String', 'is_list': False},
        'num': {'type': 'Number', 'is_list': False},
        'old_sku_properties': {'type': 'String', 'is_list': False},
        'order_200_status': {'type': 'String', 'is_list': False},
        'price': {'type': 'Price', 'is_list': False},
        'refund_fee': {'type': 'Price', 'is_list': False},
        'sku_id': {'type': 'Number', 'is_list': False},
        'sku_outer_id': {'type': 'String', 'is_list': False},
        'sku_properties': {'type': 'String', 'is_list': False},
        'snapshot_url': {'type': 'String', 'is_list': False},
        'status': {'type': 'String', 'is_list': False},
        'tc_order_id': {'type': 'Number', 'is_list': False},
        'title': {'type': 'String', 'is_list': False},
        'total_fee': {'type': 'Price', 'is_list': False}
    }


class ProductCat(TOPObject):
    """ 产品线

    @field cost_percent_agent(String): 代销采购价百分比
    @field cost_percent_dealer(String): 经销采购价百分比
    @field id(Number): 产品线ID
    @field name(String): 产品线名称
    @field product_num(Number): 产品数量
    @field retail_high_percent(String): 最高零食价百分比
    @field retail_low_percent(String): 最低零售价百分比
    """
    FIELDS = {
        'cost_percent_agent': {'type': 'String', 'is_list': False},
        'cost_percent_dealer': {'type': 'String', 'is_list': False},
        'id': {'type': 'Number', 'is_list': False},
        'name': {'type': 'String', 'is_list': False},
        'product_num': {'type': 'Number', 'is_list': False},
        'retail_high_percent': {'type': 'String', 'is_list': False},
        'retail_low_percent': {'type': 'String', 'is_list': False}
    }


class TaohuaRootDirectory(TOPObject):
    """ 文档目录根目录

    @field kids(TaohuaDirectory, list): 子目录
    @field name(String): 目录名称
    @field page(Number): 页码
    """
    FIELDS = {
        'kids': {'type': 'TaohuaDirectory', 'is_list': True},
        'name': {'type': 'String', 'is_list': False},
        'page': {'type': 'Number', 'is_list': False}
    }


class Feature(TOPObject):
    """ 类目属性

    @field attr_key(String): 属性键
    @field attr_value(String): 属性值
    """
    FIELDS = {
        'attr_key': {'type': 'String', 'is_list': False},
        'attr_value': {'type': 'String', 'is_list': False}
    }


class AppCustomer(TOPObject):
    """ 开通增量消息服务的应用用户

    @field created(Date): isv为用户开通增量消息服务的时间
    @field modified(Date): 最后修改时间，开通、用户的session生效或失效都会更改这个时间。
    @field nick(String): 开通用户的淘宝昵称
    @field status(String): 应用用户开通增量消息服务的状态：有两个返回值valid_session和invalid_session。valid_session表示已开通且seesion有效；invalid_session已开通但session失效，此时，无法接收该用户的消息。
    @field subscriptions(Subscription, list): 应用为用户开通的消息类型。只有用户开通的消息在应用所订阅的消息类别集合内时，应用才能收到相应的消息。例如：应用订阅添加商品，用户开通了添加商品和删除商品，此时应用只能收到添加商品的消息，收不到删除商品的消息。
    @field type(String, list): 用户使用的功能。get表示增量api取消息功能；notify表示主动通知功能；syn表示同步数据到ISV数据库功能。
    @field user_id(Number): 用户编号
    """
    FIELDS = {
        'created': {'type': 'Date', 'is_list': False},
        'modified': {'type': 'Date', 'is_list': False},
        'nick': {'type': 'String', 'is_list': False},
        'status': {'type': 'String', 'is_list': False},
        'subscriptions': {'type': 'Subscription', 'is_list': True},
        'type': {'type': 'String', 'is_list': True},
        'user_id': {'type': 'Number', 'is_list': False}
    }


class TaohuaDirectory(TOPObject):
    """ 文档目录

    @field name(String): 目录名称
    @field page(Number): 页码
    @field rel(String): 子类目类型
    """
    FIELDS = {
        'name': {'type': 'String', 'is_list': False},
        'page': {'type': 'Number', 'is_list': False},
        'rel': {'type': 'String', 'is_list': False}
    }


class HuabaoChannel(TOPObject):
    """ 画报频道数据结构

    @field channel_name(String): 频道名称
    @field channel_url(String): 淘宝频道连接
    @field description(String): 频道描述
    @field id(Number): 画报频道ID
    @field name_en(String): 频道英文名称
    """
    FIELDS = {
        'channel_name': {'type': 'String', 'is_list': False},
        'channel_url': {'type': 'String', 'is_list': False},
        'description': {'type': 'String', 'is_list': False},
        'id': {'type': 'Number', 'is_list': False},
        'name_en': {'type': 'String', 'is_list': False}
    }


class HuabaoPicture(TOPObject):
    """ 画报图片结构

    @field create_date(Date): 图片创建时间
    @field modified_date(Date): 图片修改时间
    @field pic_id(String): 图片ID
    @field pic_note(String): 图片说明
    @field pic_url(String): 图片URL
    @field poster_id(Number): 画报ID
    """
    FIELDS = {
        'create_date': {'type': 'Date', 'is_list': False},
        'modified_date': {'type': 'Date', 'is_list': False},
        'pic_id': {'type': 'String', 'is_list': False},
        'pic_note': {'type': 'String', 'is_list': False},
        'pic_url': {'type': 'String', 'is_list': False},
        'poster_id': {'type': 'Number', 'is_list': False}
    }


class PictureCategory(TOPObject):
    """ 图片分类

    @field created(Date): 图片类目的创建时间
    @field modified(Date): 图片分类的修改时间
    @field parent_id(Number): 一级分类的parent_id为0
        二级分类的则为其父分类的picture_category_id
    @field picture_category_id(Number): 图片分类ID
    @field picture_category_name(String): 图片分类名
    @field position(Number): 图片分类排序
    @field type(String): 图片分类型别，sys-fixture代表店铺装修分类(系统分类)，sys-auction代表宝贝图片分类(系统分类)，user-define代表用户自定义分类
    """
    FIELDS = {
        'created': {'type': 'Date', 'is_list': False},
        'modified': {'type': 'Date', 'is_list': False},
        'parent_id': {'type': 'Number', 'is_list': False},
        'picture_category_id': {'type': 'Number', 'is_list': False},
        'picture_category_name': {'type': 'String', 'is_list': False},
        'position': {'type': 'Number', 'is_list': False},
        'type': {'type': 'String', 'is_list': False}
    }


class Distributor(TOPObject):
    """ 分销API返回数据结构

    @field alipay_account(String): 分销商的支付宝帐户
    @field appraise(Number): 分销商的淘宝卖家评价
    @field category_id(Number): 分销商店铺主营类目
    @field contact_person(String): 联系人
    @field created(Date): 分销商创建时间 时间格式：yyyy-MM-dd HH:mm:ss
    @field distributor_id(Number): 分销商Id
    @field distributor_name(String): 分销商姓名
    @field email(String): 分销商的email
    @field full_name(String): 分销商的真实姓名，认证姓名
    @field level(Number): 店铺等级
    @field mobile_phone(String): 分销商的手机号
    @field phone(String): 分销商的电话
    @field shop_web_link(String): 分销商的网店链接
    @field starts(Date): 分销商卖家的开店时间
    @field user_id(Number): 分销商ID
    """
    FIELDS = {
        'alipay_account': {'type': 'String', 'is_list': False},
        'appraise': {'type': 'Number', 'is_list': False},
        'category_id': {'type': 'Number', 'is_list': False},
        'contact_person': {'type': 'String', 'is_list': False},
        'created': {'type': 'Date', 'is_list': False},
        'distributor_id': {'type': 'Number', 'is_list': False},
        'distributor_name': {'type': 'String', 'is_list': False},
        'email': {'type': 'String', 'is_list': False},
        'full_name': {'type': 'String', 'is_list': False},
        'level': {'type': 'Number', 'is_list': False},
        'mobile_phone': {'type': 'String', 'is_list': False},
        'phone': {'type': 'String', 'is_list': False},
        'shop_web_link': {'type': 'String', 'is_list': False},
        'starts': {'type': 'Date', 'is_list': False},
        'user_id': {'type': 'Number', 'is_list': False}
    }


class GroupDomain(TOPObject):
    """ 分组简单定义

    @field group_id(Number): 分组ID
    @field group_name(String): 分组名称
    """
    FIELDS = {
        'group_id': {'type': 'Number', 'is_list': False},
        'group_name': {'type': 'String', 'is_list': False}
    }


class BasicMember(TOPObject):
    """ 表示会员关系的基本信息字段，用于会员列表的基本查询

    @field biz_order_id(Number): 最后一次交易的订单号
    @field buyer_id(Number): 买家会员ID
    @field buyer_nick(String): 会员昵称
    @field close_trade_amount(Price): 交易关闭金额
    @field close_trade_count(Number): 交易关闭的笔数
    @field grade(Number): 会员等级，0：无会员等级，1：普通会员，2：高级会员，3：VIP会员， 4：至尊VIP会员
    @field group_ids(String): 分组的id集合字符串
    @field item_num(Number): 购买的宝贝件数
    @field last_trade_time(Date): 最后交易的日期
    @field relation_source(Number): 关系来源，1交易成功，2未交易成功
    @field status(String): 显示会员的状态，normal正常，delete被买家删除，blacklist黑名单
    @field trade_amount(Price): 交易的金额
    @field trade_count(Number): 交易成功的次数
    """
    FIELDS = {
        'biz_order_id': {'type': 'Number', 'is_list': False},
        'buyer_id': {'type': 'Number', 'is_list': False},
        'buyer_nick': {'type': 'String', 'is_list': False},
        'close_trade_amount': {'type': 'Price', 'is_list': False},
        'close_trade_count': {'type': 'Number', 'is_list': False},
        'grade': {'type': 'Number', 'is_list': False},
        'group_ids': {'type': 'String', 'is_list': False},
        'item_num': {'type': 'Number', 'is_list': False},
        'last_trade_time': {'type': 'Date', 'is_list': False},
        'relation_source': {'type': 'Number', 'is_list': False},
        'status': {'type': 'String', 'is_list': False},
        'trade_amount': {'type': 'Price', 'is_list': False},
        'trade_count': {'type': 'Number', 'is_list': False}
    }


class GradePromotion(TOPObject):
    """ 卖家设置的等级优惠信息

    @field cur_grade(String): 买家会员级别    1：普通会员 2：高级会员 3：VIP会员 4：至尊VIP
    @field cur_grade_name(String): 普通会员 、高级会员、VIP会员、至尊VIP
    @field discount(Number): 会员级别折扣率没有小数，990代表9.9折
    @field next_upgrade_amount(Number): 升级到下一个级别的需要的交易额，单位：分
    @field next_upgrade_count(Number): 升级到下一个级别的需要的交易量
    """
    FIELDS = {
        'cur_grade': {'type': 'String', 'is_list': False},
        'cur_grade_name': {'type': 'String', 'is_list': False},
        'discount': {'type': 'Number', 'is_list': False},
        'next_upgrade_amount': {'type': 'Number', 'is_list': False},
        'next_upgrade_count': {'type': 'Number', 'is_list': False}
    }


class RuleData(TOPObject):
    """ 规则相关信息

    @field end_trade_time(Date): 交易结束时间
    @field grade(Number): 会员等级
    @field grouplist(GroupDomain, list): 分组信息，包括分组id与分组名称
    @field max_avg_price(Price): 最大平均客单价
    @field max_close_trade_count(Number): 最大交易关闭次数
    @field max_item_count(Number): 最大宝贝件数
    @field max_trade_amount(Price): 最大交易额
    @field max_trade_count(Number): 最大交易笔数
    @field min_avg_price(Price): 最小平均客单价
    @field min_close_trade_count(Number): 最小交易关闭次数
    @field min_item_count(Number): 最少宝贝件数
    @field min_trade_amount(Price): 最小交易额
    @field min_trade_count(Number): 最小交易笔数
    @field province(Number): 省份的代码，北京=1,天津=2,河北省=3,山西省=4,内蒙古自治区=5,辽宁省=6,吉林省=7,黑龙江省=8,上海=9,江苏省=10,浙江省=11,安徽省=12,福建省=13,江西省=14,山东省=15,河南省=16,湖北省=17,湖南省=18, 广东省=19,广西壮族自治区=20,海南省=21,重庆=22,四川省=23,贵州省=24,云南省=25,西藏自治区26,陕西省=27,甘肃省=28,青海省=29,宁夏回族自治区=30,新疆维吾尔自治区=31,台湾省=32,香港特别行政区=33,澳门特别行政区=34,海外=35
    @field relation_source(Number): 客户关系来源
    @field rule_id(Number): 规则ID
    @field rule_name(String): 规则名称
    @field seller_id(Number): 卖家ID
    @field start_trade_time(Date): 交易的开始时间
    """
    FIELDS = {
        'end_trade_time': {'type': 'Date', 'is_list': False},
        'grade': {'type': 'Number', 'is_list': False},
        'grouplist': {'type': 'GroupDomain', 'is_list': True},
        'max_avg_price': {'type': 'Price', 'is_list': False},
        'max_close_trade_count': {'type': 'Number', 'is_list': False},
        'max_item_count': {'type': 'Number', 'is_list': False},
        'max_trade_amount': {'type': 'Price', 'is_list': False},
        'max_trade_count': {'type': 'Number', 'is_list': False},
        'min_avg_price': {'type': 'Price', 'is_list': False},
        'min_close_trade_count': {'type': 'Number', 'is_list': False},
        'min_item_count': {'type': 'Number', 'is_list': False},
        'min_trade_amount': {'type': 'Price', 'is_list': False},
        'min_trade_count': {'type': 'Number', 'is_list': False},
        'province': {'type': 'Number', 'is_list': False},
        'relation_source': {'type': 'Number', 'is_list': False},
        'rule_id': {'type': 'Number', 'is_list': False},
        'rule_name': {'type': 'String', 'is_list': False},
        'seller_id': {'type': 'Number', 'is_list': False},
        'start_trade_time': {'type': 'Date', 'is_list': False}
    }


class TaobaokeItemDetail(TOPObject):
    """ 淘宝客商品详情

    @field click_url(String): 商品推广URL
    @field item(Item): 商品详细信息. fields中需要设置Item下的字段,如设置:iid,detail_url等; 只设置item_detail,则不返回的Item下的所有信息.
    @field seller_credit_score(Number): 商品所属卖家的信用等级
    @field shop_click_url(String): 商品所在的店铺的推广URL
    """
    FIELDS = {
        'click_url': {'type': 'String', 'is_list': False},
        'item': {'type': 'Item', 'is_list': False},
        'seller_credit_score': {'type': 'Number', 'is_list': False},
        'shop_click_url': {'type': 'String', 'is_list': False}
    }


class CrmMember(TOPObject):
    """ 会员信息对象

    @field avg_price(Price): 平均客单价.
    @field biz_order_id(Number): 最后一次交易的订单号
    @field buyer_id(Number): 会员买家id
    @field buyer_nick(String): 买家昵称
    @field city(String): 城市
    @field close_trade_amount(Price): 交易关闭的金额
    @field close_trade_count(Number): 交易关闭的的笔数
    @field grade(Number): 会员等级，1：普通会员，2：高级会员，3：VIP会员， 4：至尊VIP会员
    @field group_ids(String): 会员拥有的所有分组
    @field item_close_count(Number): 交易关闭的宝贝件数
    @field item_num(Number): 购买的宝贝件数
    @field last_trade_time(Date): 最后交易时间
    @field province(Number): 北京=1,天津=2,河北省=3,山西省=4,内蒙古自治区=5,辽宁省=6,吉林省=7,黑龙江省=8,上海=9,江苏省=10,浙江省=11,安徽省=12,福建省=13,江西省=14,山东省=15,河南省=16,湖北省=17,湖南省=18, 广东省=19,广西壮族自治区=20,海南省=21,重庆=22,四川省=23,贵州省=24,云南省=25,西藏自治区26,陕西省=27,甘肃省=28,青海省=29,宁夏回族自治区=30,新疆维吾尔自治区=31,台湾省=32,香港特别行政区=33,澳门特别行政区=34,海外=35
    @field relation_source(Number): 关系来源，1交易成功，2未成交
    @field status(String): 显示会员的状态，normal正常，delete被买家删除，blacklist黑名单
    @field trade_amount(Price): 交易成功的金额
    @field trade_count(Number): 交易成功笔数
    """
    FIELDS = {
        'avg_price': {'type': 'Price', 'is_list': False},
        'biz_order_id': {'type': 'Number', 'is_list': False},
        'buyer_id': {'type': 'Number', 'is_list': False},
        'buyer_nick': {'type': 'String', 'is_list': False},
        'city': {'type': 'String', 'is_list': False},
        'close_trade_amount': {'type': 'Price', 'is_list': False},
        'close_trade_count': {'type': 'Number', 'is_list': False},
        'grade': {'type': 'Number', 'is_list': False},
        'group_ids': {'type': 'String', 'is_list': False},
        'item_close_count': {'type': 'Number', 'is_list': False},
        'item_num': {'type': 'Number', 'is_list': False},
        'last_trade_time': {'type': 'Date', 'is_list': False},
        'province': {'type': 'Number', 'is_list': False},
        'relation_source': {'type': 'Number', 'is_list': False},
        'status': {'type': 'String', 'is_list': False},
        'trade_amount': {'type': 'Price', 'is_list': False},
        'trade_count': {'type': 'Number', 'is_list': False}
    }


class Group(TOPObject):
    """ 描述分组的数据结构

    @field group_create(Date): 分组的创建时间
    @field group_id(Number): 分组的id
    @field group_modify(Date): 分组的修改时间
    @field group_name(String): 分组的名称
    @field member_count(Number): 分组所拥有的会员数量,如果返回值为-1，表示当前服务忙。
    @field status(String): 分组的状态，1表示正常
    """
    FIELDS = {
        'group_create': {'type': 'Date', 'is_list': False},
        'group_id': {'type': 'Number', 'is_list': False},
        'group_modify': {'type': 'Date', 'is_list': False},
        'group_name': {'type': 'String', 'is_list': False},
        'member_count': {'type': 'Number', 'is_list': False},
        'status': {'type': 'String', 'is_list': False}
    }


class HuabaoAuctionInfo(TOPObject):
    """ 画报商品数据结构

    @field auction_id(Number): 商品ID
    @field auction_note(String): 商品描述
    @field auction_position(String): 商品位置坐标,形式为："x:y",x坐标,y坐标
    @field auction_price(Price): 商品价格
    @field auction_short_title(String): 商品短标题
    @field auction_title(String): 商品标题
    @field auction_url(String): 商品链接
    @field pic_id(Number): 商品图片ID
    @field poster_id(Number): 画报ID
    """
    FIELDS = {
        'auction_id': {'type': 'Number', 'is_list': False},
        'auction_note': {'type': 'String', 'is_list': False},
        'auction_position': {'type': 'String', 'is_list': False},
        'auction_price': {'type': 'Price', 'is_list': False},
        'auction_short_title': {'type': 'String', 'is_list': False},
        'auction_title': {'type': 'String', 'is_list': False},
        'auction_url': {'type': 'String', 'is_list': False},
        'pic_id': {'type': 'Number', 'is_list': False},
        'poster_id': {'type': 'Number', 'is_list': False}
    }


class Huabao(TOPObject):
    """ 画报数据结构

    @field channel_id(Number): 画报所属频道ID
    @field cover_pic_url(String): 画报封面地址
    @field create_date(Date): 画报创建时间
    @field hits(Number): 画报点击数
    @field id(Number): 画报ID
    @field modified_date(Date): 画报修改时间
    @field tag(String): 画报标签
    @field title(String): 图片标题
    @field title_short(String): 画报短标题
    @field weight(Number): 画报权重0-10
    """
    FIELDS = {
        'channel_id': {'type': 'Number', 'is_list': False},
        'cover_pic_url': {'type': 'String', 'is_list': False},
        'create_date': {'type': 'Date', 'is_list': False},
        'hits': {'type': 'Number', 'is_list': False},
        'id': {'type': 'Number', 'is_list': False},
        'modified_date': {'type': 'Date', 'is_list': False},
        'tag': {'type': 'String', 'is_list': False},
        'title': {'type': 'String', 'is_list': False},
        'title_short': {'type': 'String', 'is_list': False},
        'weight': {'type': 'Number', 'is_list': False}
    }


class WaitingTimesOnDay(TOPObject):
    """ 客户等待（客服）平均时长列表

    @field waiting_date(Date): 等待时长（统计）日期
    @field waiting_time_by_ids(WaitingTimeById, list): 等待时长列表
    """
    FIELDS = {
        'waiting_date': {'type': 'Date', 'is_list': False},
        'waiting_time_by_ids': {'type': 'WaitingTimeById', 'is_list': True}
    }


class WlbAuthorization(TOPObject):
    """ 授权关系

    @field authorize_end_time(Date): 授权结束时间
    @field authorize_id(Number): 授权ID
    @field authorize_start_time(Date): 授权开始时间
    @field consign_user_id(Number): 代销人用户ID
    @field item_id(Number): 授权商品ID
    @field name(String): 授权名称
    @field owner_user_id(Number): 货主用户ID
    @field quantity(Number): 授权数量
    @field rule_code(String): 授权编码
    @field status(String): 状态：
        VALID -- 1 有效
        INVALIDATION -- 2 失效
    """
    FIELDS = {
        'authorize_end_time': {'type': 'Date', 'is_list': False},
        'authorize_id': {'type': 'Number', 'is_list': False},
        'authorize_start_time': {'type': 'Date', 'is_list': False},
        'consign_user_id': {'type': 'Number', 'is_list': False},
        'item_id': {'type': 'Number', 'is_list': False},
        'name': {'type': 'String', 'is_list': False},
        'owner_user_id': {'type': 'Number', 'is_list': False},
        'quantity': {'type': 'Number', 'is_list': False},
        'rule_code': {'type': 'String', 'is_list': False},
        'status': {'type': 'String', 'is_list': False}
    }


class WlbMessage(TOPObject):
    """ 通道消息

    @field gmt_create(Date): 创建时间
    @field id(Number): 消息通道ID
    @field msg_code(String): 通知消息编码： STOCK_IN_NOT_CONSISTENT---入库单不一致 CANCEL_ORDER_SUCCESS---取消订单成功 CANCEL_ORDER_FAILURE---取消订单失败 INVENTORY_CHECK---盘点   INVENTORY_CHECK---盘点消息  ORDER_REJECT--wms拒单  ORDER_CONFIRMED--订单处理成功 WMS_FAILED--wms处理失败
    @field msg_content(String): 通知内容：msg_code为STOCK_IN_NOT_CONSISTENT时,msg_content为:orderCode:code;orderItemId:111;itemId:123;planQuantity:10;relQuantity:6;
        msg_code为CANCEL_ORDER_SUCCESS及其它时,msg_content为：orderCode:code;
        msg_code为CANCEL_ORDER_SUCCESS及其它时,msg_content为：orderCode:code; msg_code为INVENTORY_CHECK时，msg_content为orderCode:code;
    @field msg_description(String): 消息描述
    @field status(String): 消息状态： 不需要确认：NO_NEED_CONFIRM 已确认：CONFIRMED 待确认：TO_BE_CONFIRM
    @field user_id(Number): 用户ID
    """
    FIELDS = {
        'gmt_create': {'type': 'Date', 'is_list': False},
        'id': {'type': 'Number', 'is_list': False},
        'msg_code': {'type': 'String', 'is_list': False},
        'msg_content': {'type': 'String', 'is_list': False},
        'msg_description': {'type': 'String', 'is_list': False},
        'status': {'type': 'String', 'is_list': False},
        'user_id': {'type': 'Number', 'is_list': False}
    }


class NonReplyStatOnDay(TOPObject):
    """ 未回复统计列表(按天)

    @field nonreply_date(Date): （某天的）未回复统计
    @field nonreply_stat_by_ids(NonreplyStatById, list): 未回复统计列表
    """
    FIELDS = {
        'nonreply_date': {'type': 'Date', 'is_list': False},
        'nonreply_stat_by_ids': {'type': 'NonreplyStatById', 'is_list': True}
    }


class WlbConsignMent(TOPObject):
    """ 物流宝代销关系

    @field id(Number): 代销关系id
    @field item_id(Number): 代销商用户前台宝贝id
    @field number(Number): 代销数量
    @field tgt_item_id(Number): 供应商商品id
    @field tgt_user_id(Number): 供应商用户id
    @field user_id(Number): 代销商用户id
    """
    FIELDS = {
        'id': {'type': 'Number', 'is_list': False},
        'item_id': {'type': 'Number', 'is_list': False},
        'number': {'type': 'Number', 'is_list': False},
        'tgt_item_id': {'type': 'Number', 'is_list': False},
        'tgt_user_id': {'type': 'Number', 'is_list': False},
        'user_id': {'type': 'Number', 'is_list': False}
    }


class StaffEvalStatOnDay(TOPObject):
    """ 客服评价统计列表(按天)

    @field eval_date(Date): 评价产生的日期
    @field staff_eval_stat_by_ids(StaffEvalStatById, list): 客服评价统计列表
    """
    FIELDS = {
        'eval_date': {'type': 'Date', 'is_list': False},
        'staff_eval_stat_by_ids': {'type': 'StaffEvalStatById', 'is_list': True}
    }


class WlbReplenish(TOPObject):
    """ 物流宝补货统计对象

    @field estimate_value(String): 根据历史统计值计算出来的预期值
        WarnByLast3Days=1; ByLast3Days=3;
        ByLast10Days=10;
        ByLast30Days=30;
        ByLast90Days=90
        WarnByLast3Days为按照过去3天的发出的件数来统计的达到安全库存的天数；其它4项分别为按照过去3、10、30、90天发出的商品件数，现有库存可以维持的天数
    @field history_value(String): 订单历史统计值
        Last3DaysTotal=3; Last10DaysTotal=10;
        Last30DaysTotal=30; Last90DaysTotal=90
        分别为过去3、10、30、90天发出的商品件数
    @field item_id(Number): 商品id
    @field retrieval_count(Number): 补货周期（单位：天）
    @field sell_count(Number): 可销售库存数
    @field store_code(String): 仓库编码
    @field transport_count(Number): 在途库存数
    @field user_id(Number): 用户id
    @field warn_count(Number): 安全库存
    """
    FIELDS = {
        'estimate_value': {'type': 'String', 'is_list': False},
        'history_value': {'type': 'String', 'is_list': False},
        'item_id': {'type': 'Number', 'is_list': False},
        'retrieval_count': {'type': 'Number', 'is_list': False},
        'sell_count': {'type': 'Number', 'is_list': False},
        'store_code': {'type': 'String', 'is_list': False},
        'transport_count': {'type': 'Number', 'is_list': False},
        'user_id': {'type': 'Number', 'is_list': False},
        'warn_count': {'type': 'Number', 'is_list': False}
    }


class OnlineTimesOnDay(TOPObject):
    """ 某天的客服在线时长列表

    @field online_date(Date): 在线日期
    @field online_time_by_ids(OnlineTimeById, list): 在线时长列表
    """
    FIELDS = {
        'online_date': {'type': 'Date', 'is_list': False},
        'online_time_by_ids': {'type': 'OnlineTimeById', 'is_list': True}
    }


class WlbProcessStatus(TOPObject):
    """ 物流宝订单流转信息对象

    @field content(String): 状态内容
    @field operate_time(Date): 操作时间
    @field operater(String): 操作人
    @field order_code(String): 物流宝订单编码
    @field remark(String): 备注
    @field status_code(String): 订单操作状态：WMS_ACCEPT;WMS_PRINT;WMS_PICK;WMS_CHECK;WMS_PACKAGE;WMS_CONSIGN;WMS_CANCEL;WMS_UNKNOWN;WMS_CONFIRMED
        TMS_ACCEPT;TMS_STATION_IN;TMS_STATION_OUT;TMS_SIGN;TMS_REJECT;TMS_CANCEL;TMS_UNKNOW;SYS_UNKNOWN
    @field store_code(String): 仓库编码
    @field store_tp_code(String): 仓库合作公司编码
    @field tms_order_code(String): tms合作公司订单编码
    @field tms_tp_code(String): tms合作公司编码
    """
    FIELDS = {
        'content': {'type': 'String', 'is_list': False},
        'operate_time': {'type': 'Date', 'is_list': False},
        'operater': {'type': 'String', 'is_list': False},
        'order_code': {'type': 'String', 'is_list': False},
        'remark': {'type': 'String', 'is_list': False},
        'status_code': {'type': 'String', 'is_list': False},
        'store_code': {'type': 'String', 'is_list': False},
        'store_tp_code': {'type': 'String', 'is_list': False},
        'tms_order_code': {'type': 'String', 'is_list': False},
        'tms_tp_code': {'type': 'String', 'is_list': False}
    }


class WlbOrderItem(TOPObject):
    """ 物流宝订单商品

    @field batch_remark(String): 批次号备注
    @field confirm_status(String): 物流宝订单确认状态：
        NO_NEED_CONFIRM--不需要确认
        WAIT_CONFIRM--待确认
        CONFIRMED--已确认
    @field ext_entity_id(String): 外部实体id
    @field ext_entity_type(String): 外部实体类型
    @field id(Number): 订单商品id
    @field inventory_type(String): INVENTORY_TYPE_SELL 可销库存
        INVENTORY_TYPE_IMPERFECTIONS 残次库存
        INVENTORY_TYPE_FREEZE 冻结库存
        INVENTORY_TYPE_ON_PASSAGE 在途库存
    @field item_code(String): 订单商品编码
    @field item_id(Number): 物流宝订单商品的物流宝商品id
    @field item_name(String): 订单商品名称
    @field item_price(Number): 商品价格
    @field order_code(String): 物流宝订单编码
    @field order_id(Number): 物流宝订单id
    @field order_sub_2code(String): 子交易号
    @field order_sub_code(String): 订单号
    @field order_sub_type(String): (1)其它: OTHER (2)淘宝交易: TAOBAO (3)调拨: ALLOCATION (4)盘点:CHECK (5)销售采购:PRUCHASE(6)其它交易：OTHER_TRADE
    @field picture_url(String): 订单商品图片url
    @field plan_quantity(Number): 计划数量
    @field provider_tp_id(Number): 货主id
    @field provider_tp_nick(String): 货主nick
    @field publish_version(Number): 商品发布版本号
    @field real_quantity(Number): 实际数量
    @field remark(String): 订单商品备注
    @field user_id(Number): 订单商品用户id
    @field user_nick(String): 订单商品用户昵称
    """
    FIELDS = {
        'batch_remark': {'type': 'String', 'is_list': False},
        'confirm_status': {'type': 'String', 'is_list': False},
        'ext_entity_id': {'type': 'String', 'is_list': False},
        'ext_entity_type': {'type': 'String', 'is_list': False},
        'id': {'type': 'Number', 'is_list': False},
        'inventory_type': {'type': 'String', 'is_list': False},
        'item_code': {'type': 'String', 'is_list': False},
        'item_id': {'type': 'Number', 'is_list': False},
        'item_name': {'type': 'String', 'is_list': False},
        'item_price': {'type': 'Number', 'is_list': False},
        'order_code': {'type': 'String', 'is_list': False},
        'order_id': {'type': 'Number', 'is_list': False},
        'order_sub_2code': {'type': 'String', 'is_list': False},
        'order_sub_code': {'type': 'String', 'is_list': False},
        'order_sub_type': {'type': 'String', 'is_list': False},
        'picture_url': {'type': 'String', 'is_list': False},
        'plan_quantity': {'type': 'Number', 'is_list': False},
        'provider_tp_id': {'type': 'Number', 'is_list': False},
        'provider_tp_nick': {'type': 'String', 'is_list': False},
        'publish_version': {'type': 'Number', 'is_list': False},
        'real_quantity': {'type': 'Number', 'is_list': False},
        'remark': {'type': 'String', 'is_list': False},
        'user_id': {'type': 'Number', 'is_list': False},
        'user_nick': {'type': 'String', 'is_list': False}
    }


class WlbOrder(TOPObject):
    """ 物流宝订单对象

    @field buyer_nick(String): 买家nick
    @field cancel_order_status(Number): 订单取消状态：
        1-取消中；
        2-取消失败；
        3-取消完成
    @field confirm_status(String): 确认状态：
        (1)不需要确认：NO_NEED_CONFIRM
        (2)等待确认：WAIT_CONFIRM
        (3)已确认:CONFIRMED
    @field expect_end_time(Date): 计划送达结束时间
    @field expect_start_time(Date): 计划送达开始时间
    @field invoice_info(String): 发票信息
    @field item_kinds_count(Number): 物流宝订单中的商品种类数量
    @field operate_type(String): 出库或者入库，IN表示入库，OUT表示出库
    @field order_code(String): 订单编码
    @field order_flag(Number): 第1位:COD,2:限时配送,3:预售,4:需要发票,5:已投诉,第6位:合单,第7位:拆单 第8位：EXCHANGE-换货， 第9位:VISIT-上门 ， 第10位: MODIFYTRANSPORT-是否可改配送方式，第11位：是否物流代理确认发货
    @field order_source(String): 订单来源:
        产生物流订单的原因，比如:
        订单来源:1:TAOBAO;2:EXT;3:ERP;4:WMS
    @field order_source_code(String): 对应创建物流宝订单top接口中的的out_biz_code字段，主要是用来去重用
    @field order_status(String): 物流状态，
        订单已创建：0
        订单已取消: -1
        订单关闭:-3
        下发中: 10
        已下发: 11
        接收方拒签 :-100
        已发货:100
        签收成功:200
    @field order_status_reason(String): 卖家取消,仓库取消标识
    @field order_sub_type(String): (1)其它:    OTHER
        (2)淘宝交易: TAOBAO
        (3)301:调拨: ALLOCATION
        (4)401:盘点:CHECK
        (5)501:销售采购:PRUCHASE
    @field order_type(String): 1:正常订单: NARMAL
        2:退货订单: RETURN
        3:换货订单: CHANGE
    @field prev_order_code(String): 原订单编码
    @field real_kinds_count(Number): 实际入库的种类数量
    @field receivable_amount(Number): 应收金额
    @field receiver_address(String): 收件人具体地址
    @field receiver_area(String): 区或者县
    @field receiver_city(String): 收件人城市
    @field receiver_mail(String): 接收人电子邮箱
    @field receiver_mobile(String): 接收人手机号码
    @field receiver_name(String): 接收人姓名
    @field receiver_phone(String): 接收人固定电话
    @field receiver_province(String): 收件人省份
    @field receiver_wangwang(String): 接收人旺旺
    @field receiver_zip_code(String): 收件人邮编
    @field remark(String): 订单备注
    @field schedule_day(String): 发货日期:
        (1)1 为工作日
        (2)2 为节假日
    @field schedule_end(String): 配送结束时间通常是HH:MM格式
    @field schedule_speed(Number): 发货速度  ，
        101-当日达，
        102-次晨达，
        103-次日达
    @field schedule_start(String): 配送开始时间通常是HH:MM格式
    @field sender_address(String): 发件人地址
    @field sender_area(String): 发件人所在区
    @field sender_city(String): 发件人城市
    @field sender_email(String): 发件人电子邮箱
    @field sender_mobile(String): 发件人移动电话
    @field sender_name(String): 发件人姓名
    @field sender_phone(String): 发件人联系电话
    @field sender_province(String): 发件人所在省份
    @field sender_zip_code(String): 发件人邮编
    @field service_fee(Number): cod服务费
    @field shipping_type(String): 物流运输方式：
        MAIL-平邮
        EXPRESS-快递
        EMS-EMS
        OTHER-其他
    @field store_code(String): 仓库编码
    @field tms_tp_code(String): 发货物流公司编码，STO,YTO,EMS等
    @field total_amount(Number): 订单总价
    @field user_id(Number): 卖家ID
    @field user_nick(String): 卖家NICK
    """
    FIELDS = {
        'buyer_nick': {'type': 'String', 'is_list': False},
        'cancel_order_status': {'type': 'Number', 'is_list': False},
        'confirm_status': {'type': 'String', 'is_list': False},
        'expect_end_time': {'type': 'Date', 'is_list': False},
        'expect_start_time': {'type': 'Date', 'is_list': False},
        'invoice_info': {'type': 'String', 'is_list': False},
        'item_kinds_count': {'type': 'Number', 'is_list': False},
        'operate_type': {'type': 'String', 'is_list': False},
        'order_code': {'type': 'String', 'is_list': False},
        'order_flag': {'type': 'Number', 'is_list': False},
        'order_source': {'type': 'String', 'is_list': False},
        'order_source_code': {'type': 'String', 'is_list': False},
        'order_status': {'type': 'String', 'is_list': False},
        'order_status_reason': {'type': 'String', 'is_list': False},
        'order_sub_type': {'type': 'String', 'is_list': False},
        'order_type': {'type': 'String', 'is_list': False},
        'prev_order_code': {'type': 'String', 'is_list': False},
        'real_kinds_count': {'type': 'Number', 'is_list': False},
        'receivable_amount': {'type': 'Number', 'is_list': False},
        'receiver_address': {'type': 'String', 'is_list': False},
        'receiver_area': {'type': 'String', 'is_list': False},
        'receiver_city': {'type': 'String', 'is_list': False},
        'receiver_mail': {'type': 'String', 'is_list': False},
        'receiver_mobile': {'type': 'String', 'is_list': False},
        'receiver_name': {'type': 'String', 'is_list': False},
        'receiver_phone': {'type': 'String', 'is_list': False},
        'receiver_province': {'type': 'String', 'is_list': False},
        'receiver_wangwang': {'type': 'String', 'is_list': False},
        'receiver_zip_code': {'type': 'String', 'is_list': False},
        'remark': {'type': 'String', 'is_list': False},
        'schedule_day': {'type': 'String', 'is_list': False},
        'schedule_end': {'type': 'String', 'is_list': False},
        'schedule_speed': {'type': 'Number', 'is_list': False},
        'schedule_start': {'type': 'String', 'is_list': False},
        'sender_address': {'type': 'String', 'is_list': False},
        'sender_area': {'type': 'String', 'is_list': False},
        'sender_city': {'type': 'String', 'is_list': False},
        'sender_email': {'type': 'String', 'is_list': False},
        'sender_mobile': {'type': 'String', 'is_list': False},
        'sender_name': {'type': 'String', 'is_list': False},
        'sender_phone': {'type': 'String', 'is_list': False},
        'sender_province': {'type': 'String', 'is_list': False},
        'sender_zip_code': {'type': 'String', 'is_list': False},
        'service_fee': {'type': 'Number', 'is_list': False},
        'shipping_type': {'type': 'String', 'is_list': False},
        'store_code': {'type': 'String', 'is_list': False},
        'tms_tp_code': {'type': 'String', 'is_list': False},
        'total_amount': {'type': 'Number', 'is_list': False},
        'user_id': {'type': 'Number', 'is_list': False},
        'user_nick': {'type': 'String', 'is_list': False}
    }


class Task(TOPObject):
    """ 批量异步任务结果

    @field check_code(String): 下载文件的MD5校验码，通过此校验码可以检查下载的文件是否是完整的。
    @field created(Date): 任务创建时间
    @field download_url(String): 大任务结果下载地址。当创建的认任务是大数据量的任务时，获取结果会返回此字段，同时subtasks列表会为空。
        通过这个地址可以下载到结果的结构体，格式同普通任务下载的一样。
        每次获取到的地址只能下载一次。下载的文件加上后缀名.zip打开。
    @field method(String): 此任务是由哪个api产生的
    @field schedule(Date): 定时类型任务的执行时间点
    @field status(String): 异步任务处理状态。new（还未开始处理），doing（处理中），done（处理结束）。
    @field subtasks(Subtask, list): 子任务处理结果，如果任务还没有处理完，返回的结果列表为空。如果任务处理完毕，返回子任务结果列表
    @field task_id(Number): 异步任务id。创建异步任务时返回的任务id号
    """
    FIELDS = {
        'check_code': {'type': 'String', 'is_list': False},
        'created': {'type': 'Date', 'is_list': False},
        'download_url': {'type': 'String', 'is_list': False},
        'method': {'type': 'String', 'is_list': False},
        'schedule': {'type': 'Date', 'is_list': False},
        'status': {'type': 'String', 'is_list': False},
        'subtasks': {'type': 'Subtask', 'is_list': True},
        'task_id': {'type': 'Number', 'is_list': False}
    }


class WlbSellerSubscription(TOPObject):
    """ 卖家定购的服务

    @field end_date(Date): 定购有效结束日期
    @field gmt_create(Date): 创建时间
    @field gmt_modified(Date): 修改时间
    @field id(Number): 定购ID
    @field is_own_service(Number): 判断该仓库是否是实体仓，还是虚拟仓，null是实体仓，10:代表虚拟仓
    @field parent_id(Number): 父定购ID
        可通过该字段来得之服务上下级关系。
        例定购了仓储服务，下又有TMS服务。
        该字段保存仓储服务ID。
    @field provider_user_id(Number): 服务商ID
    @field remark(String): 备注
    @field service_alias(String): 自有仓的别名，当当前订购记录为自有仓时才会有值
    @field service_code(String): 服务编码
    @field service_id(Number): 服务ID
    @field service_name(String): 服务名
    @field service_type(String): 服务类型，
        STORE 1-仓储、
        TMS 2-TMS、
        PACKAGE 3-包装服务
        SUPPLIER 4-供货
        INSTALL 5-安装
        COMPLEX_SERVICE 100-综合服务
    @field start_date(Date): 定购有效开始日期
    @field status(String): 状态
        AUDITING 1-待审核
        CANCEL 2-撤销
        CHECKED 3-审核通过
        FAILED 4-审核未通过
        SYNCHRONIZING 5-同步中
    @field subscriber_user_id(Number): 定购用户ID
    @field subscriber_user_nick(String): 定购用户NICK
    @field wlb_partner_address(WlbPartnerAddress): 联系人地址信息
    @field wlb_partner_contact(WlbPartnerContact): 联系人联系详情
    """
    FIELDS = {
        'end_date': {'type': 'Date', 'is_list': False},
        'gmt_create': {'type': 'Date', 'is_list': False},
        'gmt_modified': {'type': 'Date', 'is_list': False},
        'id': {'type': 'Number', 'is_list': False},
        'is_own_service': {'type': 'Number', 'is_list': False},
        'parent_id': {'type': 'Number', 'is_list': False},
        'provider_user_id': {'type': 'Number', 'is_list': False},
        'remark': {'type': 'String', 'is_list': False},
        'service_alias': {'type': 'String', 'is_list': False},
        'service_code': {'type': 'String', 'is_list': False},
        'service_id': {'type': 'Number', 'is_list': False},
        'service_name': {'type': 'String', 'is_list': False},
        'service_type': {'type': 'String', 'is_list': False},
        'start_date': {'type': 'Date', 'is_list': False},
        'status': {'type': 'String', 'is_list': False},
        'subscriber_user_id': {'type': 'Number', 'is_list': False},
        'subscriber_user_nick': {'type': 'String', 'is_list': False},
        'wlb_partner_address': {'type': 'WlbPartnerAddress', 'is_list': False},
        'wlb_partner_contact': {'type': 'WlbPartnerContact', 'is_list': False}
    }


class PicUrl(TOPObject):
    """ 图片链接

    @field url(String): 图片链接地址
    """
    FIELDS = {
        'url': {'type': 'String', 'is_list': False}
    }


class WlbItemInventoryLog(TOPObject):
    """ 库存变更记录

    @field batch_code(String): 批次号
    @field gmt_create(Date): 创建日期
    @field id(Number): 库存变更ID
    @field invent_type(String): VENDIBLE  1-可销售;
        FREEZE  201-冻结库存;
        ONWAY  301-在途库存;
        DEFECT  101-残存品;
        ENGINE_DAMAGE 102-机损;
        BOX_DAMAGE 103-箱损
    @field item_id(Number): 商品ID
    @field op_type(String): 库存操作作类型
        CHU_KU 1-出库
        RU_KU 2-入库
        FREEZE 3-冻结
        THAW 4-解冻
        CHECK_FREEZE 5-冻结确认
        CHANGE_KU 6-库存类型变更
    @field op_user_id(Number): 库存操作者ID
    @field order_code(String): 订单号
    @field order_item_id(Number): 订单商品ID
    @field quantity(Number): 处理数量变化值
    @field remark(String): 备注
    @field result_quantity(Number): 结果值
    @field store_code(String): 仓库编码
    @field user_id(Number): 用户ID
    """
    FIELDS = {
        'batch_code': {'type': 'String', 'is_list': False},
        'gmt_create': {'type': 'Date', 'is_list': False},
        'id': {'type': 'Number', 'is_list': False},
        'invent_type': {'type': 'String', 'is_list': False},
        'item_id': {'type': 'Number', 'is_list': False},
        'op_type': {'type': 'String', 'is_list': False},
        'op_user_id': {'type': 'Number', 'is_list': False},
        'order_code': {'type': 'String', 'is_list': False},
        'order_item_id': {'type': 'Number', 'is_list': False},
        'quantity': {'type': 'Number', 'is_list': False},
        'remark': {'type': 'String', 'is_list': False},
        'result_quantity': {'type': 'Number', 'is_list': False},
        'store_code': {'type': 'String', 'is_list': False},
        'user_id': {'type': 'Number', 'is_list': False}
    }


class OutEntityItem(TOPObject):
    """ 外部商品实体

    @field entity_id(String): entity_type对应的实体类型的id：
        当entity_type为IC_ITEM时，entity_id为ic的商品id
    @field entity_type(String): 外部实体类型：
        IC_ITEM--ic商品
        IC_SKU--ic销售单元
    """
    FIELDS = {
        'entity_id': {'type': 'String', 'is_list': False},
        'entity_type': {'type': 'String', 'is_list': False}
    }


class Subtask(TOPObject):
    """ 批量异步任务的子任务结果

    @field is_success(Boolean): 标记子任务是否成功。为true表示子任务成功，用户可以按照正确执行的结果格式解析sub_task_result。为false表示子任务失败了，用户需要按照失败的结果格式解析sub_task_result（里面只有sub_code和sub_msg）
    @field sub_task_request(String): 子任务的有效请求参数，以json格式进行key:value的组合
    @field sub_task_result(String): 子任务返回的结果，以json格式进行key:value组合，可以和单个api请求结果解析复用。以获取交易订单详情为例：子任务执行成功返回的结果格式为：{“trade”:{"tid":123456,"seller_nick":"淘宝卖家"}}；子任务执行失败结果格式为{"sub_code":"isv.trade-not-exist","sub_msg":"交易订单不存在"}
    """
    FIELDS = {
        'is_success': {'type': 'Boolean', 'is_list': False},
        'sub_task_request': {'type': 'String', 'is_list': False},
        'sub_task_result': {'type': 'String', 'is_list': False}
    }


class WlbOrderScheduleRule(TOPObject):
    """ 订单调度规则

    @field area_ids(String): 收货地址范围: 6位数的地址ID，用逗号分隔。如“140400,230500”。同一个卖家的订单调度规则中，设置的收货地址范围不能重复。
    @field backup_store_id(Number): 备用配送中心ID
    @field default_store_id(Number): 默认配送中心ID
    @field id(Number): 订单调度规则ID
    @field options(String): 发货规则的额外规则设置： 允许组合，用逗号隔开.
        REMARK_STOP--有订单留言不自动下发;
        COD_STOP--货到付款订单不自动下发;
        CHECK_WAREHOUSE_DELIVER--检查仓库的配送范围
    @field presell_store_id(Number): 预售配送中心ID（预留，暂未使用）
    @field rule_id(Number): wlb_base_rule表的ID
    @field user_id(Number): 商家userId
    @field user_nick(String): 商品userNick
    """
    FIELDS = {
        'area_ids': {'type': 'String', 'is_list': False},
        'backup_store_id': {'type': 'Number', 'is_list': False},
        'default_store_id': {'type': 'Number', 'is_list': False},
        'id': {'type': 'Number', 'is_list': False},
        'options': {'type': 'String', 'is_list': False},
        'presell_store_id': {'type': 'Number', 'is_list': False},
        'rule_id': {'type': 'Number', 'is_list': False},
        'user_id': {'type': 'Number', 'is_list': False},
        'user_nick': {'type': 'String', 'is_list': False}
    }


class ReplyStatOnDay(TOPObject):
    """ (某天)回复统计列表

    @field reply_date(Date): 某天（的回复统计）
    @field reply_stat_by_ids(ReplyStatById, list): 客服回复统计
    """
    FIELDS = {
        'reply_date': {'type': 'Date', 'is_list': False},
        'reply_stat_by_ids': {'type': 'ReplyStatById', 'is_list': True}
    }


class WlbTmsOrder(TOPObject):
    """ 物流订单运单信息

    @field code(String): 运单号
    @field company_code(String): 物流公司编码
    @field order_code(String): 物流订单编号
    @field user_id(Number): 物流订单的所有者ID,货主
    """
    FIELDS = {
        'code': {'type': 'String', 'is_list': False},
        'company_code': {'type': 'String', 'is_list': False},
        'order_code': {'type': 'String', 'is_list': False},
        'user_id': {'type': 'Number', 'is_list': False}
    }


class ArticleUserSubscribe(TOPObject):
    """ 用户订购信息

    @field deadline(Date): 订购关系到期时间
    @field item_code(String): 收费项目代码，从合作伙伴后台（my.open.taobao.com）-收费管理-收费项目列表 能够获得收费项目代码
    """
    FIELDS = {
        'deadline': {'type': 'Date', 'is_list': False},
        'item_code': {'type': 'String', 'is_list': False}
    }


class ArticleBizOrder(TOPObject):
    """ 应用订单信息

    @field article_code(String): 应用收费代码，从合作伙伴后台（my.open.taobao.com）-收费管理-收费项目列表 能够获得该应用的收费代码
    @field article_name(String): 应用名称
    @field biz_order_id(Number): 订单号
    @field biz_type(Number): 订单类型，1=新订 2=续订 3=升级 4=后台赠送 5=后台自动续订 6=订单审核后生成订购关系（暂时用不到）
    @field create(Date): 订单创建时间（订购时间）
    @field fee(String): 原价（单位为分）
    @field item_code(String): 收费项目代码，从合作伙伴后台（my.open.taobao.com）-收费管理-收费项目列表 能够获得收费项目代码
    @field item_name(String): 收费项目名称
    @field nick(String): 淘宝会员名
    @field order_cycle(String): 订购周期
    @field order_cycle_end(Date): 订购周期结束时间
    @field order_cycle_start(Date): 订购周期开始时间
    @field order_id(Number): 子订单号
    @field prom_fee(String): 优惠（单位为分）
    @field refund_fee(String): 退款（单位为分；升级时，系统会将升级前老版本按照剩余订购天数退还剩余金额）
    @field total_pay_fee(String): 实付（单位为分）
    """
    FIELDS = {
        'article_code': {'type': 'String', 'is_list': False},
        'article_name': {'type': 'String', 'is_list': False},
        'biz_order_id': {'type': 'Number', 'is_list': False},
        'biz_type': {'type': 'Number', 'is_list': False},
        'create': {'type': 'Date', 'is_list': False},
        'fee': {'type': 'String', 'is_list': False},
        'item_code': {'type': 'String', 'is_list': False},
        'item_name': {'type': 'String', 'is_list': False},
        'nick': {'type': 'String', 'is_list': False},
        'order_cycle': {'type': 'String', 'is_list': False},
        'order_cycle_end': {'type': 'Date', 'is_list': False},
        'order_cycle_start': {'type': 'Date', 'is_list': False},
        'order_id': {'type': 'Number', 'is_list': False},
        'prom_fee': {'type': 'String', 'is_list': False},
        'refund_fee': {'type': 'String', 'is_list': False},
        'total_pay_fee': {'type': 'String', 'is_list': False}
    }


class FenxiaoGrade(TOPObject):
    """ 分销商等级

    @field created(Date): 记录创建时间
    @field grade_id(Number): 主键
    @field modified(Date): 记录最后修改时间
    @field name(String): 分销商等级名称
    """
    FIELDS = {
        'created': {'type': 'Date', 'is_list': False},
        'grade_id': {'type': 'Number', 'is_list': False},
        'modified': {'type': 'Date', 'is_list': False},
        'name': {'type': 'String', 'is_list': False}
    }


class PromotionDetail(TOPObject):
    """ 交易的优惠信息详情

    @field discount_fee(Price): 优惠金额（免运费、限时打折时为空）,单位：元
    @field gift_item_id(String): 赠品的宝贝id
    @field gift_item_name(String): 满就送商品时，所送商品的名称
    @field gift_item_num(String): 满就送礼物的礼物数量
    @field id(Number): 交易的主订单或子订单号
    @field promotion_desc(String): 优惠活动的描述
    @field promotion_id(String): 优惠id，(由营销工具id、优惠活动id和优惠详情id组成，结构为：营销工具id-优惠活动id_优惠详情id，如mjs-123024_211143）
    @field promotion_name(String): 优惠信息的名称
    """
    FIELDS = {
        'discount_fee': {'type': 'Price', 'is_list': False},
        'gift_item_id': {'type': 'String', 'is_list': False},
        'gift_item_name': {'type': 'String', 'is_list': False},
        'gift_item_num': {'type': 'String', 'is_list': False},
        'id': {'type': 'Number', 'is_list': False},
        'promotion_desc': {'type': 'String', 'is_list': False},
        'promotion_id': {'type': 'String', 'is_list': False},
        'promotion_name': {'type': 'String', 'is_list': False}
    }


class KfcSearchResult(TOPObject):
    """ KFC 关键词过滤匹配结果

    @field content(String): 过滤后的文本：
        当匹配到B等级的词时，文本中的关键词被替换为*号，content即为关键词替换后的文本；
        其他情况，content始终为null
    @field level(String): 匹配到的关键词的等级，值为null，或为A、B、C、D。
        当匹配不到关键词时，值为null，否则值为A、B、C、D中的一个。
        A、B、C、D等级按严重程度从高至低排列。
    @field matched(Boolean): 是否匹配到关键词,匹配到则为true.
    """
    FIELDS = {
        'content': {'type': 'String', 'is_list': False},
        'level': {'type': 'String', 'is_list': False},
        'matched': {'type': 'Boolean', 'is_list': False}
    }


class WlbPartnerContact(TOPObject):
    """ 联系人联系详情

    @field name(String): 仓库联系人姓名
    @field phone(String): 联系电话
    """
    FIELDS = {
        'name': {'type': 'String', 'is_list': False},
        'phone': {'type': 'String', 'is_list': False}
    }


class WlbPartnerAddress(TOPObject):
    """ 联系人地址信息

    @field address(String): 详细地址
    @field borough(String): 区
    @field city(String): 市
    @field province(String): 省
    @field zip(String): 邮编
    """
    FIELDS = {
        'address': {'type': 'String', 'is_list': False},
        'borough': {'type': 'String', 'is_list': False},
        'city': {'type': 'String', 'is_list': False},
        'province': {'type': 'String', 'is_list': False},
        'zip': {'type': 'String', 'is_list': False}
    }


class Meal(TOPObject):
    """ 搭配套餐类。

    @field item_list(String): 搭配套餐商品列表。item_id为商品的id;item_show_name为商品显示名。因最多允许5个商品进行搭配，所以查询最多有5个，以json格式传出。
    @field meal_id(Number): 套餐id。
    @field meal_memo(String): 搭配套餐描述！
    @field meal_name(String): 搭配套餐名称。
    @field meal_price(Price): 套餐一口价(单位是：分)
    @field postage_id(Number): 普通运费模板id。若这个字段为空或0时，运费是卖家负责;若这个字段不为空，说明运费模板存在，运费是买家负责。
    @field status(String): 套餐状态。有效：VALID;失效：INVALID(有效套餐为可使用的套餐,无效套餐为套餐中有商品下架或库存为0时)。
    """
    FIELDS = {
        'item_list': {'type': 'String', 'is_list': False},
        'meal_id': {'type': 'Number', 'is_list': False},
        'meal_memo': {'type': 'String', 'is_list': False},
        'meal_name': {'type': 'String', 'is_list': False},
        'meal_price': {'type': 'Price', 'is_list': False},
        'postage_id': {'type': 'Number', 'is_list': False},
        'status': {'type': 'String', 'is_list': False}
    }


class PosterGoodsInfo(TOPObject):
    """ 与对应画报相关联的商品的信息

    @field note(String): 商品描述信息
    @field num_id(Number): 商品id
    @field pic_id(Number): 图片id
    @field poster_id(Number): 画报id
    @field price(Price): 商品价格
    @field short_title(String): 商品短标题
    @field title(String): 商品标题
    @field url(String): 手机上相应购买地址
    """
    FIELDS = {
        'note': {'type': 'String', 'is_list': False},
        'num_id': {'type': 'Number', 'is_list': False},
        'pic_id': {'type': 'Number', 'is_list': False},
        'poster_id': {'type': 'Number', 'is_list': False},
        'price': {'type': 'Price', 'is_list': False},
        'short_title': {'type': 'String', 'is_list': False},
        'title': {'type': 'String', 'is_list': False},
        'url': {'type': 'String', 'is_list': False}
    }


class ArticleSub(TOPObject):
    """ 应用订购信息

    @field article_code(String): 应用收费代码，从合作伙伴后台（my.open.taobao.com）-收费管理-收费项目列表 能够获得该应用的收费代码
    @field article_name(String): 应用名称
    @field autosub(Boolean): 是否自动续费
    @field deadline(Date): 订购关系到期时间
    @field expire_notice(Boolean): 是否到期提醒
    @field item_code(String): 收费项目代码，从合作伙伴后台（my.open.taobao.com）-收费管理-收费项目列表 能够获得收费项目代码
    @field item_name(String): 收费项目名称
    @field nick(String): 淘宝会员名
    @field status(Number): 状态，1=有效 2=过期
    """
    FIELDS = {
        'article_code': {'type': 'String', 'is_list': False},
        'article_name': {'type': 'String', 'is_list': False},
        'autosub': {'type': 'Boolean', 'is_list': False},
        'deadline': {'type': 'Date', 'is_list': False},
        'expire_notice': {'type': 'Boolean', 'is_list': False},
        'item_code': {'type': 'String', 'is_list': False},
        'item_name': {'type': 'String', 'is_list': False},
        'nick': {'type': 'String', 'is_list': False},
        'status': {'type': 'Number', 'is_list': False}
    }


class GroupMember(TOPObject):
    """ 组及其成员列表

    @field group_id(Number): 组编号
    @field group_name(String): 组名称
    @field member_list(String): 组成员列表，逗号分隔
    """
    FIELDS = {
        'group_id': {'type': 'Number', 'is_list': False},
        'group_name': {'type': 'String', 'is_list': False},
        'member_list': {'type': 'String', 'is_list': False}
    }


class Room(TOPObject):
    """ Room（酒店商品）结构。各字段详细说明可参考接口定义，如：商品发布接口。

    @field area(String): 面积
    @field bbn(String): 宽带服务
    @field bed_type(String): 床型
    @field breakfast(String): 早餐
    @field created(Date): 创建时间
    @field deposit(Number): 订金
    @field desc(String): 商品描述
    @field fee(Number): 手续费
    @field gid(Number): 酒店商品id
    @field guide(String): 购买须知
    @field hid(Number): 酒店id
    @field hotel(Hotel): 酒店信息
    @field iid(Number): 淘宝商品id
    @field modified(Date): 修改时间
    @field payment_type(String): 支付类型
    @field pic_url(String): 酒店商品图片Url。多个url用逗号隔开
    @field price_type(String): 价格类型
    @field rid(Number): 房型id
    @field room_quotas(String): 房态信息。JSON格式串
    @field room_type(RoomType): 房型信息
    @field service(String): 设施服务。JSON格式串
    @field size(String): 床宽
    @field status(Number): 状态。1：上架。2：下架。3：删除
    @field storey(String): 楼层
    @field title(String): 酒店商品名称
    """
    FIELDS = {
        'area': {'type': 'String', 'is_list': False},
        'bbn': {'type': 'String', 'is_list': False},
        'bed_type': {'type': 'String', 'is_list': False},
        'breakfast': {'type': 'String', 'is_list': False},
        'created': {'type': 'Date', 'is_list': False},
        'deposit': {'type': 'Number', 'is_list': False},
        'desc': {'type': 'String', 'is_list': False},
        'fee': {'type': 'Number', 'is_list': False},
        'gid': {'type': 'Number', 'is_list': False},
        'guide': {'type': 'String', 'is_list': False},
        'hid': {'type': 'Number', 'is_list': False},
        'hotel': {'type': 'Hotel', 'is_list': False},
        'iid': {'type': 'Number', 'is_list': False},
        'modified': {'type': 'Date', 'is_list': False},
        'payment_type': {'type': 'String', 'is_list': False},
        'pic_url': {'type': 'String', 'is_list': False},
        'price_type': {'type': 'String', 'is_list': False},
        'rid': {'type': 'Number', 'is_list': False},
        'room_quotas': {'type': 'String', 'is_list': False},
        'room_type': {'type': 'RoomType', 'is_list': False},
        'service': {'type': 'String', 'is_list': False},
        'size': {'type': 'String', 'is_list': False},
        'status': {'type': 'Number', 'is_list': False},
        'storey': {'type': 'String', 'is_list': False},
        'title': {'type': 'String', 'is_list': False}
    }


class HotelOrder(TOPObject):
    """ HotelOrder（酒店订单）结构。各字段详细说明可参考接口定义。注意：trade_status，refund_status，logistics_status不是严格准确的，请以交易API，物流API等得到的订单状态、物流状态为准确依据。

    @field alipay_trade_no(String): 支付宝交易号，22位字符
    @field buyer_nick(String): 买家淘宝账号
    @field checkin_date(Date): 入住时间
    @field checkout_date(Date): 离店时间
    @field contact_name(String): 联系人姓名
    @field contact_phone(String): 联系人电话
    @field contact_phone_bak(String): 备用联系人电话
    @field created(Date): 订单创建时间
    @field end_time(Date): 结束时间
    @field gid(Number): 商品id
    @field guests(OrderGuest, list): 入住人信息
    @field hid(Number): 酒店id
    @field logistics_status(String): 物流状态。STATUS_UNCONSIGNED：未发货 -> 等待卖家发货。STATUS_CONSIGNED：已发货 -> 等待买家确认收货。STATUS_DELIVERED：已收货 -> 交易成功。STATUS_REVERT：已经退货 -> 交易失败。STATUS_DELIVERED_PART：部分发货 -> 交易成功。STATUS_NO_OUT_ORDER：还未创建物流订单
    @field message(String): 买家留言
    @field modified(Date): 订单修改时间
    @field nights(Number): 天数
    @field oid(Number): 酒店订单id
    @field pay_time(Date): 付款时间
    @field payment(Number): 实付款（分）
    @field refund_status(String): 退款状态。STATUS_WAIT_SELLER_AGREE：买家已经申请退款，等待卖家同意。STATUS_WAIT_BUYER_RETURN_GOODS：卖家已经同意退款，等待买家退货。STATUS_WAIT_SELLER_CONFIRM_GOODS：买家已经退货，等待卖家确认收货。STATUS_CLOSED：退款关闭。STATUS_SUCCESS：退款成功。STATUS_SELLER_REFUSE_BUYER：卖家拒绝退款。STATUS_WAIT_OUT_PAY_SYSTEM_REFUND：等待外部交易系统退款。STATUS_NO_REFUND：没有申请退款。STATUS_ACTIVE_REFUND：有活动退款。STATUS_END_REFUND：退款结束。
    @field rid(Number): 房型id
    @field room_number(Number): 房间数
    @field seller_nick(String): 卖家淘宝账号
    @field tid(Number): 淘宝订单id
    @field total_room_price(Number): 总房价（分）
    @field trade_status(String): 交易状态。WAIT_BUYER_PAY：未冻结/未付款 -> 等待买家付款。WAIT_SELLER_SEND_GOODS：已冻结/已付款 -> 等待卖家发货。TRADE_CLOSED：已退款 -> 交易关闭。TRADE_FINISHED：已转交易 -> 交易成功。TRADE_NO_CREATE_PAY：没有创建支付宝交易。TRADE_CLOSED_BY_TAOBAO：交易被淘宝关闭
    @field type(String): 支付类型。A：全额支付。B：灵活支付－手续费。C：灵活支付－订金。D：灵活支付－手续费/间夜
    """
    FIELDS = {
        'alipay_trade_no': {'type': 'String', 'is_list': False},
        'buyer_nick': {'type': 'String', 'is_list': False},
        'checkin_date': {'type': 'Date', 'is_list': False},
        'checkout_date': {'type': 'Date', 'is_list': False},
        'contact_name': {'type': 'String', 'is_list': False},
        'contact_phone': {'type': 'String', 'is_list': False},
        'contact_phone_bak': {'type': 'String', 'is_list': False},
        'created': {'type': 'Date', 'is_list': False},
        'end_time': {'type': 'Date', 'is_list': False},
        'gid': {'type': 'Number', 'is_list': False},
        'guests': {'type': 'OrderGuest', 'is_list': True},
        'hid': {'type': 'Number', 'is_list': False},
        'logistics_status': {'type': 'String', 'is_list': False},
        'message': {'type': 'String', 'is_list': False},
        'modified': {'type': 'Date', 'is_list': False},
        'nights': {'type': 'Number', 'is_list': False},
        'oid': {'type': 'Number', 'is_list': False},
        'pay_time': {'type': 'Date', 'is_list': False},
        'payment': {'type': 'Number', 'is_list': False},
        'refund_status': {'type': 'String', 'is_list': False},
        'rid': {'type': 'Number', 'is_list': False},
        'room_number': {'type': 'Number', 'is_list': False},
        'seller_nick': {'type': 'String', 'is_list': False},
        'tid': {'type': 'Number', 'is_list': False},
        'total_room_price': {'type': 'Number', 'is_list': False},
        'trade_status': {'type': 'String', 'is_list': False},
        'type': {'type': 'String', 'is_list': False}
    }


class TaohuaAudioReaderTrack(TOPObject):
    """ 有声读物单曲信息

    @field duration(String): 单曲时长
    @field item_id(Number): 单曲ID
    @field last_updated(String): 单曲更新日期
    @field price(Price): 单曲价格
    @field title(String): 单曲名称
    """
    FIELDS = {
        'duration': {'type': 'String', 'is_list': False},
        'item_id': {'type': 'Number', 'is_list': False},
        'last_updated': {'type': 'String', 'is_list': False},
        'price': {'type': 'Price', 'is_list': False},
        'title': {'type': 'String', 'is_list': False}
    }


class TaohuaAudioReaderAlbumSummary(TOPObject):
    """ 有声读物专辑摘要

    @field copyright(String): 版权所属
    @field item_id(Number): 专辑ID
    @field last_updated(String): 最后更新日期
    @field pic_url(String): 专辑封面图片url
    @field price(Price): 价格
    @field status(String): 商品状态
    @field title(String): 专辑名称
    @field track_count(Number): 集数
    """
    FIELDS = {
        'copyright': {'type': 'String', 'is_list': False},
        'item_id': {'type': 'Number', 'is_list': False},
        'last_updated': {'type': 'String', 'is_list': False},
        'pic_url': {'type': 'String', 'is_list': False},
        'price': {'type': 'Price', 'is_list': False},
        'status': {'type': 'String', 'is_list': False},
        'title': {'type': 'String', 'is_list': False},
        'track_count': {'type': 'Number', 'is_list': False}
    }


class TaohuaAudioReaderAlbum(TOPObject):
    """ 有声读物专辑信息

    @field artist_name(String): 播音员名称
    @field bit_rate(String): 码流
    @field copyright(String): 版权所属
    @field description(String): 专辑简介
    @field duration(String): 时长
    @field format(String): 格式
    @field item_id(Number): 专辑ID
    @field last_updated(String): 专辑最后更新日期
    @field pic_url(String): 专辑封面图片url
    @field price(Price): 价格
    @field status(String): 专辑状态
    @field title(String): 专辑名称
    @field track_count(Number): 集数
    """
    FIELDS = {
        'artist_name': {'type': 'String', 'is_list': False},
        'bit_rate': {'type': 'String', 'is_list': False},
        'copyright': {'type': 'String', 'is_list': False},
        'description': {'type': 'String', 'is_list': False},
        'duration': {'type': 'String', 'is_list': False},
        'format': {'type': 'String', 'is_list': False},
        'item_id': {'type': 'Number', 'is_list': False},
        'last_updated': {'type': 'String', 'is_list': False},
        'pic_url': {'type': 'String', 'is_list': False},
        'price': {'type': 'Price', 'is_list': False},
        'status': {'type': 'String', 'is_list': False},
        'title': {'type': 'String', 'is_list': False},
        'track_count': {'type': 'Number', 'is_list': False}
    }


class ItemTemplate(TOPObject):
    """ 宝贝详情页面信息

    @field shop_type(Number): 用于区分宝贝模板属于内店和外店
    @field template_id(Number): 宝贝模板的id
    @field template_name(String): 宝贝详情模板的名称
    """
    FIELDS = {
        'shop_type': {'type': 'Number', 'is_list': False},
        'template_id': {'type': 'Number', 'is_list': False},
        'template_name': {'type': 'String', 'is_list': False}
    }


class Hotel(TOPObject):
    """ Hotel（酒店）结构。各字段详细说明可参考接口定义，如：酒店发布接口。

    @field address(String): 酒店地址
    @field alias_name(String): 某个卖家发布的酒店的别名
    @field city(Number): 城市编码
    @field city_str(String): 城市中文名称
    @field country(String): 国家编码
    @field country_str(String): 国家中文名称
    @field created(Date): 创建时间
    @field decorate_time(String): 装修时间
    @field desc(String): 酒店介绍
    @field district(Number): 区域编码
    @field district_str(String): 区域中文名称
    @field hid(Number): 酒店id
    @field level(String): 酒店级别
    @field modified(Date): 修改时间
    @field name(String): 酒店名称
    @field opening_time(String): 开业时间
    @field orientation(String): 酒店定位
    @field pic_url(String): 酒店图片url
    @field province(Number): 省份编码
    @field province_str(String): 省份中文名称
    @field room_types(RoomType, list): 房型列表
    @field rooms(Number): 房间数
    @field service(String): 交通距离与设施服务。JSON格式串。
    @field status(Number): 状态。0：待审核，1：正常（审核通过），2：审核否决，3：停售
    @field storeys(Number): 楼层数
    @field tel(String): 酒店电话
    """
    FIELDS = {
        'address': {'type': 'String', 'is_list': False},
        'alias_name': {'type': 'String', 'is_list': False},
        'city': {'type': 'Number', 'is_list': False},
        'city_str': {'type': 'String', 'is_list': False},
        'country': {'type': 'String', 'is_list': False},
        'country_str': {'type': 'String', 'is_list': False},
        'created': {'type': 'Date', 'is_list': False},
        'decorate_time': {'type': 'String', 'is_list': False},
        'desc': {'type': 'String', 'is_list': False},
        'district': {'type': 'Number', 'is_list': False},
        'district_str': {'type': 'String', 'is_list': False},
        'hid': {'type': 'Number', 'is_list': False},
        'level': {'type': 'String', 'is_list': False},
        'modified': {'type': 'Date', 'is_list': False},
        'name': {'type': 'String', 'is_list': False},
        'opening_time': {'type': 'String', 'is_list': False},
        'orientation': {'type': 'String', 'is_list': False},
        'pic_url': {'type': 'String', 'is_list': False},
        'province': {'type': 'Number', 'is_list': False},
        'province_str': {'type': 'String', 'is_list': False},
        'room_types': {'type': 'RoomType', 'is_list': True},
        'rooms': {'type': 'Number', 'is_list': False},
        'service': {'type': 'String', 'is_list': False},
        'status': {'type': 'Number', 'is_list': False},
        'storeys': {'type': 'Number', 'is_list': False},
        'tel': {'type': 'String', 'is_list': False}
    }


class FenxiaoItemRecord(TOPObject):
    """ 分销商品下载记录

    @field created(Date): 下载时间
    @field distributor_id(Number): 分销商ID
    @field item_id(Number): 商品ID
    @field modified(Date): 更新时间
    @field product_id(Number): 产品ID
    @field trade_type(String): 分销方式：AGENT（只做代销，默认值）、DEALER（只做经销）
    """
    FIELDS = {
        'created': {'type': 'Date', 'is_list': False},
        'distributor_id': {'type': 'Number', 'is_list': False},
        'item_id': {'type': 'Number', 'is_list': False},
        'modified': {'type': 'Date', 'is_list': False},
        'product_id': {'type': 'Number', 'is_list': False},
        'trade_type': {'type': 'String', 'is_list': False}
    }


class Cooperation(TOPObject):
    """ 合作分销关系

    @field auth_payway(String, list): 供应商授权的支付方式：ALIPAY(支付宝)、OFFPREPAY(预付款)、OFFTRANSFER(转帐)、OFFSETTLEMENT(后期结算)
    @field cooperate_id(Number): 合作关系ID
    @field distributor_id(Number): 分销商ID
    @field distributor_nick(String): 分销商nick
    @field end_date(Date): 合作终止时间
    @field grade_id(Number): 等级ID
    @field product_line(String): 授权产品线
    @field start_date(Date): 合作起始时间
    @field status(String): NORMAL END ENDING
    @field supplier_id(Number): 供应商ID
    @field supplier_nick(String): 供应商NICK
    @field trade_type(String): 分销方式： AGENT(代销) 、DEALER(经销)
    """
    FIELDS = {
        'auth_payway': {'type': 'String', 'is_list': True},
        'cooperate_id': {'type': 'Number', 'is_list': False},
        'distributor_id': {'type': 'Number', 'is_list': False},
        'distributor_nick': {'type': 'String', 'is_list': False},
        'end_date': {'type': 'Date', 'is_list': False},
        'grade_id': {'type': 'Number', 'is_list': False},
        'product_line': {'type': 'String', 'is_list': False},
        'start_date': {'type': 'Date', 'is_list': False},
        'status': {'type': 'String', 'is_list': False},
        'supplier_id': {'type': 'Number', 'is_list': False},
        'supplier_nick': {'type': 'String', 'is_list': False},
        'trade_type': {'type': 'String', 'is_list': False}
    }


class LimitDiscount(TOPObject):
    """ 限时打折

    @field end_time(Date): 限时打折结束时间。
    @field item_num(Number): 该限时打折宝贝数量。
    @field limit_discount_id(Number): 限时打折ID。
    @field limit_discount_name(String): 限时打折名称。
    @field start_time(Date): 限时打折开始时间。
    """
    FIELDS = {
        'end_time': {'type': 'Date', 'is_list': False},
        'item_num': {'type': 'Number', 'is_list': False},
        'limit_discount_id': {'type': 'Number', 'is_list': False},
        'limit_discount_name': {'type': 'String', 'is_list': False},
        'start_time': {'type': 'Date', 'is_list': False}
    }


class RoomType(TOPObject):
    """ RoomType（房型）结构。各字段详细说明可参考接口定义，如：房型发布接口。

    @field alias_name(String): 某卖家提供的房型别名
    @field created(Date): 创建时间
    @field hid(Number): 酒店id
    @field modified(Date): 修改时间
    @field name(String): 房型名称
    @field rid(Number): 房型id
    @field status(Number): 状态。0：待审核，1：正常（审核通过），2：审核否决，3：停售
    """
    FIELDS = {
        'alias_name': {'type': 'String', 'is_list': False},
        'created': {'type': 'Date', 'is_list': False},
        'hid': {'type': 'Number', 'is_list': False},
        'modified': {'type': 'Date', 'is_list': False},
        'name': {'type': 'String', 'is_list': False},
        'rid': {'type': 'Number', 'is_list': False},
        'status': {'type': 'Number', 'is_list': False}
    }


class AddressResult(TOPObject):
    """ 地址库返回数据信息

    @field addr(String): 详细街道地址，不需要重复填写省/市/区
    @field area_id(Number): 区域ID
    @field cancel_def(Boolean): 是否默认退货地址
    @field city(String): 市
    @field contact_id(Number): 地址库ID
    @field contact_name(String): 联系人姓名
    @field country(String): 区、县
    @field get_def(Boolean): 是否默认取货地址
    @field memo(String): 备注
    @field mobile_phone(String): 手机号码，手机与电话必需有一个
        手机号码不能超过20位
    @field modify_date(Date): 修改日期时间
    @field phone(String): 电话号码,手机与电话必需有一个
    @field province(String): 省
    @field seller_company(String): 公司名称,
    @field send_def(Boolean): 是否默认发货地址
    @field zip_code(String): 地区邮政编码
    """
    FIELDS = {
        'addr': {'type': 'String', 'is_list': False},
        'area_id': {'type': 'Number', 'is_list': False},
        'cancel_def': {'type': 'Boolean', 'is_list': False},
        'city': {'type': 'String', 'is_list': False},
        'contact_id': {'type': 'Number', 'is_list': False},
        'contact_name': {'type': 'String', 'is_list': False},
        'country': {'type': 'String', 'is_list': False},
        'get_def': {'type': 'Boolean', 'is_list': False},
        'memo': {'type': 'String', 'is_list': False},
        'mobile_phone': {'type': 'String', 'is_list': False},
        'modify_date': {'type': 'Date', 'is_list': False},
        'phone': {'type': 'String', 'is_list': False},
        'province': {'type': 'String', 'is_list': False},
        'seller_company': {'type': 'String', 'is_list': False},
        'send_def': {'type': 'Boolean', 'is_list': False},
        'zip_code': {'type': 'String', 'is_list': False}
    }


class OrderGuest(TOPObject):
    """ 酒店订单入住人结构。

    @field name(String): 入住人姓名
    @field oid(Number): 酒店订单id
    @field person_pos(Number): 入住人序号
    @field room_pos(Number): 房间序号
    @field tel(String): 入住人电话
    """
    FIELDS = {
        'name': {'type': 'String', 'is_list': False},
        'oid': {'type': 'Number', 'is_list': False},
        'person_pos': {'type': 'Number', 'is_list': False},
        'room_pos': {'type': 'Number', 'is_list': False},
        'tel': {'type': 'String', 'is_list': False}
    }


class RoomImage(TOPObject):
    """ RoomImage（酒店图片）结构。各字段详细说明可参考接口定义，如：商品图片上传接口。

    @field all_images(String): 商品所有图片的url，用”,”隔开。即，当前该商品的所有图片地址。
    @field gid(Number): 酒店商品id
    @field image(String): 图片url。当前接口操作的图片url。调用上传图片接口时，代表上传图片后得到的图片url。调用删除图片接口时，代表被删除掉的图片url。
    @field position(Number): 图片位置，可选值：1,2,3,4,5。代表图片的位置，如：2，代表第二张图片。
    """
    FIELDS = {
        'all_images': {'type': 'String', 'is_list': False},
        'gid': {'type': 'Number', 'is_list': False},
        'image': {'type': 'String', 'is_list': False},
        'position': {'type': 'Number', 'is_list': False}
    }


class LimitDiscountDetail(TOPObject):
    """ 限时打折详情

    @field end_time(Date): 限时打折结束时间。
    @field item_discount(Price): 该商品限时折扣
    @field item_id(Number): 商品的id(数字类型)
    @field limit_discount_name(String): 限时打折名称
    @field limit_num(Number): 每人限购数量，1、2、5、10000(不限)。
    @field start_time(Date): 限时打折开始时间。
    """
    FIELDS = {
        'end_time': {'type': 'Date', 'is_list': False},
        'item_discount': {'type': 'Price', 'is_list': False},
        'item_id': {'type': 'Number', 'is_list': False},
        'limit_discount_name': {'type': 'String', 'is_list': False},
        'limit_num': {'type': 'Number', 'is_list': False},
        'start_time': {'type': 'Date', 'is_list': False}
    }


class TaohuaSearchItems(TOPObject):
    """ 淘花商品列表

    @field cate_paths(TaohuaCategory, list): 淘花类目路径数据结构
    @field cate_stats(TaohuaCateStat, list): 搜索引擎根据搜索条件中的上一级类目统计出的子类目列表
    @field taohua_search_items(TaohuaSearchItem, list): 淘花搜索商品对象列表数据结构
    @field total_item(Number): 搜索出来的商品总数
    """
    FIELDS = {
        'cate_paths': {'type': 'TaohuaCategory', 'is_list': True},
        'cate_stats': {'type': 'TaohuaCateStat', 'is_list': True},
        'taohua_search_items': {'type': 'TaohuaSearchItem', 'is_list': True},
        'total_item': {'type': 'Number', 'is_list': False}
    }


class TaohuaItemPVPair(TOPObject):
    """ 商品属性值配对数据结构

    @field taohua_cate_prop(TaohuaCateProp): 淘花类目属性数据结构
    @field taohua_cate_prop_values(TaohuaCatePropValue, list): 淘花类目属性值数据结构
    """
    FIELDS = {
        'taohua_cate_prop': {'type': 'TaohuaCateProp', 'is_list': False},
        'taohua_cate_prop_values': {'type': 'TaohuaCatePropValue', 'is_list': True}
    }


class Role(TOPObject):
    """ 子账号角色

    @field create_time(Date): 创建时间
    @field description(String): 角色描述
    @field modified_time(Date): 修改时间
    @field permissions(Permission, list): 所拥有权限
    @field role_id(Number): 角色id
    @field role_name(String): 角色名
    @field seller_id(Number): 卖家Id
    """
    FIELDS = {
        'create_time': {'type': 'Date', 'is_list': False},
        'description': {'type': 'String', 'is_list': False},
        'modified_time': {'type': 'Date', 'is_list': False},
        'permissions': {'type': 'Permission', 'is_list': True},
        'role_id': {'type': 'Number', 'is_list': False},
        'role_name': {'type': 'String', 'is_list': False},
        'seller_id': {'type': 'Number', 'is_list': False}
    }


class TaohuaSearchItem(TOPObject):
    """ 淘花搜索商品对象数据结构

    @field author(String): 描述图书作者
    @field description(String): 商品描述信息
    @field doc_pages(Number): 文档总页数
    @field favorite(Number): 描述用户对某一商品的喜欢程度，值越大，则表示越喜欢
    @field item_id(Number): 商品ID
    @field pic_url(String): 商品图片链接
    @field price(Price): 商品价格，单位：分
    @field publish_date(String): 描述图书出版日期
    @field publisher(String): 描述商品的出版社信息
    @field root_cate_id(Number): 根类目ID
    @field sell_count(Number): 销量
    @field seller_id(Number): 淘花卖家的编号，注意：不是淘宝会员的编号。
    @field seller_nick(String): 卖家的淘宝nick
    @field shop_title(String): 商品所属店铺名称
    @field size(String): 文件大小，单位:byte
    @field suffix(String): 文档后缀名
    @field title(String): 商品标题
    @field two_level_name(String): 二级类目的名称
    @field view_count(Number): 浏览量
    """
    FIELDS = {
        'author': {'type': 'String', 'is_list': False},
        'description': {'type': 'String', 'is_list': False},
        'doc_pages': {'type': 'Number', 'is_list': False},
        'favorite': {'type': 'Number', 'is_list': False},
        'item_id': {'type': 'Number', 'is_list': False},
        'pic_url': {'type': 'String', 'is_list': False},
        'price': {'type': 'Price', 'is_list': False},
        'publish_date': {'type': 'String', 'is_list': False},
        'publisher': {'type': 'String', 'is_list': False},
        'root_cate_id': {'type': 'Number', 'is_list': False},
        'sell_count': {'type': 'Number', 'is_list': False},
        'seller_id': {'type': 'Number', 'is_list': False},
        'seller_nick': {'type': 'String', 'is_list': False},
        'shop_title': {'type': 'String', 'is_list': False},
        'size': {'type': 'String', 'is_list': False},
        'suffix': {'type': 'String', 'is_list': False},
        'title': {'type': 'String', 'is_list': False},
        'two_level_name': {'type': 'String', 'is_list': False},
        'view_count': {'type': 'Number', 'is_list': False}
    }


class TransitStepInfo(TOPObject):
    """ 物流跟踪信息的一条

    @field status_desc(String): 状态描述
    @field status_time(String): 状态发生的时间
    """
    FIELDS = {
        'status_desc': {'type': 'String', 'is_list': False},
        'status_time': {'type': 'String', 'is_list': False}
    }


class SubUserPermission(TOPObject):
    """ 子账号所拥有的权限对象(直接赋予的权限和通过角色赋予的权限的总和对象)

    @field permissions(Permission, list): 子账号被直接赋予的权限点列表
    @field roles(Role, list): 子账号被赋予的角色信息(Role)列表。列表中的角色对象只有role_id，role_name，permissions信息
    """
    FIELDS = {
        'permissions': {'type': 'Permission', 'is_list': True},
        'roles': {'type': 'Role', 'is_list': True}
    }


class TaohuaOrder(TOPObject):
    """ 淘花订单对象数据结构

    @field item_id(Number): 商品ID
    @field modified(String): 最后修改时间
    @field order_id(Number): 订单编号
    @field pay_status(String): 1、wait_pay:等待买家付款、
        2、timeout_close: 系统超时关闭、
        3、pay_suc:交易成功、
        4、uncreate_trade:没有创建外部交易（支付宝交易）、
        5、micropay_trade_close: 交易被淘宝微支付关闭、　 　　           　　　　　　　6、alipay_trade_close:交易被支付宝关闭、
    @field pic_url(String): 商品图片链接
    @field price(Price): 商品价格
    @field seller_nick(String): 卖家昵称
    @field title(String): 商品标题
    """
    FIELDS = {
        'item_id': {'type': 'Number', 'is_list': False},
        'modified': {'type': 'String', 'is_list': False},
        'order_id': {'type': 'Number', 'is_list': False},
        'pay_status': {'type': 'String', 'is_list': False},
        'pic_url': {'type': 'String', 'is_list': False},
        'price': {'type': 'Price', 'is_list': False},
        'seller_nick': {'type': 'String', 'is_list': False},
        'title': {'type': 'String', 'is_list': False}
    }


class PromotionInShop(TOPObject):
    """ 店铺级优惠信息

    @field name(String): 优惠活动名称
    @field promotion_detail_desc(String): 优惠详情描述。
    @field promotion_id(String): idValue值
    """
    FIELDS = {
        'name': {'type': 'String', 'is_list': False},
        'promotion_detail_desc': {'type': 'String', 'is_list': False},
        'promotion_id': {'type': 'String', 'is_list': False}
    }


class OrderAmount(TOPObject):
    """ 子订单的帐务数据结构

    @field adjust_fee(String): 卖家手工调整的子订单的优惠金额.格式为:1.01;单位:元;精确到小数点后两位.
    @field discount_fee(String): 子订单的系统优惠金额。精确到2位小数;单位:元。如:200.07，表示:200元7分
    @field num(Number): 子交易订单中购买商品的数量
    @field num_iid(Number): 子订单对应的商品数字id
    @field oid(Number): 子交易订单编号
    @field payment(String): 子订单实付金额。精确到2位小数，单位:元。如:200.07，表示:200元7分。计算公式如下：payment = price * num + adjust_fee - discount_fee + post_fee(邮费，单笔子订单时子订单实付金额包含邮费，多笔子订单时不包含邮费)；对于退款成功的子订单，由于主订单的优惠分摊金额，会造成该字段可能不为0.00元。建议使用退款前的实付金额减去退款单中的实际退款金额计算。
    @field price(String): 商品价格。精确到2位小数;单位:元。如:200.07，表示:200元7分
    @field promotion_name(String): 子订单的系统优惠的名称，对应于discount_fee的名称
    @field sku_id(Number): 子订单对应的商品的sku_id
    @field sku_properties_name(String): SKU的值。如：机身颜色:黑色;手机套餐:官方标配
    @field title(String): 商品标题
    """
    FIELDS = {
        'adjust_fee': {'type': 'String', 'is_list': False},
        'discount_fee': {'type': 'String', 'is_list': False},
        'num': {'type': 'Number', 'is_list': False},
        'num_iid': {'type': 'Number', 'is_list': False},
        'oid': {'type': 'Number', 'is_list': False},
        'payment': {'type': 'String', 'is_list': False},
        'price': {'type': 'String', 'is_list': False},
        'promotion_name': {'type': 'String', 'is_list': False},
        'sku_id': {'type': 'Number', 'is_list': False},
        'sku_properties_name': {'type': 'String', 'is_list': False},
        'title': {'type': 'String', 'is_list': False}
    }


class PromotionDisplayTop(TOPObject):
    """ 优惠信息对象

    @field promotion_in_item(PromotionInItem, list): 单品级优惠信息
    @field promotion_in_shop(PromotionInShop, list): 店铺级优惠信息
    """
    FIELDS = {
        'promotion_in_item': {'type': 'PromotionInItem', 'is_list': True},
        'promotion_in_shop': {'type': 'PromotionInShop', 'is_list': True}
    }


class Check(TOPObject):
    """ 判断是否是粉丝返回的结果集

    @field check(Boolean): 是否是粉丝
    """
    FIELDS = {
        'check': {'type': 'Boolean', 'is_list': False}
    }


class TaohuaItem(TOPObject):
    """ 淘花商品数据结构

    @field author(String): 描述图书作者信息
    @field description(String): 商品描述信息
    @field favorite(Number): 描述用户喜欢值
    @field file_type(String): 文件类型
    @field item_id(Number): 商品ID
    @field leaf_cate_id(Number): 叶子类目的ID
    @field leaf_cate_name(String): 叶子类目的名称
    @field pic_url(String): 商品图片链接
    @field price(Price): 商品价格属性
    @field publish_date(String): 描述出版日期
    @field publisher(String): 描述商品出版社属性
    @field root_cate_id(Number): 根类目ID
    @field root_cate_name(String): 根类目名称
    @field size(String): 文件大小，单位byte
    @field status_name(String): 从未上架 never_put_shelves,
        上架put_shelves,
        小二下架down_shevles,
        删除delete,
        用户下架down_shevles_by_seller
    @field taohua_item_pv_pairs(TaohuaItemPVPair, list): 淘花商品的属性值对数据结构
    @field title(String): 商品标题
    """
    FIELDS = {
        'author': {'type': 'String', 'is_list': False},
        'description': {'type': 'String', 'is_list': False},
        'favorite': {'type': 'Number', 'is_list': False},
        'file_type': {'type': 'String', 'is_list': False},
        'item_id': {'type': 'Number', 'is_list': False},
        'leaf_cate_id': {'type': 'Number', 'is_list': False},
        'leaf_cate_name': {'type': 'String', 'is_list': False},
        'pic_url': {'type': 'String', 'is_list': False},
        'price': {'type': 'Price', 'is_list': False},
        'publish_date': {'type': 'String', 'is_list': False},
        'publisher': {'type': 'String', 'is_list': False},
        'root_cate_id': {'type': 'Number', 'is_list': False},
        'root_cate_name': {'type': 'String', 'is_list': False},
        'size': {'type': 'String', 'is_list': False},
        'status_name': {'type': 'String', 'is_list': False},
        'taohua_item_pv_pairs': {'type': 'TaohuaItemPVPair', 'is_list': True},
        'title': {'type': 'String', 'is_list': False}
    }


class PromotionInItem(TOPObject):
    """ 单品级优惠信息

    @field desc(String): 优惠描述
    @field end_time(Date): 优惠结束时间
    @field item_promo_price(Price): 优惠折后价格
    @field name(String): 优惠展示名称
    @field other_need(String): 需要支付附加物，显示为+xxx。如：+20淘金币
    @field other_send(String): 赠送东西。如：送10商城积分
    @field promotion_id(String): idValue的值
    @field sku_id_list(String, list): sku价格对应的id（保证二者顺序相同）
    @field sku_price_list(Price, list): sku价格列表
    @field start_time(Date): 优惠开始时间
    """
    FIELDS = {
        'desc': {'type': 'String', 'is_list': False},
        'end_time': {'type': 'Date', 'is_list': False},
        'item_promo_price': {'type': 'Price', 'is_list': False},
        'name': {'type': 'String', 'is_list': False},
        'other_need': {'type': 'String', 'is_list': False},
        'other_send': {'type': 'String', 'is_list': False},
        'promotion_id': {'type': 'String', 'is_list': False},
        'sku_id_list': {'type': 'String', 'is_list': True},
        'sku_price_list': {'type': 'Price', 'is_list': True},
        'start_time': {'type': 'Date', 'is_list': False}
    }


class TaohuaOrders(TOPObject):
    """ 淘花订单列表

    @field taohua_orders(TaohuaOrder, list): 淘花用户已买到订单列表数据结构
    @field total_order(Number): 返回的订单列表的总数
    """
    FIELDS = {
        'taohua_orders': {'type': 'TaohuaOrder', 'is_list': True},
        'total_order': {'type': 'Number', 'is_list': False}
    }


class FavoriteItem(TOPObject):
    """ 推荐的关联商品

    @field item_id(Number): 商品ID
    @field item_name(String): 商品名称
    @field item_pictrue(String): 商品图片地址
    @field item_price(Price): 商品价格
    @field item_url(String): 商品的详情页面地址
    @field promotion_price(Price): 促销价格
    @field sell_count(Number): 商品销售次数
    """
    FIELDS = {
        'item_id': {'type': 'Number', 'is_list': False},
        'item_name': {'type': 'String', 'is_list': False},
        'item_pictrue': {'type': 'String', 'is_list': False},
        'item_price': {'type': 'Price', 'is_list': False},
        'item_url': {'type': 'String', 'is_list': False},
        'promotion_price': {'type': 'Price', 'is_list': False},
        'sell_count': {'type': 'Number', 'is_list': False}
    }


class FavoriteShop(TOPObject):
    """ 推荐关联店铺信息

    @field rate(Number): 店铺卖家信用
    @field seller_id(Number): 卖家ID
    @field seller_nick(String): 卖家昵称
    @field shop_id(Number): 店铺ID
    @field shop_name(String): 店铺ID
    @field shop_pic(String): 店铺LOGO图片
    @field shop_url(String): 店铺首页链接
    """
    FIELDS = {
        'rate': {'type': 'Number', 'is_list': False},
        'seller_id': {'type': 'Number', 'is_list': False},
        'seller_nick': {'type': 'String', 'is_list': False},
        'shop_id': {'type': 'Number', 'is_list': False},
        'shop_name': {'type': 'String', 'is_list': False},
        'shop_pic': {'type': 'String', 'is_list': False},
        'shop_url': {'type': 'String', 'is_list': False}
    }


class ShopPositionData(TOPObject):
    """ 聚划算应用，展示本地化服务类商品的分店地理信息的对象

    @field address(String): 店铺的地址
    @field city(String): 卖家店铺所在的城市
    @field item_id(Number): 淘宝商品的数字id，对应了商品线的一个商品对象标识
    @field phone(String): 卖家店铺的手机联系号码
    @field seller_id(Number): 卖家的账户数字id
    @field shop_position_id(Number): 标识了一个唯一的地址位置对象，具有独立的坐标和交通信息
    @field store_name(String): 描述店铺的名称
    @field traffic(String): 店铺的一些交通提示信息
    @field x(Number): 店铺所在的经度，放大100000倍
    @field y(Number): 店铺所在的纬度，放大100000倍
    """
    FIELDS = {
        'address': {'type': 'String', 'is_list': False},
        'city': {'type': 'String', 'is_list': False},
        'item_id': {'type': 'Number', 'is_list': False},
        'phone': {'type': 'String', 'is_list': False},
        'seller_id': {'type': 'Number', 'is_list': False},
        'shop_position_id': {'type': 'Number', 'is_list': False},
        'store_name': {'type': 'String', 'is_list': False},
        'traffic': {'type': 'String', 'is_list': False},
        'x': {'type': 'Number', 'is_list': False},
        'y': {'type': 'Number', 'is_list': False}
    }


class TradeAmount(TOPObject):
    """ 交易订单的帐务信息详情

    @field alipay_no(String): 支付宝交易号，如：2009112081173831
    @field buyer_cod_fee(String): 买家货到付款服务费。精确到2位小数;单位:元。如:12.07，表示:12元7分
    @field buyer_obtain_point_fee(Number): 买家获得积分,返点的积分。格式:100;单位:个
    @field cod_fee(String): 货到付款服务费。精确到2位小数;单位:元。如:12.07，表示:12元7分
    @field commission_fee(String): 交易佣金。精确到2位小数;单位:元。如:200.07，表示:200元7分
    @field created(Date): 交易创建时间
    @field end_time(Date): 交易成功时间(更新交易状态为成功的同时更新)/确认收货时间。格式:yyyy-MM-dd HH:mm:ss
    @field express_agency_fee(String): 快递代收款。精确到2位小数;单位:元。如:212.07，表示:212元7分
    @field order_amounts(OrderAmount, list): 子订单的帐务金额详情列表
    @field pay_time(Date): 付款时间。格式:yyyy-MM-dd HH:mm:ss
    @field payment(String): 主订单实付金额。精确到2位小数;单位:元。如:200.07，表示:200元7分，计算公式如下：
        如果主订单只有一笔子订单 payment = 子订单的实付金额 + 货到付款服务费(如果是货到付款订单) - 主订单的系统级优惠；如果主订单有多笔子订单 payment = 各子订单的实付金额之和 + 货到付款服务费(如果是货到付款订单) + 邮费 - 主订单的系统级优惠
    @field post_fee(String): 邮费。精确到2位小数;单位:元。如:200.07，表示:200元7分。目前只提供整笔交易的邮费，暂不提供各子订单的邮费
    @field promotion_details(PromotionDetail, list): 主交易订单的系统级优惠详情
    @field seller_cod_fee(String): 卖家货到付款服务费。精确到2位小数;单位:元。如:12.07，表示:12元7分
    @field tid(Number): 交易主订单编号
    @field total_fee(String): 主订单的商品金额（各子订单中商品price * num的和，不包括任何优惠信息）。精确到2位小数;单位:元。如:200.07，表示:200元7分
    """
    FIELDS = {
        'alipay_no': {'type': 'String', 'is_list': False},
        'buyer_cod_fee': {'type': 'String', 'is_list': False},
        'buyer_obtain_point_fee': {'type': 'Number', 'is_list': False},
        'cod_fee': {'type': 'String', 'is_list': False},
        'commission_fee': {'type': 'String', 'is_list': False},
        'created': {'type': 'Date', 'is_list': False},
        'end_time': {'type': 'Date', 'is_list': False},
        'express_agency_fee': {'type': 'String', 'is_list': False},
        'order_amounts': {'type': 'OrderAmount', 'is_list': True},
        'pay_time': {'type': 'Date', 'is_list': False},
        'payment': {'type': 'String', 'is_list': False},
        'post_fee': {'type': 'String', 'is_list': False},
        'promotion_details': {'type': 'PromotionDetail', 'is_list': True},
        'seller_cod_fee': {'type': 'String', 'is_list': False},
        'tid': {'type': 'Number', 'is_list': False},
        'total_fee': {'type': 'String', 'is_list': False}
    }


class ItemData(TOPObject):
    """ 聚划算商品对象

    @field activity_price(Number): 商品的聚划算价格，单位分
    @field category_id(Number): 商品对应的淘宝类目id
    @field child_category(Number): 商品对应的聚划算二级类目
    @field city(String): 商品所在城市
    @field current_stock(Number): 商品的当前库存
    @field discount(String): 商品对应的折扣 聚划算价/原价
    @field exist_hold_stock(Boolean): 是否存在占座（下单未支付的订单）
    @field group_id(Number): 商品对应的团id
    @field is_lock(Boolean): 商品是否为锁定状态,锁定状态的商品才显示为可销售
    @field item_desc(String): 商品对应的聚划算描述信息
    @field item_guarantee(String): 代表聚划算支持的6种消保该商品是否支持，1支持，0不支持
        第一位：如实描述
        第二位：七天退换
        第三位：假一陪三
        第四位：商城正品保障
        第五位：商城提供发票
        第六位：商城7天退换
    @field item_id(Number): 商品的数字id
    @field item_status(String): 描述商品的状态，AVAIL_BUY=可以购买
        WAIT_FOR_START=即将开始
        EXIST_HOLDER=有占座
        NO_STOCK=卖光了
        OUT_OF_TIME=团购已结束
    @field item_url(String): 商品对应的URl
    @field long_name(String): 商品的长名称
    @field online_end_time(Number): 商品活动结束时间点的毫秒值
    @field online_start_time(Number): 商品上架开始时间点的毫秒值
    @field original_price(Number): 商品的原价，单位分
    @field parent_category(Number): 商品对应的聚划算一级类目
    @field pay_postage(Boolean): 商品是否包邮
    @field pic_url(String): 商品对应的图片地址
    @field pic_url_from_ic(String): 商品对应的交易线原始图片地址
    @field pic_wide_url(String): 聚划算图片宽图的地址
    @field platform_id(Number): 商品对应的平台id，1001=聚划算
    @field seller_credit(Number): 卖家对应的信用等级
    @field seller_id(Number): 商品对应的卖家账户id
    @field seller_nick(String): 商品对应的卖家账户nick
    @field shop_position_list(ShopPositionData, list): 本地化服务对象的分店信息
    @field shop_type(String): 商品对应的店铺类型，集市，商城
    @field short_name(String): 商品短名称
    @field sold_count(Number): 已参团的人数（付款）
    """
    FIELDS = {
        'activity_price': {'type': 'Number', 'is_list': False},
        'category_id': {'type': 'Number', 'is_list': False},
        'child_category': {'type': 'Number', 'is_list': False},
        'city': {'type': 'String', 'is_list': False},
        'current_stock': {'type': 'Number', 'is_list': False},
        'discount': {'type': 'String', 'is_list': False},
        'exist_hold_stock': {'type': 'Boolean', 'is_list': False},
        'group_id': {'type': 'Number', 'is_list': False},
        'is_lock': {'type': 'Boolean', 'is_list': False},
        'item_desc': {'type': 'String', 'is_list': False},
        'item_guarantee': {'type': 'String', 'is_list': False},
        'item_id': {'type': 'Number', 'is_list': False},
        'item_status': {'type': 'String', 'is_list': False},
        'item_url': {'type': 'String', 'is_list': False},
        'long_name': {'type': 'String', 'is_list': False},
        'online_end_time': {'type': 'Number', 'is_list': False},
        'online_start_time': {'type': 'Number', 'is_list': False},
        'original_price': {'type': 'Number', 'is_list': False},
        'parent_category': {'type': 'Number', 'is_list': False},
        'pay_postage': {'type': 'Boolean', 'is_list': False},
        'pic_url': {'type': 'String', 'is_list': False},
        'pic_url_from_ic': {'type': 'String', 'is_list': False},
        'pic_wide_url': {'type': 'String', 'is_list': False},
        'platform_id': {'type': 'Number', 'is_list': False},
        'seller_credit': {'type': 'Number', 'is_list': False},
        'seller_id': {'type': 'Number', 'is_list': False},
        'seller_nick': {'type': 'String', 'is_list': False},
        'shop_position_list': {'type': 'ShopPositionData', 'is_list': True},
        'shop_type': {'type': 'String', 'is_list': False},
        'short_name': {'type': 'String', 'is_list': False},
        'sold_count': {'type': 'Number', 'is_list': False}
    }


class WidgetCartInfo(TOPObject):
    """ 组件购物车记录

    @field cart_id(Number): 购物车记录的id，同BaseCartInfo中的cart_id
    @field delete_url(String): 此条购物车记录的删除链接。服务端签名后的删除链接，isv在使用的时候前面加上“http://gw.api.taobao.com/widget?”即可生成完整的购物车记录删除链接。
    @field item_id(Number): 购买的商品的商品数字id，同BaseCartInfo中的item_id,和Item中的num_iid
    @field item_url(String): 商品详情页连接地址，同Item的detail_url字段
    @field pic_url(String): 购买的商品的图片地址，如果选择了sku并且sku有单独的图片，此地址为sku的图片地址
    @field price(Price): 购买商品的价格，如果无sku，此价格为商品的当前价格。如果有sku，此价格为购买的sku的当前价格。如果此sku已经不存在，显示商品的价格
    @field quantity(Number): 购买数量，同BaseCartInfo的quantity
    @field seller_nick(String): 商品的卖家昵称
    @field sku(String): sku的属性列表。如果购买的商品无sku，此字段为空。如果有sku，次字段返回sku的属性描述（属性名:属性值别名/属性值名，别名优先）。
    @field title(String): 购买的商品的title，同Item的title
    """
    FIELDS = {
        'cart_id': {'type': 'Number', 'is_list': False},
        'delete_url': {'type': 'String', 'is_list': False},
        'item_id': {'type': 'Number', 'is_list': False},
        'item_url': {'type': 'String', 'is_list': False},
        'pic_url': {'type': 'String', 'is_list': False},
        'price': {'type': 'Price', 'is_list': False},
        'quantity': {'type': 'Number', 'is_list': False},
        'seller_nick': {'type': 'String', 'is_list': False},
        'sku': {'type': 'String', 'is_list': False},
        'title': {'type': 'String', 'is_list': False}
    }


class NonreplyStatById(TOPObject):
    """ 客服未回复统计

    @field non_reply_customId(String): 客服人员未回复的客户ID
    @field non_reply_num(Number): 客服未回复数
    @field service_staff_id(String): 客服人员ID
    """
    FIELDS = {
        'non_reply_customId': {'type': 'String', 'is_list': False},
        'non_reply_num': {'type': 'Number', 'is_list': False},
        'service_staff_id': {'type': 'String', 'is_list': False}
    }


class WidgetSkuProps(TOPObject):
    """ Widget使用的sku属性对应信息结构体

    @field alias(String): 商品的属性值别名，对应商品中的property_alias字段中的别名部分
    @field key_name(String): 属性id对应的属性名称，对应类目属性中的属性名称
    @field pic_url(String): 商品属性图片地址，对应Item中的propImgs，卖家设置了商品属性图片就有此字段，未设置此字段为空
    @field prop_key(Number): 淘宝的属性id，对应类目属性中的pid
    @field prop_value(Number): 淘宝的属性值id，对应类目属性中的vid
    @field value_name(String): 属性值id对应的属性标准名称，对应类目属性中的属性值名称
    """
    FIELDS = {
        'alias': {'type': 'String', 'is_list': False},
        'key_name': {'type': 'String', 'is_list': False},
        'pic_url': {'type': 'String', 'is_list': False},
        'prop_key': {'type': 'Number', 'is_list': False},
        'prop_value': {'type': 'Number', 'is_list': False},
        'value_name': {'type': 'String', 'is_list': False}
    }


class StaffEvalStatById(TOPObject):
    """ 客服评价统计

    @field evaluations(Evaluation, list): 客服评价
    @field service_staff_id(String): 客服人员ID
    """
    FIELDS = {
        'evaluations': {'type': 'Evaluation', 'is_list': True},
        'service_staff_id': {'type': 'String', 'is_list': False}
    }


class WidgetSku(TOPObject):
    """ 组件sku信息

    @field price(Price): sku的价格，对应Sku的price字段
    @field props(String): sku的属性串，根据pid的大小从小到大排列，前后都加";"。类型Sku的properties字段
    @field quantity(Number): sku的库存数量，对应Sku的quantity字段
    @field sku_id(Number): sku的id，对应Sku的sku_id字段
    """
    FIELDS = {
        'price': {'type': 'Price', 'is_list': False},
        'props': {'type': 'String', 'is_list': False},
        'quantity': {'type': 'Number', 'is_list': False},
        'sku_id': {'type': 'Number', 'is_list': False}
    }


class WidgetItem(TOPObject):
    """ Widget获取到的商品信息

    @field click_url(String): 商品的点击链接，如果此商品有淘宝客会根据app所属的淘宝用户进行淘宝客连接转换，如果无淘宝客此字段为淘宝商品详情地址
    @field is_mall(Boolean): 是否商城的商品
    @field item_id(Number): 淘宝商品的数字id，与Item的num_iid一致
    @field item_pics(String, list): 商品图片列表，对应Item的itemImgs
    @field item_promotion_data(PromotionInItem, list): 商品关联的商品优惠信息
    @field pic_url(String): 商品的主图地址，对应Item的pic_url
    @field price(String): 淘宝商品的价格，对应Item的price。如果商品为无sku或者所有sku价格一致的商品，此字段为价格（199.99）；如果商品有多sku且有一个价格区间，次字段为商品的价格区间，中间用‘-’连接
    @field quantity(Number): 商品的数量，对应Item的num
    @field seller_nick(String): 商品卖家昵称，对应Item的nick
    @field shop_promotion_data(PromotionInShop, list): 商品关联的卖家店铺优惠信息
    @field sku_props(WidgetSkuProps, list): 商品关联sku对应的商品属性列表信息
    @field skus(WidgetSku, list): 商品关联的sku列表信息
    @field title(String): 淘宝商品的标题，与Item的title一致
    """
    FIELDS = {
        'click_url': {'type': 'String', 'is_list': False},
        'is_mall': {'type': 'Boolean', 'is_list': False},
        'item_id': {'type': 'Number', 'is_list': False},
        'item_pics': {'type': 'String', 'is_list': True},
        'item_promotion_data': {'type': 'PromotionInItem', 'is_list': True},
        'pic_url': {'type': 'String', 'is_list': False},
        'price': {'type': 'String', 'is_list': False},
        'quantity': {'type': 'Number', 'is_list': False},
        'seller_nick': {'type': 'String', 'is_list': False},
        'shop_promotion_data': {'type': 'PromotionInShop', 'is_list': True},
        'sku_props': {'type': 'WidgetSkuProps', 'is_list': True},
        'skus': {'type': 'WidgetSku', 'is_list': True},
        'title': {'type': 'String', 'is_list': False}
    }


class TaohuaUpdateInfo(TOPObject):
    """ 淘花终端软件版本更新信息接口

    @field message(String): 提示消息
    @field url(String): 最新下载地址
    @field version(String): 版本号
    """
    FIELDS = {
        'message': {'type': 'String', 'is_list': False},
        'url': {'type': 'String', 'is_list': False},
        'version': {'type': 'String', 'is_list': False}
    }


class HotelImage(TOPObject):
    """ 酒店图片

    @field hid(Number): 酒店id
    @field pic(String): 图片地址链接
    """
    FIELDS = {
        'hid': {'type': 'Number', 'is_list': False},
        'pic': {'type': 'String', 'is_list': False}
    }


class TaohuaCateStat(TOPObject):
    """ 淘花类目统计结构对象，  是搜索引擎统计返回回来的类目信息

    @field cate_id(Number): 类目ID
    @field count(Number): 当前类目下面的商品数量
    @field name(String): 类目名称
    """
    FIELDS = {
        'cate_id': {'type': 'Number', 'is_list': False},
        'count': {'type': 'Number', 'is_list': False},
        'name': {'type': 'String', 'is_list': False}
    }


class TaohuaCategory(TOPObject):
    """ 淘花类目对象

    @field cate_id(Number): 类目ID
    @field cate_level(Number): 类目层级
    @field name(String): 类目名称
    @field parent_id(Number): 父类目ID
    @field sort_order(Number): 排序值
    """
    FIELDS = {
        'cate_id': {'type': 'Number', 'is_list': False},
        'cate_level': {'type': 'Number', 'is_list': False},
        'name': {'type': 'String', 'is_list': False},
        'parent_id': {'type': 'Number', 'is_list': False},
        'sort_order': {'type': 'Number', 'is_list': False}
    }


class ChannelInfo(TOPObject):
    """ 渠道信息

    @field channel_display_name(String): 渠道展示名称
    @field channel_key(String): 渠道标识代码
    @field referers(String, list): 当前渠道所包含的来源referer地址。
    """
    FIELDS = {
        'channel_display_name': {'type': 'String', 'is_list': False},
        'channel_key': {'type': 'String', 'is_list': False},
        'referers': {'type': 'String', 'is_list': True}
    }


class TaohuaCatePropValue(TOPObject):
    """ 淘花类目属性值对象结构

    @field prop_value(String): 属性值
    @field value_id(Number): 属性值id
    """
    FIELDS = {
        'prop_value': {'type': 'String', 'is_list': False},
        'value_id': {'type': 'Number', 'is_list': False}
    }


class TaohuaCateProp(TOPObject):
    """ 淘花类目属性结构

    @field name(String): 属性名称
    @field prop_id(Number): 属性结构
    """
    FIELDS = {
        'name': {'type': 'String', 'is_list': False},
        'prop_id': {'type': 'Number', 'is_list': False}
    }


class AlipayAccount(TOPObject):
    """ 支付宝用户账户信息

    @field alipay_user_id(String): 支付宝用户ID
    @field available_amount(Price): 可用余额
    @field freeze_amount(Price): 不可用余额
    @field total_amount(Price): 余额总额
    """
    FIELDS = {
        'alipay_user_id': {'type': 'String', 'is_list': False},
        'available_amount': {'type': 'Price', 'is_list': False},
        'freeze_amount': {'type': 'Price', 'is_list': False},
        'total_amount': {'type': 'Price', 'is_list': False}
    }


class AlipayContract(TOPObject):
    """ 用户订购信息

    @field alipay_user_id(String): 支付宝用户ID
    @field contract_content(String): 订购的应用名称，有效时间。
    @field end_time(Date): 订购的失效时间
    @field page_url(String): 订购URL。在sign返回false时返回应用的订购地址，可以引导用户订购。
    @field start_time(Date): 订购的生效时间
    @field subscribe(Boolean): 是否订购的标识。true：代表已订购。
    """
    FIELDS = {
        'alipay_user_id': {'type': 'String', 'is_list': False},
        'contract_content': {'type': 'String', 'is_list': False},
        'end_time': {'type': 'Date', 'is_list': False},
        'page_url': {'type': 'String', 'is_list': False},
        'start_time': {'type': 'Date', 'is_list': False},
        'subscribe': {'type': 'Boolean', 'is_list': False}
    }


class WlbInventory(TOPObject):
    """ 库存详情对象。其中包括货主ID，仓库编码，库存，库存类型等属性

    @field item_id(Number): 商品ID
    @field lock_quantity(Number): 冻结(锁定)数量，用来跟踪库存的中间状态，比如前台销售了1件商品，这时lock加1，当商品出库的时候lock再减回去
    @field quantity(Number): 库存数量(有效数量)
    @field store_code(String): 仓库编码，关联到仓库类型服务的编码非托管库存(卖家自己管理的库存，物流宝不可见又称自有库存)的所在仓库编码: STORE_SYS_PRIVATE
    @field type(String): VENDIBLE--可销售库存
        FREEZE--冻结库存
        ONWAY--在途库存
        DEFECT--残次品库存
    @field user_id(Number): 货主ID
    """
    FIELDS = {
        'item_id': {'type': 'Number', 'is_list': False},
        'lock_quantity': {'type': 'Number', 'is_list': False},
        'quantity': {'type': 'Number', 'is_list': False},
        'store_code': {'type': 'String', 'is_list': False},
        'type': {'type': 'String', 'is_list': False},
        'user_id': {'type': 'Number', 'is_list': False}
    }


class AccountFreeze(TOPObject):
    """ 支付宝用户冻结明细信息

    @field freeze_amount(Price): 冻结金额
    @field freeze_name(String): 冻结类型名称
    @field freeze_type(String): 冻结类型值
    """
    FIELDS = {
        'freeze_amount': {'type': 'Price', 'is_list': False},
        'freeze_name': {'type': 'String', 'is_list': False},
        'freeze_type': {'type': 'String', 'is_list': False}
    }


class CouponDetail(TOPObject):
    """ 优惠券详细信息

    @field buyer_nick(String): 买家的昵称
    @field channel(String): 优惠券的发放渠道：渠道有rewardforgifts：满就送，marketingMessage：营销消息，activityofget：活动领取，createActivity：创建活动，ISV
    @field coupon_number(Number): 目前优惠券编号
    @field state(String): 优惠券使用情况Unused：未使用using：使用中used：已使用
    """
    FIELDS = {
        'buyer_nick': {'type': 'String', 'is_list': False},
        'channel': {'type': 'String', 'is_list': False},
        'coupon_number': {'type': 'Number', 'is_list': False},
        'state': {'type': 'String', 'is_list': False}
    }


class WlbItem(TOPObject):
    """ 物流宝商品

    @field brand_id(Number): 品牌ID
    @field color(String): 颜色
    @field creator(String): 创建人
    @field flag(String): 标记，用逗号隔开的字符串。
        BIT_HAS_AUTHORIZE 第1位 是否有授权规则;
        BATCH  第2位 是否有批次规则；
        SYNCHRONIZATION 第3位 是否有同步规则。
    @field gmt_create(Date): 创建日期
    @field gmt_modified(Date): 修改日期
    @field goods_cat(String): 货类
    @field height(Number): 高
    @field id(Number): 商品id
    @field is_dangerous(Boolean): 是否危险品
    @field is_friable(Boolean): 是否易碎
    @field is_sku(Boolean): 是不是sku商品
        值为true或false
    @field item_code(String): 商家编码
    @field last_modifier(String): 最后修改人
    @field length(Number): mm
    @field name(String): 商品的名称
    @field package_material(String): 包装材料
    @field parent_id(Number): 父item的id，当item为物流宝子商品时，parent_id必填,否则不必填
        可通过父ID来得知商品的关系。
    @field price(Number): 价格
    @field pricing_cat(String): 计价货类
    @field properties(String): 属性key:value; key:value
    @field publish_version(Number): 发布版本号，用来同步商
    @field remark(String): 商品备注
    @field status(String): 状态，item_status_valid -- 1 表示 有效 item_status_lock -- 2 表示锁住
    @field title(String): 前台商品名称
    @field type(String): 商品类型：
        NORMAL--普通类型;
        COMBINE--组合商品;
        DISTRIBUTION--分销商品;
        默认为NORMAL
    @field user_id(Number): 商品所有人淘宝ID
    @field user_nick(String): 商品所有人淘宝nick
    @field volume(Number): 立方mm
    @field weight(Number): 重量
    @field width(Number): 宽
    """
    FIELDS = {
        'brand_id': {'type': 'Number', 'is_list': False},
        'color': {'type': 'String', 'is_list': False},
        'creator': {'type': 'String', 'is_list': False},
        'flag': {'type': 'String', 'is_list': False},
        'gmt_create': {'type': 'Date', 'is_list': False},
        'gmt_modified': {'type': 'Date', 'is_list': False},
        'goods_cat': {'type': 'String', 'is_list': False},
        'height': {'type': 'Number', 'is_list': False},
        'id': {'type': 'Number', 'is_list': False},
        'is_dangerous': {'type': 'Boolean', 'is_list': False},
        'is_friable': {'type': 'Boolean', 'is_list': False},
        'is_sku': {'type': 'Boolean', 'is_list': False},
        'item_code': {'type': 'String', 'is_list': False},
        'last_modifier': {'type': 'String', 'is_list': False},
        'length': {'type': 'Number', 'is_list': False},
        'name': {'type': 'String', 'is_list': False},
        'package_material': {'type': 'String', 'is_list': False},
        'parent_id': {'type': 'Number', 'is_list': False},
        'price': {'type': 'Number', 'is_list': False},
        'pricing_cat': {'type': 'String', 'is_list': False},
        'properties': {'type': 'String', 'is_list': False},
        'publish_version': {'type': 'Number', 'is_list': False},
        'remark': {'type': 'String', 'is_list': False},
        'status': {'type': 'String', 'is_list': False},
        'title': {'type': 'String', 'is_list': False},
        'type': {'type': 'String', 'is_list': False},
        'user_id': {'type': 'Number', 'is_list': False},
        'user_nick': {'type': 'String', 'is_list': False},
        'volume': {'type': 'Number', 'is_list': False},
        'weight': {'type': 'Number', 'is_list': False},
        'width': {'type': 'Number', 'is_list': False}
    }


class TradeRecord(TOPObject):
    """ 支付宝交易明细

    @field alipay_order_no(String): 支付宝订单号
    @field create_time(Date): 订单创建时间
    @field merchant_order_no(String): 商户订单号
    @field modified_time(Date): 订单最后修改时间
    @field opposite_logon_id(String): 对方支付宝登录号，需要隐藏
    @field opposite_name(String): 对方姓名，需要隐藏
    @field opposite_user_id(String): 对方支付宝账号
    @field order_from(String): 订单来源，为空查询所有来源。淘宝(taobao)，支付宝(alipay)，其它(other)
    @field order_status(String): 订单状态
    @field order_title(String): 订单的名称，描述订单的摘要信息，如交易的商品名称
    @field order_type(String): 订单类型
    @field owner_logon_id(String): 本方支付宝登录号，需要隐藏
    @field owner_name(String): 本方姓名，需要隐藏
    @field owner_user_id(String): 本方支付宝账号
    @field service_charge(Price): 订单服务费
    @field total_amount(Price): 订单总金额
    """
    FIELDS = {
        'alipay_order_no': {'type': 'String', 'is_list': False},
        'create_time': {'type': 'Date', 'is_list': False},
        'merchant_order_no': {'type': 'String', 'is_list': False},
        'modified_time': {'type': 'Date', 'is_list': False},
        'opposite_logon_id': {'type': 'String', 'is_list': False},
        'opposite_name': {'type': 'String', 'is_list': False},
        'opposite_user_id': {'type': 'String', 'is_list': False},
        'order_from': {'type': 'String', 'is_list': False},
        'order_status': {'type': 'String', 'is_list': False},
        'order_title': {'type': 'String', 'is_list': False},
        'order_type': {'type': 'String', 'is_list': False},
        'owner_logon_id': {'type': 'String', 'is_list': False},
        'owner_name': {'type': 'String', 'is_list': False},
        'owner_user_id': {'type': 'String', 'is_list': False},
        'service_charge': {'type': 'Price', 'is_list': False},
        'total_amount': {'type': 'Price', 'is_list': False}
    }


class Activity(TOPObject):
    """ 活动数据结构

    @field activity_id(Number): 活动id
    @field activity_url(String): 领用优惠券的链接
    @field applied_count(Number): 已经领取的优惠券的数量
    @field coupon_id(Number): 活动对应的优惠券ID
    @field create_user(String): self代表自己创建，other他人创建
    @field person_limit_count(Number): 每个买家限领取优惠券的数量，1～5张
    @field status(String): enabled代表有效，invalid代表失效。other代表空值
    @field total_count(Number): 卖家设置优惠券领取的总领用量
    """
    FIELDS = {
        'activity_id': {'type': 'Number', 'is_list': False},
        'activity_url': {'type': 'String', 'is_list': False},
        'applied_count': {'type': 'Number', 'is_list': False},
        'coupon_id': {'type': 'Number', 'is_list': False},
        'create_user': {'type': 'String', 'is_list': False},
        'person_limit_count': {'type': 'Number', 'is_list': False},
        'status': {'type': 'String', 'is_list': False},
        'total_count': {'type': 'Number', 'is_list': False}
    }


class Coupon(TOPObject):
    """ 优惠券数据结构

    @field condition(Number): 订单满多少分才能用这个优惠券，501就是满501分能使用。注意：返回的是“分”，不是“元”
    @field coupon_id(Number): 优惠券ID
    @field creat_time(Date): 优惠券创建时间
    @field create_channel(String): 优惠券的创建渠道，自己创建/他人创建
    @field denominations(Number): 优惠券的面值，返回的是“分”，不是“元”，500代表500分相当于5元
    @field end_time(Date): 优惠券的截止日期
    """
    FIELDS = {
        'condition': {'type': 'Number', 'is_list': False},
        'coupon_id': {'type': 'Number', 'is_list': False},
        'creat_time': {'type': 'Date', 'is_list': False},
        'create_channel': {'type': 'String', 'is_list': False},
        'denominations': {'type': 'Number', 'is_list': False},
        'end_time': {'type': 'Date', 'is_list': False}
    }


class AfterSale(TOPObject):
    """ 卖家设置售后服务对象

    @field after_sale_id(Number): id
    @field after_sale_name(String): 名称
    @field after_sale_path(String): tfs地址
    """
    FIELDS = {
        'after_sale_id': {'type': 'Number', 'is_list': False},
        'after_sale_name': {'type': 'String', 'is_list': False},
        'after_sale_path': {'type': 'String', 'is_list': False}
    }


class TaohuaItemComment(TOPObject):
    """ 指定商品评论

    @field comment(String): 商品评论的具体内容
    @field comment_date(Date): 评论发表时间
    @field user_nick(String): 评论人
    """
    FIELDS = {
        'comment': {'type': 'String', 'is_list': False},
        'comment_date': {'type': 'Date', 'is_list': False},
        'user_nick': {'type': 'String', 'is_list': False}
    }


class PartnerDetail(TOPObject):
    """ 物流公司详细信息

    @field account_no(String): 物流公司支付宝账号
    @field company_code(String): 物流公司代码
    @field company_id(Number): 物流公司id
    @field company_name(String): 物流公司简称
    @field full_name(String): 物流公司全名
    @field reg_mail_no(String): 运单号验证正则表达式
    @field wangwang_id(String): 旺旺id
    """
    FIELDS = {
        'account_no': {'type': 'String', 'is_list': False},
        'company_code': {'type': 'String', 'is_list': False},
        'company_id': {'type': 'Number', 'is_list': False},
        'company_name': {'type': 'String', 'is_list': False},
        'full_name': {'type': 'String', 'is_list': False},
        'reg_mail_no': {'type': 'String', 'is_list': False},
        'wangwang_id': {'type': 'String', 'is_list': False}
    }


class TaohuaItemCommentResult(TOPObject):
    """ 淘花商品评论

    @field taohua_item_comments(TaohuaItemComment, list): 淘花商品评论列表
    @field total_comment_num(Number): 评论总数
    """
    FIELDS = {
        'taohua_item_comments': {'type': 'TaohuaItemComment', 'is_list': True},
        'total_comment_num': {'type': 'Number', 'is_list': False}
    }


class Discount(TOPObject):
    """ 折扣信息

    @field created(Date): 创建时间
    @field details(DiscountDetail, list): 折扣详情
    @field discount_id(Number): 折扣ID
    @field modified(Date): 修改时间
    @field name(String): 折扣名称
    """
    FIELDS = {
        'created': {'type': 'Date', 'is_list': False},
        'details': {'type': 'DiscountDetail', 'is_list': True},
        'discount_id': {'type': 'Number', 'is_list': False},
        'modified': {'type': 'Date', 'is_list': False},
        'name': {'type': 'String', 'is_list': False}
    }


class DiscountDetail(TOPObject):
    """ 折扣详情信息

    @field created(Date): 创建时间
    @field detail_id(Number): 折扣详情ID
    @field discount_type(String): 优惠方式:PERCENT（按折扣优惠）、PRICE（按减价优惠）
    @field discount_value(Number): 优惠比率或者优惠价格 10%或10
    @field modified(Date): 修改时间
    @field target_id(Number): 会员等级的id或者分销商id
    @field target_name(String): 等级名称或者分销商名称
    @field target_type(String): 折扣类型:GRADE（按会员等级优惠）、DISTRIBUTOR（按分销商优惠）
    """
    FIELDS = {
        'created': {'type': 'Date', 'is_list': False},
        'detail_id': {'type': 'Number', 'is_list': False},
        'discount_type': {'type': 'String', 'is_list': False},
        'discount_value': {'type': 'Number', 'is_list': False},
        'modified': {'type': 'Date', 'is_list': False},
        'target_id': {'type': 'Number', 'is_list': False},
        'target_name': {'type': 'String', 'is_list': False},
        'target_type': {'type': 'String', 'is_list': False}
    }


class Evaluation(TOPObject):
    """ 客服评价

    @field evaluation_name(String): 客服评价内容
    @field evaluation_num(String): 评价数量
    """
    FIELDS = {
        'evaluation_name': {'type': 'String', 'is_list': False},
        'evaluation_num': {'type': 'String', 'is_list': False}
    }


class OnlineTimeById(TOPObject):
    """ 在线时长

    @field online_times(Number): 客服在线时间长度（秒）
    @field service_staff_id(String): 客服人员ID
    """
    FIELDS = {
        'online_times': {'type': 'Number', 'is_list': False},
        'service_staff_id': {'type': 'String', 'is_list': False}
    }


class WaitingTimeById(TOPObject):
    """ 平均等待时长

    @field avg_waiting_times(Number): 平均等待时间长度（秒）
    @field service_staff_id(String): 客服人员ID
    """
    FIELDS = {
        'avg_waiting_times': {'type': 'Number', 'is_list': False},
        'service_staff_id': {'type': 'String', 'is_list': False}
    }


class ReplyStatById(TOPObject):
    """ 客服回复统计

    @field reply_num(Number): 客服回复数
    @field user_id(String): 客服ID
    """
    FIELDS = {
        'reply_num': {'type': 'Number', 'is_list': False},
        'user_id': {'type': 'String', 'is_list': False}
    }


class Chatpeer(TOPObject):
    """ 聊天对象ID列表

    @field date(String): 聊天日期
    @field uid(String): 聊天对象用户ID：cntaobao+淘宝nick，例如cntaobaotest
    """
    FIELDS = {
        'date': {'type': 'String', 'is_list': False},
        'uid': {'type': 'String', 'is_list': False}
    }


class LogisticsPartner(TOPObject):
    """ 查询揽送范围之内的物流公司信息

    @field carriage(CarriageDetail): 物流公司揽收和资费详细信息
    @field cover_remark(String): 揽收说明信息
    @field partner(PartnerDetail): 物流公司详细信息
    @field uncover_remark(String): 不可送达的说明信息
    """
    FIELDS = {
        'carriage': {'type': 'CarriageDetail', 'is_list': False},
        'cover_remark': {'type': 'String', 'is_list': False},
        'partner': {'type': 'PartnerDetail', 'is_list': False},
        'uncover_remark': {'type': 'String', 'is_list': False}
    }


class Promotion(TOPObject):
    """ 商品优惠策略详情

    @field decrease_num(Number): 减价件数，1只减一件，0表示多件
    @field discount_type(String): 优惠类型，PRICE表示按价格优惠，DISCOUNT表示按折扣优惠
    @field discount_value(String): 优惠额度
    @field end_date(Date): 优惠结束日期
    @field num_iid(Number): 商品数字ID
    @field promotion_desc(String): 优惠描述
    @field promotion_id(Number): 优惠ID
    @field promotion_title(String): 优惠标题，显示在宝贝详情页面的优惠图标的tip。
    @field start_date(Date): 优惠开始日期
    @field status(String): 优惠策略状态，ACTIVE表示有效，UNACTIVE表示无效
    @field tag_id(Number): 对应的人群标签ID
    """
    FIELDS = {
        'decrease_num': {'type': 'Number', 'is_list': False},
        'discount_type': {'type': 'String', 'is_list': False},
        'discount_value': {'type': 'String', 'is_list': False},
        'end_date': {'type': 'Date', 'is_list': False},
        'num_iid': {'type': 'Number', 'is_list': False},
        'promotion_desc': {'type': 'String', 'is_list': False},
        'promotion_id': {'type': 'Number', 'is_list': False},
        'promotion_title': {'type': 'String', 'is_list': False},
        'start_date': {'type': 'Date', 'is_list': False},
        'status': {'type': 'String', 'is_list': False},
        'tag_id': {'type': 'Number', 'is_list': False}
    }


class UserTag(TOPObject):
    """ 人群标签

    @field create_date(Date): 创建时间
    @field description(String): 标签描述
    @field tag_id(Number): 标签ID
    @field tag_name(String): 标签名称
    """
    FIELDS = {
        'create_date': {'type': 'Date', 'is_list': False},
        'description': {'type': 'String', 'is_list': False},
        'tag_id': {'type': 'Number', 'is_list': False},
        'tag_name': {'type': 'String', 'is_list': False}
    }

