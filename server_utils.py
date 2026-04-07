"""
Automatically extracted utility functions
"""


# _generate_key
    def _generate_key(self, prompt: str, model: str, options: Dict[str, Any]) -> str:
        """Generate cache key from request parameters"""
        key_data = f"{prompt}:{model}:{json.dumps(options, sort_keys=True)}"
        return hashlib.sha256(key_data.encode()).hexdigest()
