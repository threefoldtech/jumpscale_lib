from jumpscale import j


def test_forward_port_to_port():
    assert j.sal_zos.utils.is_valid_portforward(8000, 8000) is True
    assert j.sal_zos.utils.is_valid_portforward(0, 8000) is False
    assert j.sal_zos.utils.is_valid_portforward(-20, 8000) is False

    assert j.sal_zos.utils.is_valid_portforward("8000", "8000") is True
    assert j.sal_zos.utils.is_valid_portforward("0", "8000") is False
    assert j.sal_zos.utils.is_valid_portforward("-20", "8000") is False

def test_forward_ipport_to_port():
    assert j.sal_zos.utils.is_valid_portforward("127.0.0.1:8000", 8000) is True
    assert j.sal_zos.utils.is_valid_portforward("127.0.0.3:0", "8000") is False
    assert j.sal_zos.utils.is_valid_portforward("192.168.21.15:-20", "8000") is False


def test_forward_ipport_to_ipport():
    assert j.sal_zos.utils.is_valid_portforward("127.0.0.1:8000", "147.2.1.5:8000") is True
    assert j.sal_zos.utils.is_valid_portforward("127.0.0.3:0", "147.2.1.5:8000") is False
    assert j.sal_zos.utils.is_valid_portforward("192.168.21.15:-20", "147.2.1.5:8000") is False


def test_forward_ifport_to_ifport():
    assert j.sal_zos.utils.is_valid_portforward("eth0:8000", "147.2.1.5:8000") is True
    assert j.sal_zos.utils.is_valid_portforward("wifi2:0", "147.2.1.5:8000") is False
    assert j.sal_zos.utils.is_valid_portforward("eth2:-20", "147.2.1.5:") is False
    assert j.sal_zos.utils.is_valid_portforward("eth2:-20", 0) is False
