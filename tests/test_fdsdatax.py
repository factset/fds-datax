import pytest
import os
import fds.datax as dx

@pytest.fixture(scope="session")
def univ_dir(tmpdir_factory):
    univ_dir = dx.Universe(dir_path = tmpdir_factory.mktemp("data"))
    return univ_dir

def test_empty_directory(univ_dir):
    assert     univ_dir.locate() == None

def test_universe_creation(univ_dir):
    assert univ_dir.create('generate',cache_name = 'SPY_2015_16',
                         mssql_dsn = 'SDF',
                         etf_ticker = 'SPY-US',
                         currency = 'USD',
                         start_date = '2016-11-01',
                         end_date = '2016-12-31') == True
    assert len(univ_dir.locate()) == 1

def test_rebuild_cache(univ_dir):
    assert  univ_dir.rebuild(cache_name='SPY_2015_16') == True 
                        
def test_delete_cache(univ_dir):
    univ_dir.delete(cache_name='SPY_2015_16')
    assert  univ_dir.locate() == None 
                        



 