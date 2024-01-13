from random import randint, seed
from typing import Tuple

import pandas as pd
import pytest
from faker import Faker
from faker.providers import DynamicProvider
from swapanything.prep import get_all_matches
from swapanything.select import select_matches

n = 42
samples = 500

seed(n)
index = [f"Sub{i+1}" for i in range(samples)]
# Create faker object
industries_provider = DynamicProvider(
    provider_name="industry",
    elements=[
        "AI/ML",
        "AR/VR",
        "Agritech",
        "Altro",
        "Blockchain",
        "Clean Energy",
        "Cybersecurity",
        "Data Analytics",
        "E-Commerce/Online Marketplaces",
        "Edtech",
        "Fintech",
        "Foodtech",
        "Gaming",
        "Greentech",
        "Healthtech/Medtech",
        "IoT",
        "ML",
        "Media & Entertainment",
        "Mobile Apps",
        "No Code/ Low Code",
        "Online Marketplaces",
        "SaaS",
        "Social Media",
        "Sportstech",
        "Wearable tech",
        "Web Development",
        "Web3",
    ],
)

roles_provider = DynamicProvider(
    provider_name="role",
    elements=[
        "CEO",
        "CTO",
        "COO",
        "CFO",
        "Marketing Manager",
        "Sales Manager",
        "Business Development Manager",
        "Product Manager",
        "Human Resources Manager",
        "Software Developers/Engineers",
        "UX/UI Designers",
        "Customer Support Manager",
        "Data Analyst",
        "Digital Content Specialist",
        "Public Relations Specialist",
    ],
)

growth_provider = DynamicProvider(
    provider_name="growth",
    elements=["Pre-Seed", "Seed", "Bootstrap", "Series A", "Verso l'infinito ed oltre"],
)

language_provider = DynamicProvider(
    provider_name="language",
    elements=["Italian", "English", "Spanish", "Frech", "German"],
)

availabilities_provider = DynamicProvider(
    provider_name="availability",
    elements=[
        "Mon 10:00",
        "Mon 12:00",
        "Mon 16:00",
        "Mon 18:00",
        "Thu 10:00",
        "Thu 12:00",
        "Thu 16:00",
        "Thu 18:00",
        "Fri 10:00",
        "Fri 12:00",
        "Fri 16:00",
        "Fri 18:00",
    ],
)

goals_provider = DynamicProvider(
    provider_name="goals",
    elements=[
        "Creare partnership e sinergie con altri Founders",
        "Fare del buon sano networking",
        "Trovare supporto su temi specifici",
        "Confrontarmi con founders nel mio stesso stadio di crescita",
        "Confrontarmi con founders più avanti di me",
        "Dare supporto a founders più indietro di me",
        "Trovare un Co-Founder",
        "Altro",
    ],
)

index_provider = DynamicProvider(
    provider_name="index",
    elements=index,
)


def fake_ind(min, max):
    return [fake.industry() for _ in range(randint(min, max))]


def fake_lang(min, max):
    return [fake.language() for _ in range(randint(min, max))]


def fake_goal(min, max):
    return [fake.goals() for _ in range(randint(min, max))]


def fake_avail(min, max):
    return [fake.availability() for _ in range(randint(min, max))]


fake = Faker("it_IT")
Faker.seed(n)
fake.add_provider(industries_provider)
fake.add_provider(roles_provider)
fake.add_provider(availabilities_provider)
fake.add_provider(index_provider)
fake.add_provider(growth_provider)
fake.add_provider(language_provider)
fake.add_provider(goals_provider)


@pytest.fixture(scope="session")
def get_large_datasets() -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    # Creation syntetic data
    name = [fake.unique.name() for _ in range(samples)]

    subjects_data = {
        "Index": index,
        "Nome e Cognome": name,
        "Industry": [
            fake_ind(0, 3) for _ in range(samples)
        ],  # Select randomly from zero to max 3 industries among the ones currently in the airtable database
        "Role": [fake.role() for _ in range(samples)],
        "Growth Stage": [fake.growth() for _ in range(samples)],
        "Languages": [
            fake_lang(1, 3) for _ in range(samples)
        ],  # Select randomly from 1 to max 3 languages among ['Italian', 'English', 'Spanish', 'Frech', "German"]
        "Goal": [fake_goal(1, 8) for _ in range(samples)],
    }  # Select randomly from 1 to max 8 goals among the ones currently in the airtable database

    availabilities_data = {
        "Index": index,
        "Nome e Cognome": name,
        "Availabilities": [fake_avail(1, 5) for _ in range(samples)],
    }  # Select randomly from 1 to max 5 slot availabilities among ["Mon 10:00", "Mon 12:00", "Mon 16:00", "Mon 18:00", "Thu 10:00", "Thu 12:00", "Thu 16:00", "Thu 18:00", "Fri 10:00", "Fri 12:00", "Fri 16:00", "Fri 18:00"]

    exclusions_data = {
        "SubjectA": [fake.unique.index() for _ in range(3)] + index,
        "SubjectB": [fake.unique.index() for _ in range(3)] + index,
    }

    # DataFrame Creation
    subjects = pd.DataFrame(subjects_data)
    availabilities = pd.DataFrame(availabilities_data).explode("Availabilities")
    exclusions = pd.DataFrame(exclusions_data)

    for i in range(len(exclusions)):
        if int(exclusions["SubjectA"][i][3:]) > int(exclusions["SubjectB"][i][3:]):
            temp = exclusions["SubjectA"][i]
            exclusions["SubjectA"][i] = exclusions["SubjectB"][i]
            exclusions["SubjectB"][i] = temp
        else:
            pass

    exclusions.drop_duplicates(inplace=True)
    return subjects, availabilities, exclusions


def test_large_dateset(
    get_large_datasets: Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame],
):
    _, availabilities, exclusions = get_large_datasets

    slots_col = "Availabilities"
    subjects_col = "Index"

    all_possible_matches = get_all_matches(
        availabilities=availabilities,
        subject_col=subjects_col,
        slot_col=slots_col,
    )
    assert isinstance(all_possible_matches, pd.DataFrame)
    assert all_possible_matches["Index"].is_unique

    selected = select_matches(
        all_possible_matches,
        subjects_col=subjects_col,
        slots_col=slots_col,
    )
    assert isinstance(selected, pd.DataFrame)
    assert selected["Index"].is_unique
    assert len(selected) < len(all_possible_matches)
