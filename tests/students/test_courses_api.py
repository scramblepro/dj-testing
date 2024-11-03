import pytest
from model_bakery import baker
from rest_framework.test import APIClient
from students.models import Course
from django.urls import reverse


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def course_factory():
    def create_course(**kwargs):
        return baker.make('Course', **kwargs)
    return create_course


@pytest.fixture
def student_factory():
    def create_student(**kwargs):
        return baker.make('Student', **kwargs)
    return create_student


@pytest.mark.django_db
def test_retrieve_course(api_client, course_factory):
    course = course_factory()
    url = reverse('courses-detail', args=[course.id])
    response = api_client.get(url)
    assert response.status_code == 200
    assert response.json()['id'] == course.id


@pytest.mark.django_db
def test_list_courses(api_client, course_factory):
    course_factory(_quantity=3)
    url = reverse('courses-list')
    response = api_client.get(url)
    assert response.status_code == 200
    assert len(response.json()) == 3


@pytest.mark.django_db
def test_filter_courses_by_id(api_client, course_factory):
    courses = course_factory(_quantity=3)
    url = reverse('courses-list')
    response = api_client.get(url, data={'id': courses[0].id})
    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]['id'] == courses[0].id


@pytest.mark.django_db
def test_filter_courses_by_name(api_client, course_factory):
    course_factory(name="Test Course")
    url = reverse('courses-list')
    response = api_client.get(url, data={'name': "Test Course"})
    assert response.status_code == 200
    assert all(course['name'] == "Test Course" for course in response.json())


@pytest.mark.django_db
def test_create_course(api_client):
    url = reverse('courses-list')
    data = {"name": "New Course"}
    response = api_client.post(url, data=data)
    assert response.status_code == 201
    assert Course.objects.filter(name="New Course").exists()


@pytest.mark.django_db
def test_update_course(api_client, course_factory):
    course = course_factory(name="Old Course")
    url = reverse('courses-detail', args=[course.id])
    data = {"name": "Updated Course"}
    response = api_client.put(url, data=data)
    assert response.status_code == 200
    course.refresh_from_db()
    assert course.name == "Updated Course"


@pytest.mark.django_db
def test_delete_course(api_client, course_factory):
    course = course_factory()
    url = reverse('courses-detail', args=[course.id])
    response = api_client.delete(url)
    assert response.status_code == 204
    assert not Course.objects.filter(id=course.id).exists()
