import threading
from random import randint

from tracker import Tracker


def bg_fix_fingers(nodes: list[Tracker], func_stop: threading.Event):
    for node in nodes:
        for i in range(160):
            node.chord_node.fix_fingers()

    print("Fingers fixed !!!!!!!!!!!!!!!!!!!!!!!!!!")

    if not func_stop.is_set():
        threading.Timer(2, bg_fix_fingers, [nodes, func_stop]).start()


def bg_chord_stabilization(nodes: list[Tracker], func_stop: threading.Event):
    stabilize_chord_ring(nodes)
    if not func_stop.is_set():
        threading.Timer(1, bg_chord_stabilization, [nodes, func_stop]).start()


def stabilize_chord_ring(nodes: list[Tracker]):
    for index in range(len(nodes)):
        nodes[index].chord_node.stabilize()
        print(f"Node with index {index} stabilized !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")

    for index in range(len(nodes)):
        if nodes[index].chord_node.successor:
            int_val = int.from_bytes(nodes[index].chord_node.successor.node_hash, "big")
            print(f"Successor of node with index {index} is   {int_val}")
        else:
            print(f"Successor of node with index {index} unexistant")

        if nodes[index].chord_node.predecessor:
            int_val = int.from_bytes(
                nodes[index].chord_node.predecessor.node_hash, "big"
            )
            print(f"Predecessor of node with index {index} is {int_val}")
        else:
            print(f"Predecessor of node with index {index} unexistant")


def connect(client_index: int, server_index: int, nodes: list[Tracker]):
    client = nodes[client_index]
    server = nodes[server_index]
    client.chord_node.join(server.chord_node)
    print(
        f"Node with index {client_index} joined the chord ring of the node with index {server_index}"
    )


def main():

    # //\\// ----------------------- Random testing ---------------------- //\\//

    nodes_amount = 3
    nodes = []

    for i in range(nodes_amount):
        ip_hunk1 = randint(1, 255)
        ip_hunk2 = randint(1, 255)
        ip_hunk3 = randint(1, 255)
        ip_hunk4 = randint(1, 255)
        port = randint(1, 1 << 16)
        new_tracker = Tracker(f"{ip_hunk1}.{ip_hunk2}.{ip_hunk3}.{ip_hunk4}", f"{port}")
        new_tracker.chord_node.create_ring()
        nodes.append(new_tracker)

    host_ring_index = randint(0, nodes_amount - 1)
    host_ring = nodes[host_ring_index]
    idle_trackers = [index for index in range(len(nodes)) if index != host_ring_index]

    print(f"host will be node with index {host_ring_index} :D")

    bg_chord_stabilization_stop = threading.Event()
    bg_chord_stabilization(nodes, bg_chord_stabilization_stop)

    bg_fix_fingers_stop = threading.Event()
    bg_fix_fingers(nodes, bg_fix_fingers_stop)

    for index in range(len(idle_trackers)):
        next = 0
        if len(idle_trackers) != 1:
            next = randint(1, len(idle_trackers) - 1)

        next_index = idle_trackers[next]
        idle_trackers.remove(next_index)
        time = randint(1, 10)
        print(
            f"node with index {next_index} will be joining the host ring after {time} seconds"
        )
        threading.Timer(time, connect, [next_index, host_ring_index, nodes]).start()

    # //\\// ----------------------- Simple testing ---------------------- /\\//


#     node1 = Tracker('10.1.1.1', '3128')
#     node2 = Tracker('10.1.1.2', '3128')
#     node3 = Tracker('10.1.1.3', '3128')
#     node4 = Tracker('10.1.1.4', '3128')
#     node5 = Tracker('10.1.1.5', '3128')
#     node6 = Tracker('10.1.1.6', '3128')
#     node7 = Tracker('10.1.1.7', '3128')
#     node8 = Tracker('10.1.1.8', '3128')

#     print(f'\nN1 {node1.chord_node.node_hash}')
#     print(f'N2 {node2.chord_node.node_hash}')
#     print(f'N3 {node3.chord_node.node_hash}\n')

#     node1.chord_node.create_ring()
#     node2.chord_node.create_ring()

