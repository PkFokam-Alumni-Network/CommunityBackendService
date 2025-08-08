"""
Database initialization script for PkFokam Alumni Network backend.
Creates sample data for development and testing environments.

Usage:
    python init_data.py [--users N] [--announcements N] [--events N] [--all] [--force]

Examples:
    python init_data.py --users 3 (Create 3 users)
    python init_data.py --announcements 3 (create 3 announcements)
    python init_data.py --events 3 (create 3 events)
    python init_data.py --all (3 of each)
    python init_data.py --all --users 3 --announcements 2 --events 1 (create a maximum of 3 of each even if you specified a value more than 3)

"""

import argparse
import random
from datetime import datetime, timedelta
from typing import List, Dict

from faker import Faker
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from core.settings import settings
from models.user import User, UserRole
from models.event import Event
from models.announcement import Announcement
from utils.func_utils import get_password_hash
from core.logging_config import LOGGER


fake = Faker()

PROFILE_IMAGES = [
    "https://www.w3schools.com/howto/img_avatar.png",
    "https://randomuser.me/api/portraits/men/1.jpg",
    "https://randomuser.me/api/portraits/women/1.jpg",
]

EVENT_IMAGES = [
    "https://cdn-cjhkj.nitrocdn.com/krXSsXVqwzhduXLVuGLToUwHLNnSxUxO/assets/images/optimized/rev-b135bb1/spotme.com/wp-content/uploads/2020/07/Hero-1.jpg",
    "https://images.unsplash.com/photo-1540575467063-178a50c2df87",
    "https://images.unsplash.com/photo-1511578314322-379afb476865",
]

ANNOUNCEMENT_IMAGES = [
    "https://images.unsplash.com/photo-1596526131083-e8c633c948d2",
    "https://images.unsplash.com/photo-1607799279861-4dd421887fb3",
    "https://images.unsplash.com/photo-1588681664899-f142ff2dc9b1",
]

DEGREES = ["BSc", "MSc", "BEng", "MEng"]

MAJORS = [
    "Computer Science",
    "Mechanical Engineering",
    "Electrical Engineering and Technology",
]

OCCUPATIONS = ["Software Engineer", "Mechanical Engineer", "Electrical Engineer"]

EVENT_CATEGORIES = [
    "Conference",
    "Networking",
    "Educational",
    "Alumni Reunion",
]

EVENT_LOCATIONS = [
    "Kennesaw Campus - Atrium Building",
    "Marietta Campus - Norton Hall",
    "SOVA Kennesaw - Conference Room A",
    "Indy Kennesaw - Meeting Room 1",
]

ANNOUNCEMENT_TITLES = [
    "Call for Mentors: Alumni Mentorship Program",
    "Tech Industry Job Opportunities - New Openings",
    "Scholarship Opportunities for Graduate Studies",
    "Upcoming Engineering Workshop Series",
]


def _select_occupation(major: str) -> str:
    tech_keywords = [
        "Software",
        "Data",
        "IT",
        "Developer",
        "Cloud",
        "Cyber",
        "Database",
        "UI/UX",
        "System",
        "DevOps",
    ]
    econ_keywords = ["Financial", "Business", "Economic", "Investment", "Market"]
    if major in ["Computer Science", "Information Technology"]:
        return random.choice(
            [o for o in OCCUPATIONS if any(tech in o for tech in tech_keywords)]
        )
    elif major in ["Mechanical Engineering", "Electrical Engineering and Technology"]:
        return random.choice(
            [
                o
                for o in OCCUPATIONS
                if "Engineer" in o
                and not any(tech in o for tech in ["Software", "Data"])
            ]
        )
    elif major == "Economics":
        return random.choice(
            [o for o in OCCUPATIONS if any(econ in o for econ in econ_keywords)]
        )
    else:
        return random.choice(OCCUPATIONS)


