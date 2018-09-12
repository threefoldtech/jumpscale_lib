from .Minio import Minio


def test_replication_config():

    m = Minio('aminio', None, 'admin', 'admin', ['localhost:9999'], 'anamespace', 'myprivatekeystring', nr_datashards=6, nr_parityshards=0)
    conf = m.config_as_text()
    assert "parity_shards" not in conf 
    assert "data_shards: 6" in conf


def test_distribution_config():
    m = Minio('aminio', None, 'admin', 'admin', ['localhost:9999'], 'anamespace', 'myprivatekeystring', nr_datashards=6, nr_parityshards=4)
    conf = m.config_as_text()
    assert "parity_shards: 4" in conf
    assert "data_shards: 6" in conf

