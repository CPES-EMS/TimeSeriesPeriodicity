import datetime
import numpy as np
import pandas as pd
from config import *
import pymysql


def GetAllDataFromDB(table_name, time='receivetime', start_time=None, end_time=None):
    """
    :param table_name: 表名
    :param time: 表中时间列的定义名称，默认为“receivetime”
    :param start_time: 指定的起始时间，默认为空
    :param end_time:指定的结束时间，默认为空
    :return: 选取的数据
    """
    mydb = pymysql.connect(
        host=dataaddress,  # 数据库主机地址
        port=port_num,
        user=user_name,  # 数据库用户名
        passwd=password,  # 数据库密码
        database=datause
    )
    cursor = mydb.cursor()

    if start_time is not None and end_time is not None:
        sql = f"SELECT * FROM {table_name} WHERE {time} >= '{start_time}' AND {time}<='{end_time}' ORDER BY {time} "
    elif start_time is not None and end_time is None:
        sql = f"SELECT * FROM {table_name} WHERE {time} >= '{start_time}' ORDER BY {time}"
    elif start_time is None and end_time is not None:
        sql = f"SELECT * FROM {table_name} WHERE {time} <= '{end_time}' ORDER BY {time}"
    else:
        sql = f"SELECT * FROM {table_name} ORDER " \
              f"BY {time} "
    cursor.execute(sql)
    data = pd.DataFrame(np.array(cursor.fetchall()))
    # 关闭数据库
    mydb.close()

    return data


def InsertData(table_name, alarm_dict):
    """
    :param table_name: 插入的表名称
    :param alarm_dict: 插入表中的数据，字典类型，key是数据库列名,value是相应的列对应的值。
    :return:
    """
    mydb = pymysql.connect(
        host=dataaddress,  # 数据库主机地址
        port=port_num,
        user=user_name,  # 数据库用户名
        passwd=password,  # 数据库密码
        database=datause
    )
    cursor = mydb.cursor()

    # 写入时间生成
    write_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M')

    # 生成列名
    column_name = 'estimate_time'
    data = [write_time]
    for key in alarm_dict.keys():
        column_name = column_name + ',' + str(key)
        data.append(alarm_dict[key])
    data = tuple(data)

    # 生成sql语句
    tmp_s = '%' + 's'
    for key in alarm_dict.keys():
        tmp_s = tmp_s + ",%" + "s"  # 批量添加%s
    sql = """INSERT INTO """ + table_name + """(""" + column_name + """)
         VALUES (""" + tmp_s + """);"""  # 拼接sql语句

    # 执行sql语句
    cursor.execute(sql, data)
    mydb.commit()
    mydb.close()


def UpdateData(table_name, data_dict, tag_id):
    """
    :param table_name: 插入的表名称
    :param data_dict: 表中需要更新的数据，字典类型，key是数据库列名,value是相应的列对应的值。
    :param tag_id: 用于在表中筛选需要更新数据的target_id
    :return:
    """
    mydb = pymysql.connect(
        host=dataaddress,  # 数据库主机地址
        port=port_num,
        user=user_name,  # 数据库用户名
        passwd=password,  # 数据库密码
        database=datause
    )
    cursor = mydb.cursor()

    # 写入时间生成
    write_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    # 生成列名
    column_names = ['create_time']
    data = [write_time]
    for key in data_dict.keys():
        column_names.append(str(key))
        data.append(data_dict[key])

    # 生成sql语句
    tmp_s = '%' + 's'
    for key in data_dict.keys():
        tmp_s = tmp_s + ",%" + "s"  # 批量添加%s

    # 获取最新数据的时间戳
    latest_time_sql = f"SELECT MAX(create_time) FROM {table_name} WHERE tag_id = '{tag_id}'"
    cursor.execute(latest_time_sql)
    latest_time = cursor.fetchone()[0]

    set_statements = ", ".join([column_name + " = %s" for column_name in column_names])
    sql = """UPDATE """ + table_name + """
             SET """ + set_statements + """WHERE create_time = %s AND tag_id = %s;"""

    # 执行sql语句
    cursor.execute(sql, data + [latest_time, tag_id])
    mydb.commit()
    mydb.close()


if __name__ == '__main__':
    row_name = ['temperature', 'humidity']
    data_all = np.array(
        GetAllDataFromDB(table_name=test_sheet, time='receivetime'))
    print(data_all)

    data_dict = {'tag_id': area_id_3, 'temperature': 25.5, 'humidity': 27}
    InsertData(table_name=test_sheet, alarm_dict=data_dict)

    data_update_dict = {'temperature': 29.5, 'humidity': 27.3}
    UpdateData(table_name=test_sheet, data_dict=data_update_dict, tag_id=area_id_3)
