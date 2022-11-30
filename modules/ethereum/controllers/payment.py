from django.conf import settings
from django.http.request import HttpRequest
from django.http.response import HttpResponse, HttpResponseRedirect, HttpResponseNotModified
from payments.modules.ethereum.signals import *
from payments.settings import PLUGIN_NAME
import json
import web3

# for getting the current ethereum crypto price use
"""
  GET https://min-api.cryptocompare.com/data/price?fsym=ETH&tsyms=BTC,USD,EUR
  also 
  https://www.coinapi.io/ 
  it could be a good api
"""
class EthereumNetwork():
  provider: web3.Web3.HTTPProvider = None
  w3: web3.Web3 = None
  @classmethod
  async def get_node(cls,) -> web3.Web3:
    if not cls.w3:
      cls.provider = web3.Web3.HTTPProvider(endpoint_uri="http://127.0.0.1:7545")
      cls.w3 = web3.Web3(provider=cls.provider)
    return cls.w3


async def make_payment(request: HttpRequest, *args, **kwargs):
  """
   The philosophy of this entire module it is to make payments easier but securest as well, each payment must be verified
   also in backend getting as little as possible data from user or in case is possible getting only authorized payment from user
   ( This is the case of paypal but not cryptos) and make the payment in the backend, in this case (ethereum case) we are only
   verifying the request in the backend but not actually making the payment in it.. ( that will be great if we could theorically
   )
  """
  data = json.loads(request.body)
  node = await EthereumNetwork.get_node()
  transaction = node.eth.get_transaction(data.get("transaction_id"))
  if transaction:
    payment_accepted.send(transaction, **{
      "request": request,
      "args": args,
      "kwargs": kwargs
    })
  else:
    payment_rejected.send(data.get("transaction_id"), **{
      "request": request,
      "args": args,
      "kwargs": kwargs
    })
  return HttpResponse(request.body)
