
"""
Database initialization script for PkFokam Alumni Network backend.
Creates sample data for development and testing environments.

Usage:
    python init_data.py [--only-users N] [--only-announcements N] [--only-events N] [--all] [--force]

Examples:
    # Create only 10 users
    python init_data.py --only-users 10
    
    # Create only 5 announcements
    python init_data.py --only-announcements 5
    
    # Create only 8 events (requires existing users for attendees)
    python init_data.py --only-events 8
    
    # Create all types of data with default counts
    python init_data.py --all
    
    # Create all types with custom counts
    python init_data.py --all --users 30 --announcements 15 --events 20


"""

import os
import sys
import argparse
import random
from datetime import datetime, timedelta
from typing import List, Dict, Any

from faker import Faker
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError


from settings import settings


from database import init_db, SessionLocal, Base
from models.user import User, UserRole
from models.event import Event 
from models.announcement import Announcement
from models.user_event import UserEvent
from utils.func_utils import get_password_hash


fake = Faker()


PROFILE_IMAGES = [
    "https://www.w3schools.com/howto/img_avatar.png",
    "https://www.w3schools.com/howto/img_avatar2.png",
    "https://randomuser.me/api/portraits/men/1.jpg",
    "https://randomuser.me/api/portraits/women/1.jpg",
    "https://randomuser.me/api/portraits/men/2.jpg",
    "https://randomuser.me/api/portraits/women/2.jpg",
    "https://randomuser.me/api/portraits/men/3.jpg",
    "https://randomuser.me/api/portraits/women/3.jpg",
    "https://randomuser.me/api/portraits/men/4.jpg",
    "https://randomuser.me/api/portraits/women/4.jpg",
]


EVENT_IMAGES = [
    "https://cdn-cjhkj.nitrocdn.com/krXSsXVqwzhduXLVuGLToUwHLNnSxUxO/assets/images/optimized/rev-b135bb1/spotme.com/wp-content/uploads/2020/07/Hero-1.jpg",
    "https://images.unsplash.com/photo-1540575467063-178a50c2df87",
    "https://images.unsplash.com/photo-1511578314322-379afb476865",
    "https://images.unsplash.com/photo-1505373877841-8d25f7d46678",
    "https://images.unsplash.com/photo-1587825140708-dfaf72ae4b04",
]


ANNOUNCEMENT_IMAGES = [
    "https://images.unsplash.com/photo-1596526131083-e8c633c948d2",
    "https://images.unsplash.com/photo-1607799279861-4dd421887fb3",
    "https://images.unsplash.com/photo-1588681664899-f142ff2dc9b1",
    "https://images.unsplash.com/photo-1434030216411-0b793f4b4173",
    "https://images.unsplash.com/photo-1553877522-43269d4ea984",
]


DEGREES = ["BSc", "MSc", "PhD", "BEng", "MEng", "MBA", "BBA"]


MAJORS = [
    "Computer Science", 
    "Information Technology", 
    "Mechanical Engineering", 
    "Electrical Engineering and Technology", 
    "Economics"
]


OCCUPATIONS = [
    # CS/IT related
    "Software Engineer", 
    "Data Scientist", 
    "DevOps Engineer",
    "Full Stack Developer",
    "Mobile App Developer",
    "Cloud Architect",
    "Cybersecurity Analyst",
    "IT Project Manager", 
    "Product Manager", 
    "System Administrator",
    "Database Administrator",
    "UI/UX Designer",
    
    
    "Mechanical Engineer",
    "Electrical Engineer",
    "Automation Engineer",
    "Quality Engineer",
    "Design Engineer",
    "Manufacturing Engineer",
    
    
    "Financial Analyst", 
    "Business Analyst",
    "Economic Researcher",
    "Investment Analyst",
    "Market Research Analyst",
    
    
    "Consultant", 
    "Entrepreneur", 
    "Technical Lead",
    "Research Scientist"
]


