from dataclasses import dataclass, field
from typing import List, Optional
from datetime import datetime


@dataclass
class Job:
    title: str
    company: str
    location: str = ""
    description: str = ""
    url: str = ""
    source: str = ""
    ats: str = ""
    date_posted: Optional[datetime] = None
    discovered_at: datetime = field(default_factory=datetime.utcnow)

    def key(self):
        """Unique key used for deduplication."""
        return (
            self.company.strip().lower(),
            self.title.strip().lower(),
            self.location.strip().lower(),
        )


@dataclass
class Firm:
    name: str
    website: str = ""
    careers_url: str = ""
    ats: str = ""
    city: str = ""
    state: str = ""
    employee_count: Optional[int] = None
    aum: Optional[float] = None
    independent_ria: bool = False


@dataclass
class DiscoveryResult:
    jobs: List[Job]
    firms: List[Firm]
