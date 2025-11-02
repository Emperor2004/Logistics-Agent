from dataclasses import dataclass
from datetime import datetime
from src.models.package import Package
from src.models.driver import Driver


@dataclass
class NewOrderEvent:
    package: Package
    timestamp: datetime


@dataclass
class DriverStatusEvent:
    driver: Driver
    timestamp: datetime