EVENT_CATEGORIES = [
    "Workshop", 
    "Conference", 
    "Networking", 
    "Career Fair", 
    "Seminar",
    "Webinar", 
    "Social", 
    "Educational", 
    "Professional Development",
    "Panel Discussion", 
    "Alumni Reunion", 
    "Hackathon", 
    "Tech Talk", 
    "Industry Talk",
    "Mentorship Session"
]


EVENT_LOCATIONS = [
    "Kennesaw Campus - Atrium Building", 
    "Kennesaw Campus - Engineering Technology Center", 
    "Kennesaw Campus - Prillaman Hall", 
    "Kennesaw Campus - Student Center",
    "Marietta Campus - Norton Hall", 
    "Marietta Campus - Architecture Building", 
    "Marietta Campus - Student Center", 
    "SOVA Kennesaw - Conference Room A",
    "SOVA Kennesaw - Main Hall", 
    "Indy Kennesaw - Meeting Room 1", 
    "Indy Kennesaw - Event Space",
    "Virtual (Zoom)",
    "Virtual (Google Meet)", 
    "Kennesaw Campus - Library Auditorium", 
    "Marietta Campus - Joe Mack Wilson Student Center"
]


ANNOUNCEMENT_TITLES = [
    "Call for Mentors: Alumni Mentorship Program",
    "Tech Industry Job Opportunities - New Openings",
    "Alumni Network Annual Report 2024",
    "Scholarship Opportunities for Graduate Studies",
    "Partnership with Atlanta Tech Companies",
    "Alumni Success Stories: Share Your Journey",
    "Upcoming Engineering Workshop Series",
    "Research Funding for CS/IT Projects",
    "Call for Speakers: Annual Tech Conference",
    "Professional Certification Programs Available",
    "Alumni Spotlight: Tech Leaders in Atlanta",
    "International Exchange Program - Apply Now",
    "Community Coding Bootcamp Initiative",
    "Entrepreneurship Support Program Launch",
    "New Alumni Portal Features Released",
    "Annual Membership Benefits Update",
    "Graduate Program Information Sessions",
    "Industry Mentorship Matching Program",
    "Internship Opportunities at Partner Companies",
    "Campus Expansion Project Updates",
]


