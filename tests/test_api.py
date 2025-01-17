import os
import xml.etree.ElementTree as ET
import pytest
import vcr
import pandas as pd
from pandas import DataFrame
from six import string_types

from petpy.api import Petfinder

tape = vcr.VCR(
    cassette_library_dir='tests/cassettes',
    serializer='json',
    record_mode='once'
)


key = os.environ.get('PETFINDER_KEY')


def authenticate():
    pf = Petfinder(str(key))

    return pf


pf = authenticate()


@pytest.fixture
def top_level_keys():
    return ['@encoding', '@version', 'petfinder', '@xmlns:xsi']


@pytest.fixture
def petfinder_keys():
    return ['@xmlns:xsi', 'lastOffset', 'breeds', 'shelters', 'petIds',
            'pets', 'header', '@xsi:noNamespaceSchemaLocation']


@pytest.fixture
def petfinder_pet_get_keys():
    return ['@encoding', '@version', 'petfinder', 'options', 'status', 'contact', 'age',
            'pet', '@xmlns:xsi', 'header', '@xsi:noNamespaceSchemaLocation', 'size', 'media',
            'id', 'shelterPetId', 'breeds', 'name', 'sex', 'description', 'mix', 'shelterId', 'lastUpdate', 'animal']


@pytest.fixture
def petfinder_shelter_get_keys():
    return ['country', 'longitude', 'name', 'phone', 'state', 'address2',
            'email', 'city', 'zip', 'fax', 'latitude', 'id', 'address1']


@vcr.use_cassette('tests/cassettes/breed_list.yml', filter_query_parameters=['key'])
def test_breed_list(top_level_keys, petfinder_keys):

    response1 = pf.breed_list('cat')
    response2 = pf.breed_list('dog', 'xml')
    response3 = pf.breed_list('cat', return_df=True)

    r = ET.fromstring(response2.encode('utf-8'))

    assert isinstance(response1, dict)
    assert isinstance(response2, string_types)

    assert isinstance(response3, DataFrame)
    assert 'breeds' in list(response3.columns)[0]

    assert set(response1.keys()).issubset(top_level_keys)
    assert set(response1['petfinder'].keys()).issubset(petfinder_keys)

    assert str(r[1].attrib) == "{'animal': 'dog'}"
    assert r[0].tag == 'header'
    assert r[1].tag == 'breeds'


@vcr.use_cassette('tests/cassettes/pet_find.yml', filter_query_parameters=['key'])
def test_pet_find(top_level_keys, petfinder_keys):
    response1 = pf.pet_find(location='98133', count=1)
    response2 = pf.pet_find(location='98133', count=1, outputformat='xml')
    response3 = pf.pet_find('98133', outputformat='xml', return_df=True)

    r = ET.fromstring(response2.encode('utf-8'))

    assert isinstance(response1, dict)
    assert isinstance(response2, string_types)
    assert isinstance(response3, DataFrame)

    assert set(response1.keys()).issubset(top_level_keys)
    assert set(response1['petfinder'].keys()).issubset(petfinder_keys)

    assert r[0].tag == 'header'
    assert r[2].tag == 'pets'
    assert r[2][0].tag == 'pet'


@vcr.use_cassette('tests/cassettes/pet_getRandom.yml', filter_query_parameters=['key'])
def test_pet_getRandom(top_level_keys, petfinder_keys):

    response1 = pf.pet_get_random()
    response2 = pf.pet_get_random(outputformat='xml')
    response3 = pf.pet_get_random(return_df=True)

    records = 5
    response4 = pf.pet_get_random(records=records)
    response5 = pf.pet_get_random(records=records, return_df=True)

    r = ET.fromstring(response2.encode('utf-8'))

    assert isinstance(response1, dict)
    assert isinstance(response2, string_types)
    assert isinstance(response3, DataFrame)

    assert isinstance(response4, list)
    assert len(response4) == records

    assert isinstance(response5, DataFrame)

    assert set(response1.keys()).issubset(top_level_keys)
    assert set(response1['petfinder'].keys()).issubset(petfinder_keys)

    assert r[0].tag == 'header'
    assert r[1].tag == 'petIds'
    assert r[1][0].tag == 'id'


@vcr.use_cassette('tests/cassettes/pet_get.yml', filter_query_parameters=['key'])
def test_pet_get(top_level_keys, petfinder_pet_get_keys):
    # Call pet_getRandom to get a valid petId to ensure test is run
    petids = []
    ids = pf.pet_get_random(records=5)

    for i in ids:
        petids.append(i['petfinder']['petIds']['id']['$t'])

    response1 = pf.pet_get(petids[0])
    response2 = pf.pet_get(petids[0], outputformat='xml')
    response3 = pf.pet_get(petids[0], outputformat='xml', return_df=True)
    response4 = pf.pet_get(petids, outputformat='xml', return_df=True)
    response5 = pf.pets_get(petids[0])

    r = ET.fromstring(response2.encode('utf-8'))

    assert isinstance(response1, dict)
    assert isinstance(response2, string_types)
    assert isinstance(response3, DataFrame)
    assert isinstance(response4, DataFrame)
    assert isinstance(response5, dict)

    assert set(response1.keys()).issubset(top_level_keys)
    assert set(response1['petfinder'].keys()).issubset(petfinder_pet_get_keys)
    assert set(response1['petfinder']['pet'].keys()).issubset(petfinder_pet_get_keys)

    assert set(response5.keys()).issubset(top_level_keys)

    assert r[0].tag == 'header'
    assert r[1].tag == 'pet'
    assert r[1][0].tag == 'id'
    assert r[1][1].tag == 'shelterId'
    assert r[1][2].tag == 'shelterPetId'


