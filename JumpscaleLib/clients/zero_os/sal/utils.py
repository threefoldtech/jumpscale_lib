from .abstracts import ZTNic

def authorize_zerotiers(identify, nics):
    for nic in nics:
        if isinstance(nic, ZTNic):
            nic.authorize(identify)

