import logging


def setup_logger() -> logging.Logger:
    """创建并返回 OpsAtlas 的日志对象。"""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    )

    return logging.getLogger("opsatlas")