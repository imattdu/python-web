from enum import Enum
from typing import Any, Dict


class Code(Enum):
    ExternalExceptionTypeSys = (1, '系统错误')
    ExternalExceptionTypeService = (1, '服务错误')
    ExternalExceptionTypeBiz = (5, '业务错误')

    ServiceTypeBasic = (4, '组件')
    ServiceTypeService = (5, '服务')
    ServiceRedis = (4, 'mysql')

    def __int__(self, code, desc):
        self.code = code
        self.desc = desc


class ExceptionX(Exception):
    message = ''
    code = 0

    is_extern_err = False
    extern_err_type = 0
    service_type = ''
    service = ''
    err_type = 0
    is_success = False
    inner_code = 0

    def __init__(self, message: str, code: int, is_extern_err: bool = False, extern_err_type: int = -1,
                 service_type: int = -1, service: int = -1, err_type: int = -1, is_success: bool = False):
        super().__init__(message)
        self.message = message
        self.code = 1000

    def __str__(self):
        return f"{self.message}"


def wrap_exception_x(exception: Exception, is_extern_err: bool = False, extern_err_type: int = -1,
                     service_type: int = -1, service: int = -1, err_type: int = -1, is_success: bool = False):
    """
    将任意 Exception 包装成 ExceptionX
    """
    if exception is None:
        return None
    if isinstance(exception, ExceptionX):
        return exception
    return ExceptionX(str(exception), code=1000)


# 使用示例
if __name__ == "__main__":
    print(1)
