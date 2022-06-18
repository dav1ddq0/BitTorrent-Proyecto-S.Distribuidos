class ChordNode:

    """Our implementation of a chord node"""

    def __init__(self, node_hash: bytes, node_ip: str, node_port: str):
        self.node_hash: bytes = node_hash
        self.node_ip = node_ip
        self.node_port = node_port
        self.finger_table = self.__initialize_fingers()
        self.dht: dict[bytes, list[str]] = {}
        self.next_to_fix: int = 0

    def __initialize_fingers(self):
        table = [FingerTableItem(1, None)]
        hash_int_val = int.from_bytes(self.node_hash, "big")
        for i in range(1, 161):
            finger_int = hash_int_val + 2 ** (i - 1)
            table.append(FingerTableItem(finger_int, None))

        return table

    def create_ring(self) -> None:
        self.predecessor = None
        self.successor = self

    def find_successor(self, identifier: bytes) -> "ChordNode":
        if (
            ChordNode.in_range_incl(
                identifier, self.node_hash, self.successor.node_hash
            )
            or self == self.successor
        ):
            return self.successor

        prev_node = self.closest_prec_node(identifier)
        return prev_node.find_successor(identifier)

    def closest_prec_node(self, identifier) -> "ChordNode":
        for i in range(len(self.finger_table) - 1, 0, -1):
            finger_i = self.finger_table[i]
            if ChordNode.in_range_excl(
                finger_i.node.node_hash, self.node_hash, identifier
            ):
                return finger_i.node
        # print('ASD')
        return self

    def join(self, other_node: "ChordNode") -> None:
        self.predecessor = None
        self.successor = other_node.find_successor(self.node_hash)

    def stabilize(self) -> None:
        if self.successor.predecessor:
            x = self.successor.predecessor
            if (
                ChordNode.in_range_excl(
                    x.node_hash, self.node_hash, self.successor.node_hash
                )
                or self.successor == self
            ):
                self.successor = x

        self.successor.notify(self)

    def notify(self, new_node: "ChordNode") -> None:
        if not self.predecessor or ChordNode.in_range_excl(
            new_node.node_hash, self.node_hash, self.predecessor.node_hash
        ):
            self.predecessor = new_node

    def fix_fingers(self) -> None:
        self.next_to_fix += 1
        if self.next_to_fix > len(self.finger_table) - 1:
            self.next_to_fix = 1

        hash_int_val = int.from_bytes(self.node_hash, "big")
        finger_int = (hash_int_val + 2 ** (self.next_to_fix - 1)) % (2**160)
        finger_hash = finger_int.to_bytes(hash_int_val.bit_length(), "big")
        self.finger_table[self.next_to_fix].node = self.find_successor(finger_hash)

    @staticmethod
    def in_range_excl(val: bytes, lower_b: bytes, upper_b: bytes):
        return lower_b < val < upper_b or (
            lower_b > upper_b and (val > lower_b or val < upper_b )
        )

    @staticmethod
    def in_range_incl(val: bytes, lower_b: bytes, upper_b: bytes):
        return lower_b < val <= upper_b or (
            lower_b > upper_b and (val > lower_b or val <= upper_b)
        )


class FingerTableItem:

    """Our implementation of a finger table item"""

    def __init__(self, start: int, node):
        self.start = start
        self.node: ChordNode = node
