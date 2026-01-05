
# Nodes

- **Process**
    - `name`: "ALM Authentication Flow"
    - `process_type`: "oauth2_openid_connect_authentication"
    - `authentication_methods`: ["username_password", "totp_mfa"]
    - `protocol`: "OpenID Connect with OAuth2 Authorization Code Flow"
    - `NOTE`: "Complete authentication process for ALM application access. Multi-step OAuth2/OpenID Connect flow involving F5 policy enforcement, Keycloak IDP authentication with MFA (username/password + TOTP), and OAuth2 proxy handling. Process includes initial policy check, dual authentication rounds, and final application access grant. Uses authorization code flow with client_id 'idp-123' and scopes 'openid profile email'."
- **User**
    - `id`: "Web_User"
    - `user_type`: "end_user"
    - `authentication_factors`: ["username_password", "totp"]
    - `NOTE`: "End user attempting to access ALM application through web browser. Must complete multi-factor authentication including username/password credentials and TOTP (Time-based One-Time Password) before gaining access to application."
- **Component**
    - `name`: "F5 Firewall"
    - `type`: "security_component"
    - `component_subtype`: "load_balancer_firewall"
    - `domain`: "<env>-alm.website.com"
    - `policy_endpoint`: "/my.policy"
    - `NOTE`: "F5 load balancer and firewall serving as entry point for ALM application. Handles initial HTTP GET requests to <env>-alm.website.com and enforces authentication policy by redirecting users to /my.policy endpoint, then to IDP for authentication. Uses HTTP 302 redirects to guide authentication flow."
- **Component**
    - `name`: "IDP"
    - `type`: "security_component"
    - `component_subtype`: "identity_provider"
    - `domain`: "idp.cloud.website.com"
    - `realm_based`: true
    - `auth_endpoint`: "/auth/realms/{realm}/openid-connect/auth"
    - `login_endpoint`: "/auth/realms/{realm}/login-actions/authenticate"
    - `client_id`: "idp-123"
    - `supported_scopes`: ["openid", "profile", "email"]
    - `mfa_enabled`: true
    - `NOTE`: "Keycloak Identity Provider handling OpenID Connect authentication. Located at idp.cloud.website.com with realm-based configuration. Supports multi-factor authentication requiring username/password followed by TOTP. Handles OAuth2 authorization code flow with client_id 'idp-123' and issues authorization codes for authenticated users."
- **Component**
    - `name`: "IDP Proxy"
    - `type`: "security_component"
    - `component_subtype`: "oauth2_proxy"
    - `domain`: "<env>-alm.website.com"
    - `callback_endpoints`: ["/oauth/client/redirect", "/oauth2/callback"]
    - `NOTE": "OAuth2 proxy component handling OAuth2 callbacks and token exchanges. Manages dual redirect flow: first handling /oauth/client/redirect from initial authentication, then managing /oauth2/callback for final token exchange. Acts as intermediary between ALM application and IDP for complete OAuth2 flow."
- **Component**
    - `name`: "ALM app"
    - `type`: "web_app"
    - `component_subtype`: "application_lifecycle_management"
    - `domain`: "<env>-alm.website.com"
    - `protected_by_oauth2`: true
    - `NOTE`: "Application Lifecycle Management web application providing API endpoints for data access. Requires complete OAuth2/OpenID Connect authentication flow before granting access. Final destination after successful authentication process, serving content at root endpoint '/'."

# Relationships

(:Web_User)-[:PARTICIPATES_IN]->(:ALM Authentication Flow)
    - `NOTE`: "User initiates and participates in the complete authentication process to gain access to ALM application"
    - `STEP`: 0

(:F5 Firewall)-[:PARTICIPATES_IN]->(:ALM Authentication Flow)
    - `NOTE`: "F5 Firewall enforces the authentication process by implementing policy checks and redirecting unauthenticated users"
    - `STEP`: 0

(:IDP)-[:PARTICIPATES_IN]->(:ALM Authentication Flow)
    - `NOTE`: "Identity Provider performs the core authentication including MFA validation for the process"
    - `STEP`: 0

(:IDP Proxy)-[:PARTICIPATES_IN]->(:ALM Authentication Flow)
    - `NOTE`: "OAuth2 proxy manages token exchanges and callback handling for the authentication process"
    - `STEP`: 0

(:ALM app)-[:PARTICIPATES_IN]->(:ALM Authentication Flow)
    - `NOTE`: "ALM application is protected by and grants access after successful completion of authentication process"
    - `STEP`: 0

(:Web_User)-[:SENDS_REQUEST_TO]->(:F5 Firewall)
    - `NOTE`: "Initial HTTP GET request to ALM application at <env>-alm.website.com"
    - `STEP`: 1

(:F5 Firewall)-[:RESPONSES_TO]->(:Web_User)
    - `NOTE`: "302 Redirect to policy endpoint <env>-alm.website.com/my.policy"
    - `STEP`: 2

(:Web_User)-[:SENDS_REQUEST_TO]->(:F5 Firewall)
    - `NOTE`: "HTTP GET request to policy endpoint /my.policy"
    - `STEP`: 3

(:F5 Firewall)-[:RESPONSES_TO]->(:Web_User)
    - `NOTE`: