The Miro Python client library offers a comprehensive interface for integrating Miro's REST API capabilities into Python-based applications.

You can use the client to implement back-end functionality in your Miro app, such as:

- OAuth 2.0 authorization
- Programmatic data exchange with an external system
- Data storage in the app backend

The library provides two main components:

- A **stateful high-level client** ( `Miro` class) for handling user interactions, including authorization and token management.
- A **stateless low-level client** ( `MiroApi` object) for back-end communications, automation scripts, and operations requiring the OAuth access token. Additionally, `MiroApi` methods enable retrieving organization information and managing teams and users (available via Enterprise API for users on an Enterprise plan).

## Prerequisites [Skip link to Prerequisites](https://developers.miro.com/docs/miro-python-client#prerequisites)

- Python 3.9 or higher.

## Installation [Skip link to Installation](https://developers.miro.com/docs/miro-python-client#installation)

To integrate the `miro_api` package into your project, you can use either **pip** or **poetry** as follows:

**Using [pip](https://github.com/pypa/pip)**:

Bash

```rdmd-code lang-bash theme-light

pip install miro_api

```

**Using [poetry](https://python-poetry.org/docs/)**:

Bash

```rdmd-code lang-bash theme-light

poetry add miro_api

```

## Configuration [Skip link to Configuration](https://developers.miro.com/docs/miro-python-client#configuration)

The high-level client ( `Miro`) automatically loads app configuration from the following environment variables:

- `MIRO_CLIENT_ID`
- `MIRO_CLIENT_SECRET`
- `MIRO_REDIRECT_URL`

Alternatively, these values can be passed directly to the `Miro` constructor.

## Quickstart [Skip link to Quickstart](https://developers.miro.com/docs/miro-python-client#quickstart)

To start using the high-level `Miro` client, import it, and then create a new instance:

Python

```rdmd-code lang-python theme-light

import miro_api

miro = miro_api.Miro()

print(miro.auth_url)

```

Or, initialize it with custom configuration:

Python

```rdmd-code lang-python theme-light

import miro_api

miro = miro_api.Miro(
  client_id='<your_app_client_id>>',
  client_secret='<your_app_client_secret>',
  redirect_url='https://example.com/miro/redirect/url',
)

print(miro.auth_url)

```

To start using the low-level `MiroApi` client, import it, and then create a new instance:

Python

```rdmd-code lang-python theme-light

import miro_api

api = miro_api.MiroApi('<access_token>')

print(api.get_boards())

```

## OAuth authorization [Skip link to OAuth authorization](https://developers.miro.com/docs/miro-python-client#oauth-authorization)

The `Miro` client provides methods to manage the OAuth authorization flow:

1. Check if the current user has authorized the app: `miro.is_authorized`.
2. Redirect for authorization if needed: `miro.auth_url`.
3. Exchange authorization code for an access token: `miro.exchange_code_for_access_token(code)`.
4. Make API calls on behalf of the authorized user: `miro.api.get_board(board_id)`

## Storage [Skip link to Storage](https://developers.miro.com/docs/miro-python-client#storage)

For storing user access and refresh tokens, the client library requires persistent storage. The client automatically refreshes access tokens before making API calls, if they are nearing their expiration time.

By default, persistent storage uses an in-memory dictionary to store state information. Pass `storage` to the `Miro` constructor as an option:

Python

```rdmd-code lang-python theme-light

miro = miro_api.Miro(
  storage=CustomMiroStorage(),
)

```

To support the client library storage functionality in your app, implement the following `get` and `set` interface:

Python

```rdmd-code lang-python theme-light

class Storage(ABC):
    """Abstract class used by the stateful client to set and get State."""

    @abstractmethod
    def set(self, state: Optional[State]) -> None:
        pass

    @abstractmethod
    def get(self) -> Optional[State]:
        pass

```

> ## 🚧
>
> For production deployments, we recommend using a custom implementation backed by a database.

### Reference [Skip link to Reference](https://developers.miro.com/docs/miro-python-client#reference)

- [Miro Python library reference](https://miroapp.github.io/api-clients/python/)

### Examples [Skip link to Examples](https://developers.miro.com/docs/miro-python-client#examples)

See an example of implementing a simple server using Flask library in the [example](https://github.com/miroapp/api-clients/tree/main/packages/miro-api-python/example) directory.

Updated3 months ago

---

Did this page help you?

Yes

No
