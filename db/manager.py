from sqlmodel import Session, select
from db import engine, Paper, Author, Subject, MainSubject, SubjectParentLink
from typing import List, Dict, Tuple

class DatabaseManager:
    """Manages database operations"""
    def __init__(self):
        self.engine = engine
    
    def create_tables(self):
        """Create all database tables"""
        try:
            SQLModel.metadata.create_all(self.engine)
            return true
        except Exception as e:
            printf("Exception raised {e}")
    
    def add_subjects_hierarchy(self, hierarchy: Dict[str, Dict[str, List[Tuple[str, str]]]]):
        """
        Add subjects hierarchy to database
        Format: {'Computer Science': {'Computing Research Repository': {["cs.AI", "cs.CC", ...]},...},...}
        
        most formats have 1 nested dicts only
        the special case is the physics main subjects that has many sub categories
        """

        with Session(self.engine) as session:
            total_main = len(hierarchy)
            total_subjects = 0
            total_categories = 0

            print(f"Inserting {total_main} main categories into database\n")

            for main_category_name, subjects_dict in hierarchy.items():
               print(f"Adding: {main_category_name}")

               #Level 0
               main_subject = self._get_or_create_main_subject(session, main_category_name)

               for subject_name, categories in subjects_dict.items():
                   total_subjects += 1

                   #Level 1 
                   subject = self._get_or_create_subject(
                        session=session,
                        name=subject_name,
                        shorthand=self._generate_shorthand(subject_name, main_category_name),
                        level=1,
                        main_subject=main_subject
                    )
                   #Level 2 
                   category_count = 0
                   for category_name, shorthand in categories:
                       if not category_name or not shorthand:
                           continue
                        
                       category_count += 1
                       total_categories += 1

                       sub_category = self._get_or_create_subject(
                            session=session,
                            name=category_name,
                            shorthand=shorthand,
                            level=2,
                            main_subject=main_subject
                        )

                       self._add_parent_relationship(session, sub_category, subject)

                       print(f"{subject_name}: {category_name} categories")
                    
            session.commit()
            
            print(f"Added: ")
            print(f"{total_main} main categories")
            print(f"{total_subjects} subject areas")
            print(f"{total_categories} sub-categories")

                    

    def _get_or_create_main_subject(self, session: Session, name: str) -> MainSubject:
        """Get an existing MainSubject or create a new one."""
        main_subject = session.exec(
            select(MainSubject).where(MainSubject.name == name)        
        ).first()

        if not main_subject:
            main_subject = MainSubject(name=name)
            session.add(main_subject)
            session.flush()
            print(f"Created new main subject: {name}")

        return main_subject

    def _get_or_create_subject(self, session: Session, name: str, shorthand: str, level: int, main_subject: MainSubject) -> Subject:
        """Get an existing Subject or create a new one."""

        subject = session.exec(
            select(Subject).where(Subject.name == name)
        ).first()

        if not subject:
            subject = Subject(
                name=name,
                shorthand=shorthand,
                level=level
            )
            session.add(subject)
            session.flush()

            subject.main_subjects.append(main_subject)
        
        return subject

    def _add_parent_relationship(self, session: Session, child: Subject, parent: Subject):
        """Add parent-child relationship link"""

        existing_link = session.exec(
            select(SubjectParentLink).where(
                SubjectParentLink.subject_name == child.name,
                SubjectParentLink.parent_subject_name == parent.name
            )
        ).first()

        if not existing_link and child.name != parent.name:
            child.parents.append(parent)
    
    def _generate_shorthand(self, subject_name: str, main_category: str) -> str:
        """Generate shorthand for subject areas without one"""
        mapping = {
            'Astrophysics': 'astro-ph',
            'Condensed Matter': 'cond-mat',
            'General Relativity and Quantum Cosmology': 'gr-qc',
            'High Energy Physics - Experiment': 'hep-ex',
            'High Energy Physics - Lattice': 'hep-lat',
            'High Energy Physics - Phenomenology': 'hep-ph',
            'High Energy Physics - Theory': 'hep-th',
            'Mathematical Physics': 'math-ph',
            'Nonlinear Sciences': 'nlin',
            'Nuclear Experiment': 'nucl-ex',
            'Nuclear Theory': 'nucl-th',
            'Physics': 'physics',
            'Quantum Physics': 'quant-ph',
            'Mathematics': 'math',
            'Computer Science': 'cs',
            'Quantitative Biology': 'q-bio',
            'Quantitative Finance': 'q-fin',
            'Statistics': 'stat',
            'Electrical Engineering and Systems Science': 'eess',
            'Economics': 'econ'
        }

        return mapping.get(subject_name, subject_name.lower().replace(' ', '-'))

print("hello")
