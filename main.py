from tracker import Tracker

def main():
    node1 = Tracker('10.1.1.1', '3128')
    node2 = Tracker('10.1.1.2', '3128')
    node3 = Tracker('10.1.1.3', '3128')
    node4 = Tracker('10.1.1.4', '3128')
    node5 = Tracker('10.1.1.5', '3128')
    node6 = Tracker('10.1.1.6', '3128')
    node7 = Tracker('10.1.1.7', '3128')
    node8 = Tracker('10.1.1.8', '3128')

    print(f'\nN1 {node1.chord_node.node_hash}')
    print(f'N2 {node2.chord_node.node_hash}')
    print(f'N3 {node3.chord_node.node_hash}\n')
    
    node1.chord_node.create_ring()
    node2.chord_node.create_ring()

    for i in range(160):
        node1.chord_node.fix_fingers()
        # node2.chord_node.fix_fingers()

    print(f'{node1.chord_node.finger_table[160].node.node_hash}')
    # print(node2.chord_node.finger_table[160].node.node_hash)

    # print(f'\n{len(node1.chord_node.finger_table)}')

    # print(node1.chord_node.successor.node_hash)
    node2.chord_node.join(node1.chord_node)
    node2.chord_node.stabilize()
    node1.chord_node.stabilize()

    print(f'{node1.chord_node.successor.node_hash}')
    print(f'{node1.node_hash}')
    print(f'{node2.node_hash}')
    print(f'{node1.chord_node.finger_table[160].start}')
    # print(2**160)
    # print(int.from_bytes(node1.node_hash, "big"))
    # print(int.from_bytes(node2.node_hash, "big"))
    node1.chord_node.fix_fingers()
    print(f'{node1.chord_node.finger_table[1].node.node_hash}')


    # node3.chord_node.create_ring()

    # for i in range(160):
    #     node3.chord_node.fix_fingers()

    # print(f'{node3.chord_node.finger_table[40].node.node_hash}')

    # print(node1.chord_node.finger_table[161]
    # node3.chord_node.join(node1.chord_node)

    # node3.chord_node.stabilize()
    # node2.chord_node.stabilize()
    # node1.chord_node.stabilize()

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

    
if __name__ == '__main__':
    main()
