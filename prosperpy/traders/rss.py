# http://papers.ssrn.com/sol3/papers.cfm?abstract_id=962461
# SPY EFA AGG VNQ GLD

def initialize(context):
    context.securities = [sid(8554),sid(22972),sid(25485),sid(26669),sid(26807)]
    set_commission(commission.PerShare(cost=.005))
    leverage = 1.0
    context.top_k = 1
    context.weight = leverage/context.top_k

import numpy as np

@batch_transform(refresh_period=20, window_length=61)
def trailing_return(datapanel):
    if datapanel['price'] is None: return None
    pricedf = np.log(datapanel['price'])
    return pricedf.ix[-1]-pricedf.ix[0]

def reweight(context, data, weight, min_pct_diff=0.1):
    liquidity = context.portfolio.positions_value+context.portfolio.cash
    orders = {}
    pct_diff = 0
    for security in weight.keys():
        target = liquidity*weight[security]/data[security].price
        current = context.portfolio.positions[security].amount
        orders[security] = target-current
        pct_diff += abs(orders[security]*data[security].price/liquidity)
    if pct_diff > min_pct_diff:
        #log.info(("%s ordering %d" % (sec, target-current)))
        for security in orders.keys():
            order(security, orders[security])

def handle_data(context, data):
    ranks = trailing_return(data)
    abs_mom = lambda x: data[x].mavg(20)-data[x].mavg(200)

    if ranks is None: return
    ranked_securities = sorted(context.securities, key=lambda x: ranks[x], reverse=True)
    top_securities = ranked_securities[0:context.top_k]
    weight = dict(((security,context.weight if security in top_securities and abs_mom(security) > 0 else 0.0) for security in context.securities))
    reweight(context,data,weight)
