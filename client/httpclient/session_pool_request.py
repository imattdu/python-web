import copy

import requests
import threading
from typing import Dict, Any, List, Tuple, Optional
from time import time, sleep
from itertools import cycle

from flask import g, has_app_context
from requests import Response

from common.logger.logger import get_logger, info, warning
from common.trace.trace import Trace, random_id, HEADER_TRACE_ID, HEADER_SPAN_ID, HEADER_PARENT_SPAN_ID

logger = get_logger()


class SessionPoolHttpClient:
    def __init__(self, pool_size: int = 5, timeout: float = 10.0,
                 retries: int = 3, default_headers: Dict[str, str] = None):
        """
        :param pool_size: Session 池大小（通常 = 线程池大小）
        :param timeout: 超时时间
        :param retries: 重试次数
        :param default_headers: 默认请求头
        """
        self.timeout = timeout
        self.retries = retries
        self.default_headers = default_headers or {}
        self._sessions: List[requests.Session] = []

        # 初始化 session 池
        for _ in range(pool_size):
            s = requests.Session()
            s.headers.update(self.default_headers)
            self._sessions.append(s)

        # 循环分配 session
        self._session_cycle = cycle(self._sessions)

        # 线程局部变量，每个线程绑定一个 session
        self._local = threading.local()

    def _get_session(self) -> requests.Session:
        if not hasattr(self._local, "session"):
            # 给新线程分配一个 session（轮询方式）
            self._local.session = next(self._session_cycle)
        return self._local.session

    def _request(self, method: str, url: str, data: Dict[str, Any] = None,
                 params: Dict[str, Any] = None, headers: Dict[str, str] = None) -> Tuple[Dict[str, Any], Optional[Exception]]:
        attempt = 0
        session = self._get_session()
        merged_headers = {**self.default_headers, **(headers or {})}

        log_dict = {
            'url': url,
            'params': params,
            'headers': merged_headers,
            'data': data,
            'rpc_final': False,
        }
        resp = Response()
        trace = Trace()
        # 只有在 Flask 上下文可用时才访问 g
        if has_app_context():
            trace = getattr(g, "trace", trace)
        while attempt <= self.retries:
            cur_trace = copy.deepcopy(trace)
            cur_trace.parent_span_id = random_id(16)
            log_dict['attempt'] = attempt

            merged_headers[HEADER_TRACE_ID] = cur_trace.trace_id
            merged_headers[HEADER_PARENT_SPAN_ID] = cur_trace.parent_span_id
            merged_headers[HEADER_SPAN_ID] = cur_trace.span_id
            start_time = time()
            try:
                resp = session.request(
                    method=method.upper(),
                    url=url,
                    json=data,
                    params=params,
                    headers=merged_headers,
                    timeout=self.timeout
                )
                resp.raise_for_status()
                proc_time = time() - start_time
                code = 0
                err = ''

                log_dict['rpc_final'] = True
                log_dict['proc_time'] = proc_time
                log_dict['code'] = code
                exception = None
                try:
                    result = resp.json()
                    log_dict['response'] = result
                    info('_com_http_success', log_dict, trace=cur_trace)
                except Exception as e:
                    exception = e
                    err = str(e)
                    code = 1000
                    result = resp.text
                    log_dict['response'] = result
                    log_dict['code'] = code
                    log_dict['err'] = err
                    warning('_com_http_failure', log_dict, trace=cur_trace)
                return {
                    "response": result,
                    "code": code,
                    "err": err,
                }, exception
            except requests.HTTPError as e:
                exception = e
                code = resp.status_code
                err = str(e)
                rpc_final = attempt >= self.retries

                log_dict['rpc_final'] = rpc_final
                warning('_com_http_failure', log_dict, trace=cur_trace)
                if rpc_final:
                    return {"code": code, "err": err}, exception
                sleep(0.5)
                attempt += 1
            except requests.RequestException as e:
                exception = e
                code = 1000
                err = str(e)
                rpc_final = attempt >= self.retries
                log_dict['code'] = code
                log_dict['err'] = err
                log_dict['rpc_final'] = rpc_final
                warning('_com_http_failure', log_dict, trace=cur_trace)
                if rpc_final:
                    return {"code": code, "err": err}, exception
                sleep(0.5)
                attempt += 1

    def get(self, url: str, params: Dict[str, Any] = None, headers: Dict[str, str] = None) -> Tuple[Dict[str, Any], Optional[Exception]]:
        return self._request("GET", url, params=params, headers=headers)

    def post(self, url: str, data: Dict[str, Any] = None, headers: Dict[str, str] = None) -> Tuple[Dict[str, Any], Optional[Exception]]:
        return self._request("POST", url, params=data, headers=headers)


global_session_pool_http_client = SessionPoolHttpClient(10, 10, 3, {
    'Content-Type': 'application/json',
})
