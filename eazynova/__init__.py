# -*- coding: utf-8 -*-

from . import models
from . import wizard
from . import controllers

def post_init_hook(*args, **kwargs):
    """Hook post-installation du module EAZYNOVA Principal, compatible env ou cr, registry"""
    import logging
    _logger = logging.getLogger(__name__)
    if len(args) == 1:
        env = args[0]
        _logger.info("EAZYNOVA Core module installé avec succès (env)")
    elif len(args) == 2:
        cr, registry = args
        _logger.info("EAZYNOVA Core module installé avec succès (cr, registry)")
    else:
        _logger.warning("post_init_hook appelé avec une signature inattendue : %s", args)