def create_sample_users(session: Session, count: int = 20, force: bool = False) -> List[User]:
    
    print(f"Creating {count} sample users...")
    
    # Check if users already exist
    existing_count = session.query(User).count()
    if existing_count > 0 and not force:
        print(f"Found {existing_count} existing users. Use --force to recreate.")
        return session.query(User).all()
    
    users = []
    
    # First, create one admin user with known credentials
    admin_email = "admin@pkfalumni.com"
    admin_user = session.query(User).filter(User.email == admin_email).first()
    
    if not admin_user:
        admin_user = User(
            email=admin_email,
            first_name="Admin",
            last_name="User",
            password=get_password_hash("admin123"),
            address=fake.address().replace('\n', ', '),
            phone=fake.phone_number(),
            image=random.choice(PROFILE_IMAGES),
            bio="Administrator account for the PkFokam Alumni Network.",
            graduation_year=random.randint(2010, 2020),
            degree="MSc",
            major="Computer Science",
            current_occupation="System Administrator",
            linkedin_profile=f"https://linkedin.com/in/admin-pkfalumni",
            instagram_profile=f"https://instagram.com/admin.pkfalumni",
            role=UserRole.admin,
            is_active=True
        )
        session.add(admin_user)
        try:
            session.commit()
            session.refresh(admin_user)
            users.append(admin_user)
            print(f"✓ Created admin user: {admin_email} (password: admin123)")
        except IntegrityError:
            session.rollback()
            print(f"✓ Admin user {admin_email} already exists")
    else:
        users.append(admin_user)
        print(f"✓ Admin user {admin_email} already exists")

    # Create regular users
    for i in range(count - 1):  # -1 because we already created the admin user
        first_name = fake.first_name()
        last_name = fake.last_name()
        email = f"{first_name.lower()}.{last_name.lower()}{random.randint(1, 999)}@pkfalumni.com"
        
        graduation_year = random.randint(2010, 2023)
        degree = random.choice(DEGREES)
        major = random.choice(MAJORS)
        
        
        if major in ["Computer Science", "Information Technology"]:
            occupation = random.choice([o for o in OCCUPATIONS if any(tech in o for tech in ["Software", "Data", "IT", "Developer", "Cloud", "Cyber", "Database", "UI/UX", "System", "DevOps"])])
        elif major in ["Mechanical Engineering", "Electrical Engineering and Technology"]:
            occupation = random.choice([o for o in OCCUPATIONS if "Engineer" in o and not any(tech in o for tech in ["Software", "Data"])])
        elif major == "Economics":
            occupation = random.choice([o for o in OCCUPATIONS if any(econ in o for econ in ["Financial", "Business", "Economic", "Investment", "Market"])])
        else:
            occupation = random.choice(OCCUPATIONS)
        
        user = User(
            email=email,
            first_name=first_name,
            last_name=last_name,
            password=get_password_hash("password123"),
            address=fake.address().replace('\n', ', '),
            phone=fake.phone_number(),
            image=random.choice(PROFILE_IMAGES),
            bio=f"I graduated from PkFokam Institute with a {degree} in {major}. Currently working as a {occupation}. " + fake.paragraph(nb_sentences=2),
            graduation_year=graduation_year,
            degree=degree,
            major=major,
            current_occupation=occupation,
            linkedin_profile=f"https://linkedin.com/in/{first_name.lower()}-{last_name.lower()}",
            instagram_profile=f"https://instagram.com/{first_name.lower()}{last_name.lower()}" if random.random() > 0.3 else None,
            role=UserRole.user,
            is_active=True
        )
        
        session.add(user)
        try:
            session.commit()
            session.refresh(user)
            users.append(user)
            print(f"✓ Created user: {email}")
        except IntegrityError:
            session.rollback()
            print(f"✗ User with email {email} already exists")
    
    # Note: Mentor assignment has been removed as per the new schema (mentor_id instead of mentor_email)
    print(f"✓ Created {len(users)} users total")
    print(f"  Default password for all regular users: password123")
    
    return users


