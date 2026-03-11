from app import create_app, db
from app.models.user import User
from app.models.place import Place, place_amenity
from app.models.review import Review
from app.models.amenity import Amenity
import os


def ok(msg: str) -> None:
    print(f"[OK] {msg}")


def fail(msg: str, err: Exception) -> None:
    print(f"[FAIL] {msg}: {type(err).__name__}: {err}")


def run_tests() -> None:
    app = create_app()

    with app.app_context():
        # Reset DB
        db.drop_all()
        db.create_all()
        ok("Base recréée proprement")

        try:
            user = User(
                first_name="John",
                last_name="Doe",
                email="john.doe@example.com",
                password="password123",
                is_admin=False
            )
            db.session.add(user)
            db.session.commit()
            ok("Création User")
        except Exception as e:
            db.session.rollback()
            fail("Création User", e)
            return

        try:
            assert user.verify_password("password123") is True
            assert user.verify_password("wrongpassword") is False
            assert user.password != "password123"
            ok("Hash + verify_password")
        except Exception as e:
            fail("Hash + verify_password", e)

        try:
            place = Place(
                title="Maison Bordeaux",
                price=100,
                latitude=44.8378,
                longitude=-0.5792,
                description="Joli logement"
            )
            place.user = user
            db.session.add(place)
            db.session.commit()

            assert place.user.email == "john.doe@example.com"
            assert len(user.places) == 1
            assert user.places[0].title == "Maison Bordeaux"
            ok("Relation User -> Place")
        except Exception as e:
            db.session.rollback()
            fail("Relation User -> Place", e)

        try:
            review = Review(
                text="Très bon séjour",
                rating=5
            )
            review.user = user
            review.place = place
            db.session.add(review)
            db.session.commit()

            assert review.user.email == "john.doe@example.com"
            assert review.place.title == "Maison Bordeaux"
            assert len(user.reviews) == 1
            assert len(place.reviews) == 1
            ok("Relations User -> Review et Place -> Review")
        except Exception as e:
            db.session.rollback()
            fail("Relations Review", e)

        try:
            wifi = Amenity(name="WiFi")
            parking = Amenity(name="Parking")
            db.session.add_all([wifi, parking])
            db.session.commit()

            place.amenities.append(wifi)
            place.amenities.append(parking)
            db.session.commit()

            assert len(place.amenities) == 2
            assert len(wifi.places) == 1
            assert wifi.places[0].title == "Maison Bordeaux"

            rows = db.session.execute(place_amenity.select()).fetchall()
            assert len(rows) == 2
            ok("Relation many-to-many Place <-> Amenity")
        except Exception as e:
            db.session.rollback()
            fail("Relation many-to-many Place <-> Amenity", e)

        try:
            bad_user = User(
                first_name="Bad",
                last_name="Mail",
                email="not-an-email",
                password="password123"
            )
            db.session.add(bad_user)
            db.session.commit()
            fail("Validation email invalide", Exception("Aucune erreur levée"))
        except Exception:
            db.session.rollback()
            ok("Validation email invalide")

        try:
            bad_review = Review(
                text="Bof",
                rating=8
            )
            db.session.add(bad_review)
            db.session.commit()
            fail("Validation rating invalide", Exception("Aucune erreur levée"))
        except Exception:
            db.session.rollback()
            ok("Validation rating invalide")

        try:
            bad_place = Place(
                title="Erreur",
                price=50,
                latitude=100,
                longitude=2,
                description="Test"
            )
            db.session.add(bad_place)
            db.session.commit()
            fail("Validation latitude invalide", Exception("Aucune erreur levée"))
        except Exception:
            db.session.rollback()
            ok("Validation latitude invalide")

        try:
            place.update({"price": 120})
            db.session.commit()
            assert place.price == 120.0
            ok("Update valide")
        except Exception as e:
            db.session.rollback()
            fail("Update valide", e)

        try:
            place.update({"id": "hack"})
            db.session.commit()
            fail("Protection id", Exception("Aucune erreur levée"))
        except Exception:
            db.session.rollback()
            ok("Protection id")

        try:
            place.update({"latitude": 999})
            db.session.commit()
            fail("Validation update latitude invalide", Exception("Aucune erreur levée"))
        except Exception:
            db.session.rollback()
            ok("Validation update latitude invalide")

        print("\nTerminé.")


if __name__ == "__main__":
    run_tests()
