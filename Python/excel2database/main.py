# coding=utf8

from models import Order, OrderQuantity, DeliveryEntity, ReceivingEntity, ManufactureOrder, BOM

if __name__ == '__main__':
    Order.transform()
    OrderQuantity.transform()
    DeliveryEntity.transform()
    ReceivingEntity.transform()
    ManufactureOrder.transform()
    BOM.transform()

