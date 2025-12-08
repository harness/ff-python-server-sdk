=======
History
=======

1.7.3 (2021-07-07)
------------------

	FFM-12570: Testing webhooks for Harness Code, no code changes

1.7.2 (2025-03-19)
------------------

	fix: [FFM-12349]: fix bool equals clause by @conormurray95 in #109

1.7.1 (2025-01-23)
------------------

	fix: [FFM-12288]: bump lru cache default size by @conormurray95 in #107

1.7.0 (2024-08-27)
------------------

	FFM-11935 Add with_httpx_args option by @zane-zeroflucs and @erdirowlands in #106
    	See httpx options for further information
    	See with_httpx_args for a sample


1.6.4 (2024-07-05)
------------------

	FFM-11770 Fixes an issue where SDK dependencies tenacity and typing_extensions were pinned to fixed versions, which could make integration with the SDK impossible by @erdirowlands in #102

1.6.3 (2024-07-03)
------------------


    FFM-11655 Pin typing_extensions to latest release compatible with 3.7 by @erdirowlands in #98
    PL-51773 Add guard around debug log by @jcox250 in #100


1.6.2 (2024-06-25)
------------------


    FFM-11655 Sort AND/OR rules when caching group instead of during an evaluation call, which could result in latency if a group is large by @erdirowlands in #96
    FFM-11655 Fix error from being logged when metrics are processed if a target does not have any attributes by @erdirowlands in #97


1.6.1 (2024-05-08)
------------------


    [FFM-11244] - Target v2: Adding SDK support for AND/OR rules (feature not GA yet) by @andybharness in #90
    FFM-11441 Improve the retry logic used by SDK http requests, and improve the clarity of logs if requests fail by @erdirowlands in #92
    FFM-11331 Only delete cache key if it exists by @erdirowlands in #93


1.6.0 (2024-03-15)
------------------

	[FFM-7006] - Add support for custom TLS CA certs by @andybharness in #89

1.5.0 (2024-03-13)
------------------

	FFM-10837 Keeps track of targets that have been used in evaluations, and will not send already seen targets in metrics payloads. This allows fair processing of new targets for analytics purposes.


	FFM-10837 Fixes issue where if a target was marked as anonymous, it would be sent in analytics.
	FFM-10837 Fix typing of get_flag_kind method

1.4.0 (2024-01-15)
------------------

    FFM-10393 Add get_flag_type public method which enables you to check the type of a flag at any time by @erdirowlands in #87
        For an example of using this method, see get_flag_type.py
    FFM-10393 Add a more robust variation method int_or_float_variation to evaluate number flags. This method ensures that a number flag with integer or float variations (or both) will be evaluated correctly. The int_variation and number_variation methods could fail to evaluate depending on if the variation served was of the expected type. We recommend using this new method going forward for number flag evaluations.


1.3.0 (2023-11-24)
------------------

    Bump pip from 21.1 to 23.3 by @dependabot in #82

    Bump requests from 2.25.1 to 2.31.0 by @dependabot in #61

    [FFM-10040] - For percentage rollout, change Murmur3 hash calculation to be unsigned instead of signed. This ensures the Python SDK produces the same hash as other SDKs for use in percentage rollout calculation by @andybharness in #85

    FFM-10063 by @erdirowlands in #86 :
        Fixed an issue where the SDK would try to fetch deleted resources from the server receiving SSE delete events, resulting in 404 errors. Now, deleted resources are only removed from the local cache.
        If flag/group requests fails after exceeding all retry attempts, the SDK now throws and catches an exception instead of returning None, which would previously resulted in an uncaught AttributeError.
        If the SDK fails to initialize, it now stores the error. Subsequent evaluation requests return the default variation along with the error/SDK code immediately.
        Fixed an issue where requesting a variation on the wrong flag type (e.g., requesting a boolean on a string) would not behave as expected. Now, an SDK error code is logged, and the default variation is returned in such cases.
        Fixed an issue where polling would not stop if streaming is enabled. Additionally, fixed an issue where the poller would stop and not make any more flag updates after encountering an exception during a request.
        Enhanced logging to correctly indicate when a stream disconnects and the system falls back to polling.
        Changed various verbose logs from info to debug.


    Flag/group requests now implement a retry mechanism, attempting up to 10 retries on retryable errors.


