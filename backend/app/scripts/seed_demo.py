"""
Demo data seeding script.
Creates categories, filters, partners, and treasures for testing.

Usage: python -m app.scripts.seed_demo
"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from sqlalchemy.orm import Session
from sqlalchemy import text
from app.database import sync_engine
from app.models.category import Category
from app.models.filter import Filter
from app.models.partner import Partner, PartnerImage, PartnerFilter
from app.models.treasure import Treasure, TreasurePartner, TreasureCategory


def seed_demo_data():
    """Seed demo data into the database"""
    print("Seeding demo data...")

    with Session(sync_engine) as session:
        # Clear existing data
        print("Clearing existing data...")
        session.execute(text("TRUNCATE TABLE treasure_partners, treasures, partner_filters, partner_images, visits, favorites, partners, filters, categories RESTART IDENTITY CASCADE"))
        session.commit()

        # Categories
        print("Creating categories...")
        categories = [
            Category(
                slug="premium-partners",
                name_hr="Premium Partneri",
                name_en="Premium Partners",
                name_de="Premium Partner",
                description_hr="Ekskluzivni partneri s najboljim popustima",
                description_en="Exclusive partners with the best discounts",
                description_de="Exklusive Partner mit den besten Rabatten",
                icon="star",
                sort_order=1,
            ),
            Category(
                slug="nautical-foodie",
                name_hr="Nautički Gurman",
                name_en="Nautical Foodie",
                name_de="Nautischer Feinschmecker",
                description_hr="Restorani uz more",
                description_en="Seaside restaurants",
                description_de="Restaurants am Meer",
                icon="anchor",
                sort_order=2,
            ),
            Category(
                slug="liquid-treasures",
                name_hr="Tekuća Blaga",
                name_en="Liquid Treasures",
                name_de="Flüssige Schätze",
                description_hr="Vinarije i destilerije",
                description_en="Wineries and distilleries",
                description_de="Weingüter und Destillerien",
                icon="wine",
                sort_order=3,
            ),
            Category(
                slug="authentic-flavours",
                name_hr="Autentični Okusi",
                name_en="Authentic Flavours",
                name_de="Authentische Aromen",
                description_hr="Tradicionalna jela i proizvodi",
                description_en="Traditional dishes and products",
                description_de="Traditionelle Gerichte und Produkte",
                icon="utensils",
                sort_order=4,
            ),
            Category(
                slug="by-the-sea",
                name_hr="Uz More",
                name_en="By the Sea",
                name_de="Am Meer",
                description_hr="Lokacije uz obalu",
                description_en="Coastal locations",
                description_de="Küstenorte",
                icon="waves",
                sort_order=5,
            ),
            Category(
                slug="places-worth-visiting",
                name_hr="Mjesta Vrijedna Posjeta",
                name_en="Places Worth Visiting",
                name_de="Sehenswerte Orte",
                description_hr="Znamenitosti i atrakcije",
                description_en="Landmarks and attractions",
                description_de="Sehenswürdigkeiten und Attraktionen",
                icon="map-pin",
                sort_order=6,
            ),
        ]
        session.add_all(categories)
        session.flush()

        # Filters
        print("Creating filters...")
        filters = [
            # Nautical Foodie filters
            Filter(category_id=categories[1].id, slug="seafood", name_hr="Morski plodovi", name_en="Seafood", name_de="Meeresfrüchte", sort_order=1),
            Filter(category_id=categories[1].id, slug="fine-dining", name_hr="Fine dining", name_en="Fine Dining", name_de="Gehobene Küche", sort_order=2),
            Filter(category_id=categories[1].id, slug="casual", name_hr="Casual", name_en="Casual", name_de="Lässig", sort_order=3),
            # Liquid Treasures filters
            Filter(category_id=categories[2].id, slug="wine", name_hr="Vino", name_en="Wine", name_de="Wein", sort_order=1),
            Filter(category_id=categories[2].id, slug="rakija", name_hr="Rakija", name_en="Rakija", name_de="Rakija", sort_order=2),
            Filter(category_id=categories[2].id, slug="olive-oil", name_hr="Maslinovo ulje", name_en="Olive Oil", name_de="Olivenöl", sort_order=3),
            # Authentic Flavours filters
            Filter(category_id=categories[3].id, slug="cheese", name_hr="Sir", name_en="Cheese", name_de="Käse", sort_order=1),
            Filter(category_id=categories[3].id, slug="ham", name_hr="Pršut", name_en="Ham", name_de="Schinken", sort_order=2),
            Filter(category_id=categories[3].id, slug="honey", name_hr="Med", name_en="Honey", name_de="Honig", sort_order=3),
        ]
        session.add_all(filters)
        session.flush()

        # Partners
        print("Creating partners...")
        partners = [
            Partner(
                category_id=categories[1].id,
                slug="konoba-mate",
                name_hr="Konoba Mate",
                name_en="Konoba Mate",
                name_de="Konoba Mate",
                description_hr="Tradicionalna dalmatinska konoba s pogledom na more. Specijalizirana za svježu ribu i domaća jela.",
                description_en="Traditional Dalmatian tavern with sea view. Specialized in fresh fish and homemade dishes.",
                description_de="Traditionelle dalmatinische Taverne mit Meerblick. Spezialisiert auf frischen Fisch und hausgemachte Gerichte.",
                latitude=43.5081,
                longitude=16.4402,
                address="Obala 15",
                city="Split",
                country="Croatia",
                phone="+385 21 123 456",
                email="info@konoba-mate.hr",
                website="https://konoba-mate.hr",
                is_premium=True,
                discount_percent=15,
                pin_code="MATE2024",
                opening_hours={"mon": "12:00-23:00", "tue": "12:00-23:00", "wed": "12:00-23:00", "thu": "12:00-23:00", "fri": "12:00-24:00", "sat": "12:00-24:00", "sun": "12:00-22:00"},
            ),
            Partner(
                category_id=categories[2].id,
                slug="vinarija-bibich",
                name_hr="Vinarija Bibich",
                name_en="Bibich Winery",
                name_de="Weingut Bibich",
                description_hr="Moderna vinarija s dugom tradicijom. Poznati po autohtonim sortama Debit i Plavina.",
                description_en="Modern winery with long tradition. Famous for indigenous varieties Debit and Plavina.",
                description_de="Modernes Weingut mit langer Tradition. Bekannt für einheimische Sorten Debit und Plavina.",
                latitude=43.9422,
                longitude=15.6278,
                address="Plastovo bb",
                city="Skradin",
                country="Croatia",
                phone="+385 22 771 093",
                email="info@bibfresco.com",
                website="https://bibfresco.com",
                is_premium=True,
                discount_percent=20,
                pin_code="BIBICH20",
                opening_hours={"mon": "09:00-18:00", "tue": "09:00-18:00", "wed": "09:00-18:00", "thu": "09:00-18:00", "fri": "09:00-18:00", "sat": "10:00-16:00", "sun": "closed"},
            ),
            Partner(
                category_id=categories[3].id,
                slug="gligora-cheese",
                name_hr="Gligora Sir",
                name_en="Gligora Cheese",
                name_de="Gligora Käse",
                description_hr="Proizvođač nagradivanih ovčjih sireva s otoka Paga. Paški sir - zaštićena oznaka izvornosti.",
                description_en="Producer of award-winning sheep cheeses from Pag island. Paški sir - protected designation of origin.",
                description_de="Hersteller preisgekrönter Schafskäse von der Insel Pag. Paški sir - geschützte Ursprungsbezeichnung.",
                latitude=44.4438,
                longitude=15.0567,
                address="Kolan bb",
                city="Pag",
                country="Croatia",
                phone="+385 23 698 010",
                email="info@gligora.com",
                website="https://gligora.com",
                is_premium=True,
                discount_percent=10,
                pin_code="PAG2024",
                opening_hours={"mon": "08:00-20:00", "tue": "08:00-20:00", "wed": "08:00-20:00", "thu": "08:00-20:00", "fri": "08:00-20:00", "sat": "08:00-14:00", "sun": "closed"},
            ),
            Partner(
                category_id=categories[4].id,
                slug="beach-bar-luna",
                name_hr="Beach Bar Luna",
                name_en="Beach Bar Luna",
                name_de="Beach Bar Luna",
                description_hr="Opušteni bar na plaži s koktelima i laganim jelima. Savršen zalazak sunca.",
                description_en="Relaxed beach bar with cocktails and light meals. Perfect sunset views.",
                description_de="Entspannte Strandbar mit Cocktails und leichten Gerichten. Perfekter Sonnenuntergang.",
                latitude=43.2639,
                longitude=16.6332,
                address="Uvala Stiniva",
                city="Vis",
                country="Croatia",
                phone="+385 91 555 1234",
                is_premium=False,
                discount_percent=5,
                pin_code="LUNA05",
            ),
            Partner(
                category_id=categories[5].id,
                slug="diocletians-palace",
                name_hr="Dioklecijanova Palača",
                name_en="Diocletian's Palace",
                name_de="Diokletianpalast",
                description_hr="UNESCO svjetska baština. Rimska palača iz 4. stoljeća, srce grada Splita.",
                description_en="UNESCO World Heritage Site. Roman palace from 4th century, heart of Split city.",
                description_de="UNESCO-Weltkulturerbe. Römischer Palast aus dem 4. Jahrhundert, Herz der Stadt Split.",
                latitude=43.5081,
                longitude=16.4402,
                address="Dioklecijanova",
                city="Split",
                country="Croatia",
                website="https://visitsplit.com",
                is_premium=False,
                discount_percent=0,
            ),
        ]

        # Add PostGIS point for each partner
        for p in partners:
            if p.latitude and p.longitude:
                session.execute(
                    text(f"UPDATE partners SET location = ST_SetSRID(ST_MakePoint({p.longitude}, {p.latitude}), 4326) WHERE slug = :slug"),
                    {"slug": p.slug}
                )

        session.add_all(partners)
        session.flush()

        # Partner Images
        print("Creating partner images...")
        images = [
            PartnerImage(partner_id=partners[0].id, url="https://images.unsplash.com/photo-1555396273-367ea4eb4db5", is_primary=True, sort_order=1),
            PartnerImage(partner_id=partners[0].id, url="https://images.unsplash.com/photo-1414235077428-338989a2e8c0", is_primary=False, sort_order=2),
            PartnerImage(partner_id=partners[1].id, url="https://images.unsplash.com/photo-1506377247377-2a5b3b417ebb", is_primary=True, sort_order=1),
            PartnerImage(partner_id=partners[1].id, url="https://images.unsplash.com/photo-1510812431401-41d2bd2722f3", is_primary=False, sort_order=2),
            PartnerImage(partner_id=partners[2].id, url="https://images.unsplash.com/photo-1486297678162-eb2a19b0a32d", is_primary=True, sort_order=1),
            PartnerImage(partner_id=partners[3].id, url="https://images.unsplash.com/photo-1507525428034-b723cf961d3e", is_primary=True, sort_order=1),
            PartnerImage(partner_id=partners[4].id, url="https://images.unsplash.com/photo-1580737737002-dd1f6e61db3e", is_primary=True, sort_order=1),
        ]
        session.add_all(images)

        # Partner Filters
        print("Linking partners to filters...")
        partner_filters = [
            PartnerFilter(partner_id=partners[0].id, filter_id=filters[0].id),  # Konoba Mate - Seafood
            PartnerFilter(partner_id=partners[0].id, filter_id=filters[2].id),  # Konoba Mate - Casual
            PartnerFilter(partner_id=partners[1].id, filter_id=filters[3].id),  # Bibich - Wine
            PartnerFilter(partner_id=partners[2].id, filter_id=filters[6].id),  # Gligora - Cheese
        ]
        session.add_all(partner_filters)

        # Treasures
        print("Creating treasures...")
        treasures = [
            Treasure(
                slug="plavac-mali",
                category=TreasureCategory.wines,
                title_hr="Plavac Mali",
                title_en="Plavac Mali",
                title_de="Plavac Mali",
                content_hr="Plavac Mali je najvažnija crna sorta grožđa u Hrvatskoj. Uzgaja se duž dalmatinske obale, posebno na poluotocima Pelješac i Hvar.",
                content_en="Plavac Mali is Croatia's most important red grape variety. It is grown along the Dalmatian coast, especially on Pelješac peninsula and Hvar island.",
                content_de="Plavac Mali ist Kroatiens wichtigste Rotweinsorte. Sie wird entlang der dalmatinischen Küste angebaut, besonders auf der Halbinsel Pelješac und der Insel Hvar.",
                image_url="https://images.unsplash.com/photo-1510812431401-41d2bd2722f3",
                sort_order=1,
            ),
            Treasure(
                slug="paski-sir",
                category=TreasureCategory.products,
                title_hr="Paški Sir",
                title_en="Pag Cheese",
                title_de="Pager Käse",
                content_hr="Paški sir je tvrdi ovčji sir s otoka Paga, poznat po specifičnom okusu koji dolazi od aromatičnog bilja na pašnjacima natopljenim morskom soli.",
                content_en="Pag cheese is a hard sheep's milk cheese from Pag island, known for its distinctive flavor from aromatic herbs on pastures sprayed with sea salt.",
                content_de="Pager Käse ist ein Hartkäse aus Schafsmilch von der Insel Pag, bekannt für seinen charakteristischen Geschmack durch aromatische Kräuter auf mit Meersalz besprühten Weiden.",
                image_url="https://images.unsplash.com/photo-1486297678162-eb2a19b0a32d",
                sort_order=1,
            ),
            Treasure(
                slug="dalmatian-prsut",
                category=TreasureCategory.traditional_dishes,
                title_hr="Dalmatinski Pršut",
                title_en="Dalmatian Prosciutto",
                title_de="Dalmatinischer Schinken",
                content_hr="Dalmatinski pršut je suhomesnati proizvod od svinjskog buta, sušen na buri - hladnom sjevernom vjetru. Proces zrenja traje najmanje 12 mjeseci.",
                content_en="Dalmatian prosciutto is a dry-cured ham made from pork leg, dried by Bura - the cold northern wind. The aging process takes at least 12 months.",
                content_de="Dalmatinischer Schinken ist ein luftgetrockneter Schinken aus Schweinekeule, getrocknet durch Bura - den kalten Nordwind. Der Reifeprozess dauert mindestens 12 Monate.",
                image_url="https://images.unsplash.com/photo-1589985270826-4b7bb135bc9d",
                sort_order=1,
            ),
            Treasure(
                slug="lace-of-pag",
                category=TreasureCategory.crafts_souvenirs,
                title_hr="Paška Čipka",
                title_en="Pag Lace",
                title_de="Pager Spitze",
                content_hr="Paška čipka je UNESCO nematerijalna baština. Ručno izrađena čipka s geometrijskim uzorcima, tradicija stara preko 500 godina.",
                content_en="Pag lace is UNESCO intangible heritage. Handmade needle lace with geometric patterns, a tradition over 500 years old.",
                content_de="Pager Spitze ist UNESCO immaterielles Kulturerbe. Handgefertigte Nadelspitze mit geometrischen Mustern, eine über 500 Jahre alte Tradition.",
                image_url="https://images.unsplash.com/photo-1558618666-fcd25c85cd64",
                sort_order=1,
            ),
        ]
        session.add_all(treasures)
        session.flush()

        # Link treasures to partners
        print("Linking treasures to partners...")
        treasure_partners = [
            TreasurePartner(treasure_id=treasures[0].id, partner_id=partners[1].id),  # Plavac Mali - Bibich
            TreasurePartner(treasure_id=treasures[1].id, partner_id=partners[2].id),  # Paski Sir - Gligora
        ]
        session.add_all(treasure_partners)

        # Update partner locations with PostGIS
        print("Updating PostGIS locations...")
        for p in partners:
            if p.latitude and p.longitude:
                session.execute(
                    text("UPDATE partners SET location = ST_SetSRID(ST_MakePoint(:lng, :lat), 4326) WHERE id = :id"),
                    {"lng": p.longitude, "lat": p.latitude, "id": p.id}
                )

        session.commit()
        print("Demo data seeded successfully!")


if __name__ == "__main__":
    seed_demo_data()
