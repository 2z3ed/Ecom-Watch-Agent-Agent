class SourceRouter:
    SUPPORTED_SOURCE_TYPES = {"mock_playwright", "discovery", "static_scrapy"}

    def resolve(self, source_type: str) -> str:
        normalized = source_type.strip().lower()
        if normalized not in self.SUPPORTED_SOURCE_TYPES:
            supported = ", ".join(sorted(self.SUPPORTED_SOURCE_TYPES))
            raise ValueError(f"Unsupported source_type: {source_type}. Supported: {supported}")
        return normalized
