
from .Address import Address
from .Authorization import Authorization
from .Avatar import Avatar
from .BankAccount import BankAccount
from .Contract import Contract
from .DigitalAssetAddress import DigitalAssetAddress
from .EmailAddress import EmailAddress
from .Error import Error
from .JoinOrganizationInvitation import JoinOrganizationInvitation
from .KeyStoreKey import KeyStoreKey
from .Notification import Notification
from .PhoneNumberValidation import PhoneNumberValidation
from .Phonenumber import Phonenumber
from .PublicKey import PublicKey
from .RegistryEntry import RegistryEntry
from .See import See
from .SeeView import SeeView
from .TOTPSecret import TOTPSecret
from .TwoFAMethods import TwoFAMethods
from .User import User
from .UserAPIKey import UserAPIKey
from .UserOrganizations import UserOrganizations
from .api_response import APIResponse
from .unhandled_api_error import UnhandledAPIError
from .unmarshall_error import UnmarshallError
from .userview import userview
from Jumpscale import j




class UsersService():
    def __init__(self, client):
        pass
        self.client = client

    def GetAvatarImage(self, hash, headers=None, query_params=None, content_type="application/json"):
        """
        Get the avatar file associated with this id
        It is method for GET /users/avatar/img/{hash}
        """
        uri = self.client.base_url + "/users/avatar/img/" + hash
        return self.client.get(uri, None, headers, query_params, content_type)

    def DeleteUserAddress(self, label, username, headers=None, query_params=None, content_type="application/json"):
        """
        Removes an address
        It is method for DELETE /users/{username}/addresses/{label}
        """
        uri = self.client.base_url + "/users/" + username + "/addresses/" + label
        return self.client.delete(uri, None, headers, query_params, content_type)

    def GetUserAddressByLabel(self, label, username, headers=None, query_params=None, content_type="application/json"):
        """
        Get the details of an address.
        It is method for GET /users/{username}/addresses/{label}
        """
        uri = self.client.base_url + "/users/" + username + "/addresses/" + label
        resp = self.client.get(uri, None, headers, query_params, content_type)
        try:
            if resp.status_code == 200:
                return APIResponse(data=Address(resp.json()), response=resp)

            message = 'unknown status code={}'.format(resp.status_code)
            raise UnhandledAPIError(response=resp, code=resp.status_code,
                                    message=message)
        except ValueError as msg:
            raise UnmarshallError(resp, msg)
        except UnhandledAPIError as uae:
            raise uae
        except Exception as e:
            raise UnmarshallError(resp, e.message)

    def UpdateUserAddress(
            self,
            data,
            label,
            username,
            headers=None,
            query_params=None,
            content_type="application/json"):
        """
        Update the label and/or value of an existing address.
        It is method for PUT /users/{username}/addresses/{label}
        """
        uri = self.client.base_url + "/users/" + username + "/addresses/" + label
        return self.client.put(uri, data, headers, query_params, content_type)

    def GetUserAddresses(self, username, headers=None, query_params=None, content_type="application/json"):
        """
        List of all of the user his addresses.
        It is method for GET /users/{username}/addresses
        """
        uri = self.client.base_url + "/users/" + username + "/addresses"
        resp = self.client.get(uri, None, headers, query_params, content_type)
        try:
            if resp.status_code == 200:
                resps = []
                for elem in resp.json():
                    resps.append(Address(elem))
                return APIResponse(data=resps, response=resp)

            message = 'unknown status code={}'.format(resp.status_code)
            raise UnhandledAPIError(response=resp, code=resp.status_code,
                                    message=message)
        except ValueError as msg:
            raise UnmarshallError(resp, msg)
        except UnhandledAPIError as uae:
            raise uae
        except Exception as e:
            raise UnmarshallError(resp, e.message)

    def RegisterNewUserAddress(self, data, username, headers=None, query_params=None, content_type="application/json"):
        """
        Register a new address
        It is method for POST /users/{username}/addresses
        """
        uri = self.client.base_url + "/users/" + username + "/addresses"
        resp = self.client.post(uri, data, headers, query_params, content_type)
        try:
            if resp.status_code == 201:
                return APIResponse(data=Address(resp.json()), response=resp)

            message = 'unknown status code={}'.format(resp.status_code)
            raise UnhandledAPIError(response=resp, code=resp.status_code,
                                    message=message)
        except ValueError as msg:
            raise UnmarshallError(resp, msg)
        except UnhandledAPIError as uae:
            raise uae
        except Exception as e:
            raise UnmarshallError(resp, e.message)

    def DeleteAPIkey(self, label, username, headers=None, query_params=None, content_type="application/json"):
        """
        Removes an API key
        It is method for DELETE /users/{username}/apikeys/{label}
        """
        uri = self.client.base_url + "/users/" + username + "/apikeys/" + label
        return self.client.delete(uri, None, headers, query_params, content_type)

    def GetAPIkey(self, label, username, headers=None, query_params=None, content_type="application/json"):
        """
        Get an API key by label
        It is method for GET /users/{username}/apikeys/{label}
        """
        uri = self.client.base_url + "/users/" + username + "/apikeys/" + label
        resp = self.client.get(uri, None, headers, query_params, content_type)
        try:
            if resp.status_code == 200:
                return APIResponse(data=UserAPIKey(resp.json()), response=resp)

            message = 'unknown status code={}'.format(resp.status_code)
            raise UnhandledAPIError(response=resp, code=resp.status_code,
                                    message=message)
        except ValueError as msg:
            raise UnmarshallError(resp, msg)
        except UnhandledAPIError as uae:
            raise uae
        except Exception as e:
            raise UnmarshallError(resp, e.message)

    def UpdateAPIkey(self, data, label, username, headers=None, query_params=None, content_type="application/json"):
        """
        Updates the label for the API key
        It is method for PUT /users/{username}/apikeys/{label}
        """
        uri = self.client.base_url + "/users/" + username + "/apikeys/" + label
        return self.client.put(uri, data, headers, query_params, content_type)

    def ListAPIKeys(self, username, headers=None, query_params=None, content_type="application/json"):
        """
        Lists the API keys
        It is method for GET /users/{username}/apikeys
        """
        uri = self.client.base_url + "/users/" + username + "/apikeys"
        resp = self.client.get(uri, None, headers, query_params, content_type)
        try:
            if resp.status_code == 200:
                resps = []
                for elem in resp.json():
                    resps.append(UserAPIKey(elem))
                return APIResponse(data=resps, response=resp)

            message = 'unknown status code={}'.format(resp.status_code)
            raise UnhandledAPIError(response=resp, code=resp.status_code,
                                    message=message)
        except ValueError as msg:
            raise UnmarshallError(resp, msg)
        except UnhandledAPIError as uae:
            raise uae
        except Exception as e:
            raise UnmarshallError(resp, e.message)

    def AddApiKey(self, data, username, headers=None, query_params=None, content_type="application/json"):
        """
        Adds an APIKey to the user
        It is method for POST /users/{username}/apikeys
        """
        uri = self.client.base_url + "/users/" + username + "/apikeys"
        resp = self.client.post(uri, data, headers, query_params, content_type)
        try:
            if resp.status_code == 201:
                return APIResponse(data=UserAPIKey(resp.json()), response=resp)

            message = 'unknown status code={}'.format(resp.status_code)
            raise UnhandledAPIError(response=resp, code=resp.status_code,
                                    message=message)
        except ValueError as msg:
            raise UnmarshallError(resp, msg)
        except UnhandledAPIError as uae:
            raise uae
        except Exception as e:
            raise UnmarshallError(resp, e.message)

    def DeleteAuthorization(
            self,
            grantedTo,
            username,
            headers=None,
            query_params=None,
            content_type="application/json"):
        """
        Remove the authorization for an organization, the granted organization will no longer have access the user's information.
        It is method for DELETE /users/{username}/authorizations/{grantedTo}
        """
        uri = self.client.base_url + "/users/" + username + "/authorizations/" + grantedTo
        return self.client.delete(uri, None, headers, query_params, content_type)

    def GetAuthorization(self, grantedTo, username, headers=None, query_params=None, content_type="application/json"):
        """
        Get the authorization for a specific organization.
        It is method for GET /users/{username}/authorizations/{grantedTo}
        """
        uri = self.client.base_url + "/users/" + username + "/authorizations/" + grantedTo
        resp = self.client.get(uri, None, headers, query_params, content_type)
        try:
            if resp.status_code == 200:
                return APIResponse(data=Authorization(resp.json()), response=resp)

            message = 'unknown status code={}'.format(resp.status_code)
            raise UnhandledAPIError(response=resp, code=resp.status_code,
                                    message=message)
        except ValueError as msg:
            raise UnmarshallError(resp, msg)
        except UnhandledAPIError as uae:
            raise uae
        except Exception as e:
            raise UnmarshallError(resp, e.message)

    def UpdateAuthorization(
            self,
            data,
            grantedTo,
            username,
            headers=None,
            query_params=None,
            content_type="application/json"):
        """
        Modify which information an organization is able to see.
        It is method for PUT /users/{username}/authorizations/{grantedTo}
        """
        uri = self.client.base_url + "/users/" + username + "/authorizations/" + grantedTo
        return self.client.put(uri, data, headers, query_params, content_type)

    def GetAllAuthorizations(self, username, headers=None, query_params=None, content_type="application/json"):
        """
        Get the list of authorizations.
        It is method for GET /users/{username}/authorizations
        """
        uri = self.client.base_url + "/users/" + username + "/authorizations"
        resp = self.client.get(uri, None, headers, query_params, content_type)
        try:
            if resp.status_code == 200:
                resps = []
                for elem in resp.json():
                    resps.append(Authorization(elem))
                return APIResponse(data=resps, response=resp)

            message = 'unknown status code={}'.format(resp.status_code)
            raise UnhandledAPIError(response=resp, code=resp.status_code,
                                    message=message)
        except ValueError as msg:
            raise UnmarshallError(resp, msg)
        except UnhandledAPIError as uae:
            raise uae
        except Exception as e:
            raise UnmarshallError(resp, e.message)

    def CreateAvatarFromImage(
            self,
            data,
            label,
            username,
            headers=None,
            query_params=None,
            content_type="application/json"):
        """
        Create a new avatar with the specified label from a provided image file
        It is method for POST /users/{username}/avatar/img/{label}
        """
        uri = self.client.base_url + "/users/" + username + "/avatar/img/" + label
        resp = self.client.post(uri, data, headers, query_params, content_type)
        try:
            if resp.status_code == 201:
                return APIResponse(data=Avatar(resp.json()), response=resp)

            message = 'unknown status code={}'.format(resp.status_code)
            raise UnhandledAPIError(response=resp, code=resp.status_code,
                                    message=message)
        except ValueError as msg:
            raise UnmarshallError(resp, msg)
        except UnhandledAPIError as uae:
            raise uae
        except Exception as e:
            raise UnmarshallError(resp, e.message)

    def UpdateAvatarFile(
            self,
            data,
            newlabel,
            label,
            username,
            headers=None,
            query_params=None,
            content_type="application/json"):
        """
        Update the avatar and possibly the avatar file stored on itsyou.online
        It is method for PUT /users/{username}/avatar/{label}/to/{newlabel}
        """
        uri = self.client.base_url + "/users/" + username + "/avatar/" + label + "/to/" + newlabel
        resp = self.client.put(uri, data, headers, query_params, content_type)
        try:
            if resp.status_code == 200:
                return APIResponse(data=Avatar(resp.json()), response=resp)

            message = 'unknown status code={}'.format(resp.status_code)
            raise UnhandledAPIError(response=resp, code=resp.status_code,
                                    message=message)
        except ValueError as msg:
            raise UnmarshallError(resp, msg)
        except UnhandledAPIError as uae:
            raise uae
        except Exception as e:
            raise UnmarshallError(resp, e.message)

    def DeleteAvatar(self, label, username, headers=None, query_params=None, content_type="application/json"):
        """
        Delete the avatar with the specified label
        It is method for DELETE /users/{username}/avatar/{label}
        """
        uri = self.client.base_url + "/users/" + username + "/avatar/" + label
        return self.client.delete(uri, None, headers, query_params, content_type)

    def UpdateAvatarLink(self, data, label, username, headers=None, query_params=None, content_type="application/json"):
        """
        Update the avatar and possibly the link to the avatar
        It is method for PUT /users/{username}/avatar/{label}
        """
        uri = self.client.base_url + "/users/" + username + "/avatar/" + label
        resp = self.client.put(uri, data, headers, query_params, content_type)
        try:
            if resp.status_code == 200:
                return APIResponse(data=Avatar(resp.json()), response=resp)

            message = 'unknown status code={}'.format(resp.status_code)
            raise UnhandledAPIError(response=resp, code=resp.status_code,
                                    message=message)
        except ValueError as msg:
            raise UnmarshallError(resp, msg)
        except UnhandledAPIError as uae:
            raise uae
        except Exception as e:
            raise UnmarshallError(resp, e.message)

    def GetAvatars(self, username, headers=None, query_params=None, content_type="application/json"):
        """
        List all avatars for the user
        It is method for GET /users/{username}/avatar
        """
        uri = self.client.base_url + "/users/" + username + "/avatar"
        resp = self.client.get(uri, None, headers, query_params, content_type)
        try:
            if resp.status_code == 200:
                return APIResponse(data=Avatar(resp.json()), response=resp)

            message = 'unknown status code={}'.format(resp.status_code)
            raise UnhandledAPIError(response=resp, code=resp.status_code,
                                    message=message)
        except ValueError as msg:
            raise UnmarshallError(resp, msg)
        except UnhandledAPIError as uae:
            raise uae
        except Exception as e:
            raise UnmarshallError(resp, e.message)

    def CreateAvatarFromLink(self, data, username, headers=None, query_params=None, content_type="application/json"):
        """
        Create a new avatar with the specified label from a link
        It is method for POST /users/{username}/avatar
        """
        uri = self.client.base_url + "/users/" + username + "/avatar"
        resp = self.client.post(uri, data, headers, query_params, content_type)
        try:
            if resp.status_code == 201:
                return APIResponse(data=Avatar(resp.json()), response=resp)

            message = 'unknown status code={}'.format(resp.status_code)
            raise UnhandledAPIError(response=resp, code=resp.status_code,
                                    message=message)
        except ValueError as msg:
            raise UnmarshallError(resp, msg)
        except UnhandledAPIError as uae:
            raise uae
        except Exception as e:
            raise UnmarshallError(resp, e.message)

    def DeleteUserBankAccount(self, username, label, headers=None, query_params=None, content_type="application/json"):
        """
        Delete a BankAccount
        It is method for DELETE /users/{username}/banks/{label}
        """
        uri = self.client.base_url + "/users/" + username + "/banks/" + label
        return self.client.delete(uri, None, headers, query_params, content_type)

    def GetUserBankAccountByLabel(
            self,
            username,
            label,
            headers=None,
            query_params=None,
            content_type="application/json"):
        """
        Get the details of a bank account
        It is method for GET /users/{username}/banks/{label}
        """
        uri = self.client.base_url + "/users/" + username + "/banks/" + label
        resp = self.client.get(uri, None, headers, query_params, content_type)
        try:
            if resp.status_code == 200:
                return APIResponse(data=BankAccount(resp.json()), response=resp)

            message = 'unknown status code={}'.format(resp.status_code)
            raise UnhandledAPIError(response=resp, code=resp.status_code,
                                    message=message)
        except ValueError as msg:
            raise UnmarshallError(resp, msg)
        except UnhandledAPIError as uae:
            raise uae
        except Exception as e:
            raise UnmarshallError(resp, e.message)

    def UpdateUserBankAccount(
            self,
            data,
            username,
            label,
            headers=None,
            query_params=None,
            content_type="application/json"):
        """
        Update an existing bankaccount and label.
        It is method for PUT /users/{username}/banks/{label}
        """
        uri = self.client.base_url + "/users/" + username + "/banks/" + label
        resp = self.client.put(uri, data, headers, query_params, content_type)
        try:
            if resp.status_code == 200:
                return APIResponse(data=BankAccount(resp.json()), response=resp)

            message = 'unknown status code={}'.format(resp.status_code)
            raise UnhandledAPIError(response=resp, code=resp.status_code,
                                    message=message)
        except ValueError as msg:
            raise UnmarshallError(resp, msg)
        except UnhandledAPIError as uae:
            raise uae
        except Exception as e:
            raise UnmarshallError(resp, e.message)

    def GetUserBankAccounts(self, username, headers=None, query_params=None, content_type="application/json"):
        """
        List of the user his bank accounts.
        It is method for GET /users/{username}/banks
        """
        uri = self.client.base_url + "/users/" + username + "/banks"
        resp = self.client.get(uri, None, headers, query_params, content_type)
        try:
            if resp.status_code == 200:
                resps = []
                for elem in resp.json():
                    resps.append(BankAccount(elem))
                return APIResponse(data=resps, response=resp)

            message = 'unknown status code={}'.format(resp.status_code)
            raise UnhandledAPIError(response=resp, code=resp.status_code,
                                    message=message)
        except ValueError as msg:
            raise UnmarshallError(resp, msg)
        except UnhandledAPIError as uae:
            raise uae
        except Exception as e:
            raise UnmarshallError(resp, e.message)

    def CreateUserBankAccount(self, data, username, headers=None, query_params=None, content_type="application/json"):
        """
        Create new bank account
        It is method for POST /users/{username}/banks
        """
        uri = self.client.base_url + "/users/" + username + "/banks"
        resp = self.client.post(uri, data, headers, query_params, content_type)
        try:
            if resp.status_code == 201:
                return APIResponse(data=BankAccount(resp.json()), response=resp)

            message = 'unknown status code={}'.format(resp.status_code)
            raise UnhandledAPIError(response=resp, code=resp.status_code,
                                    message=message)
        except ValueError as msg:
            raise UnmarshallError(resp, msg)
        except UnhandledAPIError as uae:
            raise uae
        except Exception as e:
            raise UnmarshallError(resp, e.message)

    def GetUserContracts(self, username, headers=None, query_params=None, content_type="application/json"):
        """
        Get the contracts where the user is 1 of the parties. Order descending by date.
        It is method for GET /users/{username}/contracts
        """
        uri = self.client.base_url + "/users/" + username + "/contracts"
        resp = self.client.get(uri, None, headers, query_params, content_type)
        try:
            if resp.status_code == 200:
                resps = []
                for elem in resp.json():
                    resps.append(Contract(elem))
                return APIResponse(data=resps, response=resp)

            message = 'unknown status code={}'.format(resp.status_code)
            raise UnhandledAPIError(response=resp, code=resp.status_code,
                                    message=message)
        except ValueError as msg:
            raise UnmarshallError(resp, msg)
        except UnhandledAPIError as uae:
            raise uae
        except Exception as e:
            raise UnmarshallError(resp, e.message)

    def CreateUserContract(self, data, username, headers=None, query_params=None, content_type="application/json"):
        """
        Create a new contract.
        It is method for POST /users/{username}/contracts
        """
        uri = self.client.base_url + "/users/" + username + "/contracts"
        resp = self.client.post(uri, data, headers, query_params, content_type)
        try:
            if resp.status_code == 201:
                return APIResponse(data=Contract(resp.json()), response=resp)

            message = 'unknown status code={}'.format(resp.status_code)
            raise UnhandledAPIError(response=resp, code=resp.status_code,
                                    message=message)
        except ValueError as msg:
            raise UnmarshallError(resp, msg)
        except UnhandledAPIError as uae:
            raise uae
        except Exception as e:
            raise UnmarshallError(resp, e.message)

    def DeleteDigitalAssetAddress(
            self,
            label,
            username,
            headers=None,
            query_params=None,
            content_type="application/json"):
        """
        Removes an address
        It is method for DELETE /users/{username}/digitalwallet/{label}
        """
        uri = self.client.base_url + "/users/" + username + "/digitalwallet/" + label
        return self.client.delete(uri, None, headers, query_params, content_type)

    def GetDigitalAssetAddressByLabel(
            self,
            label,
            username,
            headers=None,
            query_params=None,
            content_type="application/json"):
        """
        Get the details of a digital wallet address.
        It is method for GET /users/{username}/digitalwallet/{label}
        """
        uri = self.client.base_url + "/users/" + username + "/digitalwallet/" + label
        resp = self.client.get(uri, None, headers, query_params, content_type)
        try:
            if resp.status_code == 200:
                return APIResponse(data=DigitalAssetAddress(resp.json()), response=resp)

            message = 'unknown status code={}'.format(resp.status_code)
            raise UnhandledAPIError(response=resp, code=resp.status_code,
                                    message=message)
        except ValueError as msg:
            raise UnmarshallError(resp, msg)
        except UnhandledAPIError as uae:
            raise uae
        except Exception as e:
            raise UnmarshallError(resp, e.message)

    def UpdateDigitalAssetAddress(
            self,
            data,
            label,
            username,
            headers=None,
            query_params=None,
            content_type="application/json"):
        """
        Update the label and/or value of an existing address.
        It is method for PUT /users/{username}/digitalwallet/{label}
        """
        uri = self.client.base_url + "/users/" + username + "/digitalwallet/" + label
        return self.client.put(uri, data, headers, query_params, content_type)

    def GetDigitalWallet(self, username, headers=None, query_params=None, content_type="application/json"):
        """
        List all of the user his digital wallets.
        It is method for GET /users/{username}/digitalwallet
        """
        uri = self.client.base_url + "/users/" + username + "/digitalwallet"
        resp = self.client.get(uri, None, headers, query_params, content_type)
        try:
            if resp.status_code == 200:
                resps = []
                for elem in resp.json():
                    resps.append(DigitalAssetAddress(elem))
                return APIResponse(data=resps, response=resp)

            message = 'unknown status code={}'.format(resp.status_code)
            raise UnhandledAPIError(response=resp, code=resp.status_code,
                                    message=message)
        except ValueError as msg:
            raise UnmarshallError(resp, msg)
        except UnhandledAPIError as uae:
            raise uae
        except Exception as e:
            raise UnmarshallError(resp, e.message)

    def RegisterNewDigitalAssetAddress(
            self,
            data,
            username,
            headers=None,
            query_params=None,
            content_type="application/json"):
        """
        Register a new digital asset address
        It is method for POST /users/{username}/digitalwallet
        """
        uri = self.client.base_url + "/users/" + username + "/digitalwallet"
        resp = self.client.post(uri, data, headers, query_params, content_type)
        try:
            if resp.status_code == 201:
                return APIResponse(data=DigitalAssetAddress(resp.json()), response=resp)

            message = 'unknown status code={}'.format(resp.status_code)
            raise UnhandledAPIError(response=resp, code=resp.status_code,
                                    message=message)
        except ValueError as msg:
            raise UnmarshallError(resp, msg)
        except UnhandledAPIError as uae:
            raise uae
        except Exception as e:
            raise UnmarshallError(resp, e.message)

    def ValidateEmailAddress(
            self,
            data,
            label,
            username,
            headers=None,
            query_params=None,
            content_type="application/json"):
        """
        Sends validation email to email address
        It is method for POST /users/{username}/emailaddresses/{label}/validate
        """
        uri = self.client.base_url + "/users/" + username + "/emailaddresses/" + label + "/validate"
        return self.client.post(uri, data, headers, query_params, content_type)

    def DeleteEmailAddress(self, label, username, headers=None, query_params=None, content_type="application/json"):
        """
        Removes an email address
        It is method for DELETE /users/{username}/emailaddresses/{label}
        """
        uri = self.client.base_url + "/users/" + username + "/emailaddresses/" + label
        return self.client.delete(uri, None, headers, query_params, content_type)

    def UpdateEmailAddress(
            self,
            data,
            label,
            username,
            headers=None,
            query_params=None,
            content_type="application/json"):
        """
        Updates the label and/or value of an email address
        It is method for PUT /users/{username}/emailaddresses/{label}
        """
        uri = self.client.base_url + "/users/" + username + "/emailaddresses/" + label
        return self.client.put(uri, data, headers, query_params, content_type)

    def GetEmailAddresses(self, username, headers=None, query_params=None, content_type="application/json"):
        """
        Get a list of the user his email addresses.
        It is method for GET /users/{username}/emailaddresses
        """
        uri = self.client.base_url + "/users/" + username + "/emailaddresses"
        resp = self.client.get(uri, None, headers, query_params, content_type)
        try:
            if resp.status_code == 200:
                resps = []
                for elem in resp.json():
                    resps.append(EmailAddress(elem))
                return APIResponse(data=resps, response=resp)

            message = 'unknown status code={}'.format(resp.status_code)
            raise UnhandledAPIError(response=resp, code=resp.status_code,
                                    message=message)
        except ValueError as msg:
            raise UnmarshallError(resp, msg)
        except UnhandledAPIError as uae:
            raise uae
        except Exception as e:
            raise UnmarshallError(resp, e.message)

    def RegisterNewEmailAddress(self, data, username, headers=None, query_params=None, content_type="application/json"):
        """
        Register a new email address
        It is method for POST /users/{username}/emailaddresses
        """
        uri = self.client.base_url + "/users/" + username + "/emailaddresses"
        resp = self.client.post(uri, data, headers, query_params, content_type)
        try:
            if resp.status_code == 201:
                return APIResponse(data=EmailAddress(resp.json()), response=resp)

            message = 'unknown status code={}'.format(resp.status_code)
            raise UnhandledAPIError(response=resp, code=resp.status_code,
                                    message=message)
        except ValueError as msg:
            raise UnmarshallError(resp, msg)
        except UnhandledAPIError as uae:
            raise uae
        except Exception as e:
            raise UnmarshallError(resp, e.message)

    def DeleteFacebookAccount(self, username, headers=None, query_params=None, content_type="application/json"):
        """
        Delete the associated facebook account
        It is method for DELETE /users/{username}/facebook
        """
        uri = self.client.base_url + "/users/" + username + "/facebook"
        return self.client.delete(uri, None, headers, query_params, content_type)

    def DeleteGithubAccount(self, username, headers=None, query_params=None, content_type="application/json"):
        """
        Unlink Github Account
        It is method for DELETE /users/{username}/github
        """
        uri = self.client.base_url + "/users/" + username + "/github"
        return self.client.delete(uri, None, headers, query_params, content_type)

    def GetUserInformation(self, username, headers=None, query_params=None, content_type="application/json"):
        """
        Get all of the user his information. This will be limited to the scopes that the user has authorized. See https://gig.gitbooks.io/itsyouonline/content/oauth2/scopes.html and https://gig.gitbooks.io/itsyouonline/content/oauth2/availableScopes.html for more information.
        It is method for GET /users/{username}/info
        """
        uri = self.client.base_url + "/users/" + username + "/info"
        resp = self.client.get(uri, None, headers, query_params, content_type)
        try:
            if resp.status_code == 200:
                return APIResponse(data=userview(resp.json()), response=resp)

            message = 'unknown status code={}'.format(resp.status_code)
            raise UnhandledAPIError(response=resp, code=resp.status_code,
                                    message=message)
        except ValueError as msg:
            raise UnmarshallError(resp, msg)
        except UnhandledAPIError as uae:
            raise uae
        except Exception as e:
            raise UnmarshallError(resp, e.message)

    def GetKeyStoreKey(self, label, username, headers=None, query_params=None, content_type="application/json"):
        """
        Gets the key written to this users keystore for the given label by the accessing organization
        It is method for GET /users/{username}/keystore/{label}
        """
        uri = self.client.base_url + "/users/" + username + "/keystore/" + label
        resp = self.client.get(uri, None, headers, query_params, content_type)
        try:
            if resp.status_code == 200:
                return APIResponse(data=KeyStoreKey(resp.json()), response=resp)

            message = 'unknown status code={}'.format(resp.status_code)
            raise UnhandledAPIError(response=resp, code=resp.status_code,
                                    message=message)
        except ValueError as msg:
            raise UnmarshallError(resp, msg)
        except UnhandledAPIError as uae:
            raise uae
        except Exception as e:
            raise UnmarshallError(resp, e.message)

    def GetKeyStore(self, username, headers=None, query_params=None, content_type="application/json"):
        """
        Lists all keys written to this users keystore by the accessing organization
        It is method for GET /users/{username}/keystore
        """
        uri = self.client.base_url + "/users/" + username + "/keystore"
        resp = self.client.get(uri, None, headers, query_params, content_type)
        try:
            if resp.status_code == 200:
                resps = []
                for elem in resp.json():
                    resps.append(KeyStoreKey(elem))
                return APIResponse(data=resps, response=resp)

            message = 'unknown status code={}'.format(resp.status_code)
            raise UnhandledAPIError(response=resp, code=resp.status_code,
                                    message=message)
        except ValueError as msg:
            raise UnmarshallError(resp, msg)
        except UnhandledAPIError as uae:
            raise uae
        except Exception as e:
            raise UnmarshallError(resp, e.message)

    def SaveKeyStoreKey(self, data, username, headers=None, query_params=None, content_type="application/json"):
        """
        Saves a new key to this users keystore. The username, globalid and timestamp will be overwritten
        It is method for POST /users/{username}/keystore
        """
        uri = self.client.base_url + "/users/" + username + "/keystore"
        resp = self.client.post(uri, data, headers, query_params, content_type)
        try:
            if resp.status_code == 201:
                return APIResponse(data=KeyStoreKey(resp.json()), response=resp)

            message = 'unknown status code={}'.format(resp.status_code)
            raise UnhandledAPIError(response=resp, code=resp.status_code,
                                    message=message)
        except ValueError as msg:
            raise UnmarshallError(resp, msg)
        except UnhandledAPIError as uae:
            raise uae
        except Exception as e:
            raise UnmarshallError(resp, e.message)

    def UpdateUserName(self, data, username, headers=None, query_params=None, content_type="application/json"):
        """
        Update the user his firstname and lastname
        It is method for PUT /users/{username}/name
        """
        uri = self.client.base_url + "/users/" + username + "/name"
        return self.client.put(uri, data, headers, query_params, content_type)

    def GetNotifications(self, username, headers=None, query_params=None, content_type="application/json"):
        """
        Get the list of notifications, these are pending invitations or approvals or other requests.
        It is method for GET /users/{username}/notifications
        """
        uri = self.client.base_url + "/users/" + username + "/notifications"
        resp = self.client.get(uri, None, headers, query_params, content_type)
        try:
            if resp.status_code == 200:
                return APIResponse(data=Notification(resp.json()), response=resp)

            message = 'unknown status code={}'.format(resp.status_code)
            raise UnhandledAPIError(response=resp, code=resp.status_code,
                                    message=message)
        except ValueError as msg:
            raise UnmarshallError(resp, msg)
        except UnhandledAPIError as uae:
            raise uae
        except Exception as e:
            raise UnmarshallError(resp, e.message)

    def LeaveOrganization(self, globalid, username, headers=None, query_params=None, content_type="application/json"):
        """
        Removes the user from an organization
        It is method for DELETE /users/{username}/organizations/{globalid}/leave
        """
        uri = self.client.base_url + "/users/" + username + "/organizations/" + globalid + "/leave"
        resp = self.client.delete(uri, None, headers, query_params, content_type)
        try:

            message = 'unknown status code={}'.format(resp.status_code)
            raise UnhandledAPIError(response=resp, code=resp.status_code,
                                    message=message)
        except ValueError as msg:
            raise UnmarshallError(resp, msg)
        except UnhandledAPIError as uae:
            raise uae
        except Exception as e:
            raise UnmarshallError(resp, e.message)

    def RejectMembership(
            self,
            globalid,
            role,
            username,
            headers=None,
            query_params=None,
            content_type="application/json"):
        """
        Reject membership invitation in an organization.
        It is method for DELETE /users/{username}/organizations/{globalid}/roles/{role}
        """
        uri = self.client.base_url + "/users/" + username + "/organizations/" + globalid + "/roles/" + role
        return self.client.delete(uri, None, headers, query_params, content_type)

    def AcceptMembership(
            self,
            data,
            globalid,
            role,
            username,
            headers=None,
            query_params=None,
            content_type="application/json"):
        """
        Accept membership in organization
        It is method for POST /users/{username}/organizations/{globalid}/roles/{role}
        """
        uri = self.client.base_url + "/users/" + username + "/organizations/" + globalid + "/roles/" + role
        resp = self.client.post(uri, data, headers, query_params, content_type)
        try:
            if resp.status_code == 201:
                return APIResponse(data=JoinOrganizationInvitation(resp.json()), response=resp)

            message = 'unknown status code={}'.format(resp.status_code)
            raise UnhandledAPIError(response=resp, code=resp.status_code,
                                    message=message)
        except ValueError as msg:
            raise UnmarshallError(resp, msg)
        except UnhandledAPIError as uae:
            raise uae
        except Exception as e:
            raise UnmarshallError(resp, e.message)

    def GetUserOrganizations(self, username, headers=None, query_params=None, content_type="application/json"):
        """
        Get the list organizations a user is owner or member of
        It is method for GET /users/{username}/organizations
        """
        uri = self.client.base_url + "/users/" + username + "/organizations"
        resp = self.client.get(uri, None, headers, query_params, content_type)
        try:
            if resp.status_code == 200:
                return APIResponse(data=UserOrganizations(resp.json()), response=resp)

            message = 'unknown status code={}'.format(resp.status_code)
            raise UnhandledAPIError(response=resp, code=resp.status_code,
                                    message=message)
        except ValueError as msg:
            raise UnmarshallError(resp, msg)
        except UnhandledAPIError as uae:
            raise uae
        except Exception as e:
            raise UnmarshallError(resp, e.message)

    def UpdatePassword(self, data, username, headers=None, query_params=None, content_type="application/json"):
        """
        Update the user his password
        It is method for PUT /users/{username}/password
        """
        uri = self.client.base_url + "/users/" + username + "/password"
        resp = self.client.put(uri, data, headers, query_params, content_type)
        try:

            message = 'unknown status code={}'.format(resp.status_code)
            raise UnhandledAPIError(response=resp, code=resp.status_code,
                                    message=message)
        except ValueError as msg:
            raise UnmarshallError(resp, msg)
        except UnhandledAPIError as uae:
            raise uae
        except Exception as e:
            raise UnmarshallError(resp, e.message)

    def ValidatePhonenumber(
            self,
            data,
            label,
            username,
            headers=None,
            query_params=None,
            content_type="application/json"):
        """
        Sends a validation text message to the phone number.
        It is method for POST /users/{username}/phonenumbers/{label}/validate
        """
        uri = self.client.base_url + "/users/" + username + "/phonenumbers/" + label + "/validate"
        resp = self.client.post(uri, data, headers, query_params, content_type)
        try:
            if resp.status_code == 200:
                return APIResponse(data=PhoneNumberValidation(resp.json()), response=resp)

            message = 'unknown status code={}'.format(resp.status_code)
            raise UnhandledAPIError(response=resp, code=resp.status_code,
                                    message=message)
        except ValueError as msg:
            raise UnmarshallError(resp, msg)
        except UnhandledAPIError as uae:
            raise uae
        except Exception as e:
            raise UnmarshallError(resp, e.message)

    def VerifyPhoneNumber(
            self,
            data,
            label,
            username,
            headers=None,
            query_params=None,
            content_type="application/json"):
        """
        Verifies a phone number
        It is method for PUT /users/{username}/phonenumbers/{label}/validate
        """
        uri = self.client.base_url + "/users/" + username + "/phonenumbers/" + label + "/validate"
        resp = self.client.put(uri, data, headers, query_params, content_type)
        try:

            message = 'unknown status code={}'.format(resp.status_code)
            raise UnhandledAPIError(response=resp, code=resp.status_code,
                                    message=message)
        except ValueError as msg:
            raise UnmarshallError(resp, msg)
        except UnhandledAPIError as uae:
            raise uae
        except Exception as e:
            raise UnmarshallError(resp, e.message)

    def DeleteUserPhonenumber(self, label, username, headers=None, query_params=None, content_type="application/json"):
        """
        Removes a phonenumber
        It is method for DELETE /users/{username}/phonenumbers/{label}
        """
        uri = self.client.base_url + "/users/" + username + "/phonenumbers/" + label
        return self.client.delete(uri, None, headers, query_params, content_type)

    def GetUserPhonenumberByLabel(
            self,
            label,
            username,
            headers=None,
            query_params=None,
            content_type="application/json"):
        """
        Get the details of a phone number.
        It is method for GET /users/{username}/phonenumbers/{label}
        """
        uri = self.client.base_url + "/users/" + username + "/phonenumbers/" + label
        resp = self.client.get(uri, None, headers, query_params, content_type)
        try:
            if resp.status_code == 200:
                return APIResponse(data=Phonenumber(resp.json()), response=resp)

            message = 'unknown status code={}'.format(resp.status_code)
            raise UnhandledAPIError(response=resp, code=resp.status_code,
                                    message=message)
        except ValueError as msg:
            raise UnmarshallError(resp, msg)
        except UnhandledAPIError as uae:
            raise uae
        except Exception as e:
            raise UnmarshallError(resp, e.message)

    def UpdateUserPhonenumber(
            self,
            data,
            label,
            username,
            headers=None,
            query_params=None,
            content_type="application/json"):
        """
        Update the label and/or value of an existing phonenumber.
        It is method for PUT /users/{username}/phonenumbers/{label}
        """
        uri = self.client.base_url + "/users/" + username + "/phonenumbers/" + label
        return self.client.put(uri, data, headers, query_params, content_type)

    def GetUserPhoneNumbers(self, username, headers=None, query_params=None, content_type="application/json"):
        """
        List of all of the user his phone numbers.
        It is method for GET /users/{username}/phonenumbers
        """
        uri = self.client.base_url + "/users/" + username + "/phonenumbers"
        resp = self.client.get(uri, None, headers, query_params, content_type)
        try:
            if resp.status_code == 200:
                resps = []
                for elem in resp.json():
                    resps.append(Phonenumber(elem))
                return APIResponse(data=resps, response=resp)

            message = 'unknown status code={}'.format(resp.status_code)
            raise UnhandledAPIError(response=resp, code=resp.status_code,
                                    message=message)
        except ValueError as msg:
            raise UnmarshallError(resp, msg)
        except UnhandledAPIError as uae:
            raise uae
        except Exception as e:
            raise UnmarshallError(resp, e.message)

    def RegisterNewUserPhonenumber(
            self,
            data,
            username,
            headers=None,
            query_params=None,
            content_type="application/json"):
        """
        Register a new phonenumber
        It is method for POST /users/{username}/phonenumbers
        """
        uri = self.client.base_url + "/users/" + username + "/phonenumbers"
        resp = self.client.post(uri, data, headers, query_params, content_type)
        try:
            if resp.status_code == 201:
                return APIResponse(data=Phonenumber(resp.json()), response=resp)

            message = 'unknown status code={}'.format(resp.status_code)
            raise UnhandledAPIError(response=resp, code=resp.status_code,
                                    message=message)
        except ValueError as msg:
            raise UnmarshallError(resp, msg)
        except UnhandledAPIError as uae:
            raise uae
        except Exception as e:
            raise UnmarshallError(resp, e.message)

    def DeletePublicKey(self, label, username, headers=None, query_params=None, content_type="application/json"):
        """
        Delete a public key
        It is method for DELETE /users/{username}/publickeys/{label}
        """
        uri = self.client.base_url + "/users/" + username + "/publickeys/" + label
        return self.client.delete(uri, None, headers, query_params, content_type)

    def GetPublicKey(self, label, username, headers=None, query_params=None, content_type="application/json"):
        """
        Get a public key
        It is method for GET /users/{username}/publickeys/{label}
        """
        uri = self.client.base_url + "/users/" + username + "/publickeys/" + label
        resp = self.client.get(uri, None, headers, query_params, content_type)
        try:
            if resp.status_code == 200:
                return APIResponse(data=PublicKey(resp.json()), response=resp)

            message = 'unknown status code={}'.format(resp.status_code)
            raise UnhandledAPIError(response=resp, code=resp.status_code,
                                    message=message)
        except ValueError as msg:
            raise UnmarshallError(resp, msg)
        except UnhandledAPIError as uae:
            raise uae
        except Exception as e:
            raise UnmarshallError(resp, e.message)

    def UpdatePublicKey(self, data, label, username, headers=None, query_params=None, content_type="application/json"):
        """
        Upates the label and/or key of an existing public key
        It is method for PUT /users/{username}/publickeys/{label}
        """
        uri = self.client.base_url + "/users/" + username + "/publickeys/" + label
        resp = self.client.put(uri, data, headers, query_params, content_type)
        try:
            if resp.status_code == 201:
                return APIResponse(data=PublicKey(resp.json()), response=resp)

            message = 'unknown status code={}'.format(resp.status_code)
            raise UnhandledAPIError(response=resp, code=resp.status_code,
                                    message=message)
        except ValueError as msg:
            raise UnmarshallError(resp, msg)
        except UnhandledAPIError as uae:
            raise uae
        except Exception as e:
            raise UnmarshallError(resp, e.message)

    def ListPublicKeys(self, username, headers=None, query_params=None, content_type="application/json"):
        """
        Lists all public keys
        It is method for GET /users/{username}/publickeys
        """
        uri = self.client.base_url + "/users/" + username + "/publickeys"
        resp = self.client.get(uri, None, headers, query_params, content_type)
        try:
            if resp.status_code == 200:
                resps = []
                for elem in resp.json():
                    resps.append(PublicKey(elem))
                return APIResponse(data=resps, response=resp)

            message = 'unknown status code={}'.format(resp.status_code)
            raise UnhandledAPIError(response=resp, code=resp.status_code,
                                    message=message)
        except ValueError as msg:
            raise UnmarshallError(resp, msg)
        except UnhandledAPIError as uae:
            raise uae
        except Exception as e:
            raise UnmarshallError(resp, e.message)

    def AddPublicKey(self, data, username, headers=None, query_params=None, content_type="application/json"):
        """
        Add a public key
        It is method for POST /users/{username}/publickeys
        """
        uri = self.client.base_url + "/users/" + username + "/publickeys"
        resp = self.client.post(uri, data, headers, query_params, content_type)
        try:
            if resp.status_code == 201:
                return APIResponse(data=PublicKey(resp.json()), response=resp)

            message = 'unknown status code={}'.format(resp.status_code)
            raise UnhandledAPIError(response=resp, code=resp.status_code,
                                    message=message)
        except ValueError as msg:
            raise UnmarshallError(resp, msg)
        except UnhandledAPIError as uae:
            raise uae
        except Exception as e:
            raise UnmarshallError(resp, e.message)

    def DeleteUserRegistryEntry(self, key, username, headers=None, query_params=None, content_type="application/json"):
        """
        Removes a RegistryEntry from the user's registry
        It is method for DELETE /users/{username}/registry/{key}
        """
        uri = self.client.base_url + "/users/" + username + "/registry/" + key
        return self.client.delete(uri, None, headers, query_params, content_type)

    def GetUserRegistryEntry(self, key, username, headers=None, query_params=None, content_type="application/json"):
        """
        Get a RegistryEntry from the user's registry.
        It is method for GET /users/{username}/registry/{key}
        """
        uri = self.client.base_url + "/users/" + username + "/registry/" + key
        resp = self.client.get(uri, None, headers, query_params, content_type)
        try:
            if resp.status_code == 200:
                return APIResponse(data=RegistryEntry(resp.json()), response=resp)

            message = 'unknown status code={}'.format(resp.status_code)
            raise UnhandledAPIError(response=resp, code=resp.status_code,
                                    message=message)
        except ValueError as msg:
            raise UnmarshallError(resp, msg)
        except UnhandledAPIError as uae:
            raise uae
        except Exception as e:
            raise UnmarshallError(resp, e.message)

    def ListUserRegistry(self, username, headers=None, query_params=None, content_type="application/json"):
        """
        Lists the Registry entries
        It is method for GET /users/{username}/registry
        """
        uri = self.client.base_url + "/users/" + username + "/registry"
        resp = self.client.get(uri, None, headers, query_params, content_type)
        try:
            if resp.status_code == 200:
                resps = []
                for elem in resp.json():
                    resps.append(RegistryEntry(elem))
                return APIResponse(data=resps, response=resp)

            message = 'unknown status code={}'.format(resp.status_code)
            raise UnhandledAPIError(response=resp, code=resp.status_code,
                                    message=message)
        except ValueError as msg:
            raise UnmarshallError(resp, msg)
        except UnhandledAPIError as uae:
            raise uae
        except Exception as e:
            raise UnmarshallError(resp, e.message)

    def AddUserRegistryEntry(self, data, username, headers=None, query_params=None, content_type="application/json"):
        """
        Adds a RegistryEntry to the user's registry, if the key is already used, it is overwritten.
        It is method for POST /users/{username}/registry
        """
        uri = self.client.base_url + "/users/" + username + "/registry"
        resp = self.client.post(uri, data, headers, query_params, content_type)
        try:
            if resp.status_code == 201:
                return APIResponse(data=RegistryEntry(resp.json()), response=resp)

            message = 'unknown status code={}'.format(resp.status_code)
            raise UnhandledAPIError(response=resp, code=resp.status_code,
                                    message=message)
        except ValueError as msg:
            raise UnmarshallError(resp, msg)
        except UnhandledAPIError as uae:
            raise uae
        except Exception as e:
            raise UnmarshallError(resp, e.message)

    def SignSeeObject(
            self,
            data,
            version,
            uniqueid,
            globalid,
            username,
            headers=None,
            query_params=None,
            content_type="application/json"):
        """
        Sign a see object
        It is method for PUT /users/{username}/see/{uniqueid}/{globalid}/sign/{version}
        """
        uri = self.client.base_url + "/users/" + username + "/see/" + uniqueid + "/" + globalid + "/sign/" + version
        resp = self.client.put(uri, data, headers, query_params, content_type)
        try:
            if resp.status_code == 201:
                return APIResponse(data=SeeView(resp.json()), response=resp)

            message = 'unknown status code={}'.format(resp.status_code)
            raise UnhandledAPIError(response=resp, code=resp.status_code,
                                    message=message)
        except ValueError as msg:
            raise UnmarshallError(resp, msg)
        except UnhandledAPIError as uae:
            raise uae
        except Exception as e:
            raise UnmarshallError(resp, e.message)

    def GetSeeObject(
            self,
            uniqueid,
            globalid,
            username,
            headers=None,
            query_params=None,
            content_type="application/json"):
        """
        Get a see object
        It is method for GET /users/{username}/see/{uniqueid}/{globalid}
        """
        uri = self.client.base_url + "/users/" + username + "/see/" + uniqueid + "/" + globalid
        resp = self.client.get(uri, None, headers, query_params, content_type)
        try:
            if resp.status_code == 200:
                return APIResponse(data=See(resp.json()), response=resp)

            message = 'unknown status code={}'.format(resp.status_code)
            raise UnhandledAPIError(response=resp, code=resp.status_code,
                                    message=message)
        except ValueError as msg:
            raise UnmarshallError(resp, msg)
        except UnhandledAPIError as uae:
            raise uae
        except Exception as e:
            raise UnmarshallError(resp, e.message)

    def UpdateSeeObject(
            self,
            data,
            uniqueid,
            globalid,
            username,
            headers=None,
            query_params=None,
            content_type="application/json"):
        """
        Updates a see object
        It is method for PUT /users/{username}/see/{uniqueid}/{globalid}
        """
        uri = self.client.base_url + "/users/" + username + "/see/" + uniqueid + "/" + globalid
        resp = self.client.put(uri, data, headers, query_params, content_type)
        try:
            if resp.status_code == 201:
                return APIResponse(data=SeeView(resp.json()), response=resp)

            message = 'unknown status code={}'.format(resp.status_code)
            raise UnhandledAPIError(response=resp, code=resp.status_code,
                                    message=message)
        except ValueError as msg:
            raise UnmarshallError(resp, msg)
        except UnhandledAPIError as uae:
            raise uae
        except Exception as e:
            raise UnmarshallError(resp, e.message)

    def GetSeeObjects(self, username, headers=None, query_params=None, content_type="application/json"):
        """
        Get a list of all see objects.
        It is method for GET /users/{username}/see
        """
        uri = self.client.base_url + "/users/" + username + "/see"
        resp = self.client.get(uri, None, headers, query_params, content_type)
        try:
            if resp.status_code == 200:
                resps = []
                for elem in resp.json():
                    resps.append(SeeView(elem))
                return APIResponse(data=resps, response=resp)

            message = 'unknown status code={}'.format(resp.status_code)
            raise UnhandledAPIError(response=resp, code=resp.status_code,
                                    message=message)
        except ValueError as msg:
            raise UnmarshallError(resp, msg)
        except UnhandledAPIError as uae:
            raise uae
        except Exception as e:
            raise UnmarshallError(resp, e.message)

    def CreateSeeObject(self, data, username, headers=None, query_params=None, content_type="application/json"):
        """
        Create new see object
        It is method for POST /users/{username}/see
        """
        uri = self.client.base_url + "/users/" + username + "/see"
        resp = self.client.post(uri, data, headers, query_params, content_type)
        try:
            if resp.status_code == 201:
                return APIResponse(data=SeeView(resp.json()), response=resp)

            message = 'unknown status code={}'.format(resp.status_code)
            raise UnhandledAPIError(response=resp, code=resp.status_code,
                                    message=message)
        except ValueError as msg:
            raise UnmarshallError(resp, msg)
        except UnhandledAPIError as uae:
            raise uae
        except Exception as e:
            raise UnmarshallError(resp, e.message)

    def RemoveTOTP(self, username, headers=None, query_params=None, content_type="application/json"):
        """
        Disable TOTP two-factor authentication.
        It is method for DELETE /users/{username}/totp
        """
        uri = self.client.base_url + "/users/" + username + "/totp"
        return self.client.delete(uri, None, headers, query_params, content_type)

    def GetTOTPSecret(self, username, headers=None, query_params=None, content_type="application/json"):
        """
        Get a TOTP secret and issuer that can be used for setting up two-factor authentication.
        It is method for GET /users/{username}/totp
        """
        uri = self.client.base_url + "/users/" + username + "/totp"
        resp = self.client.get(uri, None, headers, query_params, content_type)
        try:
            if resp.status_code == 200:
                return APIResponse(data=TOTPSecret(resp.json()), response=resp)

            message = 'unknown status code={}'.format(resp.status_code)
            raise UnhandledAPIError(response=resp, code=resp.status_code,
                                    message=message)
        except ValueError as msg:
            raise UnmarshallError(resp, msg)
        except UnhandledAPIError as uae:
            raise uae
        except Exception as e:
            raise UnmarshallError(resp, e.message)

    def SetupTOTP(self, data, username, headers=None, query_params=None, content_type="application/json"):
        """
        Enable two-factor authentication using TOTP.
        It is method for POST /users/{username}/totp
        """
        uri = self.client.base_url + "/users/" + username + "/totp"
        return self.client.post(uri, data, headers, query_params, content_type)

    def GetTwoFAMethods(self, username, headers=None, query_params=None, content_type="application/json"):
        """
        Get the possible two-factor authentication methods"
        It is method for GET /users/{username}/twofamethods
        """
        uri = self.client.base_url + "/users/" + username + "/twofamethods"
        resp = self.client.get(uri, None, headers, query_params, content_type)
        try:
            if resp.status_code == 200:
                return APIResponse(data=TwoFAMethods(resp.json()), response=resp)

            message = 'unknown status code={}'.format(resp.status_code)
            raise UnhandledAPIError(response=resp, code=resp.status_code,
                                    message=message)
        except ValueError as msg:
            raise UnmarshallError(resp, msg)
        except UnhandledAPIError as uae:
            raise uae
        except Exception as e:
            raise UnmarshallError(resp, e.message)

    def GetUser(self, username, headers=None, query_params=None, content_type="application/json"):
        """
        It is method for GET /users/{username}
        """
        uri = self.client.base_url + "/users/" + username
        resp = self.client.get(uri, None, headers, query_params, content_type)
        try:
            if resp.status_code == 200:
                return APIResponse(data=User(resp.json()), response=resp)

            message = 'unknown status code={}'.format(resp.status_code)
            raise UnhandledAPIError(response=resp, code=resp.status_code,
                                    message=message)
        except ValueError as msg:
            raise UnmarshallError(resp, msg)
        except UnhandledAPIError as uae:
            raise uae
        except Exception as e:
            raise UnmarshallError(resp, e.message)

    def CreateUser(self, data, headers=None, query_params=None, content_type="application/json"):
        """
        Create a new user
        It is method for POST /users
        """
        uri = self.client.base_url + "/users"
        return self.client.post(uri, data, headers, query_params, content_type)
