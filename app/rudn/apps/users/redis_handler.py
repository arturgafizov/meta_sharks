from typing import Union, Optional

from django_redis import get_redis_connection
import json
from redis import Redis
from django.conf import settings


class RedisHandler():
    KEY_LOGIN_DOWNTIME = 'login_downtime'
    KEY_ADMIN_LOGIN_DOWNTIME = 'admin_login_downtime'
    KEY_PERCENT_INCOME = 'percent_income'
    KEY_MAX_SUM_INCOME_NO_PERCENT = 'max_sum_income_no_percent_swh'
    KEY_MAX_SUM_INCOME_NO_PERCENT_USDT = 'max_sum_income_no_percent_usdt'
    KEY_CURRENCY_TAXES = 'currency_taxes'
    KEY_MAX_SUM_WITHDRAW_NO_CHECK_SWH = 'sum_withdraw_with_check_swh'
    KEY_MAX_SUM_WITHDRAW_NO_CHECK_USDT = 'sum_withdraw_with_check_usdt'
    KEY_MAX_SUM_WITHDRAW_NO_CHECK_BTC = 'sum_withdraw_with_check_btc'
    KEY_SUM_ISSUE_SWH_DAILY = 'sum_issue_swh_daily'

    def __init__(self):
        self.redis: Redis = get_redis_connection()
        # self.redis.delete('sum_withdraw_with_check_btc')

    def get(self, key: str) -> Optional[str]:
        if value := self.redis.get(key):
            return value.decode('utf-8')
        return None

    def set(self, key: str, value: Union[str, int, float]):
        return self.redis.set(key, value)

    def lpush(self, key: str, *values):
        return self.redis.lpush(key, *values)

    def lrange(self, key: str, start: int, end: int) -> Optional[dict]:
        if values := self.redis.lrange(key, start, end):
            for value in values:
                str_value = value.decode("utf-8").replace("'", '"')
                json_value = json.loads(str_value)
                # print('json', json_value, type(json_value))
                # eval_value = eval(str_value)
                return json_value
        return None

    def get_currency_taxes(self):
        if currency_taxes := self.lrange(self.KEY_CURRENCY_TAXES, 0, -1):
            return currency_taxes
        self.lpush(self.KEY_CURRENCY_TAXES, str(settings.CURRENCY_TAXES))
        return settings.CURRENCY_TAXES

    def get_login_downtime(self) -> int:
        if login_downtime := self.get(self.KEY_LOGIN_DOWNTIME):
            return int(login_downtime)
        self.set(self.KEY_LOGIN_DOWNTIME, int(settings.LOGIN_DOWNTIME))
        return settings.LOGIN_DOWNTIME

    def get_admin_login_downtime(self) -> int:
        if admin_login_downtime := self.get(self.KEY_ADMIN_LOGIN_DOWNTIME):
            return int(admin_login_downtime)
        self.set(self.KEY_ADMIN_LOGIN_DOWNTIME, int(settings.ADMIN_LOGIN_DOWNTIME))
        return settings.ADMIN_LOGIN_DOWNTIME

    def get_percent_income(self) -> float:
        if percent_income := self.get(self.KEY_PERCENT_INCOME):
            return float(percent_income)
        self.set(self.KEY_PERCENT_INCOME, settings.PERCENT_INCOME)
        return settings.PERCENT_INCOME

    def get_max_sum_income_no_percent_swh(self) -> int:
        if max_sum_income_no_percent_swh := self.get(self.KEY_MAX_SUM_INCOME_NO_PERCENT):
            return int(max_sum_income_no_percent_swh)
        self.set(self.KEY_MAX_SUM_INCOME_NO_PERCENT, settings.MAX_SUM_INCOME_NO_PERCENT_SWH)
        return settings.MAX_SUM_INCOME_NO_PERCENT_SWH

    def get_max_sum_income_no_percent_usdt(self) -> int:
        if max_sum_income_no_percent_usdt := self.get(self.KEY_MAX_SUM_INCOME_NO_PERCENT_USDT):
            return int(max_sum_income_no_percent_usdt)
        self.set(self.KEY_MAX_SUM_INCOME_NO_PERCENT_USDT, settings.MAX_SUM_INCOME_NO_PERCENT_USDT)
        return settings.MAX_SUM_INCOME_NO_PERCENT_USDT

    def get_sum_withdraw_with_check_swh(self) -> int:
        if sum_withdraw_with_check_swh := self.get(self.KEY_MAX_SUM_WITHDRAW_NO_CHECK_SWH):
            return int(sum_withdraw_with_check_swh)
        self.set(self.KEY_MAX_SUM_WITHDRAW_NO_CHECK_SWH, settings.MAX_SUM_WITHDRAW_NO_CHECK_SWH)
        return settings.MAX_SUM_WITHDRAW_NO_CHECK_SWH

    def get_sum_withdraw_with_check_usdt(self) -> int:
        if sum_withdraw_with_check_usdt := self.get(self.KEY_MAX_SUM_WITHDRAW_NO_CHECK_USDT):
            return int(sum_withdraw_with_check_usdt)
        self.set(self.KEY_MAX_SUM_WITHDRAW_NO_CHECK_USDT, settings.MAX_SUM_WITHDRAW_NO_CHECK_USDT)
        return settings.MAX_SUM_WITHDRAW_NO_CHECK_USDT

    def get_sum_withdraw_with_check_btc(self) -> float:
        if sum_withdraw_with_check_btc := self.get(self.KEY_MAX_SUM_WITHDRAW_NO_CHECK_BTC):
            return float(sum_withdraw_with_check_btc)
        self.set(self.KEY_MAX_SUM_WITHDRAW_NO_CHECK_BTC, settings.MAX_SUM_WITHDRAW_NO_CHECK_BTC)
        return settings.MAX_SUM_WITHDRAW_NO_CHECK_BTC

    def get_sum_issue_swh_daily(self) -> int:
        if sum_issue_swh_daily := self.get(self.KEY_SUM_ISSUE_SWH_DAILY):
            return int(sum_issue_swh_daily)
        self.set(self.KEY_SUM_ISSUE_SWH_DAILY, settings.SUM_ISSUE_SWH_DAILY)
        return settings.SUM_ISSUE_SWH_DAILY
