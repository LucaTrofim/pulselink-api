import secrets
import string
import redis
from sqlalchemy.orm import Session
from app.models.link import Link
from app.core.config import settings

redis_client = redis.Redis.from_url(settings.REDIS_URL, decode_responses=True)

def _generate_code(length: int = 6) -> str:
    alphabet = string.ascii_letters + string.digits
    return "".join(secrets.choice(alphabet) for _ in range(length))

class LinkService:
    @staticmethod
    def create_link(db: Session, target_url: str, custom_alias: str | None = None) -> Link:
        code = custom_alias or _generate_code()
        if db.query(Link).filter(Link.short_code == code).first():
            raise ValueError("Alias already in use")

        link = Link(short_code=code, target_url=str(target_url))
        db.add(link)
        db.commit()
        db.refresh(link)

        redis_client.setex(f"link:{code}", settings.CACHE_TTL_SECONDS, link.target_url)
        return link

    @staticmethod
    def resolve_link(db: Session, short_code: str) -> str | None:
        cached_url = redis_client.get(f"link:{short_code}")
        if cached_url:
            redis_client.incr(f"clicks:{short_code}")
            return cached_url

        link = db.query(Link).filter(Link.short_code == short_code).first()
        if not link:
            return None

        link.clicks += 1
        db.commit()
        redis_client.setex(f"link:{short_code}", settings.CACHE_TTL_SECONDS, link.target_url)
        return link.target_url
