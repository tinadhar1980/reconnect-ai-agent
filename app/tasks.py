from .worker import celery
from .db import SessionLocal
from .models import Guest, Stay
from datetime import datetime
from .embeddings import embed_text, to_list, from_list, cosine_similarity
from .llm_agent import decide_offer
from .faiss_index import get_faiss_index
import json, os, requests

POS_CONCEPT = "Wonderful, happy, excellent stay"
NEG_CONCEPT = "Awful, terrible, dirty room"

_pos_vec = None
_neg_vec = None

def ensure_concept_vectors():
    global _pos_vec, _neg_vec
    if _pos_vec is None:
        _pos_vec = embed_text(POS_CONCEPT)
    if _neg_vec is None:
        _neg_vec = embed_text(NEG_CONCEPT)
    return _pos_vec, _neg_vec

@celery.task(name="app.tasks.process_checkout")
def process_checkout(event_payload: dict):
    db = SessionLocal()
    try:
        guest = db.query(Guest).filter_by(guest_id=event_payload["guest_id"]).one_or_none()
        if guest is None:
            guest = Guest(guest_id=event_payload["guest_id"], metadata={})
            db.add(guest)
            db.flush()

        existing = db.query(Stay).filter_by(stay_id=event_payload["stay_id"]).one_or_none()
        if existing:
            print("Duplicate stay detected; skipping.")
            return {"status":"duplicate"}

        review_text = event_payload.get("review_text", "")
        emb = embed_text(review_text)
        pos_vec, neg_vec = ensure_concept_vectors()
        pos_score = cosine_similarity(emb, pos_vec)
        neg_score = cosine_similarity(emb, neg_vec)

        co_date = datetime.fromisoformat(event_payload["check_out_date"])
        stay = Stay(
            stay_id=event_payload["stay_id"],
            guest_id_fk=guest.id,
            check_out_date=co_date,
            total_spend=float(event_payload["total_spend"]),
            review_text=review_text,
            positive_score=pos_score,
            negative_score=neg_score,
            embedding=json.dumps(to_list(emb))
        )
        db.add(stay)

        guest.stays_count = (guest.stays_count or 0) + 1
        guest.total_lifetime_spend = (guest.total_lifetime_spend or 0.0) + float(event_payload["total_spend"])
        prev_avg = guest.average_sentiment or 0.0
        guest.average_sentiment = ((prev_avg * (guest.stays_count - 1)) + pos_score) / (guest.stays_count)
        guest.last_stay_date = co_date

        db.commit()

        # Index embedding in FAISS
        faiss_index = get_faiss_index()
        faiss_index.add(vecs=from_list(emb).reshape(1,-1), stay_ids=[stay.stay_id])

        evaluate_reconnect_offer.delay(guest.guest_id)
        return {"status":"queued_analysis"}
    except Exception as e:
        db.rollback()
        print("Error in process_checkout:", e)
        raise
    finally:
        db.close()

@celery.task(name="app.tasks.evaluate_reconnect_offer")
def evaluate_reconnect_offer(guest_id: str):
    db = SessionLocal()
    try:
        guest = db.query(Guest).filter_by(guest_id=guest_id).one_or_none()
        if not guest:
            print("Guest not found:", guest_id)
            return

        profile = {
            "guest_id": guest.guest_id,
            "total_lifetime_spend": guest.total_lifetime_spend or 0.0,
            "average_sentiment": guest.average_sentiment or 0.0,
            "stays_count": guest.stays_count or 0,
            "last_stay_date": guest.last_stay_date.isoformat() if guest.last_stay_date else None
        }

        decision = decide_offer(profile)
        if decision.get("action") == "send_offer":
            payload = {"guest_id": guest.guest_id, "template_name": decision.get("offer_type")}
            notification_url = os.getenv("NOTIFICATION_URL", "http://web:8000/mock-api/send-notification")
            try:
                r = requests.post(notification_url, json=payload, timeout=5)
                print("Notification sent:", r.status_code, r.text)
            except Exception as e:
                print("Failed to call notification:", e)
        else:
            guest.metadata = guest.metadata or {}
            guest.metadata["flagged_for_review"] = True
            db.add(guest)
            db.commit()
        return {"decision": decision}
    except Exception as e:
        print("Error in evaluate_reconnect_offer:", e)
        raise
    finally:
        db.close()