def _create_admin_user(session: Session, users: list) -> None:
    admin_email = "admin@pkfalumni.com"
    admin_user = session.query(User).filter(User.email == admin_email).first()
    if not admin_user:
        admin_user = User(
            email=admin_email,
            first_name="Admin",
            last_name="User",
            password=get_password_hash("admin123"),
            address=fake.address().replace("\n", ", "),
            phone=fake.phone_number(),
            image=random.choice(PROFILE_IMAGES),
            bio="Administrator account for the PkFokam Alumni Network.",
            graduation_year=random.randint(2010, 2020),
            degree="MSc",
            major="Computer Science",
            current_occupation="System Administrator",
            linkedin_profile="https://linkedin.com/in/admin-pkfalumni",
            instagram_profile="https://instagram.com/admin.pkfalumni",
            role=UserRole.admin,
            is_active=True,
        )
        session.add(admin_user)
        try:
            session.commit()
            session.refresh(admin_user)
            users.append(admin_user)
            LOGGER.info(f"Created admin user: {admin_email}")
        except IntegrityError:
            session.rollback()
            LOGGER.info(f"Admin user {admin_email} already exists")
    else:
        users.append(admin_user)


def create_sample_users(
    session: Session, count: int = 3, force: bool = False
) -> List[User]:
    existing_count = session.query(User).count()
    if existing_count > 0 and not force:
        LOGGER.info(f"Found {existing_count} existing users. Use --force to recreate.")
        return session.query(User).all()

    users = []
    _create_admin_user(session, users)

    for _ in range(count - 1):
        first_name = fake.first_name()
        last_name = fake.last_name()
        email = f"{first_name.lower()}.{last_name.lower()}{random.randint(1, 999)}@pkfalumni.com"

        graduation_year = random.randint(2010, 2023)
        degree = random.choice(DEGREES)
        major = random.choice(MAJORS)
        occupation = _select_occupation(major)

        user = User(
            email=email,
            first_name=first_name,
            last_name=last_name,
            password=get_password_hash("password123"),
            address=fake.address().replace("\n", ", "),
            phone=fake.phone_number(),
            image=random.choice(PROFILE_IMAGES),
            bio=f"I graduated from PkFokam Institute with a {degree} in {major}. Currently working as a {occupation}. "
            + fake.paragraph(nb_sentences=2),
            graduation_year=graduation_year,
            degree=degree,
            major=major,
            current_occupation=occupation,
            linkedin_profile=f"https://linkedin.com/in/{first_name.lower()}-{last_name.lower()}",
            instagram_profile=f"https://instagram.com/{first_name.lower()}{last_name.lower()}"
            if random.random() > 0.3
            else None,
            role=UserRole.user,
            is_active=True,
        )

        session.add(user)
        try:
            session.commit()
            session.refresh(user)
            users.append(user)
            LOGGER.info(f"Created user: {email}")
        except IntegrityError:
            session.rollback()
            LOGGER.error(f"User with email {email} already exists")

    LOGGER.info(f"Created {len(users)} users total")
    return users


