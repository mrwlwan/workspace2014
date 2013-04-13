# coding=utf8

import os, sys, json

# 是否SAE部署.
is_ae = 'SERVER_SOFTWARE' in os.environ
is_sae = is_ae
is_bae = is_ae
# 是否 Python 3.
is_py3 = tuple(sys.version_info)[0] >= 3


if is_ae:
    from bae.api import logging
else:
    import logging
    logging.basicConfig(level=logging.DEBUG)

