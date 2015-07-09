__author__ = 'jonathan'

import _fixtures as models
from lib.rome.core.orm.query import Query
import collections
import logging
import time

current_milli_time = lambda: int(round(time.time() * 1000))


def compute_ip(network_id, fixed_ip_id):
    digits = [fixed_ip_id / 255, fixed_ip_id % 255]
    return "172.%d.%d.%d" % (network_id, digits[0], digits[1])


def create_mock_data(network_count=3, fixed_ip_count=200):

    for i in range(1, network_count):
        network = models.Network()
        network.id = i
        network.save()

    for i in range(1, network_count):
        for j in range(1, fixed_ip_count):
            fixed_ip = models.FixedIp()
            fixed_ip.id = i * fixed_ip_count + j
            fixed_ip.network_id = i
            fixed_ip.address = compute_ip(i, j)
            fixed_ip.save()

    pass



if __name__ == '__main__':

    logging.getLogger().setLevel(logging.DEBUG)
    # create_mock_data(3, 2000)

    fixed_ips = Query(models.FixedIp).filter(models.FixedIp.deleted==None).filter(models.FixedIp.deleted==None).filter(models.FixedIp.updated_at!=None).all()
    # print(fixed_ips)

    # from lib.rome.core.session.session import Session as Session
    # logging.getLogger().setLevel(logging.DEBUG)
    # session = Session()
    #
    # with session.begin():
    #     for i in range(1, 10):
    #         network = models.Network()
    #         network.id = i
    #         network.save()
    # for i in range(1, 5):
    #     query = Query(models.FixedIp.id, models.Network.id)\
    #         .join(models.FixedIp.network_id == models.Network.id)
    #     # query.filter(models.FixedIp.address == "172.1.1.13")
    #     result = query.all()

    # print(len(result))

    # for each in result:
    #     print(each)
