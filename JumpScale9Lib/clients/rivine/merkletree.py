
# // A Tree takes data as leaves and returns the Merkle root. Each call to 'Push'
# // adds one leaf to the Merkle tree. Calling 'Root' returns the Merkle root.
# // The Tree also constructs proof that a single leaf is a part of the tree. The
# // leaf can be chosen with 'SetIndex'. The memory footprint of Tree grows in
# // O(log(n)) in the number of leaves.
class Tree:
    """
    // The Tree is stored as a stack of subtrees. Each subtree has a height,
	// and is the Merkle root of 2^height leaves. A Tree with 11 nodes is
	// represented as a subtree of height 3 (8 nodes), a subtree of height 1 (2
	// nodes), and a subtree of height 0 (1 node). Head points to the smallest
	// tree. When a new leaf is inserted, it is inserted as a subtree of height
	// 0. If there is another subtree of the same height, both can be removed,
	// combined, and then inserted as a subtree of height n + 1.
    """
    def __init__(self, hash_func):
        self.head = None
        self.hash_func = hash_func
        self._current_index = 0
        self._proof_index = 0
        self._proof_set = [[]]
    
    
    def push(self, data):
        """
        // Push will add data to the set, building out the Merkle tree and Root. The
        // tree does not remember all elements that are added, instead only keeping the
        // log(n) elements that are necessary to build the Merkle root and keeping the
        // log(n) elements necessary to build a proof that a piece of data is in the
        // Merkle tree.
        """
        if self._current_index == self._proof_index:
            self._proof_set.append(data)
        
        # // Hash the data to create a subtree of height 0. The sum of the new node
        # // is going to be the data for cached trees, and is going to be the result
        # // of calling leafSum() on the data for standard trees. Doing a check here
        # // prevents needing to duplicate the entire 'Push' function for the trees.
        self.head = SubTree(next=self.head, height=0)

        self.head.sum = leaf_sum(self.hash_func, data)
        
        # // Insert the subTree into the Tree. As long as the height of the next
        # // subTree is the same as the height of the current subTree, the two will
        # // be combined into a single subTree of height n+1.
        if self.head.next is not None and self.head.height == self.head.next.height:
            # // Before combining subtrees, check whether one of the subtree hashes
            # // needs to be added to the proof set. This is going to be true IFF the
            # // subtrees being combined are one height higher than the previous
            # // subtree added to the proof set. The height of the previous subtree
            # // added to the proof set is equal to len(t.proofSet) - 1.
            if self.head.height == len(self._proof_set) -1:
                # // One of the subtrees needs to be added to the proof set. The
                # // subtree that needs to be added is the subtree that does not
                # // contain the proofIndex. Because the subtrees being compared are
                # // the smallest and rightmost trees in the Tree, this can be
                # // determined by rounding the currentIndex down to the number of
                # // nodes in the subtree and comparing that index to the proofIndex.
                leaves = 1 << self.head.height
                mid = (self._current_index / leaves) * leaves
                if self._proof_index < mid:
                    self._proof_set.append(self.head.sum)
                else:
                    self._proof_set.append(self.head.next.sum)
                
            # // Join the two subTrees into one subTree with a greater height. Then
            # // compare the new subTree to the next subTree.
            self.head = join_subtree(self.hash_func, self.head.next, self.head)

        self._current_index += 1
    
    def root(self):
        """
        // Root returns the Merkle root of the data that has been pushed.
        """
        if self.head is None:
            return sum(self.hash_func, bytearray())

        # // The root is formed by hashing together subTrees in order from least in
        # // height to greatest in height. The taller subtree is the first subtree in
        # // the join.
        current = self.head
        while current.next is not None:
            current = join_subtree(self.hash_func, current.next, current)
        return current.sum
    

class SubTree:
    """
    // A subTree contains the Merkle root of a complete (2^height leaves) subTree
    // of the Tree. 'sum' is the Merkle root of the subTree. If 'next' is not nil,
    // it will be a tree with a higher height.
    """
    def __init__(self, next, height):
        self.next = next
        self.height = height
        self.sum = bytearray()
    

def sum_(hash_func, data):
    """
    // sum returns the hash of the input data using the specified algorithm.
    """
    if data is None:
        return None
    result = hash_func(data).digest()
    # print("Data is: {} Result is: {}".format(data.hex(), result.hex()))
    return result


def leaf_sum(hash_func, data):
    """
    // leafSum returns the hash created from data inserted to form a leaf. Leaf
    // sums are calculated using:
    //		Hash( 0x00 || data)
    """
    # print("Calling leafSum")
    data_ = bytearray([0])
    data_.extend(data)
    return sum_(hash_func, data_)

def node_sum(hash_func, a, b):
    """
    // nodeSum returns the hash created from two sibling nodes being combined into
    // a parent node. Node sums are calculated using:
    //		Hash( 0x01 || left sibling sum || right sibling sum)
    """
    # print("Calling node_sum")
    data_ = bytearray([1])
    data_.extend(a)
    data_.extend(b)
    return sum_(hash_func, data_)


def join_subtree(hash_func, a, b):
    """
    // joinSubTrees combines two equal sized subTrees into a larger subTree.
    """
    # print('Calling joinSubtree')
    stree = SubTree(next = a.next, height=a.height+1)
    stree.sum = node_sum(hash_func, a.sum, b.sum)
    return stree



if __name__ == '__main__':
    from pyblake2 import blake2b
    from functools import partial
    hash_func = partial(blake2b, digest_size=32)
    tree = Tree(hash_func=hash_func)
    a = bytearray([1])
    b = bytearray([2])
    c = bytearray([3])
    tree.push(a)
    tree.push(b)
    tree.push(c)
    root = tree.root().hex()
    assert root == '3029eb81c13fa0b1ed2a2130d985ba82072e9c3478b1a00c01c0407dfd5a037f'
    print('Root is {}'.format(root))
