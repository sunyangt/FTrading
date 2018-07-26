# -*- coding:utf-8 -*- 
'''
Created on 2018/06/06
@author: Jimmy
@group: Tushare
@email: waditu@163.com
'''

from fcoin.dataapi import DataAPI

def authorize(key='', secret=''):
    api = DataAPI(key=key, secret=secret)
    return api


if __name__ == '__main__':
    api = authorize()
    print(api.symbols())
