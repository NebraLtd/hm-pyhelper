from jsonrpcclient import request


class Client(object):

    def __init__(self, url='http://helium-miner:4467'):
        self.url = url

    def __fetch_data(self, method, **kwargs):
        response = request(self.url, method, **kwargs)
        return response.data.result

    def get_height(self):
        return self.__fetch_data('info_height')

    def get_region(self):
        return self.__fetch_data('info_region')

    def get_summary(self):
        return self.__fetch_data('info_summary')

    def get_peer_addr(self):
        return self.__fetch_data('peer_addr')

    def get_peer_book(self):
        return self.__fetch_data('peer_book', addr='self')
