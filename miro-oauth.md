Getting Started with Miro's OAuth 2.0 in 3 minutes - YouTube

Miro for Developers

782 subscribers

[Getting Started with Miro's OAuth 2.0 in 3 minutes](https://www.youtube.com/watch?v=2vqZK4qPcno)

Miro for Developers

Search

Watch later

Share

Copy link

Info

Shopping

Tap to unmute

If playback doesn't begin shortly, try restarting your device.

More videos

## More videos

You're signed out

Videos you watch may be added to the TV's watch history and influence TV recommendations. To avoid this, cancel and sign in to YouTube on your computer.

CancelConfirm

Share

Include playlist

An error occurred while retrieving sharing information. Please try again later.

[Watch on](https://www.youtube.com/watch?v=2vqZK4qPcno&embeds_widget_referrer=https%3A%2F%2Fdevelopers.miro.com%2F&embeds_referring_euri=https%3A%2F%2Fcdn.embedly.com%2F&embeds_referring_origin=https%3A%2F%2Fcdn.embedly.com)

0:00

0:00 / 4:53
•Live

•

[Watch on YouTube](https://www.youtube.com/watch?v=2vqZK4qPcno "Watch on YouTube")

This guide explains how to implement the OAuth 2.0 authorization code flow for Miro. By following these steps, you can obtain an access token and interact with Miro’s REST API on behalf of a user. You will learn how to:

1. Prompt users to install your app in Miro.
2. Exchange an authorization code for an access token.
3. Use the access token in REST API calls.
4. Request a new access token with a refresh token.

## Goal [Skip link to Goal](https://developers.miro.com/docs/getting-started-with-oauth#goal)

Acquire an OAuth 2.0 access token that allows you to make REST API calls to Miro on behalf of a user.

## Prerequisites [Skip link to Prerequisites](https://developers.miro.com/docs/getting-started-with-oauth#prerequisites)

Before you begin, ensure that you have:

- [Created a Developer team](https://developers.miro.com/docs/create-a-developer-team).
- [Created your app](https://developers.miro.com/docs/rest-api-build-your-first-hello-world-app#step-1-create-your-app-in-miro).
- [Configured your app](https://developers.miro.com/docs/rest-api-build-your-first-hello-world-app#step-2-configure-your-app-in-miro).
- [Installed your app](https://developers.miro.com/docs/rest-api-build-your-first-hello-world-app#step-3-install-the-app).

> ## 🚧 Client ID and client secret
>
> Be sure to note your **client ID** and **client secret**. You’ll need both values when exchanging codes for tokens and when requesting refresh tokens.

## Step 1: Prompt users to install your app [Skip link to Step 1: Prompt users to install your app](https://developers.miro.com/docs/getting-started-with-oauth#step-1-prompt-users-to-install-your-app)

The OAuth 2.0 authorization code flow begins with prompting a user to install and authorize your app in Miro. This step is where the user grants your app permission to interact with their Miro content.

> ## 📘 Tip
>
> For details about the specific permissions you can request, see the [Scopes reference](https://miro-ea.readme.io/reference/scopes).

1. Create an authorization request link. You’ll need the following parameters to build the link:

   - **Miro authorization base URL**: `https://miro.com/oauth/authorize`
   - **response_type**: `code`
   - **client_id**: Your app’s client ID
   - **redirect_uri**: A redirect URI that you configure in your [App Settings](https://miro.com/app/settings/user-profile/apps)

**Example request link**:

Shell

```rdmd-code lang-sh theme-light

https://miro.com/oauth/authorize
    ?response_type=code
    &client_id={YOUR_CLIENT_ID}
    &redirect_uri={YOUR_REDIRECT_URI}

```

Make sure that your `redirect_uri` can handle both successful and unsuccessful authorization attempts.

2. Direct the user to this link. In your application, you might have a **Sign in to Miro** or **Sync to Miro** button. When the user clicks this button, redirect them to the authorization link. The user is then prompted to:

   - Sign in with Miro credentials.
   - Review the permissions your app is requesting.
   - Approve or reject the request.

> ## 📘 Note
>
> If you are using the Miro logo in your app or integration, ensure your usage complies with the [Miro branding guidelines](https://brandkit.miro.com/corporate-visual-identity/introduction).

## Step 2: Exchange authorization code for an access token [Skip link to Step 2: Exchange authorization code for an access token](https://developers.miro.com/docs/getting-started-with-oauth#step-2-exchange-authorization-code-for-an-access-token)

After the user installs and authorizes your application, Miro returns an **authorization code**. This authorization code **cannot** be used for API calls directly; you must exchange it for an **access token**.

> ## 📘 Note
>
> Some authentication endpoints have `v1` in the URL; these endpoints are not deprecated.

To exchange the authorization code for an access token, make an HTTP POST request to Miro’s token endpoint. Include:

- **client_id** (required)
- **client_secret** (required)
- **code** (the authorization code you received)
- **redirect_uri** (must match your app settings)
- **grant_type**: `authorization_code`

**Example cURL**:

Bash

```rdmd-code lang-bash theme-light

curl --request POST
    --url '<https://api.miro.com/v1/oauth/token>
        ?grant_type=authorization_code
        &client_id={CLIENT_ID}
        &client_secret={CLIENT_SECRET}
        &code={AUTHORIZATION_CODE}
        &redirect_uri={REDIRECT_URI}'

```

**Example response**:

JSON

```rdmd-code lang-json theme-light

{
    "user_id": "9876543210123456789",
    "refresh_token": "eyJtaXJvLm9yaWdpbiI6ImV1MDEifQ_-PIBKmE9rzQuL3bUeAvUEGFEhLk",
    "access_token": "eyJtaXJvLm9yaWdpbiI6ImV1MDEifQ_o-P91OccaII0A63CDSK--x21xiI",
    "expires_in": 3599,
    "team_id": "1234567890987654321",
    "scope": "boards:write boards:read",
    "token_type": "bearer"
}

```

You are responsible for storing and securing this token data. A common practice is to store these tokens in a database, linked to your users’ Miro information.

## Step 3: Use the access token for REST API requests [Skip link to Step 3: Use the access token for REST API requests](https://developers.miro.com/docs/getting-started-with-oauth#step-3-use-the-access-token-for-rest-api-requests)

With a valid access token, you can make REST API calls on behalf of the user.

- Include the access token in the `Authorization` header.
- Use the format `Bearer {ACCESS_TOKEN}`.

**Example cURL**:

Bash

```rdmd-code lang-bash theme-light

curl --request GET
    --url <https://api.miro.com/v2/boards/{BOARD_ID}>
    --header 'Authorization: Bearer {ACCESS_TOKEN}'

```

## Step 4: Request a new access token using a refresh token [Skip link to Step 4: Request a new access token using a refresh token](https://developers.miro.com/docs/getting-started-with-oauth#step-4-request-a-new-access-token-using-a-refresh-token)

Miro recommends using expiring access tokens. By default, an access token is valid for 60 minutes and includes a **refresh token** that remains valid for 60 days. If the access token expires or is compromised, you can use the refresh token to request a new access token.

When you request a new access token using a refresh token, the response includes:

- A **new access token**
- A **new refresh token** (resetting the validity period for 60 days)

To request a new token with the refresh token, make an HTTP `POST` request to the same Miro token endpoint. This time, set **grant_type** to `refresh_token` and include your current refresh token. You do not need to include the `redirect_uri`.

**Example cURL**:

Bash

```rdmd-code lang-bash theme-light

curl --request POST
    --url '<https://api.miro.com/v1/oauth/token>
        ?grant_type=refresh_token
        &client_id={CLIENT_ID}
        &client_secret={CLIENT_SECRET}
        &refresh_token={REFRESH_TOKEN}'

```

Updated4 months ago

---

Learn how to enable REST API authentication from Miro's Web SDK authorization.

- [Enable REST API authentication from Miro's Web SDK authorization](https://developers.miro.com/docs/enable-rest-api-authentication-from-miros-web-sdk-authorization-1)

Did this page help you?

Yes

No
