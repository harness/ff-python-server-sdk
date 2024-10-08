# Further Reading

Covers advanced topics (different config options and scenarios)

## Configuration Options
The following configuration options are available to control the behaviour of the SDK.
You can pass the configuration in as options when the SDK client is created.
```python
    # Create a Feature Flag Client
    client = CfClient(apiKey,
                      with_base_url("https://config.ff.harness.io/api/1.0"),
                      with_events_url("https://events.ff.harness.io/api/1.0"),
                      with_stream_enabled(True),
                      with_analytics_enabled(True),
                      config=Config(pull_interval=60))
```

| Name            | Config Option                                            | Description                                                                                                                                      | default                              |
|-----------------|----------------------------------------------------------|--------------------------------------------------------------------------------------------------------------------------------------------------|--------------------------------------|
| baseUrl         | with_base_url("https://config.ff.harness.io/api/1.0")    | the URL used to fetch feature flag evaluations. You should change this when using the Feature Flag proxy to http://localhost:7000                | https://config.ff.harness.io/api/1.0 |
| eventsUrl       | with_events_url("https://events.ff.harness.io/api/1.0"), | the URL used to post metrics data to the feature flag service. You should change this when using the Feature Flag proxy to http://localhost:7000 | https://events.ff.harness.io/api/1.0 |
| pollInterval    | Config(pull_interval=60)                                 | when running in stream mode, the interval in seconds that we poll for changes.                                                                   | 60                                   |
| enableStream    | with_stream_enabled(True),                               | Enable streaming mode.                                                                                                                           | true                                 |
| enableAnalytics | with_analytics_enabled(True)                             | Enable analytics.  Metrics data is posted every 60s                                                                                              | true                                 |
| pollInterval    | with_poll_interval(120)                                  | When running in stream mode, the interval in seconds that we poll for changes.                                                                   | 60                                   |
| maxAuthRetries  | with_max_auth_retries(10)                                | The number of retry attempts to make if client authentication fails on a retryable HTTP error                                                    | 10                                   |

# Anonymous Target

If you do not want a `Target` to be sent to Harness servers, you can use the `anonymous` attribute. 

```python
    target = Target(identifier='my_identifier', name='my_name', anonymous=True)
```            


## Logging Configuration
The SDK provides a logger that wraps the standard python logging package.  You can import and use it with:
```python
from featureflags.util import log
log.info("Hello, World!")
```

If you want to change the default log level, you can use the standard logging levels
```python
from featureflags.util import log
import logging

log.setLevel(logging.WARN)
```

## Recommended reading

[Feature Flag Concepts](https://ngdocs.harness.io/article/7n9433hkc0-cf-feature-flag-overview)

[Feature Flag SDK Concepts](https://ngdocs.harness.io/article/rvqprvbq8f-client-side-and-server-side-sdks)

## Setting up your Feature Flags

[Feature Flags Getting Started](https://ngdocs.harness.io/article/0a2u2ppp8s-getting-started-with-feature-flags)

## Other Variation Types

### String Variation 
```python
client.string_variation('identifier_of_your_string_flag', target, "default string")
```
[Example](../examples/string_variation_example/string_variation.py)

### Number Variation
```python
client.number_variation('identifier_of_your_number_flag', target, -1)
```
[Example](../examples/number_variation_example/number_variation.py)

### JSON Variation
```python
client.json_variation('identifier_of_your_json_flag', target, {})
```
[Example](../examples/json_variation_example/json_variation.py)

## Cleanup
Call the close function on the client 

```python
client.close()
```
[Example](../examples/cleanup_example/cleanup.py)

## Change default URL

When using your Feature Flag SDKs with a [Harness Relay Proxy](https://ngdocs.harness.io/article/q0kvq8nd2o-relay-proxy) you need to change the default URL.

To do this you import the url helper functions 

```python
from featureflags.config import with_base_url
from featureflags.config import with_events_url

```

Then pass them with the new URLs when creating your client.

```python
    client = CfClient(api_key,
                      with_base_url("https://config.feature-flags.uat.harness.io/api/1.0"),
                      with_events_url("https://event.feature-flags.uat.harness.io/api/1.0"))
```

[Example](../examples/url_change_example/url_change.py)

## HTTPX Configuration Options
The `httpx` client allows you to apply various configurations to all outgoing requests by passing parameters to the Client constructor. 

Here are some of the options you can configure:

* `proxies`: Configure proxy settings to route requests through a specific proxy server.
* `headers`: Add custom headers to all outgoing requests.
* `timeout`: Set request and connection timeouts.
* `transport`: Use a custom transport layer for advanced scenarios.

**Important**: ensure you supply a valid httpx option. if you supply an option that doesn't exist in `httpx` the SDK will fail to initialize with `got an unexpected keyword argument` 

Further Reading:

* [HTTPX Advanced Client Configuration](https://www.python-httpx.org/advanced/clients/)

Example of Custom HTTPX Client Configuration

Here's an example demonstrating how to use httpx client arguments in the SDK:


```python
from featureflags.config import with_httpx_args

client = CfClient(api_key,
                  with_base_url("https://config.ff.harness.io/api/1.0"),
                  with_httpx_args({
                      'proxies': 'http://localhost:8888'}
                  }))
```

[Example](../examples/with_httpx_args_example/with_httpx_args.py)
