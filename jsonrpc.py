from bitcoinrpc.authproxy import AuthServiceProxy

class JsonRpc:
  
  def __init__(self,conn_string):
    self.conn = AuthServiceProxy(conn_string)
  
  def getTransaction(self, tx_id):
    return self.conn.getrawtransaction(tx_id, 1)

  def getTxs(self, pub_key):
    txs=self.conn.searchrawtransactions(pub_key, 1, 0, 2000)
    return txs

  def getInBalance(self, txs, pub_key):
    inBalance = float(0.0)
  
    if not txs:
      return inBalance

    for tx in txs:
      for inputs in tx['vin']:
        input_tx = self.getTransaction(inputs['txid'])
        vout = inputs['vout']

        #match output addresses for the given public key
        for outputs in input_tx['vout']:
          output = outputs['scriptPubKey']
          if outputs['n'] == vout:
            if output['addresses'].__contains__(pub_key):
              inBalance = inBalance + float(outputs['value'])
    
    return inBalance
  
  def getOutBalance(self, txs, pub_key):
    outBalance = float(0.0)

    if not txs:
      return outBalance

    for tx in txs:
      for outputs in tx['vout']:
        output = outputs['scriptPubKey']
        if output['addresses'].__contains__(pub_key):
          outBalance = outBalance + float(outputs['value'])
    return outBalance
  
  def getOtherInPubKeys(self, tx_id, pub_key):
    assoc_keys = []

    #match output addresses for the given public key
    #if it matches add other public keys as associated keys for the given
    #public key
    found = False
    
    tx = self.getTransaction(tx_id)
    for inputs in tx['vin']:
      input_tx = self.getTransaction(inputs['txid'])
      vout = inputs['vout']
      
      for outputs in input_tx['vout']:
        output = outputs['scriptPubKey']
        if outputs['n'] == vout:
          if output['addresses'].__contains__(pub_key):
            found = True
          else:
            assoc_keys += output['addresses']

    if found:
      return assoc_keys
    else:
      return []
  
  def getUserKeys(self, pub_key): 
    user_keys = [pub_key]
    key_stack = [pub_key]

    while len(key_stack):
      top_key = key_stack.pop()
      txids = map(lambda x:x['txid'], self.getTxs(top_key))
      for tx_id in txids:
        for key in self.getOtherInPubKeys(tx_id, top_key):
          if not user_keys.__contains__(key):
            key_stack.append(key)
            user_keys.append(key)
            
    return user_keys