@vcr.use_cassette('tests/cassettes/shelter_find.yml', filter_query_parameters=['key'])
def test_shelter_find(top_level_keys, petfinder_keys):

    response1 = pf.shelter_find('98115')
    response2 = pf.shelter_find('98115', outputformat='xml')
    response3 = pf.shelter_find('98115', outputformat='xml', return_df=True)

    r = ET.fromstring(response2.encode('utf-8'))

    assert isinstance(response1, dict)
    assert isinstance(response2, string_types)
    assert isinstance(response3, DataFrame)

    assert set(response1.keys()).issubset(top_level_keys)
    assert set(response1['petfinder'].keys()).issubset(petfinder_keys)

    assert r[0].tag == 'header'
    assert r[1].tag == 'lastOffset'
    assert r[2].tag == 'shelters'


@vcr.use_cassette('tests/cassettes/shelter_get.yml', filter_query_parameters=['key'])
def test_shelter_get(top_level_keys, petfinder_shelter_get_keys):
    shelterid = pf.shelter_find('98133', count=1)['petfinder']['shelters']['shelter']['id']['$t']

    response1 = pf.shelter_get(shelterid)
    response2 = pf.shelter_get(shelterid, outputformat='xml')
    response3 = pf.shelter_get(shelterid, return_df=True, outputformat='xml')

    response4 = pf.shelters_get(shelterid)

    r = ET.fromstring(response2.encode('utf-8'))

    assert isinstance(response1, dict)
    assert isinstance(response2, string_types)
    assert isinstance(response3, DataFrame)
    assert isinstance(response4, dict)

    assert set(response1.keys()).issubset(top_level_keys)
    assert set(response1['petfinder']['shelter'].keys()).issubset(petfinder_shelter_get_keys)

    assert set(response4.keys()).issubset(top_level_keys)

    assert r[0].tag == 'header'
    assert r[1].tag == 'shelter'
    assert r[1][0].tag == 'id'


@vcr.use_cassette('tests/cassettes/shelters_get.yml', filter_query_parameters=['key'])
def test_shelters_get(top_level_keys, petfinder_shelter_get_keys):
    shelterids = []
    ids = pf.shelter_find(location='WA', count=5)

    for i in ids['petfinder']['shelters']['shelter']:
        shelterids.append(i['id']['$t'])

    response1 = pf.shelters_get(shelterids, return_df=True, outputformat='xml')
    response2 = pf.shelters_get(shelterids)
    response3 = pf.shelters_get(shelterids, outputformat='xml')
    response4 = pf.shelters_get(shelterids[0])

    assert isinstance(response1, DataFrame)
    assert isinstance(response2, list)
    assert isinstance(response3[0], string_types)
    assert isinstance(response4, dict)


@vcr.use_cassette('tests/cassettes/shelter_get_pets.yml', filter_query_parameters=['key'])
def test_shelter_getPets(top_level_keys, petfinder_keys):
    shelterid = pf.shelter_find('98133', count=1)['petfinder']['shelters']['shelter']['id']['$t']

    response1 = pf.shelter_get_pets(shelterid, count=1)
    response2 = pf.shelter_get_pets(shelterid, count=1, outputformat='xml')
    response3 = pf.shelter_get_pets(shelterid, outputformat='xml', return_df=True)

    r = ET.fromstring(response2.encode('utf-8'))

    assert isinstance(response1, dict)
    assert isinstance(response2, string_types)
    assert isinstance(response3, DataFrame)

    assert set(response1.keys()).issubset(top_level_keys)
    assert set(response1['petfinder'].keys()).issubset(petfinder_keys)

    assert r[0].tag == 'header'
    assert r[1].tag == 'lastOffset'
    assert r[2].tag == 'pets'

    response4 = pf.shelter_get_pets(shelterid, count='1')
    assert isinstance(response4, dict)


@vcr.use_cassette('tests/cassettes/shelter_list_by_breed.yml', filter_query_parameters=['key'])
def test_shelter_listByBreed(top_level_keys, petfinder_keys):

    response1 = pf.shelter_list_by_breed('cat', 'American Shorthair', count=1)
    response2 = pf.shelter_list_by_breed('cat', 'American Shorthair', count=1, outputformat='xml')
    response3 = pf.shelter_list_by_breed('cat', 'American Shorthair', outputformat='json')

    r = ET.fromstring(response2.encode('utf-8'))

    assert isinstance(response1, dict)
    assert isinstance(response2, string_types)
    #assert isinstance(response3, DataFrame)

    assert set(response1.keys()).issubset(top_level_keys)
    assert set(response1['petfinder'].keys()).issubset(petfinder_keys)

    assert r[0].tag == 'header'
    assert r[1].tag == 'shelters'


@vcr.use_cassette('tests/cassettes/paging.yml', filter_query_parameters=['key'])
def test_paging_results(top_level_keys):

    response1 = pf.pet_find(location='98133', pages=3)
    response2 = pf.pet_find(location='98133', pages=3, outputformat='xml')

    assert isinstance(response1, list)

    assert len(response1) == len(response2) == 3

    for i in response1:
        assert set(i.keys()).issubset(top_level_keys)

    for j in response2:
        r = ET.fromstring(j.encode('utf-8'))
        assert r[0].tag == 'header'
        assert r[1].tag == 'lastOffset'

    response3 = pf.pet_find(location='98133', pages='3')
    assert isinstance(response3, list)


def test_parameter_checks():

    with pytest.raises(ValueError):
        pf.pet_find(location='98133', count=2000)
    with pytest.raises(ValueError):
        pf.pet_find(location='98133', pages=5, count=1000)

    with pytest.raises(ValueError):
        pf.pet_find(location='98133', count='aks')
    with pytest.raises(ValueError):
        pf.pet_find(location='98133', pages='aks')
