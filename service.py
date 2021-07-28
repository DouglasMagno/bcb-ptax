import traceback

import requests

from helpers import string2datetime


class Service:

    def get_data_bcb_ptax(self, currency: str, start_date: str, end_date: str):

        url = "https://ptax.bcb.gov.br/ptax_internet/consultaBoletim.do"
        # string2datetime()
        params = {
            'method': 'gerarCSVFechamentoMoedaNoPeriodo',
            'ChkMoeda': currency,
            'DATAINI': string2datetime(start_date).strftime('%d/%m/%Y'),
            'DATAFIM': string2datetime(end_date).strftime('%d/%m/%Y')
        }

        try:
            response = requests.request("GET", url, params=params)
            return response.text
        except Exception as e:
            traceback.print_exc()
            return None


