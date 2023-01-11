class AuthWrapper:
    #{'access_token': '00D28000000dVa8!ARsAQFW1qnzGfcN1044jW6HibjRHyxa34I9aDugKh8fH4AS2k3XLQ0CE1WcNFj47PflYUTRiSO8Kyf..jcMwcqHNSvDG2xEz', 'instance_url': 'https://ashlightningtest-dev-ed.my.salesforce.com', 'id': 'https://login.salesforce.com/id/00D28000000dVa8EAE/00528000000TIgmAAG', 'token_type': 'Bearer', 'issued_at': '1673443263523', 'signature': 'VBK2w1FWUJPBqO+EeziCb2yTqg/evwj6tALTG9zTwwA='}
    def __init__(self,jsonResponse):
        self.access_token = jsonResponse['access_token']
        self.instance_url = jsonResponse['instance_url']
        self.issued_at = jsonResponse['issued_at']