def _generate_event_details(
    i: int, count: int, current_date: datetime, event_titles: List[str]
) -> dict:
    if i < count // 3:
        start_date = current_date - timedelta(days=random.randint(1, 180))
    elif i < 2 * (count // 3):
        start_date = current_date + timedelta(days=random.randint(1, 30))
    else:
        start_date = current_date + timedelta(days=random.randint(31, 180))

    start_date = start_date.replace(
        hour=random.randint(9, 18),
        minute=random.choice([0, 30]),
        second=0,
        microsecond=0,
    )

    duration_hours = random.randint(1, 4)
    end_date = start_date + timedelta(hours=duration_hours)

    if i < len(event_titles):
        title = event_titles[i]
    else:
        title = fake.sentence(nb_words=random.randint(4, 8)).rstrip(".")

    location = random.choice(EVENT_LOCATIONS)

    if "Workshop" in title:
        description = f"Join us for this hands-on workshop where you'll learn practical skills. {fake.paragraph(nb_sentences=2)}"
    elif "Career" in title:
        description = f"Connect with top employers and explore career opportunities. {fake.paragraph(nb_sentences=2)}"
    elif "Panel" in title:
        description = f"Hear from industry experts and alumni leaders. {fake.paragraph(nb_sentences=2)}"
    else:
        description = fake.paragraph(nb_sentences=random.randint(3, 5))

    num_categories = random.randint(1, 3)
    categories = ",".join(random.sample(EVENT_CATEGORIES, num_categories))

    return {
        "title": title,
        "start_time": start_date,
        "end_time": end_date,
        "location": location,
        "description": description,
        "categories": categories,
        "image": random.choice(EVENT_IMAGES),
    }


def create_sample_events(
    session: Session, count: int = 3, force: bool = False
) -> List[Event]:
    existing_count = session.query(Event).count()
    if existing_count > 0 and not force:
        LOGGER.info(f"Found {existing_count} existing events. Use --force to recreate.")
        return session.query(Event).all()

    users = session.query(User).all()
    if not users:
        LOGGER.warning("No users found in database. Creating events without attendees.")

    events = []
    current_date = datetime.now()

    event_titles = [
        "Introduction to Machine Learning Workshop",
        "Career Fair: Tech Companies Hiring",
        "Alumni Networking Night",
    ]

    for i in range(count):
        details = _generate_event_details(i, count, current_date, event_titles)
        event = Event(
            title=details["title"],
            start_time=details["start_time"],
            end_time=details["end_time"],
            location=details["location"],
            description=details["description"],
            categories=details["categories"],
            image=details["image"],
        )

        session.add(event)
        try:
            session.commit()
            session.refresh(event)
            events.append(event)
            LOGGER.info(f"Created event: {details['title']}")
        except IntegrityError:
            session.rollback()
            LOGGER.error(f"Event with title '{details['title']}' already exists")

    return events


def _generate_announcement_title(
    i: int, current_date: datetime, base_titles: List[str]
) -> str:
    if i < len(base_titles):
        return f"{base_titles[i]} - {current_date.strftime('%Y%m%d%H%M%S')}{i}"
    return f"{fake.sentence(nb_words=random.randint(5, 10)).rstrip('.')} - {current_date.strftime('%Y%m%d%H%M%S')}{i}"


def _generate_announcement_description(title: str) -> str:
    if "Mentor" in title:
        return (
            "We are looking for experienced alumni to mentor current students. Share your knowledge and help shape the next generation of professionals. "
            + fake.paragraph(nb_sentences=3)
        )
    if "Job" in title or "Opportunit" in title:
        return (
            "New positions available at our partner companies. Opportunities for recent graduates and experienced professionals in various fields. "
            + fake.paragraph(nb_sentences=3)
        )
    if "Scholarship" in title:
        return (
            "Financial support available for qualifying students pursuing graduate studies. Applications are now open. "
            + fake.paragraph(nb_sentences=3)
        )
    return fake.paragraph(nb_sentences=random.randint(4, 8))


def create_sample_announcements(
    session: Session, count: int = 3, force: bool = False
) -> List[Announcement]:
    existing_count = session.query(Announcement).count()
    if existing_count > 0 and not force:
        LOGGER.info(
            f"Found {existing_count} existing announcements. Use --force to recreate."
        )
        return session.query(Announcement).all()

    announcements = []
    current_date = datetime.now()
    base_titles = [
        "Call for Mentors: Alumni Mentorship Program",
        "Tech Industry Job Opportunities - New Openings",
        "Alumni Network Annual Report 2024",
    ]

    for i in range(count):
        if i < count // 2:
            announcement_date = current_date - timedelta(days=random.randint(1, 30))
            deadline_date = current_date + timedelta(days=random.randint(10, 60))
        else:
            announcement_date = current_date + timedelta(days=random.randint(1, 15))
            deadline_date = announcement_date + timedelta(days=random.randint(30, 90))

        has_deadline = random.random() < 0.8

        title = _generate_announcement_title(i, current_date, base_titles)
        description = _generate_announcement_description(title)

        announcement = Announcement(
            title=title,
            description=description,
            announcement_date=announcement_date,
            announcement_deadline=deadline_date if has_deadline else None,
            image=random.choice(ANNOUNCEMENT_IMAGES),
        )

        session.add(announcement)
        try:
            session.commit()
            session.refresh(announcement)
            announcements.append(announcement)
            LOGGER.info(f"Created announcement: {title}")
        except IntegrityError:
            session.rollback()
            LOGGER.error(f"Announcement with title '{title}' already exists")

    return announcements


def check_existing_data(session: Session) -> Dict[str, int]:
    counts = {
        "users": session.query(User).count(),
        "events": session.query(Event).count(),
        "announcements": session.query(Announcement).count(),
    }
    return counts


def main():
    parser = argparse.ArgumentParser(
        description="Initialize database with sample data."
    )

    parser.add_argument("--users", type=int, metavar="N", help="Create N sample users")
    parser.add_argument(
        "--announcements", type=int, metavar="N", help="Create N sample announcements"
    )
    parser.add_argument(
        "--events", type=int, metavar="N", help="Create N sample events"
    )
    parser.add_argument(
        "--all",
        action="store_true",
        help="Create all types of data (3 each by default)",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Force recreation of data even if records exist",
    )

    args = parser.parse_args()

    if not any([args.users, args.announcements, args.events, args.all]):
        LOGGER.error("You must specify what to create. Use --help for all options.")
        return

    import core.database as database

    database.init_db(settings.DATABASE_URL)
    database.Base.metadata.create_all(bind=database.engine)

    session = database.SessionLocal()

    try:
        existing_counts = check_existing_data(session)
        LOGGER.info(
            f"Current database state - Users: {existing_counts['users']}, Events: {existing_counts['events']}, Announcements: {existing_counts['announcements']}"
        )

        if args.users:
            count = min(args.users, 3)
            users = create_sample_users(session, count, args.force)
            LOGGER.info(f"Successfully created/found {len(users)} users")

        elif args.events:
            count = min(args.events, 3)
            events = create_sample_events(session, count, args.force)
            LOGGER.info(f"Successfully created/found {len(events)} events")

        elif args.announcements:
            count = min(args.announcements, 3)
            announcements = create_sample_announcements(session, count, args.force)
            LOGGER.info(
                f"Successfully created/found {len(announcements)} announcements"
            )

        elif args.all:
            LOGGER.info("Creating all types of sample data...")
            user_count = min(args.users, 3) if args.users else 3
            event_count = min(args.events, 3) if args.events else 3
            announcement_count = min(args.announcements, 3) if args.announcements else 3

            users = create_sample_users(session, user_count, args.force)
            events = create_sample_events(session, event_count, args.force)
            announcements = create_sample_announcements(
                session, announcement_count, args.force
            )

            LOGGER.info(
                f"Sample data creation completed - Users: {len(users)}, Events: {len(events)}, Announcements: {len(announcements)}"
            )

        final_counts = check_existing_data(session)
        LOGGER.info(
            f"Final database state - Users: {final_counts['users']}, Events: {final_counts['events']}, Announcements: {final_counts['announcements']}"
        )

        if args.users or args.all:
            LOGGER.info(
                "Login credentials - Admin: admin@pkfalumni.com / admin123, Regular users: [firstname].[lastname][number]@pkfalumni.com / password123"
            )

    except Exception as e:
        LOGGER.error(f"Error creating sample data: {e}")
        session.rollback()
    finally:
        session.close()


if __name__ == "__main__":
    main()