def create_sample_events(session: Session, count: int = 15, force: bool = False) -> List[Event]:
    
    print(f"\nCreating {count} sample events...")
    
    # Check if events already exist
    existing_count = session.query(Event).count()
    if existing_count > 0 and not force:
        print(f"Found {existing_count} existing events. Use --force to recreate.")
        return session.query(Event).all()
    
    # Get existing users for event registration
    users = session.query(User).all()
    if not users:
        print("⚠ No users found in database. Creating events without attendees.")
        print("  Consider running: python init_data.py --only-users 10")
    
    events = []
    current_date = datetime.now()
    
    
    event_titles = [
        "Introduction to Machine Learning Workshop",
        "Career Fair: Tech Companies Hiring",
        "Alumni Networking Night",
        "Cybersecurity Best Practices Seminar",
        "Mechanical Design with CAD Tools",
        "Electrical Circuit Design Workshop",
        "Economics and Data Analytics",
        "Entrepreneurship Panel Discussion",
        "Cloud Computing Fundamentals",
        "Industry 4.0 and IoT Applications",
        "Financial Technology Trends",
        "Software Development Best Practices",
        "Research Opportunities in Engineering",
        "Alumni Success Stories: From Student to CEO",
        "Professional Skills Development Workshop"
    ]
    
    for i in range(count):
        
        if i < count // 3:
            # Past event
            start_date = current_date - timedelta(days=random.randint(1, 180))
        elif i < 2 * (count // 3):
            
            start_date = current_date + timedelta(days=random.randint(1, 30))
        else:
            # Future event
            start_date = current_date + timedelta(days=random.randint(31, 180))
    
        
        start_date = start_date.replace(
            hour=random.randint(9, 18),
            minute=random.choice([0, 30]),
            second=0,
            microsecond=0
        )
        
        
        duration_hours = random.randint(1, 4)
        end_date = start_date + timedelta(hours=duration_hours)
        
        
        if i < len(event_titles):
            title = event_titles[i]
        else:
            title = fake.sentence(nb_words=random.randint(4, 8)).rstrip('.')
        
        location = random.choice(EVENT_LOCATIONS)
        
        # Generate relevant description based on event type
        if "Workshop" in title:
            description = f"Join us for this hands-on workshop where you'll learn practical skills. {fake.paragraph(nb_sentences=2)}"
        elif "Career" in title:
            description = f"Connect with top employers and explore career opportunities. {fake.paragraph(nb_sentences=2)}"
        elif "Panel" in title:
            description = f"Hear from industry experts and alumni leaders. {fake.paragraph(nb_sentences=2)}"
        else:
            description = fake.paragraph(nb_sentences=random.randint(3, 5))
        
        # Random categories (1-3)
        num_categories = random.randint(1, 3)
        categories = ','.join(random.sample(EVENT_CATEGORIES, num_categories))
        
        event = Event(
            title=title,
            start_time=start_date,
            end_time=end_date,
            location=location,
            description=description,
            categories=categories,
            image=random.choice(EVENT_IMAGES)
        )
        
        session.add(event)
        try:
            session.commit()
            session.refresh(event)
            events.append(event)
            print(f"✓ Created event: {title}")
            
            # Register random users for this event (only if users exist)
            if users and start_date > current_date:  # Only register for future events
                num_attendees = random.randint(5, min(len(users), 20))
                attendees = random.sample(users, num_attendees)
                
                registered_count = 0
                for user in attendees:
                    user_event = UserEvent(
                        user_id=user.id,
                        event_id=event.id
                    )
                    session.add(user_event)
                    try:
                        session.commit()
                        registered_count += 1
                    except IntegrityError:
                        session.rollback()
                
                if registered_count > 0:
                    print(f"  ✓ Registered {registered_count} users for this event")
            
        except IntegrityError:
            session.rollback()
            print(f"✗ Event with title '{title}' already exists or other integrity error")
    
    return events


def create_sample_announcements(session: Session, count: int = 10, force: bool = False) -> List[Announcement]:
    """Create sample announcements."""
    print(f"\nCreating {count} sample announcements...")
    
    # Check if announcements already exist
    existing_count = session.query(Announcement).count()
    if existing_count > 0 and not force:
        print(f"Found {existing_count} existing announcements. Use --force to recreate.")
        return session.query(Announcement).all()
    
    announcements = []
    current_date = datetime.now()
    
    for i in range(count):
        
        if i < count // 2:
            # Current announcement (posted in the past)
            announcement_date = current_date - timedelta(days=random.randint(1, 30))
            deadline_date = current_date + timedelta(days=random.randint(10, 60))
        else:
            # Future announcement
            announcement_date = current_date + timedelta(days=random.randint(1, 15))
            deadline_date = announcement_date + timedelta(days=random.randint(30, 90))
        
        # Some announcements might not have a deadline
        has_deadline = random.random() < 0.8  # 80% chance of having a deadline
        
        if i < len(ANNOUNCEMENT_TITLES):
            title = ANNOUNCEMENT_TITLES[i]
        else:
            title = fake.sentence(nb_words=random.randint(5, 10)).rstrip('.')
        
        # Generate relevant descriptions
        if "Mentor" in title:
            description = "We are looking for experienced alumni to mentor current students. Share your knowledge and help shape the next generation of professionals. " + fake.paragraph(nb_sentences=3)
        elif "Job" in title or "Opportunit" in title:
            description = "New positions available at our partner companies. Opportunities for recent graduates and experienced professionals in various fields. " + fake.paragraph(nb_sentences=3)
        elif "Scholarship" in title:
            description = "Financial support available for qualifying students pursuing graduate studies. Applications are now open. " + fake.paragraph(nb_sentences=3)
        else:
            description = fake.paragraph(nb_sentences=random.randint(4, 8))
        
        announcement = Announcement(
            title=title,
            description=description,
            announcement_date=announcement_date,
            announcement_deadline=deadline_date if has_deadline else None,
            image=random.choice(ANNOUNCEMENT_IMAGES)
        )
        
        session.add(announcement)
        try:
            session.commit()
            session.refresh(announcement)
            announcements.append(announcement)
            print(f"✓ Created announcement: {title}")
        except IntegrityError:
            session.rollback()
            print(f"✗ Announcement with title '{title}' already exists")
    
    return announcements


def check_existing_data(session: Session) -> Dict[str, int]:
    
    counts = {
        'users': session.query(User).count(),
        'events': session.query(Event).count(),
        'announcements': session.query(Announcement).count(),
    }
    
    return counts


def main():
    parser = argparse.ArgumentParser(description='Initialize database with sample data.')
    
    # Individual creation options
    parser.add_argument('--only-users', type=int, metavar='N', help='Create only N sample users')
    parser.add_argument('--only-announcements', type=int, metavar='N', help='Create only N sample announcements')
    parser.add_argument('--only-events', type=int, metavar='N', help='Create only N sample events')
    
    # All data creation option
    parser.add_argument('--all', action='store_true', help='Create all types of data')
    parser.add_argument('--users', type=int, default=20, help='Number of sample users when using --all')
    parser.add_argument('--announcements', type=int, default=10, help='Number of sample announcements when using --all')
    parser.add_argument('--events', type=int, default=15, help='Number of sample events when using --all')
    
    # Other options
    parser.add_argument('--force', action='store_true', help='Force recreation of data even if records exist')
    
    args = parser.parse_args()
    
    # Check if any creation option is specified
    if not any([args.only_users, args.only_announcements, args.only_events, args.all]):
        print("Error: You must specify what to create.")
        print("\nExamples:")
        print("  python init_data.py --only-users 10")
        print("  python init_data.py --only-events 5")
        print("  python init_data.py --only-announcements 8")
        print("  python init_data.py --all")
        print("\nUse --help for all options.")
        return
    
    # Initialize database exactly like main.py does
    import database
    from settings import settings
    
    print(f"🗄 Database: {settings.database_url}")
    print(f"🌍 Environment: {settings.ENV}")
    
    # Initialize the database
    database.init_db(settings.database_url)
    database.Base.metadata.create_all(bind=database.engine)
    
    # Create session
    session = database.SessionLocal()
    
    try:
        # Show current database state
        existing_counts = check_existing_data(session)
        print(f"\n Current database state:")
        print(f"   Users: {existing_counts['users']}")
        print(f"   Events: {existing_counts['events']}")
        print(f"   Announcements: {existing_counts['announcements']}")
        print()
        
        
        if args.only_users:
            users = create_sample_users(session, args.only_users, args.force)
            print(f"\n Successfully created/found {len(users)} users")
            
        elif args.only_events:
            events = create_sample_events(session, args.only_events, args.force)
            print(f"\n Successfully created/found {len(events)} events")
            
        elif args.only_announcements:
            announcements = create_sample_announcements(session, args.only_announcements, args.force)
            print(f"\n Successfully created/found {len(announcements)} announcements")
            
        elif args.all:
            print(" Creating all types of sample data...\n")
            users = create_sample_users(session, args.users, args.force)
            events = create_sample_events(session, args.events, args.force)
            announcements = create_sample_announcements(session, args.announcements, args.force)
            
            print(f"\n Sample data creation completed!")
            print(f"   👥 Users: {len(users)}")
            print(f"   📅 Events: {len(events)}")
            print(f"   📢 Announcements: {len(announcements)}")
        
        
        final_counts = check_existing_data(session)
        print(f"\n Final database state:")
        print(f"   Users: {final_counts['users']}")
        print(f"   Events: {final_counts['events']}")
        print(f"   Announcements: {final_counts['announcements']}")
        
        
        if args.only_users or args.all:
            print(f"\n Login credentials:")
            print(f"   Admin: admin@pkfalumni.com / admin123")
            print(f"   Regular users: [firstname].[lastname][number]@pkfalumni.com / password123")
        
    except Exception as e:
        print(f"\n Error creating sample data: {e}")
        session.rollback()
        import traceback
        traceback.print_exc()
    finally:
        session.close()


if __name__ == "__main__":
    main()