import json
import hashlib as _hl

#__all__ = ['hash_string_256', 'hash_block']


def hash_string_256(string):
    return _hl.sha256(string).hexdigest()


def hash_block(block):
    """Hashes a block and retrns a string representation of it.

    Arguments:
      :block" The block that should be hashed.
    """
    hashable_block = block.__dict__.copy()
    hashable_block['transactions'] = [
        tx.to_ordered_dict() for tx in hashable_block['transactions']]
    return hash_string_256(json.dumps(hashable_block, sort_keys=True).encode())
