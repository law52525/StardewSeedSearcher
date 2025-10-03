"""
Core functionality for hash and random seed calculations
Based on Underscore76's implementation
"""

import xxhash
from typing import List


class HashHelper:
    """Provides hash and random seed calculation functionality"""
    
    def __init__(self):
        self.hasher = xxhash.xxh32(seed=0)
    
    def get_hash_from_string(self, value: str) -> int:
        """Get deterministic hash value from string"""
        data = value.encode('utf-8')
        return self.get_hash_from_bytes(data)
    
    def get_hash_from_array(self, *values: int) -> int:
        """Get deterministic hash value from integer array"""
        data = bytearray()
        for value in values:
            # Convert to little-endian 32-bit unsigned integer (like Go's binary.LittleEndian.PutUint32)
            # Handle negative values by converting to unsigned 32-bit representation
            if value < 0:
                # Convert negative int to unsigned 32-bit representation
                unsigned_value = value + 2**32
            else:
                unsigned_value = value
            data.extend(unsigned_value.to_bytes(4, byteorder='little', signed=False))
        return self.get_hash_from_bytes(bytes(data))
    
    def get_hash_from_bytes(self, data: bytes) -> int:
        """Get deterministic hash value from byte array"""
        # Reset hasher to initial state
        self.hasher.reset()
        self.hasher.update(data)
        hash32 = self.hasher.intdigest()
        
        # Simulate Go's int32(hash32) behavior
        # Convert to signed 32-bit integer
        if hash32 >= 2**31:
            return hash32 - 2**32
        else:
            return hash32
    
    def get_random_seed(self, a: int, b: int, c: int, d: int, e: int, use_legacy_random: bool) -> int:
        """Calculate random seed
        Simulates StardewValley.Utility.CreateRandomSeed()
        """
        # Ensure parameters are within valid range (like Go's modulo behavior)
        def go_modulo(x: int, m: int) -> int:
            """Go-style modulo that preserves sign for negative numbers"""
            # In Go, negative numbers modulo positive numbers return negative numbers
            # Python's % always returns positive, so we need to adjust
            result = x % m
            if x < 0 and result > 0:
                return result - m
            return result
        
        a = go_modulo(a, 2147483647)
        b = go_modulo(b, 2147483647)
        c = go_modulo(c, 2147483647)
        d = go_modulo(d, 2147483647)
        e = go_modulo(e, 2147483647)
        
        if use_legacy_random:
            # Legacy random: simple addition with modulo (like Go's int64 calculation)
            total = (a + b + c + d + e) % 2147483647
            return total
        else:
            # New random: use XXHash
            return self.get_hash_from_array(a, b, c, d, e)


# Global instance for convenience
_default_hash_helper = HashHelper()


def get_hash_from_string(value: str) -> int:
    """Convenience function using global instance"""
    helper = HashHelper()
    return helper.get_hash_from_string(value)


def get_hash_from_array(*values: int) -> int:
    """Convenience function using global instance"""
    helper = HashHelper()
    return helper.get_hash_from_array(*values)


def get_random_seed(a: int, b: int, c: int, d: int, e: int, use_legacy_random: bool) -> int:
    """Convenience function using global instance"""
    helper = HashHelper()
    return helper.get_random_seed(a, b, c, d, e, use_legacy_random)
