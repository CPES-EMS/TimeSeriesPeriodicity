import time


def time_series_deal(time_series):
    """处理时间序列

    :param time_series: 输入main函数处理过的以sip，dip聚合的告警list
    :return:x是不为0的时间间隔，y为对应时间间隔在一个时间序列中出现的个数
    """
    time_list = []
    time_array = time.strptime(time_series[0][1], "%Y-%m-%d %H:%M:%S")
    # 转换为时间戳
    time_stamp_first = int(time.mktime(time_array))

    # 时间间隔序列
    for d in time_series:
        t = time.strptime(d[1], "%Y-%m-%d %H:%M:%S")
        time_stamp = int(time.mktime(t))
        time_list.append(time_stamp - time_stamp_first)
        time_stamp_first = time_stamp
    # 统计相同个数的时间间隔大小
    count_dict = {}
    for t in time_list:
        if t in count_dict.keys():
            count_dict[t] += 1
        else:
            count_dict[t] = 1
    # 按照出现次数大小排序(时间间隔，个数)
    count_dict = sorted(count_dict.items(), key=lambda i: i[0])
    x = []
    y = []
    for xy in count_dict:
        if xy[0] != 0:
            x.append(xy[0])
            y.append(xy[1])
    return x, y


def periodicity_judgment(x, y):
    """判断上述得到的间隔在告警序列中是否具有周期性

    :param x:时间间隔的列表
    :param y:相同时间间隔个数的列表
    :return:此时间间隔是否符合周期性要求，如果符合则返回周期值，符合周期性特征的告警总数
    """
    if x != []:
        num = sum(y)
        max_x = x[y.index(max(y))]
        if (x[0] == 1) and (y[0] >= 0.7 * num):
            return 1, y[0]
        else:
            # 判断第一个时间间隔
            period = x[0]
            period_alarm = 0
            es = period * 0.05
            if es >= 5:
                es = 5
            for i in range(len(x)):
                for ts in range(5):
                    if (x[i] <= (period * ts + es)) and (x[i] >= (period * ts - es)):
                        period_alarm += y[i]

            if period_alarm > 0.7 * num:
                return period, y[0]

            else:
                # 判断第二个时间间隔
                period = x[1]
                period_alarm = 0
                es = period * 0.05
                if es >= 5:
                    es = 5
                for i in range(len(x)):
                    for ts in range(5):
                        if (x[i] <= period * ts + es) and (x[i] >= period * ts - es):
                            period_alarm += y[i]
                if period_alarm > 0.7 * num:
                    return period, y[1]

                else:
                    return False
    else:
        return False
