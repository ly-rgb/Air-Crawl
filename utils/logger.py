# -*- coding:utf-8 -*-
__author__ = 'vfeng'
__date__ = '2020/2/10 18:30'

# -*- coding:utf-8 -*-
import logging.config
import os
from config import config

LOG_PATH = os.path.join(config.log_path, 'log')
if not os.path.exists(LOG_PATH):
    os.makedirs(LOG_PATH)

LOGGING = {
    # 基本设置
    'version': 1,  # 日志级别
    'disable_existing_loggers': False,  # 是否禁用现有的记录器

    # 日志格式集合
    'formatters': {
        # 标准输出格式
        'standard': {
            'format': '%(levelname)s [%(asctime)s][%(pathname)s %(module)s(%(lineno)d):%(funcName)s][%(thread)d]:%(message)s'
        }
    },

    # 过滤器
    'filters': {
        # 'require_debug_true': {
        #     '()': RequireDebugTrue,
        # }
    },

    # 处理器集合
    'handlers': {
        # 输出到控制台
        'console': {
            'level': 'DEBUG',  # 输出信息的最低级别
            'class': 'logging.StreamHandler',
            'formatter': 'standard',  # 使用standard格式
            # 'filters': ['require_debug_true', ],  # 仅当 DEBUG = True 该处理器才生效
        },
    },

    # 日志管理器集合
    'loggers': {
        # 管理器
        'default': {
            'handlers': ['console'],
            'level': logging.DEBUG,
            'propagate': True,  # 是否传递给父记录器
        },
    }
}


def add_log_handlers(name, level, log_path, maxBytes=1024 * 1024 * 100, backupCount=10, encoding='utf8'):

    handlers = {
        'level': level,
        'class': 'logging.handlers.TimedRotatingFileHandler',  # ConcurrentRotatingFileHandler
        'formatter': 'standard',
        'filename': os.path.join(log_path, '{}.log'.format(level)),  # 输出位置
        # 'maxBytes': 1024 * 1024 * 100,  # 文件大小 100M
        'when': 'D',
        'backupCount': config.log_count,  # 备份份数
        'encoding': 'utf8',  # 文件编码
    }
    key = "{}_{}".format(name, level)
    if key in LOGGING['handlers'].keys():
        raise Exception(f"handler {key} is exist")
    LOGGING['handlers']["{}_{}".format(name, level)] = handlers
    return key


def register_log(name):
    log_path = os.path.join(config.log_path, name)
    if not os.path.exists(log_path):
        os.makedirs(log_path)
    debug_handlers = add_log_handlers(name, "DEBUG", log_path)
    error_handlers = add_log_handlers(name, "ERROR", log_path)
    warning_handlers = add_log_handlers(name, "WARNING", log_path)
    handlers = ['console', debug_handlers, error_handlers, warning_handlers]
    if name in LOGGING['loggers'].keys():
        raise Exception(f"logger {name} is exist")
    LOGGING['loggers'][name] = {
        'handlers': handlers,
        'level': logging.DEBUG,
        'propagate': True,  # 是否传递给父记录器
    }
