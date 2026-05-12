#!/usr/bin/env python3
"""Create deterministic local data for Playwright browser QA."""

import os
import sys
from datetime import date, timedelta
from pathlib import Path

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "campfire_connections.settings.local")
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import django

django.setup()

from django.contrib.auth import get_user_model

from enrollment.models.facility import FacilityEnrollment
from enrollment.models.faction import FactionEnrollment
from enrollment.models.attendee import AttendeeEnrollment
from enrollment.models.organization import OrganizationEnrollment
from enrollment.models.temporal import Period, Week
from facility.models.facility import Facility
from facility.models.quarters import Quarters, QuartersType
from facility.models.faculty import FacultyProfile
from faction.models.faction import Faction
from faction.models.attendee import AttendeeProfile
from organization.models import Organization


def get_or_create_user():
    User = get_user_model()
    user, created = User.objects.get_or_create(
        username="qa.admin",
        defaults={
            "email": "qa.admin@example.com",
            "user_type": User.UserType.ADMIN,
            "is_staff": True,
            "is_superuser": True,
        },
    )
    changed = False
    for attr, value in {
        "email": "qa.admin@example.com",
        "user_type": User.UserType.ADMIN,
        "is_staff": True,
        "is_superuser": True,
    }.items():
        if getattr(user, attr) != value:
            setattr(user, attr, value)
            changed = True
    if created or changed or not user.check_password("pass12345"):
        user.set_password("pass12345")
        user.save()
    return user


def get_or_create_attendee_user():
    User = get_user_model()
    user, created = User.objects.get_or_create(
        username="qa.riley",
        defaults={
            "email": "qa.riley@example.com",
            "first_name": "QA Riley",
            "last_name": "Chen",
            "user_type": User.UserType.ATTENDEE,
        },
    )
    changed = False
    for attr, value in {
        "email": "qa.riley@example.com",
        "first_name": "QA Riley",
        "last_name": "Chen",
        "user_type": User.UserType.ATTENDEE,
    }.items():
        if getattr(user, attr) != value:
            setattr(user, attr, value)
            changed = True
    if created or changed or not user.check_password("pass12345"):
        user.set_password("pass12345")
        user.save()
    return user


def get_or_create_role_user(username, email, first_name, last_name, user_type):
    User = get_user_model()
    user, created = User.objects.get_or_create(
        username=username,
        defaults={
            "email": email,
            "first_name": first_name,
            "last_name": last_name,
            "user_type": user_type,
        },
    )
    changed = False
    for attr, value in {
        "email": email,
        "first_name": first_name,
        "last_name": last_name,
        "user_type": user_type,
    }.items():
        if getattr(user, attr) != value:
            setattr(user, attr, value)
            changed = True
    if created or changed or not user.check_password("pass12345"):
        user.set_password("pass12345")
        user.save()
    return user


def ensure_faculty_profile(user, organization, facility, role):
    profile = FacultyProfile.objects.filter(user=user).first()
    if not profile:
        return FacultyProfile.objects.create(
            user=user,
            organization=organization,
            facility=facility,
            role=role,
        )
    changed = False
    for attr, value in {
        "organization": organization,
        "facility": facility,
        "role": role,
    }.items():
        if getattr(profile, attr) != value:
            setattr(profile, attr, value)
            changed = True
    if changed:
        profile.save()
    return profile


def find_or_create(model, lookup, create_values=None):
    instance = model.objects.filter(**lookup).first()
    if instance:
        return instance
    values = dict(lookup)
    if create_values:
        values.update(create_values)
    return model.objects.create(**values)


def main():
    get_or_create_user()

    organization = Organization.objects.filter(name="QA Council", parent=None).first()
    if not organization:
        organization = Organization.objects.create(
            name="QA Council",
            abbreviation="QA",
            max_depth=5,
        )
    if organization.abbreviation != "QA":
        organization.abbreviation = "QA"
        organization.max_depth = 5
        organization.save()

    facility = Facility.objects.filter(
        name="QA Camp",
        organization=organization,
    ).first()
    if not facility:
        facility = Facility.objects.create(name="QA Camp", organization=organization)

    faculty_staff = get_or_create_role_user(
        "qa.faculty.staff",
        "qa.faculty.staff@example.com",
        "QA",
        "Faculty Staff",
        get_user_model().UserType.FACULTY,
    )
    ensure_faculty_profile(
        faculty_staff,
        organization,
        facility,
        FacultyProfile.FacultyRole.STAFF,
    )
    faculty_department_admin = get_or_create_role_user(
        "qa.faculty.department",
        "qa.faculty.department@example.com",
        "QA",
        "Department Admin",
        get_user_model().UserType.FACULTY,
    )
    ensure_faculty_profile(
        faculty_department_admin,
        organization,
        facility,
        FacultyProfile.FacultyRole.DEPARTMENT_ADMIN,
    )

    faction = Faction.objects.filter(
        name="QA Eagle Patrol",
        organization=organization,
    ).first()
    if not faction:
        faction = Faction.objects.create(
            name="QA Eagle Patrol",
            organization=organization,
            abbreviation="QAE",
        )

    org_enrollment = find_or_create(
        OrganizationEnrollment,
        {"name": "QA Summer Session", "organization": organization},
        {"start": date(2026, 6, 1), "end": date(2026, 6, 30)},
    )
    facility_enrollment = find_or_create(
        FacilityEnrollment,
        {
            "name": "QA Facility Enrollment",
            "organization_enrollment": org_enrollment,
            "facility": facility,
        },
        {"start": date(2026, 6, 1), "end": date(2026, 6, 15)},
    )
    week = find_or_create(
        Week,
        {"name": "QA Week 1", "facility_enrollment": facility_enrollment},
        {"start": date(2026, 6, 1), "end": date(2026, 6, 7)},
    )
    find_or_create(
        Period,
        {"name": "QA Morning", "week": week},
        {"start": "08:00", "end": "09:00"},
    )
    quarters_type = find_or_create(
        QuartersType,
        {"name": "QA Cabin", "organization": organization},
    )
    quarters = find_or_create(
        Quarters,
        {"name": "QA Cabin 1", "facility": facility, "type": quarters_type},
        {"capacity": 12},
    )
    faction_enrollment = find_or_create(
        FactionEnrollment,
        {
            "name": "QA Eagle Patrol Enrollment",
            "faction": faction,
            "facility_enrollment": facility_enrollment,
            "week": week,
            "quarters": quarters,
        },
        {
            "start": week.start,
            "end": week.start + timedelta(days=6),
            "description": "Browser QA enrollment fixture.",
        },
    )
    attendee_user = get_or_create_attendee_user()
    attendee = AttendeeProfile.objects.filter(user=attendee_user).first()
    if not attendee:
        attendee = AttendeeProfile.objects.create(
            user=attendee_user,
            organization=organization,
            faction=faction,
        )
    else:
        changed = False
        for attr, value in {"organization": organization, "faction": faction}.items():
            if getattr(attendee, attr) != value:
                setattr(attendee, attr, value)
                changed = True
        if attendee.slug != "qa-riley-chen":
            attendee.slug = "qa-riley-chen"
            changed = True
        if changed:
            attendee.save()

    find_or_create(
        AttendeeEnrollment,
        {
            "attendee": attendee,
            "faction_enrollment": faction_enrollment,
            "quarters": quarters,
        },
        {
            "start": faction_enrollment.start,
            "end": faction_enrollment.end,
            "role": "Participant",
        },
    )
    print("Browser QA seed data ready.")


if __name__ == "__main__":
    main()
