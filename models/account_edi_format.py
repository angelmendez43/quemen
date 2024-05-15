# -*- coding: utf-8 -*-
from odoo import api, models, fields, tools, _
from odoo.tools.xml_utils import _check_with_xsd
from odoo.tools.float_utils import float_round, float_is_zero

import logging
import re
import base64
import json
import requests
import random
import string

from lxml import etree
from lxml.objectify import fromstring
from math import copysign
from datetime import datetime
from io import BytesIO
from json.decoder import JSONDecodeError

from odoo.tools.zeep import Client

_logger = logging.getLogger(__name__)
EQUIVALENCIADR_PRECISION_DIGITS = 10


class AccountEdiFormat(models.Model):
    _inherit = 'account.edi.format'


    def _l10n_mx_edi_get_common_cfdi_values(self, move):
        cfdi_common_values = super(AccountEdiFormat, self)._l10n_mx_edi_get_common_cfdi_values(move)
        cfdi_common_values.update({
            'anio': str(move.invoice_date.year),
            'meses': '{:02d}'.format(move.invoice_date.month),
            'periodicidad': "01",
        })
        logging.warning('_l10n_mx_edi_get_common_cfdi_values')
        logging.warning(cfdi_common_values)        
        return cfdi_common_values