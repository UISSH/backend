from upgrade import CURRENT_VERSION


SPECTACULAR_DEFAULTS = {
    # path prefix is used for tagging the discovered operations.
    # use '/api/v[0-9]' for tagging apis like '/api/v1/albums' with ['albums']
    "SCHEMA_PATH_PREFIX": r"/api/",
    "DEFAULT_GENERATOR_CLASS": "drf_spectacular.generators.SchemaGenerator",
    # Schema generation parameters to influence how components are constructed.
    # Some schema features might not translate well to your target.
    # Demultiplexing/modifying components might help alleviate those issues.
    #
    # Create separate components for PATCH endpoints (without required list)
    "COMPONENT_SPLIT_PATCH": True,
    # Split components into request and response parts where appropriate
    "COMPONENT_SPLIT_REQUEST": False,
    # Aid client generator targets that have trouble with read-only properties.
    "COMPONENT_NO_READ_ONLY_REQUIRED": False,
    # Configuration for serving the schema with SpectacularAPIView
    "SERVE_URLCONF": None,
    # complete public schema or a subset based on the requesting user
    "SERVE_PUBLIC": True,
    # is the
    "SERVE_INCLUDE_SCHEMA": True,
    "SERVE_PERMISSIONS": ["rest_framework.permissions.AllowAny"],
    # Dictionary of configurations to pass to the SwaggerUI({ ... })
    # https://swagger.io/docs/open-source-tools/swagger-ui/usage/configuration/
    "SWAGGER_UI_SETTINGS": {
        "deepLinking": True,
    },
    "SWAGGER_UI_DIST": "//fastly.jsdelivr.net/npm/swagger-ui-dist@3.51.1",
    "SWAGGER_UI_FAVICON_HREF": "//fastly.jsdelivr.net/npm/swagger-ui-dist@3.51.1/favicon-32x32.png",
    # Append OpenAPI objects to path and components in addition to the generated objects
    "APPEND_PATHS": {},
    "APPEND_COMPONENTS": {},
    # DISCOURAGED - please don't use this anymore as it has tricky implications that
    # are hard to get right. For authentication, OpenApiAuthenticationExtension are
    # strongly preferred because they are more robust and easy to write.
    # However if used, the list of methods is appended to every endpoint in the schema!
    "SECURITY": [],
    # Postprocessing functions that run at the end of schema generation.
    # must satisfy interface result = hook(generator, request, public, result)
    "POSTPROCESSING_HOOKS": ["drf_spectacular.hooks.postprocess_schema_enums"],
    # Preprocessing functions that run before schema generation.
    # must satisfy interface result = hook(endpoints=result) where result
    # is a list of Tuples (path, path_regex, method, callback).
    # Example: 'drf_spectacular.hooks.preprocess_exclude_path_format'
    "PREPROCESSING_HOOKS": [],
    # enum name overrides. dict with keys "YourEnum" and their choice values "field.choices"
    "ENUM_NAME_OVERRIDES": {},
    # function that returns a list of all classes that should be excluded from doc string extraction
    "GET_LIB_DOC_EXCLUDES": "drf_spectacular.plumbing.get_lib_doc_excludes",
    # Function that returns a mocked request for view processing. For CLI usage
    # original_request will be None.
    # interface: request = build_mock_request(method, path, view, original_request, **kwargs)
    "GET_MOCK_REQUEST": "drf_spectacular.plumbing.build_mock_request",
    # Camelize names like operationId and path parameter names
    "CAMELIZE_NAMES": False,
    # General schema metadata. Refer to spec for valid inputs
    # https://github.com/OAI/OpenAPI-Specification/blob/master/versions/3.0.3.md#openapi-object
    "TITLE": "UISSH",
    "DESCRIPTION": "轻量、简约的面板",
    "TOS": None,
    # Optional: MAY contain "name", "url", "email"
    "CONTACT": {"name": "zmaplex", "email": "zmaplex@gmail.com"},
    # Optional: MUST contain "name", MAY contain URL
    "LICENSE": {"name": "Apache 2.0"},
    "VERSION": CURRENT_VERSION,
    # Optional list of servers.
    # Each entry MUST contain "url", MAY contain "description", "variables"
    "SERVERS": [],
    # Tags defined in the global scope
    "TAGS": [],
    # Optional: MUST contain 'url', may contain "description"
    "EXTERNAL_DOCS": {},
    # Oauth2 related settings. used for example by django-oauth2-toolkit.
    # https://github.com/OAI/OpenAPI-Specification/blob/master/versions/3.0.3.md#oauth-flows-object
    "OAUTH2_FLOWS": [],
    "OAUTH2_AUTHORIZATION_URL": None,
    "OAUTH2_TOKEN_URL": None,
    "OAUTH2_REFRESH_URL": None,
    "OAUTH2_SCOPES": None,
}