# for i in range(160):
#     node1.chord_node.fix_fingers()
#     node2.chord_node.fix_fingers()

# print(f'{node1.chord_node.finger_table[160].node.node_hash}')
# print(node2.chord_node.finger_table[160].node.node_hash)

# print(f'\n{len(node1.chord_node.finger_table)}')

# print(node1.chord_node.successor.node_hash)
# print('Before stabilizing the ring')
# print(f'{node1.chord_node.finger_table[160].node.node_hash}')
# print(f'{node2.node_hash}')
# print(f'{node2.chord_node.finger_table[159].node.node_hash}')
# print(f'{node1.node_hash}')

# node2.chord_node.join(node1.chord_node)
# node2.chord_node.stabilize()
# node1.chord_node.stabilize()

# print(f'{node1.chord_node.successor.node_hash}')
# print(f'{node1.node_hash}')
# print(f'{node2.node_hash}')
# print(f'{node1.chord_node.finger_table[160].start}')
# print(2**160)

# print(f'{node2.chord_node.successor.node_hash}')

# for i in range(160):
#     node1.chord_node.fix_fingers()
#     node2.chord_node.fix_fingers()

# print(f'2^160 -------------------- {2**160}')
# print(f'{int.from_bytes(node1.node_hash, "big")}')
# print(f'{int.from_bytes(node2.node_hash, "big")}')
# print(f'{int.from_bytes(node3.node_hash, "big")}')
# print(f'{int.from_bytes(node1.chord_node.node_hash, "big")}')

# node3.chord_node.create_ring()

# for i in range(160):
#     node3.chord_node.fix_fingers()

# print(f'{node3.chord_node.finger_table[40].node.node_hash}')

# print(node1.chord_node.finger_table[161]
# node3.chord_node.join(node1.chord_node)

# node3.chord_node.stabilize()
# node1.chord_node.stabilize()
# node2.chord_node.stabilize()

# print(f'node1 successor {node1.chord_node.successor.node_hash}')
# print(f'node1 predecessor {node1.chord_node.predecessor.node_hash}')
# print(f'node2 successor {node2.chord_node.successor.node_hash}')
# print(f'node2 predecessor {node2.chord_node.predecessor.node_hash}')
# print(f'node3 successor {node3.chord_node.successor.node_hash}')
# print(f'node3 predecessor {node3.chord_node.predecessor.node_hash}')

# for i in range(160):
#     node1.chord_node.fix_fingers()
#     node2.chord_node.fix_fingers()
#     node3.chord_node.fix_fingers()

# print('After stabilizing the ring')
# print(f'node 1 last finger node hash {node1.chord_node.finger_table[160].node.node_hash}')
# print(f'node 1                  hash {node1.node_hash}')
# print(f'node 2 last finger node hash {node2.chord_node.finger_table[160].node.node_hash}')
# print(f'node 2 hash                  {node2.node_hash}')
# print(f'node 3 last finger node hash {node3.chord_node.finger_table[160].node.node_hash}')
# print(f'node 3                  hash {node3.node_hash}')

# print(node2.chord_node.node_hash < node1.chord_node.node_hash)
# print(node3.chord_node.node_hash < node1.chord_node.node_hash)
# print(node3.chord_node.node_hash < node2.chord_node.node_hash)
# print(f'N1\'s successor hash {node1.chord_node.successor.node_hash}')
# print(f'N1\'s predecessor hash {node1.chord_node.predecessor.node_hash}')
# print(f'N2\'s successor hash {node2.chord_node.successor.node_hash}')
# print(f'N2\'s predecessor hash {node2.chord_node.predecessor.node_hash}')
# print(f'N3\'s successor hash {node3.chord_node.successor.node_hash}')
# print(f'N3\'s predecessor hash {node3.chord_node.predecessor.node_hash}')

# my_int = 12345678
# bytes = my_int.to_bytes(5, 'big')
# print(f'\n{bytes}')
# int_from_bytes = int.from_bytes(bytes, 'big')
# print(int_from_bytes)
# print(my_int)
# bytes = int_from_bytes.to_bytes(5, 'big')
# print(bytes)


if __name__ == "__main__":
    main()
