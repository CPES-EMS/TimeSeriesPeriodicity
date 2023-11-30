import logging
import TimeSeriesPeriodicity
import sql

"""
该模型主要用于在海量告警日志数据中快速挖掘周期性告警，应用时序关联特征进行周期性分析
"""
if __name__ == '__main__':
    # logging日志输出
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s %(message)s %(filename)s %(lineno)s %(levelname)s',
        filemode='w',
        filename='./logfile/log.txt'
    )

    logging.info('读取数据')
    data = sql.GetAllDataFromDB('ems_information_network_alarm')
    combination_counts = data.groupby([data[2], data[4]]).size().reset_index(name='count')
    combination_counts = combination_counts.sort_values('count', ascending=False)
    combination_counts_list = combination_counts.values.tolist()
    logging.info('数据归并完毕')
    period_list = []
    i = 0
    for sp in combination_counts_list:
        logging.info('第' + str(i) + "个时刻--------------")
        i += 1
        if sp[2] >= 10:  # 告警个数大于10
            result = data[(data[2] == sp[0]) & (data[4] == sp[1])]
            logging.info('获取告警个数大于10的归并告警')
            time_series = result.values.tolist()
            logging.info('获取时间序列')
            device_list = []
            category_list = []
            for d in time_series:
                if d[6] not in category_list:
                    category_list.append(d[6])
                if d[8] not in device_list:
                    device_list.append(d[8])
            device_str = ','.join(device_list)
            category_str = ','.join(category_list)
            logging.info('获取设备与告警类型')
            num = len(time_series)
            logging.info('计算告警总数')
            x, y = TimeSeriesPeriodicity.time_series_deal(time_series)
            logging.info('计算时间间隔与对应出现次数')
            logging.info('判断此时间间隔周期性')
            single_alarm_dict = {}
            if TimeSeriesPeriodicity.periodicity_judgment(x, y) != False:
                period, period_num = TimeSeriesPeriodicity.periodicity_judgment(x, y)
                logging.info('判断周期性完毕')
                logging.info(period)
                single_alarm_dict['source_ip'] = sp[0]
                single_alarm_dict['dest_ip'] = sp[1]
                single_alarm_dict['dest_name'] = device_str
                single_alarm_dict['alarm_type'] = category_str
                single_alarm_dict['cycle'] = period
                single_alarm_dict['alarm_num'] = num
                single_alarm_dict['special_num'] = period_num
                logging.info('写入数据库')
                try:
                    sql.InsertData('ems_information_alarm_estimate', single_alarm_dict)
                except:
                    logging.warning("写入失败")
        logging.info("写入完毕")