1.2.5 (2023-11-08)
------------------

	FFM-9866 Only log Flag/Segment not found warning in valid scenarios @erdirowlands in #84

1.2.4 (2023-11-08)
------------------

	FFM-9866 Set default log level to WARNING by @erdirowlands in #83

1.2.3 (2023-10-26)
------------------

	FFM-9737 Fixes an issue where SDKCODE1003 was logged even when wait_for_initialzation was not called by @erdirowlands in #81

1.2.2 (2023-07-17)
------------------

	FFM-8544 Fixes an issue where the SDK will crash when used with the relay proxy

1.2.1 (2023-07-04)
------------------

	FFM-8544: Low level streaming logs no longer get logged as errors.

1.2.0 (2023-06-28)
------------------

	FFM-8300:
    	The SDK now sends targets to the metrics service in batches of 1000. Up to 200 batches, or 200K unique targets, can be sent in the metrics window. This is not user configurable, and is controlled via the SDK.
    	Does not allow events_sync_interval to be set below 60 seconds. If it is, the value will default to 60 seconds.


1.1.16 (2023-06-21)
-------------------

	FFM-8231 - Sets a maximum metrics Target limit of 50k for a single interval and increases the Metrics API timeout to 30 seconds.

1.1.15 (2023-06-09)
-------------------

    FFM-7363 - Adds a list of codes which are logged for each lifecycle of the SDK:
        Initialization
        Authentication
        Polling
        Streaming
        Evaluation
        Metrics
        Close
        For the full list of codes see https://developer.harness.io/docs/feature-flags/ff-sdks/server-sdks/python-sdk-reference/#troubleshooting

    FFM-7363 - Previously the SDK would crash if client.close() was called if at any point before a stream event was sent to SDK. The SDK now closes all threads correctly.
    Full Changelog: 1.1.14...1.1.15


1.1.14 (2023-06-05)
-------------------


    FFM-7177 - The SDK will now retry on failed Client authentication requests for specific HTTP errors. If Client authentication fails, the SDK will serve the default values you provide in variation calls.
    FFM-7362 - Adds additional headers to requests to the Feature Flags service to aid debugging.
    Full Changelog: 1.1.12...1.1.13


1.1.12 (2023-05-25)
------------------

	FFM-7880 - If an error occurs when processing a new stream event, the SDK will now log that error correctly instead of potentially logging a blank string by @erdirowlands in #63

1.1.11 (2023-05-24)
------------------

	FFM-6410 - The SDK will now evaluate a flag with multiple and/or nested prerequisites correctly by @erdirowlands in #62

1.1.10 (2023-04-05)
------------------

	FFM-7360 - The SDK will now log an error if an evaluation fails and the default variation is returned by @erdirowlands in #58


1.1.9 (2023-02-21)
------------------

	FFM-6932 - SDK seems to disconnect from the relay proxy by @andybharness in #57

1.1.8 (2023-02-08)
------------------

    [FFM-6549]: Add wait_for_initialization to the client API which can be called to block the thread until all groups and flags have been retrieved and loaded into cache.
    [FFM-6549]: Add is_initialized to the client API which can be called at any time to check if the initial retrieval and caching of groups and flags has been completed.


1.1.7 (2023-02-06)
------------------

	[FFM-5991]:

    	Adding Targets to Group based on conditions: the in operator is now case-sensitive in the SDK.

	Important: Please read before upgrading to this release:

    	if you are targeting any Groups using the in operator, please ensure that your Target condition takes into account the case sensitivity of the operator.


1.1.6 (2022-12-14)
------------------

	[FFM-5995]: Target Attribute values which were not strings would result in a 500 error from the metric service.

1.1.5 (2022-12-13)
------------------

	[FFM-5995]:
    	All unique Targets would not get registered during a metrics interval
    	The first metrics posting after Client initialisation could result in a 400 error


1.1.4 (2022-11-29)
------------------

	[FFM-5352]: Stream errors cause the SDK to spam ff server requests
	[FFM-5263]: Fix pre-req evaluations


1.0.1 (2021-07-07)
------------------

	* First release on PyPI.
