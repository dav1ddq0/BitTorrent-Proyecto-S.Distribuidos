class PeerInfo:

    """Class to store the info of a peer in a tracker request"""

    def __init__(self, peer_id: str, ip_addr: str, port: str):
        self.peer_id: str = peer_id
        self.ip_addr: str = ip_addr
        self.port: str = port
