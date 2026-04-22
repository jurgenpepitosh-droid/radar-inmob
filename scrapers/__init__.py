"""Scraper registry — add a new portal by subclassing BaseScraper and registering here."""
from scrapers.base import BaseScraper
from scrapers.idealista import IdealistaScraper
from scrapers.fotocasa import FotocasaScraper
from scrapers.habitaclia import HabitacliaScraper
from scrapers.pisos_com import PisosComScraper

REGISTRY: dict[str, type[BaseScraper]] = {
    IdealistaScraper.portal_name: IdealistaScraper,
    FotocasaScraper.portal_name: FotocasaScraper,
    HabitacliaScraper.portal_name: HabitacliaScraper,
    PisosComScraper.portal_name: PisosComScraper,
}
