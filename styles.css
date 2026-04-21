"""Core data models."""
from dataclasses import dataclass, field, asdict
from typing import Optional, List


@dataclass
class Listing:
    portal: str              # 'idealista', 'fotocasa', 'habitaclia', 'pisos'
    external_id: str         # Portal's native ID
    url: str
    title: str
    price: int               # EUR/month
    rooms: Optional[int] = None
    bathrooms: Optional[int] = None
    size_m2: Optional[int] = None
    location: str = ""       # Normalized location slug
    raw_location: str = ""   # What the portal showed
    description: str = ""
    images: List[str] = field(default_factory=list)
    features: List[str] = field(default_factory=list)

    @property
    def uid(self) -> str:
        """Stable unique ID across portals and runs."""
        return f"{self.portal}:{self.external_id}"

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class ListingChange:
    listing: Listing
    change_type: str  # 'new' | 'price_drop' | 'price_rise' | 'removed' | 'relisted'
    old_price: Optional[int] = None
    new_price: Optional[int] = None

    @property
    def price_delta(self) -> Optional[int]:
        if self.old_price is not None and self.new_price is not None:
            return self.new_price - self.old_price
        return None

    @property
    def price_delta_pct(self) -> Optional[float]:
        if self.old_price and self.new_price:
            return round((self.new_price - self.old_price) / self.old_price * 100, 1)
        return None
